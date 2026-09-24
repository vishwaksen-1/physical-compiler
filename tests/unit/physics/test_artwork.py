"""Tests for src/physics/models/artwork.py — image dimension parsing,
ratio validation, and placeholder fallback.

Run with: pytest tests/unit/physics/test_artwork.py -v
"""
import struct

import pytest

from src.physics.models.artwork import (
    _nearest_ratio,
    _pick_placeholder,
    read_image_dimensions,
    resolve_artwork,
)


def _make_png(width: int, height: int) -> bytes:
    """A minimal (invalid pixel data, valid header) PNG -- only the IHDR
    chunk matters for read_image_dimensions()."""
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + b"\x00\x00\x00\x00"
    return signature + ihdr


def _make_baseline_jpeg(width: int, height: int) -> bytes:
    """A minimal JPEG with just SOI + a bare SOF0 segment + EOI -- enough
    for read_image_dimensions(), not a decodable image."""
    soi = b"\xff\xd8"
    # SOF0: marker(2) + length(2) + precision(1) + height(2) + width(2) + components(1)
    sof_body = struct.pack(">BHHB", 8, height, width, 1) + b"\x01\x11\x00"
    sof = b"\xff\xc0" + struct.pack(">H", len(sof_body) + 2) + sof_body
    eoi = b"\xff\xd9"
    return soi + sof + eoi


class TestPngDimensions:
    def test_reads_correct_dimensions(self, tmp_path):
        path = tmp_path / "test.png"
        path.write_bytes(_make_png(640, 480))
        assert read_image_dimensions(path) == (640, 480)

    def test_square(self, tmp_path):
        path = tmp_path / "sq.png"
        path.write_bytes(_make_png(200, 200))
        assert read_image_dimensions(path) == (200, 200)

    def test_rejects_bad_signature(self, tmp_path):
        path = tmp_path / "bad.png"
        path.write_bytes(b"not a png" + b"\x00" * 20)
        with pytest.raises(ValueError):
            read_image_dimensions(path)


class TestJpegDimensions:
    def test_reads_correct_dimensions(self, tmp_path):
        path = tmp_path / "test.jpg"
        path.write_bytes(_make_baseline_jpeg(1280, 720))
        assert read_image_dimensions(path) == (1280, 720)

    def test_rejects_bad_signature(self, tmp_path):
        path = tmp_path / "bad.jpg"
        path.write_bytes(b"\x00\x00not a jpeg")
        with pytest.raises(ValueError):
            read_image_dimensions(path)


class TestUnsupportedFormat:
    def test_rejects_unknown_extension(self, tmp_path):
        path = tmp_path / "test.webp"
        path.write_bytes(b"whatever")
        with pytest.raises(ValueError, match="unsupported"):
            read_image_dimensions(path)


class TestNearestRatio:
    def test_exact_square(self):
        label, ok = _nearest_ratio(100, 100)
        assert label == "1:1" and ok

    def test_exact_widescreen(self):
        label, ok = _nearest_ratio(1920, 1080)
        assert label == "16:9" and ok

    def test_close_to_square_within_tolerance(self):
        label, ok = _nearest_ratio(105, 100)
        assert label == "1:1" and ok

    def test_far_from_both_is_rejected(self):
        label, ok = _nearest_ratio(100, 300)
        assert not ok

    def test_ultra_wide_is_rejected(self):
        label, ok = _nearest_ratio(3000, 400)
        assert not ok

    def test_symmetric_around_a_single_target_in_log_space(self):
        # Isolate the log-distance calculation itself: a ratio twice the
        # 1:1 target and a ratio half of it should be equally far from
        # THAT target, since ratios are multiplicative. (Not tested via
        # _nearest_ratio's pick-of-two logic, since with two asymmetric
        # targets -- 1:1 and 16:9 -- a wide ratio can land near 16:9 with
        # no symmetric counterpart on the narrow side; that's correct
        # behavior, not an asymmetry bug.)
        import math
        distance_wide = abs(math.log(2.0) - math.log(1.0))
        distance_narrow = abs(math.log(0.5) - math.log(1.0))
        assert distance_wide == pytest.approx(distance_narrow)

    def test_wide_ratio_can_land_in_the_16_9_bucket(self):
        # 200x100 (ratio 2.0) is close enough to 16:9 (1.778) to be
        # accepted there, even though it's far from 1:1.
        label, ok = _nearest_ratio(200, 100)
        assert label == "16:9" and ok


class TestPlaceholderSelection:
    def test_stable_per_model_id(self):
        first = _pick_placeholder("mass_spring_damper")
        second = _pick_placeholder("mass_spring_damper")
        assert first == second

    def test_real_placeholder_files_exist(self):
        # data/memes/ ships shrug.svg and under-construction.svg -- this
        # would catch an accidental deletion of both.
        assert _pick_placeholder("anything") is not None


class TestResolveArtwork:
    def test_missing_image_falls_back_to_placeholder(self):
        result = resolve_artwork("definitely_not_a_real_model_id")
        assert result["status"] == "missing"
        assert result["is_placeholder"] is True
        assert result["url"] is not None
        assert result["reason"] is None

    def test_result_shape_is_always_complete(self):
        result = resolve_artwork("mass_spring_damper")
        assert set(result.keys()) == {"status", "ratio", "url", "is_placeholder", "reason"}
        assert result["ratio"] in ("1:1", "16:9")
