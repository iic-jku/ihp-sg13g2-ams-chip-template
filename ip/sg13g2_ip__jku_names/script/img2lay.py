# SPDX-FileCopyrightText: 2024 Leo Moser, 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Convert an image to a GDS layout, pixels on one layer framed by boundary layers.
#
# Light pixels are drawn by default and --invert draws the dark ones, which is the usual case for a
# dark logo on a white background. Every horizontal run of drawn pixels becomes one rectangle of
# --pixel-size um height on the foreground layer, and --merge joins the rectangles into polygons.
# The block edge is set with --block-size, which scales the image so that the GDS boundary and the
# LEF SIZE written by the Makefile agree, or with --scale for a plain downscale factor.
# Layers are given as <layer>/<datatype> or as a drawing-layer name of the active PDK such as
# Metal4, TopMetal1, prBoundary or NoMetFiller, which is resolved through the PDK's KLayout layer
# properties file $PDK_ROOT/$PDK/libs.tech/klayout/tech/<pdk>.lyp.

import argparse
import math
import os
import sys
import xml.etree.ElementTree as ET

import klayout.db as db
from PIL import Image


def pdk_layers():
    """Return {name: (layer, datatype)} for the drawing layers of the active PDK, or {} without a PDK."""
    pdk_root = os.environ.get("PDK_ROOT")
    pdk = os.environ.get("PDK")
    if not pdk_root or not pdk:
        return {}
    short = pdk[len("ihp-"):] if pdk.startswith("ihp-") else pdk
    lyp = os.path.join(pdk_root, pdk, "libs.tech", "klayout", "tech", f"{short}.lyp")
    if not os.path.isfile(lyp):
        return {}
    table = {}

    def walk(node):
        for props in node.findall("properties"):
            name = props.findtext("name") or ""
            source = props.findtext("source") or ""
            if name.endswith(".drawing") and "/" in source:
                layer, datatype = source.split("@")[0].split("/")
                table[name[: -len(".drawing")]] = (int(layer), int(datatype))
            walk(props)

    walk(ET.parse(lyp).getroot())
    return table


def layer_info(spec, table):
    """Turn '50/0' or a PDK drawing-layer name such as 'Metal4' into a LayerInfo."""
    if "/" in spec:
        layer, datatype = spec.split("/")
        return db.LayerInfo(int(layer), int(datatype))
    if spec in table:
        return db.LayerInfo(*table[spec])
    names = ", ".join(sorted(table)) if table else "none, PDK_ROOT or PDK is not set"
    sys.exit(f"[ERROR] Unknown layer '{spec}'. Use <layer>/<datatype> or a PDK drawing layer: {names}")


def load_bitmap(path, threshold, invert_alpha):
    """Open the image, put it on a white (or black) background and threshold it to a 1-bit image."""
    img = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", img.size, "BLACK" if invert_alpha else "WHITE")
    background.paste(img, (0, 0), img)
    gray = background.convert("L")
    return gray.point(lambda x: 255 if x > threshold else 0).convert("1")


def convert_to_gds(image_path, gds_path, cellname, pixel_size, scale, block_size, threshold,
                   invert, invert_alpha, merge, smooth, foreground, boundaries):
    table = pdk_layers()
    foreground_layer = layer_info(foreground, table)
    boundary_layers = [layer_info(boundary, table) for boundary in boundaries]

    bitmap = load_bitmap(image_path, threshold, invert_alpha)
    width, height = bitmap.size
    if block_size is not None:
        # Whole pixels only, so the artwork never exceeds the boundary drawn at block_size.
        columns = max(1, math.floor(block_size / pixel_size + 1e-9))
        rows = max(1, round(columns * height / width))
        bitmap.thumbnail((columns, rows), Image.LANCZOS)
    elif scale != 1.0:
        bitmap.thumbnail((width * scale, height * scale), Image.LANCZOS)
    width, height = bitmap.size

    ly = db.Layout()
    ly.dbu = 0.001
    top = ly.create_cell(cellname)
    step = int(round(pixel_size / ly.dbu))
    pixels = bitmap.load()

    region = db.Region()
    runs = 0
    for y in range(height):
        bottom = (height - y - 1) * step
        x = 0
        while x < width:
            if bool(pixels[x, y]) == invert:
                x += 1
                continue
            start = x
            while x < width and bool(pixels[x, y]) != invert:
                x += 1
            region.insert(db.Box(start * step, bottom, x * step, bottom + step))
            runs += 1

    if merge:
        region.merge()
        if smooth:
            region = region.smoothed(int(round(pixel_size * 0.99 / ly.dbu)))
    top.shapes(ly.layer(foreground_layer)).insert(region)

    if block_size is not None:
        block_width, block_height = block_size, block_size * height / width
    else:
        block_width, block_height = width * pixel_size, height * pixel_size
    for layer in boundary_layers:
        top.shapes(ly.layer(layer)).insert(db.DBox(0, 0, block_width, block_height))

    ly.write(gds_path)
    shapes = f"{region.count()} polygons" if merge else f"{runs} rectangles"
    print(f"[INFO] {gds_path}: cell {cellname}, {block_width:g} um x {block_height:g} um, "
          f"{width} x {height} pixels of {pixel_size:g} um, {shapes} on {foreground}.")


def main():
    parser = argparse.ArgumentParser(prog="img2lay", description="Convert an image to a GDS layout.")
    parser.add_argument("image_path", help="input image (PNG or any other format Pillow reads)")
    parser.add_argument("gds_path", help="output GDS file")
    parser.add_argument("--cellname", default="TOP", help="name of the top cell (default: TOP)")
    parser.add_argument("--pixel-size", type=float, default=0.5,
                        help="edge of one pixel in um (default: 0.5)")
    size = parser.add_mutually_exclusive_group()
    size.add_argument("--block-size", type=float,
                      help="block edge in um, the image is scaled to it and the boundary layers are drawn at that size")
    size.add_argument("--scale", type=float, default=1.0,
                      help="downscale factor for the image, e.g. 0.5 (default: 1.0)")
    parser.add_argument("--threshold", type=int, default=128,
                        help="gray level above which a pixel counts as light (default: 128)")
    parser.add_argument("--invert", action="store_true",
                        help="draw the dark pixels instead of the light ones")
    parser.add_argument("--invert-alpha", action="store_true",
                        help="put transparent pixels on a black instead of a white background")
    parser.add_argument("--merge", action="store_true",
                        help="merge the pixel rectangles into polygons")
    parser.add_argument("--smooth", action="store_true",
                        help="smooth the merged polygons by one pixel (needs --merge)")
    parser.add_argument("--foreground", default="Metal5",
                        help="layer of the pixels as <layer>/<datatype> or PDK drawing-layer name (default: Metal5)")
    parser.add_argument("--boundary", nargs="*", default=["prBoundary", "NoMetFiller"],
                        help="boundary layers around the block (default: prBoundary NoMetFiller)")
    args = parser.parse_args()

    if args.pixel_size <= 0:
        sys.exit("[ERROR] --pixel-size must be positive.")
    if args.block_size is not None and args.block_size <= 0:
        sys.exit("[ERROR] --block-size must be positive.")
    if not os.path.isfile(args.image_path):
        sys.exit(f"[ERROR] No such image: {args.image_path}")

    convert_to_gds(args.image_path, args.gds_path, args.cellname, args.pixel_size, args.scale,
                   args.block_size, args.threshold, args.invert, args.invert_alpha, args.merge,
                   args.smooth, args.foreground, args.boundary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
