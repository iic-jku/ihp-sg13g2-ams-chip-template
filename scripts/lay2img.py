# SPDX-FileCopyrightText: 2025 Leo Moser, 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0

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
        (1, 0),      # Activ        (gf180: COMP 22/0)
        (31, 0),     # NWell        (gf180: Nwell 21/0)
        (32, 0),     # nBuLay       (gf180: LVPWELL 204/0)
        (44, 0),     # ThickGateOx  (gf180: Dualgate 55/0)
        (5, 0),      # GatPoly      (gf180: Poly2 30/0)
        (7, 0),      # nSD          (gf180: Nplus 32/0)
        (14, 0),     # pSD          (gf180: Pplus 31/0)
        (28, 0),     # SalBlock     (gf180: SAB 49/0)
        (6, 0),      # Cont         (gf180: Contact 33/0)
        (8, 0),      # Metal1       (gf180: Metal1 34/0)
        (19, 0),     # Via1         (gf180: Via1 35/0)
        (10, 0),     # Metal2       (gf180: Metal2 36/0)
        (29, 0),     # Via2         (gf180: Via2 38/0)
        (30, 0),     # Metal3       (gf180: Metal3 42/0)
        (49, 0),     # Via3         (gf180: Via3 40/0)
        (50, 0),     # Metal4       (gf180: Metal4 46/0)
        (66, 0),     # Via4         (gf180: Via4 41/0)
        (67, 0),     # Metal5       (gf180: Metal5 81/0)
        (125, 0),    # TopVia1
        (126, 0),    # TopMetal1
        (133, 0),    # TopVia2
        (134, 0),    # TopMetal2
        (9, 0),      # Passiv       (gf180: Pad 37/0)
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
