"""Central configuration. Everything is an env var so the same image runs as the
render worker (RENDER_WORKER_URL) and the QA worker (QA_WORKER_URL)."""
import os
from pathlib import Path

WORKERS_DIR = Path(__file__).resolve().parent.parent          # .../rebuild/workers
REBUILD_DIR = WORKERS_DIR.parent                              # .../rebuild (spec files live here)


def _path_env(name: str, default: Path) -> Path:
    return Path(os.environ.get(name, str(default))).resolve()


# Spec inputs (mounted into the container at /app/spec in the Dockerfile)
SPEC_DIR = _path_env("SPEC_DIR", REBUILD_DIR)
PROMPTS_DIR = _path_env("PROMPTS_DIR", SPEC_DIR / "prompts")
BLOCKED_CLAIMS_PATH = _path_env("BLOCKED_CLAIMS_PATH", PROMPTS_DIR / "blocked_claims.json")
SAFETY_RULES_PATH = _path_env("SAFETY_RULES_PATH", SPEC_DIR / "SAFETY_RULES.md")
EVIDENCE_PATH = _path_env("EVIDENCE_PATH", SPEC_DIR / "EVIDENCE.md")

# Work + output storage
WORK_DIR = _path_env("WORK_DIR", Path(os.environ.get("TMPDIR", "/tmp")) / "csw-work")
OUTPUT_DIR = _path_env("OUTPUT_DIR", WORKERS_DIR / "out")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")   # e.g. https://render.example.com (serves /files)

# R2 / S3 (optional). When set, outputs are uploaded and R2_PUBLIC_BASE URLs are returned.
R2_ENDPOINT = os.environ.get("R2_ENDPOINT", "")
R2_BUCKET = os.environ.get("R2_BUCKET", "")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
R2_PUBLIC_BASE = os.environ.get("R2_PUBLIC_BASE", "").rstrip("/")

# Supabase (optional): resolves library asset ids and sibling fingerprints
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Auth (AUDIT H9): n8n sends X-Worker-Token (credential "Render/QA worker X-Worker-Token") or an HMAC signature.
# Fail closed: without WORKER_TOKEN every endpoint returns 503, unless DEV_NO_AUTH=1 (local dev only).
WORKER_TOKEN = os.environ.get("WORKER_TOKEN", "")
DEV_NO_AUTH = os.environ.get("DEV_NO_AUTH", os.environ.get("ALLOW_NO_AUTH", "0")) == "1"
HMAC_MAX_SKEW_S = int(os.environ.get("HMAC_MAX_SKEW_S", "300"))
PUBLIC_FILES = os.environ.get("PUBLIC_FILES", "0") == "1"      # serve /files without auth (dev only)

# Fetch policy (AUDIT H9 SSRF): https only, allow-listed hosts, no private/loopback/link-local IPs, byte cap.
# FETCH_ALLOWED_HOSTS: comma list; ".example.com" matches subdomains. The R2/public base hosts are always added.
FETCH_ALLOWED_HOSTS = [h.strip().lower() for h in os.environ.get(
    "FETCH_ALLOWED_HOSTS", ".fal.media,.fal.run,.wavespeed.ai,.cloudfront.net,.r2.dev,.r2.cloudflarestorage.com"
).split(",") if h.strip()]
MAX_FETCH_BYTES = int(os.environ.get("MAX_FETCH_BYTES", str(1024 * 1024 * 1024)))   # 1 GiB
FETCH_TIMEOUT_S = float(os.environ.get("FETCH_TIMEOUT_S", "120"))
# Local directories whose files may be referenced by path (besides OUTPUT_DIR). Empty in production.
LOCAL_MEDIA_ROOTS = [p for p in os.environ.get("LOCAL_MEDIA_ROOTS", "").split(os.pathsep) if p]

# Reviewer gate (AUDIT M4): only the worker's own env decides, never a request field.
REVIEWER_SIGNED = os.environ.get("REVIEWER_SIGNED", "0") == "1"

# LLM judge. Two layers: deterministic scan, then a MANDATORY LLM judge (REQUIRE_JUDGE=1, the default).
# Without a key, or on error / timeout / bad JSON, the final verdict is "human": nothing passes unjudged.
REQUIRE_JUDGE = os.environ.get("REQUIRE_JUDGE", "1") == "1"
JUDGE_TIMEOUT_S = float(os.environ.get("JUDGE_TIMEOUT_S", "60"))
ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
MODEL_JUDGE = os.environ.get("MODEL_JUDGE", "claude-opus-5-5")

# Encoding
X264_PRESET = os.environ.get("X264_PRESET", "medium")
FONTS_DIR = _path_env("FONTS_DIR", WORKERS_DIR / "fonts")
CAPTION_FONT = _path_env("CAPTION_FONT", FONTS_DIR / "Figtree-ExtraBold.ttf")

# C2PA
C2PA_SIGN_CERT = os.environ.get("C2PA_SIGN_CERT", "")      # PEM chain path (leaf first)
C2PA_PRIVATE_KEY = os.environ.get("C2PA_PRIVATE_KEY", "")  # PEM key path
C2PA_TSA_URL = os.environ.get("C2PA_TSA_URL", "") or None
C2PA_ALLOW_DEV_CERT = os.environ.get("C2PA_ALLOW_DEV_CERT", "0") == "1"   # AUDIT M10: off by default


def ensure_dirs() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
