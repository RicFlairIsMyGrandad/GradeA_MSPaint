import json
from pathlib import Path
from PySide6.QtCore import Qt, QSize, Signal, QUrl
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QSlider,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QLabel,
)


class AssetList(QListWidget):
    def mimeData(self, items):
        mime = super().mimeData(items)
        mime.setUrls(
            [QUrl.fromLocalFile(i.data(Qt.ItemDataRole.UserRole)) for i in items]
        )
        return mime


class AssetLibrary(QWidget):
    insert = Signal(list)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.folders = json.loads(settings.value("assetFolders", "[]"))
        self.favorites = json.loads(settings.value("favorites", "[]"))
        self.recent = json.loads(settings.value("recent", "[]"))
        if not settings.contains("assetFolders"):
            samples = Path(__file__).resolve().parents[1] / "examples" / "Assets"
            if samples.is_dir():
                self.folders = [
                    {"name": p.name, "path": str(p)}
                    for p in sorted(samples.iterdir())
                    if p.is_dir()
                ]
                self.persist()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search assets…")
        layout.addWidget(self.search)
        self.category = QComboBox()
        layout.addWidget(self.category)
        row = QHBoxLayout()
        layout.addLayout(row)
        for title, fn in (
            ("+ Folder", self.add_folder),
            ("Manage", self.manage),
            ("+ PNGs", self.add_files),
        ):
            b = QPushButton(title)
            b.clicked.connect(fn)
            row.addWidget(b)
        self.list = AssetList()
        self.list.setViewMode(QListWidget.ViewMode.IconMode)
        self.list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list.setWordWrap(True)
        self.list.setSpacing(6)
        self.list.setDragEnabled(True)
        layout.addWidget(self.list)
        self.list.itemDoubleClicked.connect(
            lambda item: self.send([item.data(Qt.ItemDataRole.UserRole)])
        )
        row = QHBoxLayout()
        layout.addLayout(row)
        b = QPushButton("Insert selected")
        b.clicked.connect(self.insert_selected)
        row.addWidget(b)
        b = QPushButton("☆ Favorite")
        b.clicked.connect(self.favorite)
        row.addWidget(b)
        layout.addWidget(QLabel("Ctrl+click for multiple • Double-click to insert"))
        row = QHBoxLayout()
        row.addWidget(QLabel("Thumbnail size:"))
        layout.addLayout(row)
        self.size = QSlider(Qt.Orientation.Horizontal)
        self.size.setRange(48, 160)
        self.size.setValue(int(settings.value("thumbnailSize", 88)))
        row.addWidget(self.size)
        self.size.valueChanged.connect(self.resize_thumbnails)
        self.search.textChanged.connect(self.refresh)
        self.category.currentIndexChanged.connect(self.refresh)
        self.categories()
        self.resize_thumbnails()

    def persist(self):
        for key, val in (
            ("assetFolders", self.folders),
            ("favorites", self.favorites),
            ("recent", self.recent),
        ):
            self.settings.setValue(key, json.dumps(val))

    def categories(self):
        index = max(0, self.category.currentIndex())
        self.category.blockSignals(True)
        self.category.clear()
        self.category.addItems(
            ["All assets", "★ Favorites", "◷ Recently used"]
            + [f["name"] for f in self.folders]
        )
        self.category.setCurrentIndex(min(index, self.category.count() - 1))
        self.category.blockSignals(False)
        self.refresh()

    def paths(self):
        index = self.category.currentIndex()
        if index == 1:
            return self.favorites
        if index == 2:
            return self.recent
        folders = self.folders if index == 0 else self.folders[index - 3 : index - 2]
        paths = []
        for f in folders:
            folder = Path(f["path"])
            if folder.is_dir():
                paths.extend(
                    str(p)
                    for p in sorted(folder.glob("*"))
                    if p.is_file() and p.suffix.lower() == ".png"
                )
        return list(dict.fromkeys(paths))

    def refresh(self):
        self.list.clear()
        query = self.search.text().casefold()
        for path in self.paths():
            p = Path(path)
            if query not in p.stem.casefold() or not p.is_file():
                continue
            pixmap = QPixmap(path)
            if pixmap.isNull():
                continue
            item = QListWidgetItem(
                QIcon(
                    pixmap.scaled(
                        160,
                        160,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                ),
                ("★ " if path in self.favorites else "") + p.stem,
            )
            item.setToolTip(path)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.list.addItem(item)

    def resize_thumbnails(self):
        size = self.size.value()
        self.list.setIconSize(QSize(size, size))
        self.list.setGridSize(QSize(size + 28, size + 42))
        self.settings.setValue("thumbnailSize", size)

    def add_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "Reference an existing PNG folder"
        )
        if path and not any(f["path"] == path for f in self.folders):
            self.folders.append({"name": Path(path).name, "path": path})
            self.persist()
            self.categories()
            self.category.setCurrentIndex(len(self.folders) + 2)

    def manage(self):
        index = self.category.currentIndex() - 3
        if index < 0:
            QMessageBox.information(self, "Folders", "Choose a folder category first.")
            return
        menu = QMessageBox(self)
        menu.setWindowTitle("Manage folder")
        menu.setText(
            "Rename this library category, create a subfolder, or remove its reference?\nRemoving a reference leaves your files on disk."
        )
        rename = menu.addButton("Rename", QMessageBox.ButtonRole.ActionRole)
        create = menu.addButton("New subfolder", QMessageBox.ButtonRole.ActionRole)
        remove = menu.addButton(
            "Remove reference", QMessageBox.ButtonRole.DestructiveRole
        )
        menu.addButton(QMessageBox.StandardButton.Cancel)
        menu.exec()
        if menu.clickedButton() == rename:
            name, ok = QInputDialog.getText(
                self, "Rename category", "Name:", text=self.folders[index]["name"]
            )
            if ok and name.strip():
                self.folders[index]["name"] = name.strip()
        elif menu.clickedButton() == create:
            name, ok = QInputDialog.getText(self, "New subfolder", "Folder name:")
            if (
                ok
                and name.strip()
                and not any(c in name for c in '/\\<>:"|?*')
                and name not in (".", "..")
            ):
                path = Path(self.folders[index]["path"]) / name
                try:
                    path.mkdir()
                    self.folders.append({"name": name, "path": str(path)})
                except OSError as e:
                    QMessageBox.warning(self, "Folder", str(e))
        elif menu.clickedButton() == remove:
            self.folders.pop(index)
        self.persist()
        self.categories()

    def add_files(self):
        index = self.category.currentIndex() - 3
        if index < 0:
            QMessageBox.information(
                self,
                "Add PNGs",
                "Choose a folder category first. New PNGs will be copied there only when you request it.",
            )
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add PNGs to this folder", filter="PNG images (*.png)"
        )
        import shutil
        from .model import unique_path

        try:
            for path in paths:
                p = Path(path)
                destination = Path(self.folders[index]["path"])
                if p.parent.resolve() != destination.resolve():
                    shutil.copy2(p, unique_path(destination, p.stem, ".png"))
        except OSError as e:
            QMessageBox.warning(self, "Add PNGs", str(e))
        self.refresh()

    def favorite(self):
        for item in self.list.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path in self.favorites:
                self.favorites.remove(path)
            else:
                self.favorites.append(path)
        self.persist()
        self.refresh()

    def insert_selected(self):
        self.send([i.data(Qt.ItemDataRole.UserRole) for i in self.list.selectedItems()])

    def send(self, paths):
        if not paths:
            return
        self.recent = list(dict.fromkeys(paths + self.recent))[:100]
        self.persist()
        self.insert.emit(paths)
