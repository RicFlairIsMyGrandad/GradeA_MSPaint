"""Build-time only. TLS verified download with pinned content hash."""

import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from paintplus.background import MODEL_SHA256

path = ROOT / "models" / "u2netp.onnx"
if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != MODEL_SHA256:
    with urllib.request.urlopen(
        "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx",
        timeout=120,
    ) as response:
        data = response.read(8_000_001)
    if len(data) > 8_000_000 or hashlib.sha256(data).hexdigest() != MODEL_SHA256:
        raise SystemExit("Model integrity verification failed; refusing to save it.")
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(data)
print(f"Verified {path.name}: {MODEL_SHA256}")
