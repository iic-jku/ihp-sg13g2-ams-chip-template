# SPDX-FileCopyrightText: 2025 Leo Moser, 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1

import os
import argparse
import klayout.lay as lay
import klayout.db as db


def main(input_layout, output_image, width, height, oversampling, pdk_root, pdk):

    # Background colors
    background_white = "#FFFFFF"
    background_black = "#000000"

    lv = lay.LayoutView()

    lv.set_config("grid-visible", "false")
    lv.set_config("grid-show-ruler", "false")
    lv.set_config("text-visible", "false")

    lv.load_layout(input_layout, 0)
    lv.max_hier()

    top_cell = lv.active_cellview().layout().top_cell()
    top_bbox = top_cell.dbbox()
    aspect_ratio = top_bbox.width() / top_bbox.height()

    if not height and not width:
        width = 1024

    if not height:
        height = int(width / aspect_ratio)

    # Load the layer properties
    lv.load_layer_props(
        os.path.join(pdk_root, pdk, "libs.tech", "klayout", "tech", "sg13g2.lyp")
    )

    # Disable some layers
    enabled_layers = [
        (1, 0),      # Activ
        (31, 0),     # NWell
        (32, 0),     # nBuLay
        (44, 0),     # ThickGateOx
        (5, 0),      # GatPoly
        (7, 0),      # nSD
        (14, 0),     # pSD
        (28, 0),     # SalBlock
        (6, 0),      # Cont
        (8, 0),      # Metal1
        (19, 0),     # Via1
        (10, 0),     # Metal2
        (29, 0),     # Via2
        (30, 0),     # Metal3
        (49, 0),     # Via3
        (50, 0),     # Metal4
        (66, 0),     # Via4
        (36, 0),     # MIM
        (129, 0),    # Via MIM
        (67, 0),     # Metal5
        (125, 0),    # TopVia1
        (126, 0),    # TopMetal1
        (133, 0),    # TopVia2
        (134, 0),    # TopMetal2
        # (134, 22), # TopMetal2 Filler
        (9, 0),      # Passiv
    ]
    for lyp in lv.each_layer():
        layer_datatype = (lyp.source_layer, lyp.source_datatype)

        if layer_datatype not in enabled_layers:
            lyp.visible = False

    # Save the images
    base_name = os.path.splitext(os.path.basename(output_image))[0]
    directory = os.path.dirname(output_image)

    lv.set_config("background-color", background_white)
    lv.save_image_with_options(
        os.path.join(directory, base_name + "_white.png"),
        width,
        height,
        oversampling=oversampling,
    )

    lv.set_config("background-color", background_black)
    lv.save_image_with_options(
        os.path.join(directory, base_name + "_black.png"),
        width,
        height,
        oversampling=oversampling,
    )


if __name__ == "__main__":

    pdk_root = os.getenv("PDK_ROOT", "IHP-Open-PDK")
    pdk = os.getenv("PDK", "ihp-sg13g2")

    parser = argparse.ArgumentParser(
        prog="lay2img", description="Convert a layout to an image."
    )
    parser.add_argument("layout", help="input layout")
    parser.add_argument("image", help="output image")
    parser.add_argument("--width", type=int, default=None, help="image width")
    parser.add_argument("--height", type=int, default=None, help="image height")
    parser.add_argument(
        "--oversampling", type=int, default=1, help="oversampling factor"
    )

    args = parser.parse_args()

    main(
        args.layout,
        args.image,
        args.width,
        args.height,
        args.oversampling,
        pdk_root,
        pdk,
    )
