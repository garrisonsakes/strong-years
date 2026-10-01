"""Audio fingerprints -> assets.audio_fp.

Primary: Chromaprint via ffmpeg's `chromaprint` muxer (raw 32-bit sub-fingerprints). Fallback: a Haitsma–Kalker
style spectral hash computed with numpy (32 bits per ~93 ms frame from band-energy differences).
Stored as "<method>:<base64 of little-endian uint32 array>". Similarity = 1 - bit error rate at the best offset.
"""
from __future__ import annotations

import base64
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np


@lru_cache(maxsize=1)
def chromaprint_available() -> bool:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-muxers"], capture_output=True, text=True)
    return "chromaprint" in p.stdout


def _decode(path: str | Path, sr: int) -> np.ndarray:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr),
                        "-f", "s16le", "-"], capture_output=True, timeout=600)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode()[-300:])
    return np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def chromaprint(path: str | Path) -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".fp") as tf:
        p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", str(path), "-vn", "-ac", "1",
                            "-f", "chromaprint", "-fp_format", "raw", tf.name], capture_output=True, timeout=600)
        if p.returncode != 0:
            raise RuntimeError(p.stderr.decode()[-300:])
        data = Path(tf.name).read_bytes()
    return np.frombuffer(data, dtype="<u4").copy()


def spectral_hash(path: str | Path, sr: int = 11025, frame: int = 2048, hop: int = 1024, bands: int = 33) -> np.ndarray:
    x = _decode(path, sr)
    if len(x) < frame * 2:
        return np.zeros(0, dtype=np.uint32)
    win = np.hanning(frame).astype(np.float32)
    n = 1 + (len(x) - frame) // hop
    idx = np.arange(frame)[None, :] + hop * np.arange(n)[:, None]
    spec = np.abs(np.fft.rfft(x[idx] * win, axis=1)) ** 2
    freqs = np.fft.rfftfreq(frame, 1 / sr)
    edges = np.geomspace(300, 2000, bands + 1)
    e = np.stack([spec[:, (freqs >= lo) & (freqs < hi)].sum(axis=1) for lo, hi in zip(edges[:-1], edges[1:])], axis=1)
    e = np.log1p(e)
    d = (e[1:, :-1] - e[1:, 1:]) - (e[:-1, :-1] - e[:-1, 1:])      # (n-1, 32)
    bits = (d > 0).astype(np.uint32)
    weights = (1 << np.arange(31, -1, -1, dtype=np.uint64)).astype(np.uint64)
    return (bits.astype(np.uint64) @ weights).astype(np.uint32)


def fingerprint(path: str | Path, method: str | None = None) -> str:
    method = method or ("chromaprint" if chromaprint_available() else "spectral")
    arr = chromaprint(path) if method == "chromaprint" else spectral_hash(path)
    return f"{method}:" + base64.b64encode(arr.astype("<u4").tobytes()).decode()


def decode_fp(fp: str) -> tuple[str, np.ndarray]:
    method, _, b64 = fp.partition(":")
    return method, np.frombuffer(base64.b64decode(b64), dtype="<u4")


def _popcount32(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.uint32)
    return np.unpackbits(a.view(np.uint8)).reshape(-1, 32).sum(axis=1) if a.size else np.zeros(0)


def similarity(fp_a: str, fp_b: str, max_offset: int = 120, min_overlap: int = 20) -> float:
    """1 - BER at the best alignment. Identical tracks ~1.0; unrelated audio ~0.5."""
    ma, a = decode_fp(fp_a)
    mb, b = decode_fp(fp_b)
    if ma != mb or not a.size or not b.size:
        return 0.0
    best = 0.0
    for off in range(-max_offset, max_offset + 1):
        if off >= 0:
            x, y = a[off:], b
        else:
            x, y = a, b[-off:]
        n = min(len(x), len(y))
        if n < min(min_overlap, min(len(a), len(b))):
            continue
        ber = _popcount32(np.bitwise_xor(x[:n], y[:n])).sum() / (32 * n)
        best = max(best, 1 - ber)
    return round(float(best), 4)
