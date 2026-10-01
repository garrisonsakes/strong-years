"""Per-second perceptual hashes (DCT pHash, 64-bit) of video keyframes -> assets.phash_seq (hex strings)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

N = 32


def _dct_matrix(n: int = N) -> np.ndarray:
    k = np.arange(n)
    m = np.cos(np.pi * (2 * k[None, :] + 1) * k[:, None] / (2 * n)) * np.sqrt(2 / n)
    m[0] /= np.sqrt(2)
    return m


_D = _dct_matrix()


def phash_gray32(img: np.ndarray) -> int:
    """img: 32x32 grayscale array -> 64-bit int."""
    c = _D @ img.astype(np.float64) @ _D.T
    low = c[:8, :8].flatten()
    med = np.median(low[1:])
    bits = low > med
    v = 0
    for b in bits:
        v = (v << 1) | int(b)
    return v


def phash_image(path: str | Path) -> int:
    from PIL import Image
    im = Image.open(path).convert("L").resize((N, N), Image.Resampling.LANCZOS)
    return phash_gray32(np.asarray(im))


def video_phash_seq(path: str | Path, fps: float = 1.0) -> list[str]:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-vf",
                        f"fps={fps},scale={N}:{N}:flags=area,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, timeout=600)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode()[-400:])
    raw = np.frombuffer(p.stdout, dtype=np.uint8)
    frames = raw.reshape(-1, N, N) if raw.size else np.zeros((0, N, N), np.uint8)
    return [f"{phash_gray32(f):016x}" for f in frames]


def hamming(a: str | int, b: str | int) -> int:
    x = (int(a, 16) if isinstance(a, str) else a) ^ (int(b, 16) if isinstance(b, str) else b)
    return bin(x).count("1")


def seq_overlap(a: list[str], b: list[str], max_dist: int = 10, max_offset: int = 3) -> float:
    """Fraction of seconds (of the shorter sequence) within Hamming <= max_dist, best alignment within
    ±max_offset seconds (PIPELINE §2.3 guard 3: block if > 0.40)."""
    if not a or not b:
        return 0.0
    ia = [int(x, 16) for x in a]
    ib = [int(x, 16) for x in b]
    n = min(len(ia), len(ib))
    best = 0.0
    for off in range(-max_offset, max_offset + 1):
        hits = total = 0
        for i, h in enumerate(ia):
            j = i + off
            if 0 <= j < len(ib):
                total += 1
                hits += hamming(h, ib[j]) <= max_dist
        if total:
            best = max(best, hits / max(n, 1))
    return round(min(best, 1.0), 4)
