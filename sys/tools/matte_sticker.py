#!/usr/bin/env python3
"""Deterministic Morphological Flood-fill Matting and Sticker Outline generator.

Designed for Video Pilot stick-figure artwork on flat-white backgrounds.
Unlike general AI segmentation (rembg, u2net) which erroneously hollows out white
heads, plates, and speech bubbles, this morphological algorithm flood-fills strictly
from the image borders, preserving 100% of interior white regions bounded by black outlines.
"""

import argparse
import glob
import os
from pathlib import Path
from typing import Optional, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
try:
    from scipy import ndimage as ndi
except ImportError:
    ndi = None


def floodfill_matte(
    image_input: Union[str, Path, Image.Image],
    white_thresh: int = 225,
    delta_thresh: int = 22,
    min_island_ratio: float = 0.002,
    blur_radius: float = 0.8,
    edge_darken: float = 0.35,
) -> Image.Image:
    """Extract foreground transparent PNG from a flat-white background image.

    Args:
        image_input: Path to image file or PIL Image instance.
        white_thresh: Minimum brightness on RGB channels to classify as white background.
        delta_thresh: Maximum difference between max and min channel (ensures neutrality).
        min_island_ratio: Minimum area ratio of foreground component to keep (filters JPEG/watermark noise).
        blur_radius: Gaussian blur radius on alpha mask for smooth anti-aliased edges.
        edge_darken: Multiplier to darken semi-transparent edge pixels to kill white halos.

    Returns:
        PIL Image in RGBA mode with background removed.
    """
    if isinstance(image_input, (str, Path)):
        im = Image.open(str(image_input)).convert("RGB")
    else:
        im = image_input.convert("RGB")

    rgb = np.array(im).astype(np.int16)

    # 1. Identify near-white pixels
    white = (rgb.min(-1) > white_thresh) & ((rgb.max(-1) - rgb.min(-1)) < delta_thresh)

    # 2. Connected Component Labeling / Flood-fill of white regions
    if ndi is not None:
        lab, n_features = ndi.label(white)
        border_pixels = np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]])
        border_labels = set(np.unique(border_pixels)) - {0}
        bg = np.isin(lab, list(border_labels))
        fg = ~bg
        fg = ndi.binary_opening(fg, iterations=1)  # eliminate single JPEG noise pixels
        lab2, n_fg = ndi.label(fg)
        if n_fg > 0:
            sizes = ndi.sum(fg, lab2, range(1, n_fg + 1))
            keep_labels = 1 + np.where(sizes > min_island_ratio * fg.size)[0]
            fg = np.isin(lab2, keep_labels)
    else:
        # Morphological flood-fill fallback using Pillow when scipy is not installed
        white_mask = Image.fromarray((white * 255).astype(np.uint8), mode="L").copy()
        w, h = white_mask.size
        for x in range(w):
            if white_mask.getpixel((x, 0)) == 255:
                ImageDraw.floodfill(white_mask, (x, 0), 128)
            if white_mask.getpixel((x, h - 1)) == 255:
                ImageDraw.floodfill(white_mask, (x, h - 1), 128)
        for y in range(h):
            if white_mask.getpixel((0, y)) == 255:
                ImageDraw.floodfill(white_mask, (0, y), 128)
            if white_mask.getpixel((w - 1, y)) == 255:
                ImageDraw.floodfill(white_mask, (w - 1, y), 128)
        bg = (np.array(white_mask) == 128)
        fg = ~bg
        fg_img = Image.fromarray((fg * 255).astype(np.uint8), mode="L")
        fg_cleaned = fg_img.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
        fg = np.array(fg_cleaned) > 128

    # 4. Soft anti-aliased edge mask
    alpha_img = Image.fromarray((fg * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(blur_radius)
    )
    alpha = np.array(alpha_img)

    out = np.dstack([rgb.astype(np.uint8), alpha])

    # 5. Fringe decontamination: darken translucent boundary pixels to match black stroke
    edge = (alpha > 0) & (alpha < 255)
    out[edge, :3] = (out[edge, :3] * edge_darken).astype(np.uint8)

    return Image.fromarray(out, "RGBA")


def make_sticker_outline(
    image_input: Union[str, Path, Image.Image],
    border: int = 10,
    blur: float = 1.0,
    text: Optional[str] = None,
    font_path: Optional[str] = None,
    font_size: Optional[int] = None,
    text_color: tuple = (20, 20, 20, 255),
) -> Image.Image:
    """Add a thick, smooth white sticker halo around a transparent RGBA image.

    Args:
        image_input: Path to transparent RGBA image or PIL Image instance.
        border: Sticker border width in pixels.
        blur: Edge smoothing Gaussian blur radius.
        text: Optional text to overlay on the sticker (e.g. for speech bubbles).
        font_path: Optional path to TTF font.
        font_size: Optional explicit font size.
        text_color: RGBA color tuple for text.

    Returns:
        PIL Image in RGBA mode with white sticker border.
    """
    if isinstance(image_input, (str, Path)):
        im = Image.open(str(image_input)).convert("RGBA")
    else:
        im = image_input.convert("RGBA")

    # Crop tightly to non-transparent bbox
    alpha_channel = im.getchannel("A")
    bbox = alpha_channel.point(lambda v: 255 if v > 16 else 0).getbbox()
    if bbox:
        im = im.crop(bbox)

    pad = border * 2
    padded = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    padded.paste(im, (pad, pad))

    # Dilate alpha mask with MaxFilter to create expanded sticker border
    a = padded.getchannel("A").point(lambda v: 255 if v > 100 else 0)
    filter_size = max(3, border * 2 + 1)
    halo = a.filter(ImageFilter.MaxFilter(filter_size)).filter(ImageFilter.GaussianBlur(blur))

    # Composite white halo under foreground
    base = Image.new("RGBA", padded.size, (255, 255, 255, 0))
    base.putalpha(halo)
    out = Image.alpha_composite(base, padded)

    # Optional text overlay (for speech bubbles, signage)
    if text:
        draw = ImageDraw.Draw(out)
        font = _resolve_font(font_path, font_size or int(out.width * 0.09))
        bb = out.getchannel("A").getbbox()
        if bb:
            cx = (bb[0] + bb[2]) / 2
            cy = bb[1] + (bb[3] - bb[1]) * 0.45
        else:
            cx, cy = out.width / 2, out.height / 2
        draw.text((cx, cy), text, font=font, fill=text_color, anchor="mm")

    return out


def _resolve_font(font_path: Optional[str], size: int) -> ImageFont.ImageFont:
    if font_path and os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def process_image(
    src: Union[str, Path],
    dst: Union[str, Path],
    create_sticker: bool = True,
    border: int = 10,
    blur: float = 1.0,
    text: Optional[str] = None,
) -> None:
    """Full pipeline: flood-fill matte then optional sticker halo."""
    matted = floodfill_matte(src)
    if create_sticker:
        final = make_sticker_outline(matted, border=border, blur=blur, text=text)
    else:
        final = matted
    os.makedirs(os.path.dirname(os.path.abspath(str(dst))), exist_ok=True)
    final.save(str(dst))


def crop_background_plate(
    image_input: Union[str, Path, Image.Image],
    white_thresh: int = 220,
    min_content_fraction: float = 0.40,
    max_top_fraction: float = 0.15,
    max_bottom_fraction: float = 0.45,
) -> Image.Image:
    """Crop contiguous white margins (such as reserved caption clearance bands) from a background plate.

    Scans rows from the top border downwards and bottom border upwards.
    Rows that are predominantly near-white (clearance bands) are cropped off,
    leaving the actual illustration content to fill the screen full-bleed without letterbox bands.

    Includes safeguards against over-cropping:
    - Entirely near-white images are preserved untouched.
    - Top crop is capped at max_top_fraction (default 15%).
    - Bottom crop is capped at max_bottom_fraction (default 45%).
    - Cropped height must retain at least min_content_fraction (default 40%).
    - Noise-tolerant (resilient to JPEG compression ringing, 1-2px edge frame lines, and gradients).
    """
    if isinstance(image_input, (str, Path)):
        im = Image.open(str(image_input)).convert("RGB")
    else:
        im = image_input.convert("RGB")

    w, h = im.size

    # If entire image is near-white (no illustration content), do not crop
    extrema = im.getextrema()
    if all(ch[0] >= white_thresh for ch in extrema):
        return im

    arr = np.array(im).astype(np.int16)
    min_ch = arr.min(axis=-1)
    delta = arr.max(axis=-1) - min_ch

    # A pixel is white/near-white if minimum channel is high and channels are neutral
    is_white = (min_ch >= white_thresh) & (delta < 32)
    white_frac = is_white.mean(axis=1)
    row_mean = min_ch.mean(axis=1)

    def is_clearance_row(y: int) -> bool:
        return bool(white_frac[y] >= 0.94 and row_mean[y] >= (white_thresh - 15))

    top = 0
    max_top = int(h * max_top_fraction)
    start_y = 0
    if max_top > 3 and not is_clearance_row(0):
        if is_clearance_row(1) or is_clearance_row(2):
            start_y = 1

    for y in range(start_y, min(h, max_top)):
        if is_clearance_row(y):
            top = y + 1
        else:
            break

    bottom = h
    min_bottom = int(h * (1.0 - max_bottom_fraction))
    end_y = h - 1
    if (h - 1) > min_bottom + 3 and not is_clearance_row(h - 1):
        if is_clearance_row(h - 2) or is_clearance_row(h - 3):
            end_y = h - 2

    for y in range(end_y, max(-1, min_bottom - 1), -1):
        if is_clearance_row(y):
            bottom = y
        else:
            break

    if bottom - top >= int(h * min_content_fraction):
        return im.crop((0, top, w, bottom))
    return im


def process_background(
    src: Union[str, Path],
    dst: Union[str, Path],
    white_thresh: int = 225,
) -> None:
    """Process a background plate image, cropping outer white bands and saving to destination."""
    cropped = crop_background_plate(src, white_thresh=white_thresh)
    dst_p = Path(dst)
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(str(dst_p), quality=95)


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic Flood-fill Matte & Sticker Outline Tool for Video Pilot."
    )
    parser.add_argument("--input", "-i", required=True, help="Input image file or directory.")
    parser.add_argument("--output", "-o", required=True, help="Output PNG file or directory.")
    parser.add_argument("--sticker", action="store_true", default=True, help="Generate white sticker outline.")
    parser.add_argument("--no-sticker", action="store_false", dest="sticker", help="Skip sticker outline.")
    parser.add_argument("--border", type=int, default=10, help="Sticker border width in px (default: 10).")
    parser.add_argument("--text", type=str, default=None, help="Text to overlay inside sticker.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        files = sorted(glob.glob(str(input_path / "*.jpg")) + glob.glob(str(input_path / "*.png")))
        print(f"Processing {len(files)} files from {input_path} -> {output_path}...")
        for f in files:
            stem = Path(f).stem
            out_file = output_path / f"{stem}.png"
            process_image(f, out_file, create_sticker=args.sticker, border=args.border, text=args.text)
            print(f"  ✓ {stem} -> {out_file.name}")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        process_image(input_path, output_path, create_sticker=args.sticker, border=args.border, text=args.text)
        print(f"Processed: {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
