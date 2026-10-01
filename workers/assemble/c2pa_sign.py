"""C2PA signing (PIPELINE §5.2): ffmpeg re-encodes strip manifests, so every master and platform variant is
re-signed with digitalSourceType = trainedAlgorithmicMedia.

Backends, in order: c2pa-python (pip `c2pa-python`, Rust c2pa-rs bindings) -> `c2patool` CLI -> stub.
Certificates: C2PA_SIGN_CERT + C2PA_PRIVATE_KEY (PEM paths). Without them, a throwaway dev CA + ES256 signer is
generated (C2PA_ALLOW_DEV_CERT=1). Dev-signed files carry a valid manifest but show "signing certificate untrusted".
TODO(production): buy a signing cert from a CA on the C2PA trust list so Instagram/TikTok/YouTube read the
manifest as trusted and auto-apply "AI info".
"""
from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from common import config

SOURCE_TYPE = "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
GENERATOR = {"name": "ChangSunStudio-assembler", "version": "1.0"}


def backend() -> str:
    try:
        import c2pa  # noqa: F401
        return "c2pa-python"
    except Exception:  # pragma: no cover - depends on env
        pass
    if shutil.which("c2patool"):
        return "c2patool"
    return "stub"


def _dev_credentials() -> tuple[bytes, bytes]:
    d = Path(config.WORK_DIR) / "c2pa_dev"
    chain_p, key_p = d / "chain.pem", d / "key.pem"
    if chain_p.exists() and key_p.exists():
        return chain_p.read_bytes(), key_p.read_bytes()
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    now = datetime.datetime.now(datetime.timezone.utc)
    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ChangSun DEV C2PA Root (not trusted)"),
                         x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ChangSun Studio DEV")])
    ku_ca = x509.KeyUsage(digital_signature=False, content_commitment=False, key_encipherment=False, data_encipherment=False,
                          key_agreement=False, key_cert_sign=True, crl_sign=True, encipher_only=False, decipher_only=False)
    ca = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name).public_key(ca_key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(days=1))
          .not_valid_after(now + datetime.timedelta(days=3650))
          .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
          .add_extension(ku_ca, critical=True)
          .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False)
          .sign(ca_key, hashes.SHA256()))
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ChangSun DEV assembler signer"),
                      x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ChangSun Studio DEV")])
    ku = x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=False, data_encipherment=False,
                       key_agreement=False, key_cert_sign=False, crl_sign=False, encipher_only=False, decipher_only=False)
    leaf = (x509.CertificateBuilder().subject_name(name).issuer_name(ca_name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=365))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(ku, critical=True)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.EMAIL_PROTECTION]), critical=False)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False)
            .sign(ca_key, hashes.SHA256()))
    from cryptography.hazmat.primitives import serialization as S
    chain = leaf.public_bytes(S.Encoding.PEM) + ca.public_bytes(S.Encoding.PEM)
    pk = key.private_bytes(S.Encoding.PEM, S.PrivateFormat.PKCS8, S.NoEncryption())
    d.mkdir(parents=True, exist_ok=True)
    chain_p.write_bytes(chain)
    key_p.write_bytes(pk)
    return chain, pk


def credentials() -> tuple[bytes, bytes, bool]:
    if config.C2PA_SIGN_CERT and config.C2PA_PRIVATE_KEY:
        return Path(config.C2PA_SIGN_CERT).read_bytes(), Path(config.C2PA_PRIVATE_KEY).read_bytes(), False
    if not config.C2PA_ALLOW_DEV_CERT:
        raise RuntimeError("C2PA_SIGN_CERT/C2PA_PRIVATE_KEY not set and dev certs disabled")
    chain, key = _dev_credentials()
    return chain, key, True


def manifest(title: str, extra_assertions: list | None = None) -> dict:
    return {
        "claim_generator_info": [GENERATOR],
        "title": title,
        "format": "video/mp4",
        "assertions": [
            {"label": "c2pa.actions", "data": {"actions": [
                {"action": "c2pa.created", "digitalSourceType": SOURCE_TYPE,
                 "softwareAgent": {"name": "ChangSun content pipeline (AI characters)"}},
            ]}},
            *(extra_assertions or []),
        ],
    }


def sign(src: Path, dst: Path, title: str | None = None) -> dict:
    """Sign src -> dst. Always leaves a playable file at dst."""
    src, dst = Path(src), Path(dst)
    be = backend()
    title = title or dst.name
    if be == "stub":  # pragma: no cover - env without c2pa-python and c2patool
        shutil.copyfile(src, dst)
        return {"signed": False, "backend": "stub",
                "todo": "Install c2pa-python (pip) or c2patool and set C2PA_SIGN_CERT/C2PA_PRIVATE_KEY."}
    try:
        chain, key, dev = credentials()
    except RuntimeError as e:   # AUDIT M10: no cert and dev certs off -> ship unsigned, QA blocks auto-publish
        shutil.copyfile(src, dst)
        return {"signed": False, "present": False, "trusted": False, "backend": be, "reason": str(e)}
    if be == "c2pa-python":
        import c2pa
        info = c2pa.C2paSignerInfo(c2pa.C2paSigningAlg.ES256, chain, key, config.C2PA_TSA_URL)
        signer = c2pa.Signer.from_info(info)
        builder = c2pa.Builder(manifest(title))
        tmp = dst.with_suffix(".c2pa.tmp.mp4")
        with open(src, "rb") as s, open(tmp, "w+b") as d:
            builder.sign(signer, "video/mp4", s, d)
        tmp.replace(dst)
    else:  # pragma: no cover - c2patool path
        with tempfile.TemporaryDirectory() as td:
            mp, cp, kp = Path(td) / "m.json", Path(td) / "c.pem", Path(td) / "k.pem"
            m = manifest(title)
            m.update({"alg": "es256", "sign_cert": str(cp), "private_key": str(kp)})
            mp.write_text(json.dumps(m))
            cp.write_bytes(chain)
            kp.write_bytes(key)
            subprocess.run(["c2patool", str(src), "-m", str(mp), "-o", str(dst), "-f"], check=True,
                           capture_output=True, timeout=300)
    info = read(dst)
    info.update({"signed": info.get("present", False), "backend": be, "dev_cert": dev})
    if dev:
        info["warning"] = "dev certificate (untrusted). TODO: production C2PA signing certificate."
    return info


def read(path: Path) -> dict:
    be = backend()
    if be == "c2pa-python":
        import c2pa
        try:
            r = c2pa.Reader(str(path))
            j = json.loads(r.json())
        except Exception as e:  # no manifest
            return {"present": False, "reason": str(e)[:200]}
        am = j.get("manifests", {}).get(j.get("active_manifest"), {})
        actions = []
        for a in am.get("assertions", []):
            if a.get("label", "").startswith("c2pa.actions"):
                actions += a.get("data", {}).get("actions", [])
        dst_types = sorted({a.get("digitalSourceType", "") for a in actions if a.get("digitalSourceType")})
        codes = [s.get("code") for s in (j.get("validation_status") or []) if isinstance(s, dict)]
        return {"present": True, "active_manifest": j.get("active_manifest"),
                "trusted": "signingCredential.untrusted" not in codes and j.get("validation_state") in ("Valid", "Trusted"),
                "validation_state": j.get("validation_state"),
                "digital_source_types": dst_types,
                "ai_generated": SOURCE_TYPE in dst_types,
                "claim_generator": (am.get("claim_generator_info") or [{}])[0].get("name")}
    if be == "c2patool":  # pragma: no cover
        p = subprocess.run(["c2patool", str(path)], capture_output=True, text=True)
        return {"present": p.returncode == 0 and "manifests" in p.stdout}
    return {"present": None, "reason": "no C2PA backend installed"}  # pragma: no cover
