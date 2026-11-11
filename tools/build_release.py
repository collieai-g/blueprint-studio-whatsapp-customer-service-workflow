"""Build the fixed-name public ZIP, excluding private and generated run state."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from check_settings import resolve_settings


ROOT = Path(__file__).resolve().parent.parent
ASSET_NAME = "whatsapp-customer-service-agent.zip"
ARCHIVE_ROOT = "whatsapp-customer-service-agent"
FILES = (
    "README.md",
    "START_HERE.md",
    "AUTOMATION_PROMPT.md",
    "settings.defaults.json",
    "workflow.json",
    "portable/AGENT_INSTRUCTIONS.md",
    "portable/company-profile.example.json",
    "portable/runtime-state.example.json",
    "portable/ACCEPTANCE.md",
    "tools/check_settings.py",
)
PRIVATE_MARKERS = re.compile(
    r"\b[A-Za-z]:[\\/]|\b(?:task|event|workflow)_[a-f0-9]{24,}\b"
    r"|blueprint-agent-studio\.onrender\.com|sk-[A-Za-z0-9_-]{16,}",
    re.IGNORECASE,
)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def collect_files():
    payloads = {}
    for name in FILES:
        path = ROOT / name
        if path.is_symlink():
            raise ValueError(f"unexpected symlink: {name}")
        data = path.read_bytes()
        if PRIVATE_MARKERS.search(data.decode("utf-8-sig")):
            raise ValueError(f"private demo marker in {name}")
        payloads[name] = data
    workflow = json.loads(payloads["workflow.json"])
    version = workflow["package_version"]
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("workflow package_version must have three numeric components")
    if workflow["release_asset"] != ASSET_NAME:
        raise ValueError("workflow release_asset differs from the stable ZIP name")
    for key in ("entrypoint", "agent_instructions", "defaults", "profile_example", "state_example", "recurring_prompt"):
        if workflow[key] not in payloads:
            raise ValueError(f"workflow entry is missing from archive: {key}")
    profile = json.loads(payloads[workflow["profile_example"]])
    if profile["authorization"]["auto_patrol_allowed"] or profile["authorization"]["auto_send_allowed"]:
        raise ValueError("the public example must not carry authorization")
    json.loads(payloads[workflow["state_example"]])
    resolve_settings(profile)
    manifest = {
        "package_version": version,
        "workflow_title": workflow["workflow"]["title"],
        "publisher": workflow["publisher"],
        "entrypoint": workflow["entrypoint"],
        "files": {name: {"sha256": sha256(data), "bytes": len(data)} for name, data in payloads.items()},
    }
    payloads["manifest.json"] = json_bytes(manifest)
    return version, payloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    version, payloads = collect_files()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / ASSET_NAME
    with ZipFile(output, "w") as archive:
        for name, data in payloads.items():
            info = ZipInfo(f"{ARCHIVE_ROOT}/{name}")
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=ZIP_DEFLATED)
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("archive failed CRC verification")
        for name, data in payloads.items():
            if archive.read(f"{ARCHIVE_ROOT}/{name}") != data:
                raise ValueError(f"archive file differs from source: {name}")
    digest = sha256(output.read_bytes())
    output.with_suffix(".zip.sha256").write_text(f"{digest}  {ASSET_NAME}\n", encoding="ascii")
    print(json.dumps({"version": version, "entries": len(payloads), "sha256": digest, "zip": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
