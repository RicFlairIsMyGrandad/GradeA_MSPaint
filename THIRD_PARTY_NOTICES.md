# Third-party notices

GradeA PaintPlus is independent of Microsoft. Its icon and sample illustrations
are original. The supplied reference screenshot is not distributed with the app.

The Windows package contains the following separately licensed components.
Upstream license files are retained in the runtime and wheel `.dist-info`
directories. The source is supplied separately and can also be viewed directly
in the application's `paintplus` directory. No binaries are intentionally hidden.

| Component | License | Source |
| --- | --- | --- |
| CPython 3.12.10 | Python Software Foundation License | https://github.com/python/cpython/tree/v3.12.10 |
| Qt / Qt for Python / Shiboken 6.8.3 | LGPL-3.0 (used modules); license texts supplied | https://code.qt.io/cgit/pyside/pyside-setup.git/?h=6.8.3 and https://code.qt.io/cgit/qt/qtbase.git/?h=v6.8.3 |
| Pillow 11.1.0 | HPND / Pillow license, with bundled image codec notices | https://github.com/python-pillow/Pillow/tree/11.1.0 |
| NumPy 2.2.4 | BSD-3-Clause, bundled library notices | https://github.com/numpy/numpy/tree/v2.2.4 |
| ONNX Runtime 1.21.0 | MIT, third-party notices supplied | https://github.com/microsoft/onnxruntime/tree/v1.21.0 |
| U²-Net small model | Apache-2.0 upstream project; license in models/U2NET-LICENSE.txt | https://github.com/xuebinqin/U-2-Net |
| coloredlogs / humanfriendly | MIT | https://github.com/xolox/python-coloredlogs and https://github.com/xolox/python-humanfriendly |
| FlatBuffers | Apache-2.0 | https://github.com/google/flatbuffers |
| packaging | Apache-2.0 / BSD-2-Clause | https://github.com/pypa/packaging |
| protobuf | BSD-3-Clause | https://github.com/protocolbuffers/protobuf |
| SymPy / mpmath | BSD | https://github.com/sympy/sympy and https://github.com/mpmath/mpmath |
| NSIS installer runtime | zlib/libpng license; components have separate notices | https://nsis.sourceforge.io/License |

Qt libraries are dynamically loaded from `runtime/Lib/site-packages/PySide6`.
You may replace these with compatible libraries and inspect/debug the application
for modifications to those libraries under the LGPL. PaintPlus adds no prohibition
on reverse engineering for this purpose. This application does not use the GPL-only
Qt add-on modules. Obtain exact corresponding Qt/PySide source from the links above;
retain LGPL/GPL license texts included with the runtime when redistributing.

Windows runtime DLLs supplied in the official Python / Qt binary distributions
remain subject to their original redistribution terms. The application uses no
Microsoft logos, Paint artwork, or proprietary application resources. ONNX Runtime
is an open-source library, not Microsoft Paint application code.

Build-only tools (pytest, pip, NSIS) have their own licenses; they are not runtime
requirements for users. SHA-256 hashes identify downloaded build artifacts, but
are not a malware scan or a publisher signature.
