from __future__ import annotations

import io
import secrets

from PIL import Image, UnidentifiedImageError

from app.services.common import FormError

# Vercel rejects request bodies above 4.5 MB, so the cap leaves room for the other form fields.
MAX_PHOTO_BYTES = 4 * 1024 * 1024
MAX_DIMENSION = 1600
ALLOWED_FORMATS = {"JPEG": ("jpg", "image/jpeg"), "PNG": ("png", "image/png")}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def process_photo(filename: str, content: bytes) -> tuple[str, str, bytes]:
    """Validate with Pillow (not just the extension), re-encode, and return (name, mime, bytes)."""
    if len(content) > MAX_PHOTO_BYTES:
        raise FormError({"photo": "Photo must be 4 MB or smaller."})
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise FormError({"photo": "Photo must be a JPG, JPEG or PNG image."})
    try:
        with Image.open(io.BytesIO(content)) as probe:
            probe.verify()
        image = Image.open(io.BytesIO(content))
        fmt = image.format
        image.load()
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise FormError({"photo": "The uploaded file is not a valid image."}) from None
    if fmt not in ALLOWED_FORMATS:
        raise FormError({"photo": "Photo must be a JPG, JPEG or PNG image."})

    image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
    out = io.BytesIO()
    if fmt == "PNG":
        image.save(out, "PNG", optimize=True)
    else:
        image.convert("RGB").save(out, "JPEG", quality=85, optimize=True)
    suffix, mime = ALLOWED_FORMATS[fmt]
    return f"{secrets.token_hex(16)}.{suffix}", mime, out.getvalue()
