# Sticker matting

Tool: `sys/tools/matte_sticker.py` (bundled to Colab by the render request; runs in `job_worker.py`).

1. Near-white, neutral pixels (min channel > 225, spread < 22) are labelled; only components touching the image border are background.
2. Closed black outlines protect interior white (heads, plates, bubbles). AI segmentation (rembg/isnet/BiRefNet) was tested and hollowed these interiors — do not use it for this style.
3. Small islands (< 0.2% area) are dropped (JPEG noise, Flow watermark); edges are softened and darkened to kill halos.
4. Tight crop, then a white halo (MaxFilter ≈ 2×border+1, GaussianBlur 1 px) gives the sticker look.

Failure signs: holes in a head (open outline) → reject that sticker image with correction "continuous closed black outline"; grey box around sticker (non-white backdrop) → correction "perfectly flat pure white background, no shadow".
`layers-report.json` lists each sticker's size and transparent fraction for evidence.
