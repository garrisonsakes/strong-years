"""Identity consistency hook (ArcFace via InsightFace) and lip-sync hook (SyncNet).

Both are optional heavy models. The interface is fixed so n8n's 'Decide QA Route' bands work unchanged:
metrics face_sim_median / face_sim_min (cosine vs the character reference centroid) and syncnet_conf / syncnet_dist.
When the models aren't installed the checks return None with a skip reason (the n8n band() skips nulls).

Enable: pip install insightface onnxruntime (CPU) and set INSIGHTFACE_HOME / model pack 'buffalo_l'.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import numpy as np


@lru_cache(maxsize=1)
def _app():
    try:
        from insightface.app import FaceAnalysis  # type: ignore
    except Exception as e:
        return None, f"insightface not installed ({e.__class__.__name__})"
    try:
        app = FaceAnalysis(name=os.environ.get("INSIGHTFACE_MODEL", "buffalo_l"),
                           root=os.environ.get("INSIGHTFACE_HOME", "~/.insightface"),
                           providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        return app, None
    except Exception as e:  # pragma: no cover - model download/availability
        return None, f"insightface model unavailable: {e}"[:200]


def available() -> tuple[bool, str | None]:
    app, why = _app()
    return app is not None, why


def embed(img_bgr: np.ndarray) -> np.ndarray | None:  # pragma: no cover - needs models
    app, _ = _app()
    faces = app.get(img_bgr) if app else []
    if not faces:
        return None
    f = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    v = f.normed_embedding
    return v / np.linalg.norm(v)


def face_similarity(frames: list[Path], references: list[Path]) -> dict:
    """Cosine similarity of each frame's largest face vs the reference centroid."""
    ok, why = available()
    if not ok:
        return {"face_sim_median": None, "face_sim_min": None, "face_status": "skipped", "face_reason": why}
    import cv2  # pragma: no cover  (installed with insightface)
    refs = [e for e in (embed(cv2.imread(str(p))) for p in references) if e is not None]  # pragma: no cover
    if not refs:  # pragma: no cover
        return {"face_sim_median": None, "face_sim_min": None, "face_status": "skipped",
                "face_reason": "no face found in reference images"}
    c = np.mean(refs, axis=0)  # pragma: no cover
    c /= np.linalg.norm(c)
    sims = [float(e @ c) for e in (embed(cv2.imread(str(p))) for p in frames) if e is not None]
    if not sims:
        return {"face_sim_median": None, "face_sim_min": None, "face_status": "no_faces_in_frames"}
    return {"face_sim_median": round(float(np.median(sims)), 4), "face_sim_min": round(min(sims), 4),
            "face_status": "ok", "face_frames": len(sims)}


def syncnet(_video: Path) -> dict:
    """SyncNet (LSE-C / LSE-D) hook. TODO: wire a SyncNet ONNX export on the GPU QA worker."""
    return {"syncnet_conf": None, "syncnet_dist": None, "syncnet_status": "skipped",
            "syncnet_reason": "SyncNet model not bundled in this worker (GPU QA worker TODO)"}
