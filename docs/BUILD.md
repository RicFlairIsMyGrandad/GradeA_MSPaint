# Reproducing Windows packages

End users should use the installer; this page is for developers.

The package assembler is cross-platform and does not rely on running a compiler
or Python installer on the user's computer. It bundles official CPython 3.12.10
for Windows x64 from the Python team's NuGet package, pinned by SHA-512, and
Windows wheels pinned by SHA-256 in `packaging/requirements-windows.lock` and
`wheel-manifest.json`. NSIS generates the installer. The selected Qt modules are
Core/Gui/Widgets/Test/Svg/Network/DBus/OpenGL plus relevant desktop plugins; unused
QML, browser, multimedia and GPL-only modules are excluded. No MS Paint assets.

On Windows, with Python 3.12 and NSIS 3.11 installed for development:

```powershell
python -m pip install -e ".[test,ai]"
python packaging/fetch_model.py
python -m pytest -q
python packaging/build_windows.py --makensis "C:\Program Files (x86)\NSIS\makensis.exe"
& "build\windows\GradeA PaintPlus\runtime\python.exe" "build\windows\GradeA PaintPlus\smoke_windows.py"
```

On Linux the same build runs with a local `makensis` executable. Linux cannot
verify native Windows behavior; run the generated payload smoke test and manual
checks on Windows before promotion. TLS/signature/checksum checks must remain
enabled. Required build download hosts: `pypi.org`, `files.pythonhosted.org`, `api.nuget.org`, `github.com`,
`release-assets.githubusercontent.com` (model), and Debian mirrors only if
installing Linux NSIS build tools.

Outputs under `artifacts/`:

- `GradeA-PaintPlus-0.1.0-Windows-x64-Setup.exe` — per-user installer and uninstaller.
- `GradeA-PaintPlus-0.1.0-Windows-x64-Portable.zip` — unpack and launch the VBS helper.
- `SHA256SUMS.txt` — SHA-256 for the exact generated packages.

The payload includes an individual-file hash manifest, source, notices, user docs
and model. Installer adds Start menu/desktop shortcuts, Apps uninstall information
and an Open With registration for `.paintplus`; it does not take over default
image associations, create startup entries, services or scheduled tasks. It does
not require administrator access. Uninstall removes the installation directory
and shortcuts; preferences, external images/assets and saved projects remain.
Do not save your personal projects inside the application installation directory.

`.github/workflows/windows.yml` performs tests and the packaged-runtime smoke
check on a Windows runner before uploading artifacts. The first published preview passed native Windows tests and packaged/runtime installation checks; see the linked run in docs/STATUS.md. Successful main-branch builds publish the preview installer, portable ZIP, source archive and checksums to the v0.1.0-preview GitHub release. Pull requests never publish. Windows GUI tests use the native Windows Qt backend to exercise system fonts and the real clipboard.
For a public release, also test installation/uninstallation on a clean Windows
10/11 x64 machine and sign the executable with an appropriate publisher
certificate. Signing credentials are never stored in this repository.

Dependencies and runtime hashes are pinned, but output ZIP/installer bytes are
not promised bit-for-bit reproducible because file timestamps/tool versions can
vary. Each build produces its own exact SHA-256 checksums.
