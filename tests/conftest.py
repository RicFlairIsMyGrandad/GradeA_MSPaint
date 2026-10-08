import os
import sys
from pathlib import Path

os.environ.setdefault(
    "QT_QPA_PLATFORM", "windows" if sys.platform == "win32" else "offscreen"
)
os.environ.setdefault("XDG_CONFIG_HOME", "/tmp/paintplus-test-config")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/paintplus-test-cache")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def app():
    from paintplus.app import STYLE

    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    return app


@pytest.fixture
def window(app, tmp_path, monkeypatch):
    import paintplus.app as application
    from paintplus.app import MainWindow

    monkeypatch.setattr(
        application,
        "QSettings",
        lambda *args: QSettings(
            str(tmp_path / "settings.ini"), QSettings.Format.IniFormat, args[-1]
        ),
    )
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(
        QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(tmp_path)
    )
    w = MainWindow()
    w.resize(1600, 1000)
    w.show()
    app.processEvents()
    yield w
    if w.ai_worker:
        w.ai_worker.wait(30000)
    w.doc.dirty = False
    w.close()
    w.deleteLater()
    app.processEvents()
