#!/usr/bin/env python3
"""
test_upload_validation.py — BandLens upload endpoint validation script.

Generates minimal PNG images using stdlib only (no Pillow required) and
exercises the POST /v1/upload endpoint.

Usage:
    python test_upload_validation.py [--base-url http://localhost:8000]
"""
from __future__ import annotations

import argparse
import io
import struct
import sys
import zlib

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)


BASE_URL = "http://localhost:8000"


# ---------------------------------------------------------------------------
# Minimal PNG generator (stdlib only)
# ---------------------------------------------------------------------------

def _png_chunk(ctype: bytes, data: bytes) -> bytes:
    c = ctype + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def make_png(width: int = 100, height: int = 100, color: tuple[int, int, int] = (128, 128, 128)) -> bytes:
    """Generate a valid RGB PNG image without Pillow."""
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    scanline = b"\x00" + bytes(color) * width
    raw_data = scanline * height
    idat = _png_chunk(b"IDAT", zlib.compress(raw_data))
    iend = _png_chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_passed = 0
_failed = 0


def _ok(label: str, detail: str = "") -> None:
    global _passed
    _passed += 1
    suffix = f" — {detail}" if detail else ""
    print(f"  ✓ {label}{suffix}")


def _fail(label: str, detail: str = "") -> None:
    global _failed
    _failed += 1
    suffix = f" — {detail}" if detail else ""
    print(f"  ✗ {label}{suffix}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_successful_uploads(base_url: str) -> list[dict]:
    """Upload 3 valid PNG images and validate responses."""
    print("\n[1] Uploading 3 valid PNG images")
    results = []
    colors = [(255, 100, 50), (0, 200, 100), (30, 60, 255)]

    for i, color in enumerate(colors, start=1):
        png_bytes = make_png(width=100, height=100, color=color)
        filename = f"test_image_{i}.png"
        try:
            resp = requests.post(
                f"{base_url}/v1/upload",
                files={"file": (filename, png_bytes, "image/png")},
                timeout=10,
            )
        except requests.ConnectionError:
            _fail(f"Image {i} upload", "Connection refused — is the server running?")
            continue

        if resp.status_code == 200:
            data = resp.json()
            request_id = data.get("request_id", "")
            embedding_dim = data.get("embedding_dim", 0)

            if request_id:
                _ok(f"Image {i} uploaded", f"request_id={request_id[:8]}…")
            else:
                _fail(f"Image {i} missing request_id")

            if embedding_dim == 512:
                _ok(f"Image {i} embedding 512-dim", f"dim={embedding_dim}")
            else:
                _fail(f"Image {i} wrong embedding dim", f"got {embedding_dim}, expected 512")

            results.append(data)
        else:
            _fail(f"Image {i} upload HTTP {resp.status_code}", resp.text[:120])

    return results


def test_error_empty_file(base_url: str) -> None:
    """Upload an empty file — expect HTTP 400."""
    print("\n[2] Error case: empty file upload")
    try:
        resp = requests.post(
            f"{base_url}/v1/upload",
            files={"file": ("empty.png", b"", "image/png")},
            timeout=10,
        )
    except requests.ConnectionError:
        _fail("Empty file → 400", "Connection refused")
        return

    if resp.status_code == 400:
        _ok("Empty file → 400", f"detail={resp.json().get('detail', '')[:60]}")
    else:
        _fail("Empty file → 400", f"got {resp.status_code}")


def test_error_invalid_format(base_url: str) -> None:
    """Upload a .txt file — expect HTTP 400."""
    print("\n[3] Error case: invalid file format (.txt)")
    try:
        resp = requests.post(
            f"{base_url}/v1/upload",
            files={"file": ("data.txt", b"This is not an image.", "text/plain")},
            timeout=10,
        )
    except requests.ConnectionError:
        _fail("Text file → 400", "Connection refused")
        return

    if resp.status_code == 400:
        _ok("Text file → 400", f"detail={resp.json().get('detail', '')[:60]}")
    else:
        _fail("Text file → 400", f"got {resp.status_code}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="BandLens upload endpoint validator")
    parser.add_argument("--base-url", default=BASE_URL, help="API base URL")
    args = parser.parse_args()

    print(f"BandLens Upload Validation — target: {args.base_url}")
    print("=" * 60)

    upload_results = test_successful_uploads(args.base_url)
    test_error_empty_file(args.base_url)
    test_error_invalid_format(args.base_url)

    print("\n" + "=" * 60)
    print(f"Results: {_passed} passed, {_failed} failed")

    if _failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
