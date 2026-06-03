"""Generate icon.ico and banner.png for MouseRecorder.

Run once from project root. Requires Pillow.
"""
from PIL import Image, ImageDraw, ImageFilter
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)


def _cursor_path(size: int) -> Image.Image:
    """Draw a stylized mouse cursor on a transparent canvas."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    s = size / 256.0

    # Cursor arrow (classic shape) — points up-left
    pts = [
        (72 * s, 36 * s),
        (72 * s, 188 * s),
        (112 * s, 152 * s),
        (140 * s, 220 * s),
        (168 * s, 208 * s),
        (140 * s, 140 * s),
        (192 * s, 136 * s),
    ]
    # Drop shadow
    shadow = [(p[0] + 4 * s, p[1] + 4 * s) for p in pts]
    d.polygon(shadow, fill=(0, 0, 0, 110))
    # Cursor fill — white with subtle border
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(15, 15, 20, 255))

    # Red record dot
    cx, cy, r = 196 * s, 196 * s, 36 * s
    d.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        fill=(239, 68, 68, 255),
        outline=(255, 255, 255, 230),
        width=max(2, int(4 * s)),
    )

    return img


def make_icon() -> None:
    # Render at high res, then downscale for crisp small sizes
    big = _cursor_path(512)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    out = os.path.join(OUT_DIR, "icon.ico")
    # PIL: pass a single high-res image and let it generate all sizes via `sizes`
    big.save(out, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"  -> {out}")


def make_banner() -> None:
    w, h = 1600, 480
    img = Image.new("RGB", (w, h), (13, 13, 16))  # #0d0d10
    d = ImageDraw.Draw(img, "RGBA")

    # Diagonal gradient stripes (subtle)
    for i in range(0, w + h, 4):
        alpha = max(0, 18 - abs(i - w // 2) // 30)
        d.line([(i, 0), (i - h, h)], fill=(124, 92, 255, alpha), width=1)

    # Soft violet glow top-left
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-200, -300, 700, 400], fill=(124, 92, 255, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img.paste(glow, (0, 0), glow)

    # Soft teal glow bottom-right
    glow2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(glow2)
    gd2.ellipse([1100, 250, 1900, 800], fill=(16, 185, 129, 55))
    glow2 = glow2.filter(ImageFilter.GaussianBlur(140))
    img.paste(glow2, (0, 0), glow2)

    # Cursor illustration on the right
    cursor = _cursor_path(420)
    img.paste(cursor, (1040, 30), cursor)

    # Use Segoe UI on Windows, fallback to default if not available
    try:
        from PIL import ImageFont
        winfonts = "C:/Windows/Fonts"
        title_font = ImageFont.truetype(f"{winfonts}/seguisb.ttf", 92)  # Segoe UI Semibold
        sub_font = ImageFont.truetype(f"{winfonts}/segoeui.ttf", 34)
        tag_font = ImageFont.truetype(f"{winfonts}/segoeuib.ttf", 22)  # Segoe UI Bold
    except OSError:
        try:
            title_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 92
            )
            sub_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34
            )
            tag_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22
            )
        except OSError:
            title_font = sub_font = tag_font = ImageFont.load_default()

    d.text(
        (80, 130),
        "MouseRecorder",
        fill=(245, 245, 250, 255),
        font=title_font,
    )
    d.text(
        (84, 250),
        "Record, save and automate your mouse.",
        fill=(190, 195, 210, 255),
        font=sub_font,
    )

    # Tag pill
    tx, ty = 84, 340
    tag_w = d.textlength("Windows 11  •  Python", font=tag_font)
    d.rounded_rectangle(
        [tx, ty, tx + tag_w + 56, ty + 44],
        radius=22,
        fill=(124, 92, 255, 60),
        outline=(124, 92, 255, 200),
        width=2,
    )
    d.text(
        (tx + 28, ty + 11),
        "Windows 11  •  Python",
        fill=(220, 215, 255, 255),
        font=tag_font,
    )

    out = os.path.join(OUT_DIR, "banner.png")
    img.save(out, format="PNG", optimize=True)
    print(f"  -> {out}")


if __name__ == "__main__":
    print("Generating assets...")
    make_icon()
    make_banner()
    print("Done.")
