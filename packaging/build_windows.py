"""Assemble a self-contained Windows x64 runtime without executing Windows code.

Uses the official CPython NuGet distribution and hash-locked PyPI wheels.
Can run on Windows or Linux. NSIS produces a standard per-user installer.
"""

import argparse
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_VERSION = "3.12.10"
PYTHON_SHA512 = "u9pNz2iKlCEbYtUJaKkbOPMF0LjR7NkCafdKhvigpPzrt8oWKgdTpHaR6z3wyWQAm9PYGUxv0Zr66NX9AeHMDw=="
QT_MODULES = {"Core", "Gui", "Widgets", "Test", "Svg", "Network", "DBus", "OpenGL"}


def wanted(name):
    if not name.startswith("PySide6/"):
        return True
    rel = name[len("PySide6/") :]
    if rel in ("pyside6qml.abi3.dll", "plugins/imageformats/qpdf.dll"):
        return False
    if rel.startswith(
        (
            "support/",
            "plugins/platforms/",
            "plugins/imageformats/",
            "plugins/iconengines/",
            "plugins/styles/",
        )
    ):
        return True
    if "/" in rel:
        return False
    if rel.startswith("Qt6") and rel.endswith(".dll"):
        return rel[3:-4] in QT_MODULES
    if rel.startswith("Qt") and rel.endswith((".pyd", ".pyi")):
        return rel[2:].split(".")[0] in QT_MODULES
    return rel.endswith((".py", ".dll", ".json"))


def extract_safe(archive, destination, predicate=lambda n: True, prefix=""):
    for entry in archive.infolist():
        if entry.is_dir() or not entry.filename.startswith(prefix):
            continue
        name = entry.filename[len(prefix) :]
        if not predicate(name):
            continue
        path = destination / name
        if not path.resolve().is_relative_to(destination.resolve()):
            raise ValueError("Unsafe archive path")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(archive.read(entry))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel-dir", type=Path, default=ROOT / "build" / "wheels")
    parser.add_argument("--makensis", default="makensis")
    parser.add_argument("--skip-installer", action="store_true")
    args = parser.parse_args()
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    wheels = args.wheel_dir
    wheels.mkdir(parents=True, exist_ok=True)
    # Always validate the locked wheels, including an existing cache.
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--dest",
            str(wheels),
            "--platform",
            "win_amd64",
            "--python-version",
            "312",
            "--implementation",
            "cp",
            "--abi",
            "cp312",
            "--only-binary=:all:",
            "--require-hashes",
            "-r",
            str(ROOT / "packaging" / "requirements-windows.lock"),
        ],
        check=True,
    )
    package = build / f"python-{PYTHON_VERSION}.nupkg"
    if (
        not package.exists()
        or base64.b64encode(hashlib.sha512(package.read_bytes()).digest()).decode()
        != PYTHON_SHA512
    ):
        with urllib.request.urlopen(
            f"https://api.nuget.org/v3-flatcontainer/python/{PYTHON_VERSION}/python.{PYTHON_VERSION}.nupkg",
            timeout=120,
        ) as response:
            data = response.read(30_000_001)
        if (
            len(data) > 30_000_000
            or base64.b64encode(hashlib.sha512(data).digest()).decode() != PYTHON_SHA512
        ):
            raise ValueError("CPython checksum verification failed")
        package.write_bytes(data)
    app = build / "windows" / "GradeA PaintPlus"
    if app.exists():
        shutil.rmtree(app)
    app.mkdir(parents=True)
    runtime = app / "runtime"
    with zipfile.ZipFile(package) as z:
        extract_safe(z, runtime, prefix="tools/")
    lock = json.loads((ROOT / "packaging" / "wheel-manifest.json").read_text())
    for filename, expected in lock.items():
        wheel = wheels / filename
        if hashlib.sha256(wheel.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Wheel integrity failed: {filename}")
        with zipfile.ZipFile(wheel) as z:
            extract_safe(z, runtime / "Lib" / "site-packages", wanted)
    # Remove developer headers/scripts/tests, never runtime modules or licensing.
    for path in (
        runtime / "include",
        runtime / "libs",
        runtime / "Scripts",
        runtime / "Lib" / "test",
        runtime / "Lib" / "idlelib",
        runtime / "Lib" / "tkinter",
        runtime / "tcl",
    ):
        if path.exists():
            shutil.rmtree(path)
    shutil.copytree(
        ROOT / "paintplus",
        app / "paintplus",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(ROOT / "models", app / "models")
    shutil.copytree(ROOT / "licenses", app / "licenses")
    shutil.copytree(
        ROOT / "examples",
        app / "examples",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    if not (app / "models" / "u2netp.onnx").is_file():
        raise ValueError(
            "Run packaging/fetch_model.py first; AI builds must include the verified model."
        )
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        shutil.copy2(ROOT / name, app / name)
    shutil.copytree(ROOT / "docs", app / "docs", ignore=shutil.ignore_patterns("*.png"))
    shutil.copy2(ROOT / "packaging" / "launcher.py", app / "launch.py")
    shutil.copy2(ROOT / "packaging" / "smoke_windows.py", app / "smoke_windows.py")
    shutil.copy2(ROOT / "packaging" / "app.ico", app / "app.ico")
    # Source and runtime are visible/replacable, including Qt libraries (LGPL).
    shutil.copy2(ROOT / "packaging" / "portable.vbs", app / "Launch PaintPlus.vbs")
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    manifest = {
        str(p.relative_to(app)).replace("\\", "/"): hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
        for p in sorted(app.rglob("*"))
        if p.is_file()
    }
    (app / "FILE_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    if not args.skip_installer:
        command = [args.makensis]
        prefix = "/" if sys.platform == "win32" else "-"
        command += [
            f"{prefix}WX",
            f"{prefix}DAPP_DIR={app}",
            f"{prefix}DOUTPUT={artifacts / 'GradeA-PaintPlus-0.1.0-Windows-x64-Setup.exe'}",
            str(ROOT / "packaging" / "installer.nsi"),
        ]
        subprocess.run(command, check=True)
    shutil.make_archive(
        str(artifacts / "GradeA-PaintPlus-0.1.0-Windows-x64-Portable"),
        "zip",
        app.parent,
        app.name,
    )
    outputs = sorted(p for p in artifacts.iterdir() if p.suffix in (".exe", ".zip"))
    (artifacts / "SHA256SUMS.txt").write_text(
        "".join(
            f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in outputs
        )
    )
    print(
        f"Windows payload: {sum(p.stat().st_size for p in app.rglob('*') if p.is_file()) / 1_000_000:.1f} MB"
    )
    for p in outputs:
        print(f"{p.name}: {p.stat().st_size / 1_000_000:.1f} MB")


if __name__ == "__main__":
    main()
