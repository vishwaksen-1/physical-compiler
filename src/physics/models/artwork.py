"""
src/physics/models/artwork.py

Resolves and validates the illustrative image for a physical model, per the
convention: `data/images/<model_id>.<ext>`. Not part of
INTERFACE_CONTRACTS.md — an additive extension, logged in docs/STATUS.md,
same as `description_blanks` was for ExperimentOutput.

DEPENDENCY NOTE: reads PNG/JPEG dimensions via a small hand-rolled header
parser rather than adding Pillow. This project has twice now been bitten by
dependency-sync problems between requirements.txt and pyproject.toml's
mirrored `[project.dependencies]` on Vercel deploy (see docs/STATUS.md) --
for a need this narrow (read two integers from a file header), a few dozen
lines of well-tested parsing is a better trade than a new dependency to keep
in sync forever. Only PNG and JPEG are supported; anything else is treated
as an unsupported format (rejected, with a clear reason).

ASPECT RATIO POLICY: exactly two display ratios are supported, 1:1 and
16:9. An image's ratio is compared to both on a LOG scale (consistent with
the same log-scale-for-multiplicative-quantities reasoning already used in
src/errors/__init__.py's _edge_position() -- ratios are multiplicative
quantities, not additive ones) and accepted if within _TOLERANCE of
whichever is closer; otherwise rejected with a warning, per the "reject at
compile-time and show a warning" requirement -- "compile-time" here means
registry-load time (import time), once per process, not per HTTP request.
"""
from __future__ import annotations

import hashlib
import math
import struct
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parents[3]
_IMAGES_DIR = _REPO_ROOT / "data" / "images"
_MEMES_DIR = _REPO_ROOT / "data" / "memes"

_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
_PLACEHOLDER_EXTENSIONS = (".png", ".jpg", ".jpeg", ".svg")

ALLOWED_RATIOS = {"1:1": 1.0, "16:9": 16 / 9}
_TOLERANCE = 0.15  # 15%, multiplicative (see module docstring)


# ---------------------------------------------------------------------------
# Dimension readers (PNG, JPEG) -- no Pillow, see module docstring
# ---------------------------------------------------------------------------

def _read_png_dimensions(data: bytes) -> Optional[tuple]:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    # IHDR is always the first chunk: 4-byte length, 4-byte type "IHDR",
    # then width (4 bytes) and height (4 bytes), both big-endian.
    if data[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def _read_jpeg_dimensions(data: bytes) -> Optional[tuple]:
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        return None
    # Standalone SOF markers that carry a frame header (baseline through
    # progressive); DHT/DQT/APPn/COM etc are skipped via their length field.
    sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    pos = 2
    n = len(data)
    while pos + 4 <= n:
        if data[pos] != 0xFF:
            pos += 1  # resync -- some encoders pad with extra 0xFF fill bytes
            continue
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9):  # SOI/EOI: no length field
            pos += 2
            continue
        if 0xD0 <= marker <= 0xD7:  # RSTn: no length field
            pos += 2
            continue
        if marker == 0x01 or marker == 0x00:
            pos += 2
            continue
        if pos + 4 > n:
            break
        length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker in sof_markers:
            if pos + 9 > n:
                return None
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + length
    return None


def read_image_dimensions(path: Path) -> tuple:
    """(width, height) for a PNG or JPEG file. Raises ValueError for an
    unsupported format or a file that doesn't parse as one."""
    data = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".png":
        dims = _read_png_dimensions(data)
    elif suffix in (".jpg", ".jpeg"):
        dims = _read_jpeg_dimensions(data)
    else:
        raise ValueError(f"unsupported image format {suffix!r} (only .png/.jpg/.jpeg are read)")
    if dims is None:
        raise ValueError(f"couldn't read dimensions from {path.name} -- not a valid {suffix} file?")
    return dims


# ---------------------------------------------------------------------------
# Ratio matching
# ---------------------------------------------------------------------------

def _nearest_ratio(width: int, height: int) -> tuple:
    """(label, is_within_tolerance) for whichever of ALLOWED_RATIOS is
    closer to width/height, judged on a log scale (see module docstring)."""
    actual = width / height
    best_label, best_distance = None, math.inf
    for label, target in ALLOWED_RATIOS.items():
        distance = abs(math.log(actual) - math.log(target))
        if distance < best_distance:
            best_label, best_distance = label, distance
    return best_label, best_distance <= math.log(1 + _TOLERANCE)


# ---------------------------------------------------------------------------
# Placeholder selection
# ---------------------------------------------------------------------------

def _list_placeholders() -> list:
    if not _MEMES_DIR.is_dir():
        return []
    return sorted(
        p.name for p in _MEMES_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in _PLACEHOLDER_EXTENSIONS
    )


def _pick_placeholder(model_id: str) -> Optional[str]:
    """A stable (not insertion-order-dependent) pick per model_id, so the
    same model always gets the same placeholder rather than it depending on
    directory listing order or dict iteration."""
    placeholders = _list_placeholders()
    if not placeholders:
        return None
    index = int(hashlib.sha256(model_id.encode()).hexdigest(), 16) % len(placeholders)
    return placeholders[index]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def resolve_artwork(model_id: str) -> dict:
    """Always returns a usable {"status", "ratio", "url", "is_placeholder",
    "reason"} dict -- "url" is never None as long as at least one file
    exists in data/memes/, so callers never need a null-check before using it.

    status: "ok" (a real, validated image) | "missing" (no image file found
    for this model_id) | "rejected" (an image was found but its aspect
    ratio doesn't fit either allowed bucket, or the format/file was
    unreadable).
    """
    found_path = None
    if _IMAGES_DIR.is_dir():
        for ext in _IMAGE_EXTENSIONS:
            candidate = _IMAGES_DIR / f"{model_id}{ext}"
            if candidate.is_file():
                found_path = candidate
                break

    if found_path is not None:
        try:
            width, height = read_image_dimensions(found_path)
            label, ok = _nearest_ratio(width, height)
            if ok:
                return {
                    "status": "ok",
                    "ratio": label,
                    "url": f"/media/images/{found_path.name}",
                    "is_placeholder": False,
                    "reason": None,
                }
            actual = round(width / height, 3)
            reason = (
                f"{found_path.name} is {width}x{height} (ratio {actual}), too far from "
                f"either allowed ratio (1:1 = 1.0, 16:9 = {16/9:.3f}) -- rejected, showing a placeholder."
            )
        except ValueError as exc:
            reason = f"{found_path.name}: {exc} -- rejected, showing a placeholder."
    else:
        reason = None  # "missing" isn't a warning-worthy problem, just an unfilled slot

    placeholder = _pick_placeholder(model_id)
    return {
        "status": "rejected" if found_path is not None else "missing",
        "ratio": "1:1",
        "url": f"/media/memes/{placeholder}" if placeholder else None,
        "is_placeholder": True,
        "reason": reason,
    }
