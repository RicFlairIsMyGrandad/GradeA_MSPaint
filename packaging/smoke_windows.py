"""Run with the bundled runtime on Windows; verifies actual packaged imports and UI."""

import os
import sys

os.environ.setdefault(
    "QT_QPA_PLATFORM", "windows" if sys.platform == "win32" else "offscreen"
)
import tempfile
from pathlib import Path
from PIL import Image
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from paintplus.app import MainWindow, STYLE
from paintplus.model import Document
from paintplus.background import remove_background

app = QApplication([])
app.setStyleSheet(STYLE)
with tempfile.TemporaryDirectory() as folder:
    import paintplus.app as editor

    editor.QSettings = lambda *args: QSettings(
        str(Path(folder) / "settings.ini"), QSettings.Format.IniFormat, args[-1]
    )
    window = MainWindow()
    window.show()
    app.processEvents()
    p = Path(folder) / "asset.png"
    Image.new("RGBA", (40, 30), (24, 71, 241, 128)).save(p)
    window.insert_images([str(p)])
    assert len(window.doc.layers) == 2
    window.copy_selection()
    window.paste()
    assert len(window.doc.layers) == 3
    window.output_folder = folder
    window.filename.setText("scene")
    window.quick_save()
    assert (Path(folder) / "scene.png").exists()
    project = Path(folder) / "scene.paintplus"
    window.doc.save(project)
    assert len(Document.load(project).layers) == 3
    result = remove_background(Image.open(p))
    assert result.size == (40, 30)
    window.doc.dirty = False
    window.close()
    app.processEvents()
print(
    "Packaged Windows UI, clipboard, save/export, project loading and offline CPU AI checks passed."
)
