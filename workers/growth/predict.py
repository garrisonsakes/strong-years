"""Early-signal predictor (stub): 1 h scorecard -> 24 h composite (ENGINE_100X §6.9, [S45] early popularity predicts
later popularity). Ridge regression on the 1 h component scores (missing components imputed at 50, plus a
"reported" indicator per component). It refuses to train below MIN_POSTS paired posts and only ranks: nothing in
the engine acts on a prediction alone. Pure numpy; no network."""
from __future__ import annotations

import numpy as np

from growth.scorecard import COMPONENTS

MIN_POSTS = 200


def _x(card: dict) -> list[float]:
    s = card.get("scores") or {}
    return [1.0] + [float(s.get(c, 50.0)) / 100.0 for c in COMPONENTS] + [1.0 if c in s else 0.0 for c in COMPONENTS]


def pairs(cards: list[dict]) -> list[tuple[dict, float]]:
    """(1 h card, 24 h composite) for every post that has both reads."""
    one, day = {}, {}
    for c in cards:
        h = int(c.get("horizon_h") or 0)
        if h == 1:
            one[str(c["post_id"])] = c
        elif h == 24 and c.get("composite") is not None and not c.get("provisional"):
            day[str(c["post_id"])] = float(c["composite"])
    return [(one[k], day[k]) for k in sorted(one) if k in day]


class EarlySignalPredictor:
    def __init__(self, ridge: float = 1.0):
        self.ridge, self.coef, self.n = ridge, None, 0

    def train(self, cards: list[dict]) -> dict:
        ps = pairs(cards)
        if len(ps) < MIN_POSTS:
            return {"trained": False, "n": len(ps), "reason": f"needs >= {MIN_POSTS} posts with 1 h and 24 h reads"}
        X = np.array([_x(c) for c, _ in ps])
        y = np.array([v for _, v in ps])
        reg = self.ridge * np.eye(X.shape[1])
        reg[0, 0] = 0.0                                      # don't shrink the intercept
        self.coef = np.linalg.solve(X.T @ X + reg, X.T @ y)
        self.n = len(ps)
        pred = X @ self.coef
        ss = float(((y - y.mean()) ** 2).sum()) or 1.0
        return {"trained": True, "n": self.n, "r2_in_sample": round(1 - float(((y - pred) ** 2).sum()) / ss, 4)}

    def predict(self, card_1h: dict) -> float | None:
        if self.coef is None:
            return None
        return float(min(100.0, max(0.0, np.array(_x(card_1h)) @ self.coef)))
