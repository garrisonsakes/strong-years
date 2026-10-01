"""Input fetching and output publishing, with the AUDIT H9 / L12 hardening.

fetch():
  * https only, host on FETCH_ALLOWED_HOSTS (+ the R2 / PUBLIC_BASE_URL hosts), every resolved IP public
    (no loopback / private / link-local / reserved / multicast), redirects re-validated hop by hop, byte cap,
    time budget.
  * local paths / file:// only inside OUTPUT_DIR or LOCAL_MEDIA_ROOTS (never /etc/passwd).
  * the downloaded bytes must look like a media container we render (mp4/mov, webm/mkv, wav, mp3, aac, ogg,
    flac, png, jpeg, webp). Playlists (HLS, ffconcat) and text are refused, so ffmpeg can't be steered into
    reading other local files.
publish(): keys are validated and confined to OUTPUT_DIR (no path traversal); R2 when configured.
"""
from __future__ import annotations

import hashlib
import ipaddress
import re
import shutil
import socket
import uuid
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import httpx

from common import config

SAFE_ID_RX = re.compile(r"[A-Za-z0-9_-]{1,64}")
SAFE_KEY_RX = re.compile(r"[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*")


class FetchError(ValueError):
    """Rejected or failed media fetch (maps to HTTP 422/502 without leaking internals)."""


def safe_id(value, what: str = "id") -> str:
    v = str(value)
    if not SAFE_ID_RX.fullmatch(v):
        raise ValueError(f"invalid {what}: must match [A-Za-z0-9_-]{{1,64}}")
    return v


def confine(base: Path, *parts: str) -> Path:
    """Join and resolve; raise if the result escapes `base`."""
    base = Path(base).resolve()
    p = base.joinpath(*parts).resolve()
    if p != base and base not in p.parents:
        raise ValueError("path escapes its base directory")
    return p


def _cache_name(src: str) -> str:
    suffix = Path(urlparse(src).path).suffix.lower()
    suffix = suffix if re.fullmatch(r"\.[a-z0-9]{1,5}", suffix or "") else ".bin"
    return hashlib.sha1(src.encode()).hexdigest()[:16] + suffix


def allowed_hosts() -> list[str]:
    hosts = list(config.FETCH_ALLOWED_HOSTS)
    for base in (config.R2_PUBLIC_BASE, config.PUBLIC_BASE_URL):
        h = urlparse(base).hostname if base else None
        if h:
            hosts.append(h.lower())
    return hosts


def host_allowed(host: str) -> bool:
    host = (host or "").lower().rstrip(".")
    for a in allowed_hosts():
        if a.startswith("."):
            if host.endswith(a) or host == a[1:]:
                return True
        elif host == a:
            return True
    return False


def _public_ip(ip: str) -> bool:
    a = ipaddress.ip_address(ip)
    return not (a.is_private or a.is_loopback or a.is_link_local or a.is_reserved or a.is_multicast
                or a.is_unspecified or (a.version == 6 and a.ipv4_mapped and not _public_ip(str(a.ipv4_mapped))))


def check_url(url: str) -> None:
    u = urlparse(url)
    if u.scheme != "https":
        raise FetchError("only https media URLs are accepted")
    if not u.hostname or not host_allowed(u.hostname):
        raise FetchError("media host is not on FETCH_ALLOWED_HOSTS")
    try:
        infos = socket.getaddrinfo(u.hostname, u.port or 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise FetchError("media host does not resolve") from e
    for info in infos:
        if not _public_ip(info[4][0]):
            raise FetchError("media host resolves to a non-public address")


def _local_allowed(p: Path) -> bool:
    p = p.resolve()
    roots = [config.OUTPUT_DIR, config.WORK_DIR, *config.LOCAL_MEDIA_ROOTS]
    return any(p == Path(r).resolve() or Path(r).resolve() in p.parents for r in roots)


MAGIC = [
    (4, b"ftyp"),                  # mp4 / mov / m4a / 3gp
    (0, b"\x1aE\xdf\xa3"),         # matroska / webm
    (0, b"RIFF"),                  # wav / webp (checked below)
    (0, b"ID3"), (0, b"\xff\xfb"), (0, b"\xff\xf3"), (0, b"\xff\xf2"), (0, b"\xff\xf1"), (0, b"\xff\xf9"),  # mp3 / aac
    (0, b"OggS"), (0, b"fLaC"),
    (0, b"\x89PNG\r\n\x1a\n"), (0, b"\xff\xd8\xff"),
]


def sniff_media(path: Path) -> None:
    head = Path(path).read_bytes()[:64] if Path(path).stat().st_size else b""
    for off, sig in MAGIC:
        if head[off:off + len(sig)] == sig:
            if sig == b"RIFF" and head[8:12] not in (b"WAVE", b"WEBP", b"AVI "):
                break
            return
    raise FetchError("unsupported media container (playlists and non-media files are refused)")


def fetch(src: str, workdir: Path | None = None, client: httpx.Client | None = None) -> Path:
    """Materialise `src` locally and return the path (policy above)."""
    if not src or not isinstance(src, str):
        raise FetchError("empty media source")
    workdir = Path(workdir or config.WORK_DIR)
    workdir.mkdir(parents=True, exist_ok=True)
    u = urlparse(src)
    if u.scheme in ("", "file"):
        p = Path(unquote(u.path) if u.scheme == "file" else src)
        if not _local_allowed(p):
            raise FetchError("local paths are only accepted inside the worker's output/media roots")
        if not p.is_file():
            raise FetchError("media file not found")
        sniff_media(p)
        return p.resolve()
    if config.PUBLIC_BASE_URL and src.startswith(config.PUBLIC_BASE_URL + "/files/"):
        p = confine(config.OUTPUT_DIR, unquote(src[len(config.PUBLIC_BASE_URL) + len("/files/"):]))
        if p.is_file():
            return p
    dest = workdir / _cache_name(src)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    own = client is None
    client = client or httpx.Client(timeout=config.FETCH_TIMEOUT_S, follow_redirects=False)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        url = src
        for _hop in range(4):
            check_url(url)
            with client.stream("GET", url) as r:
                if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
                    url = urljoin(url, r.headers["location"])
                    continue
                if r.status_code >= 400:
                    raise FetchError(f"media fetch failed: upstream HTTP {r.status_code}")
                if int(r.headers.get("content-length") or 0) > config.MAX_FETCH_BYTES:
                    raise FetchError("media exceeds MAX_FETCH_BYTES")
                n = 0
                with open(tmp, "wb") as f:
                    for chunk in r.iter_bytes(1 << 16):
                        n += len(chunk)
                        if n > config.MAX_FETCH_BYTES:
                            raise FetchError("media exceeds MAX_FETCH_BYTES")
                        f.write(chunk)
                break
        else:
            raise FetchError("too many redirects")
        sniff_media(tmp)
        tmp.rename(dest)
        return dest
    except httpx.HTTPError as e:
        raise FetchError(f"media fetch failed: {e.__class__.__name__}") from e
    finally:
        tmp.unlink(missing_ok=True)
        if own:
            client.close()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def r2_enabled() -> bool:
    return bool(config.R2_ENDPOINT and config.R2_BUCKET and config.R2_ACCESS_KEY_ID and config.R2_SECRET_ACCESS_KEY)


def publish(local: Path, key: str, content_type: str | None = None) -> dict:
    """Store `local` under `key` (validated, confined to OUTPUT_DIR); return {storage_key, url, bytes, sha256}."""
    if not SAFE_KEY_RX.fullmatch(key) or ".." in key.split("/"):
        raise ValueError("invalid storage key")
    local = Path(local)
    meta = {"bytes": local.stat().st_size, "sha256": sha256(local)}
    if r2_enabled():  # pragma: no cover - needs real credentials
        import boto3
        s3 = boto3.client("s3", endpoint_url=config.R2_ENDPOINT, aws_access_key_id=config.R2_ACCESS_KEY_ID,
                          aws_secret_access_key=config.R2_SECRET_ACCESS_KEY, region_name="auto")
        extra = {"ContentType": content_type} if content_type else {}
        s3.upload_file(str(local), config.R2_BUCKET, key, ExtraArgs=extra)
        return {"storage_key": f"r2://{config.R2_BUCKET}/{key}", "url": f"{config.R2_PUBLIC_BASE}/{key}", **meta}
    dest = confine(config.OUTPUT_DIR, key)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.resolve() != local.resolve():
        shutil.copyfile(local, dest)
    url = f"{config.PUBLIC_BASE_URL}/files/{key}" if config.PUBLIC_BASE_URL else dest.resolve().as_uri()
    return {"storage_key": f"local://{key}", "url": url, "local_path": str(dest.resolve()), **meta}


def new_id() -> str:
    return str(uuid.uuid4())
