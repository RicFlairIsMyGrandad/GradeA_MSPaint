from __future__ import annotations
import json
import sys
import uuid
import copy
from pathlib import Path
from PIL import Image
from PySide6.QtCore import Qt, QSize, QSettings, QTimer, Signal
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QKeySequence,
    QColor,
    QFont,
    QPainter,
    QImage,
    QPixmap,
    QIcon,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QToolButton,
    QLabel,
    QTabWidget,
    QScrollArea,
    QDockWidget,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QToolBar,
    QSizePolicy,
    QSlider,
    QFileDialog,
    QMessageBox,
    QColorDialog,
    QInputDialog,
    QCheckBox,
    QMenu,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
)
from .icons import tool_icon
from .model import Document, Layer, SPECIAL_BLUE, unique_path, MAX_PIXELS
from .canvas import Canvas, qimage
from .assets import AssetLibrary
from .dialogs import TransformDialog, ShortcutDialog, TextDialog

PALETTE = [
    "#000000",
    "#7f7f7f",
    "#880015",
    "#ed1c24",
    "#ff7f27",
    "#fff200",
    "#22b14c",
    "#00a2e8",
    "#3f48cc",
    "#a349a4",
    "#ffffff",
    "#c3c3c3",
    "#b97a57",
    "#ffaec9",
    "#ffc90e",
    "#efe4b0",
    "#b5e61d",
    "#99d9ea",
    "#7092be",
    "#c8bfe7",
    SPECIAL_BLUE,
]
TOOLS = [
    ("select", "▧", "Select", "0"),
    ("pencil", "✎", "Pencil", "1"),
    ("brush", "🖌", "Brush", "2"),
    ("eraser", "▱", "Eraser", "3"),
    ("fill", "◩", "Fill", "4"),
    ("text", "A", "Text", "5"),
    ("shape", "◇", "Shape", "6"),
    ("eyedropper", "⌖", "Picker", "7"),
    ("crop", "⊞", "Crop", "8"),
    ("move", "✥", "Move", "9"),
]
STYLE = """
QMainWindow, QWidget { font-family: 'Segoe UI', 'DejaVu Sans'; font-size: 12px; color: #20252b; }
QMainWindow { background: #f5f6f8; }
QMenuBar { background: #fafbfd; padding: 3px; border-bottom: 1px solid #d6dce5; }
QMenuBar::item { padding: 6px 15px; }
QMenuBar::item:selected { background: #ddecff; }
QTabWidget::pane { border: 0; border-bottom: 1px solid #cdd5df; background: #f8f9fb; }
QTabBar::tab { padding: 7px 24px; background: #f6f7f9; border: 1px solid transparent; }
QTabBar::tab:selected { background: #fff; border: 1px solid #d5dce6; border-bottom: 0; }
QPushButton, QToolButton { background: #ffffff; border: 1px solid #ccd4df; border-radius: 3px; padding: 5px 8px; }
QPushButton:hover, QToolButton:hover { background: #e6f2ff; border-color: #8cbcf1; }
QPushButton:pressed, QToolButton:checked { background: #cfe5ff; border-color: #0078d4; }
QPushButton:disabled { color: #9a9fa8; }
QToolButton::menu-button { width: 12px; background: #e5f0fd; border-left: 1px solid #9fbfe5; border-radius: 2px; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QFontComboBox { background: white; border: 1px solid #cbd3df; border-radius: 3px; padding: 4px; min-height: 20px; }
QDockWidget { font-weight: bold; }
QDockWidget::title { background: #f5f6f8; padding: 9px; }
QListWidget { background: #f8f9fb; border: 1px solid #d9dee7; border-radius: 3px; outline: 0; }
QListWidget::item { padding: 4px; border-radius: 3px; }
QListWidget::item:selected { background: #cfe5ff; color: #172a43; }
QStatusBar { border-top: 1px solid #ccd4df; background: #f7f8fa; }
QSlider::groove:horizontal { height: 5px; background: #c4cbd4; border-radius: 2px; }
QSlider::handle:horizontal { background: #0078d4; width: 13px; margin: -5px 0; border-radius: 4px; }
QScrollArea { border: 0; background: #e8edf3; }
QDialog { background: #f8f9fb; }
"""


class LayerList(QListWidget):
    reordered = Signal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.reordered.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("GradeA", "PaintPlus", self)
        self.doc = Document()
        self.project_path = None
        self.actions = {}
        self.ai_worker = None
        self._closing = False
        self.setWindowTitle("Untitled — GradeA PaintPlus")
        self.resize(1500, 950)
        self.setMinimumSize(1000, 650)
        self.setDockOptions(QMainWindow.DockOption.AnimatedDocks)
        self.canvas = Canvas(self.doc)
        self.canvas.changed.connect(self.sync)
        self.canvas.selected.connect(self.sync_layers)
        self.canvas.picked.connect(self.choose_color)
        self.canvas.text_requested.connect(self.add_text)
        self.canvas.dropped.connect(self.insert_images)
        self.create_actions()
        self.create_menu()
        center = QWidget()
        vertical = QVBoxLayout(center)
        vertical.setContentsMargins(0, 0, 0, 0)
        vertical.setSpacing(0)
        self.ribbon = QTabWidget()
        self.ribbon.setFixedHeight(150)
        toolbar = QToolBar("Ribbon", self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.ribbon.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        toolbar.addWidget(self.ribbon)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.create_ribbon()
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.canvas)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        vertical.addWidget(self.scroll)
        self.setCentralWidget(center)
        self.create_assets()
        self.create_layers()
        self.create_status()
        self.sync()
        self.restore_shortcuts()
        self.asset_dock.setVisible(
            self.settings.value("assetsVisible", True, type=bool)
        )
        self.layer_dock.setVisible(
            self.settings.value("layersVisible", True, type=bool)
        )
        self.asset_dock.visibilityChanged.connect(
            lambda v: self.panel_visibility("assetsVisible", v)
        )
        self.layer_dock.visibilityChanged.connect(
            lambda v: self.panel_visibility("layersVisible", v)
        )
        QTimer.singleShot(0, self.fit_canvas)

    def panel_visibility(self, name, visible):
        if self.isVisible() and not self._closing:
            self.settings.setValue(name, visible)

    def action(self, name, title, shortcut, fn):
        action = QAction(title, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(fn)
        self.addAction(action)
        self.actions[name] = action
        return action

    def create_actions(self):
        self.tool_group = QActionGroup(self)
        for name, symbol, title, key in TOOLS:
            action = self.action(
                name, title, key, lambda checked=False, n=name: self.set_tool(n)
            )
            action.setCheckable(True)
            self.tool_group.addAction(action)
            action.setIcon(tool_icon(name))
        self.actions["select"].setChecked(True)
        self.action(
            "region", "Rectangular selection", "", lambda: self.set_tool("region")
        )
        definitions = [
            ("new", "New", "Ctrl+N", self.new_document),
            ("open", "Open…", "Ctrl+O", self.open_document),
            ("save", "Save project", "Ctrl+S", self.save_project),
            (
                "saveas",
                "Save project as…",
                "Ctrl+Shift+S",
                lambda: self.save_project(True),
            ),
            ("export", "Export image…", "Ctrl+E", self.export_image),
            ("quick", "Quick Save", "F6", self.quick_save),
            ("undo", "Undo", "Ctrl+Z", self.undo),
            ("redo", "Redo", "Ctrl+Y", self.redo),
            ("copy", "Copy", "Ctrl+C", self.copy_selection),
            ("cut", "Cut", "Ctrl+X", self.cut_selection),
            ("paste", "Paste", "Ctrl+V", self.paste),
            ("delete", "Delete selection", "Delete", self.delete_layers),
            ("duplicate", "Duplicate", "Ctrl+D", self.duplicate_layers),
            ("all", "Select all unlocked layers", "Ctrl+A", self.select_all),
            ("transform", "Resize & Rotate…", "Ctrl+R", self.transform_selected),
            ("group", "Group", "Ctrl+G", self.group_layers),
            ("ungroup", "Ungroup", "Ctrl+Shift+G", self.ungroup_layers),
            ("merge", "Merge selected", "Ctrl+M", self.merge_layers),
            ("lockbg", "Lock Background", "Ctrl+L", self.lock_background),
            ("shortcuts", "Edit shortcuts…", "", self.shortcuts),
            ("removebg", "Remove Background…", "", self.remove_background),
            ("insert", "Insert image…", "Ctrl+I", self.insert_dialog),
            ("edittext", "Edit text…", "", self.edit_text),
            ("rename", "Rename layer…", "F2", self.rename_layer),
            ("fit", "Fit canvas", "Ctrl+0", self.fit_canvas),
        ]
        for args in definitions:
            self.action(*args)

    def create_menu(self):
        file = self.menuBar().addMenu("File")
        for key in ("new", "open", "save", "saveas", "export", "quick"):
            file.addAction(self.actions[key])
        file.addSeparator()
        file.addAction("Exit", self.close)
        edit = self.menuBar().addMenu("Edit")
        for key in (
            "undo",
            "redo",
            "cut",
            "copy",
            "paste",
            "all",
            "delete",
            "duplicate",
            "group",
            "ungroup",
            "merge",
        ):
            edit.addAction(self.actions[key])
        self.view_menu = self.menuBar().addMenu("View")
        self.view_menu.addAction(self.actions["fit"])
        settings = self.menuBar().addMenu("Settings")
        settings.addAction(self.actions["shortcuts"])
        settings.addAction(
            "Background removal edge smoothing…", self.background_settings
        )
        helpmenu = self.menuBar().addMenu("Help")
        helpmenu.addAction("Getting started", self.help)
        helpmenu.addAction("Open example scene", self.open_demo)
        helpmenu.addAction("About", self.about)

    def group_widget(self, title):
        widget = QWidget()
        outer = QVBoxLayout(widget)
        outer.setContentsMargins(10, 4, 10, 2)
        outer.setSpacing(3)
        content = QHBoxLayout()
        outer.addLayout(content, 1)
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color:#68727d;font-size:11px")
        outer.addWidget(label)
        widget.setStyleSheet("QWidget { background:transparent; }")
        return widget, content

    def toolbutton(self, action, symbol=None):
        b = QToolButton()
        b.setDefaultAction(action)
        b.setIcon(
            action.icon() if not action.icon().isNull() else tool_icon("clipboard")
        )
        b.setIconSize(QSize(30, 30))
        b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        b.setMinimumSize(54, 50)
        return b

    def create_ribbon(self):
        home = QWidget()
        row = QHBoxLayout(home)
        row.setContentsMargins(4, 2, 4, 2)
        row.setSpacing(0)
        w, layout = self.group_widget("Clipboard")
        layout.addWidget(self.toolbutton(self.actions["paste"], "▣"))
        stack = QVBoxLayout()
        layout.addLayout(stack)
        for key in ("cut", "copy"):
            b = QPushButton(self.actions[key].text())
            b.clicked.connect(self.actions[key].trigger)
            stack.addWidget(b)
        row.addWidget(w)
        w, layout = self.group_widget("Image")
        select_button = self.toolbutton(self.actions["select"], "▧")
        selection_menu = QMenu(select_button)
        selection_menu.addAction(self.actions["select"])
        selection_menu.addAction(self.actions["region"])
        select_button.setMenu(selection_menu)
        select_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        layout.addWidget(select_button)
        stack = QVBoxLayout()
        layout.addLayout(stack)
        for key in ("crop", "transform", "insert"):
            b = QPushButton(
                "Crop"
                if key == "crop"
                else "Resize / Rotate"
                if key == "transform"
                else "Insert image"
            )
            b.clicked.connect(self.actions[key].trigger)
            stack.addWidget(b)
        row.addWidget(w)
        w, layout = self.group_widget("Tools")
        grid = QGridLayout()
        layout.addLayout(grid)
        for i, (name, symbol, title, key) in enumerate(TOOLS[1:8]):
            b = QToolButton()
            b.setDefaultAction(self.actions[name])
            b.setIcon(tool_icon(name))
            b.setIconSize(QSize(24, 24))
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            b.setToolTip(title + " (" + key + ")")
            b.setFixedSize(32, 30)
            grid.addWidget(b, i // 4, i % 4)
        row.addWidget(w)
        w, layout = self.group_widget("Brushes & Shapes")
        stack = QVBoxLayout()
        layout.addLayout(stack)
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(
            ["Rectangle", "Ellipse", "Line", "Triangle", "Rounded rectangle"]
        )
        self.shape_combo.currentTextChanged.connect(
            lambda text: setattr(self.canvas, "shape", text)
        )
        stack.addWidget(self.shape_combo)
        self.brush_combo = QComboBox()
        self.brush_combo.addItems(["Round brush", "Marker", "Calligraphy", "Airbrush"])
        self.brush_combo.setToolTip("Brush style")
        self.brush_combo.currentTextChanged.connect(self.choose_brush)
        stack.addWidget(self.brush_combo)
        self.shape_fill = QCheckBox("Fill shape")
        self.shape_fill.toggled.connect(lambda v: setattr(self.canvas, "shape_fill", v))
        stack.addWidget(self.shape_fill)
        row.addWidget(w)
        w, layout = self.group_widget("Size")
        self.brush_size = QSpinBox()
        self.brush_size.setRange(1, 200)
        self.brush_size.setValue(5)
        self.brush_size.setSuffix(" px")
        self.brush_size.valueChanged.connect(
            lambda n: setattr(self.canvas, "brush_size", n)
        )
        layout.addWidget(self.brush_size)
        row.addWidget(w)
        w, layout = self.group_widget("Colors")
        self.primary = QPushButton("Color 1")
        self.primary.setFixedSize(64, 65)
        self.primary.clicked.connect(self.custom_color)
        layout.addWidget(self.primary)
        self.secondary = QPushButton("Color 2")
        self.secondary.setFixedSize(64, 65)
        self.secondary.clicked.connect(self.custom_secondary)
        layout.addWidget(self.secondary)
        grid = QGridLayout()
        grid.setSpacing(3)
        layout.addLayout(grid)
        for i, color in enumerate(PALETTE):
            b = QPushButton()
            b.setFixedSize(22, 22)
            b.setToolTip(
                "Special blue • RGB 24, 71, 241" if color == SPECIAL_BLUE else color
            )
            b.setStyleSheet(
                f"background:{color};border:{'2px solid #425bc2' if color == SPECIAL_BLUE else '1px solid #aab2bd'};border-radius:2px;"
            )
            b.clicked.connect(lambda checked=False, c=color: self.choose_color(c))
            b.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            b.customContextMenuRequested.connect(
                lambda pos, c=color: self.choose_secondary(c)
            )
            grid.addWidget(b, i // 11, i % 11)
        b = QPushButton("Edit\ncolors")
        b.clicked.connect(self.custom_color)
        layout.addWidget(b)
        row.addWidget(w)
        row.addStretch()
        w, layout = self.group_widget("Scene")
        stack = QVBoxLayout()
        layout.addLayout(stack)
        for title, key in (
            ("Lock Background", "lockbg"),
            ("Remove Background", "removebg"),
            ("Shortcuts", "shortcuts"),
        ):
            b = QPushButton(title)
            b.clicked.connect(self.actions[key].trigger)
            stack.addWidget(b)
        row.addWidget(w)
        self.ribbon.addTab(home, "Home")
        view = QWidget()
        v = QHBoxLayout(view)
        v.setContentsMargins(14, 12, 14, 12)
        for title, fn in (
            ("Fit canvas", self.fit_canvas),
            ("100%", lambda: self.set_zoom(100)),
            ("Canvas size…", self.canvas_size),
        ):
            b = QPushButton(title)
            b.clicked.connect(fn)
            v.addWidget(b)
        self.aspect = QCheckBox("Lock resize aspect ratio")
        self.aspect.setChecked(True)
        self.aspect.toggled.connect(lambda b: setattr(self.canvas, "aspect_lock", b))
        v.addWidget(self.aspect)
        self.assets_toggle = QPushButton("Assets panel")
        self.assets_toggle.clicked.connect(
            lambda: self.asset_dock.setVisible(not self.asset_dock.isVisible())
        )
        v.addWidget(self.assets_toggle)
        self.layers_toggle = QPushButton("Layers panel")
        self.layers_toggle.clicked.connect(
            lambda: self.layer_dock.setVisible(not self.layer_dock.isVisible())
        )
        v.addWidget(self.layers_toggle)
        v.addStretch()
        self.ribbon.addTab(view, "View")
        self.choose_color(SPECIAL_BLUE)
        self.choose_secondary("#ffffff")

    def create_assets(self):
        self.asset_dock = QDockWidget("Assets", self)
        self.asset_dock.setObjectName("assets")
        self.asset_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.asset_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.assets = AssetLibrary(self.settings)
        self.assets.insert.connect(self.insert_images)
        self.asset_dock.setWidget(self.assets)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.asset_dock)
        self.asset_dock.setMinimumWidth(260)
        self.resizeDocks([self.asset_dock], [285], Qt.Orientation.Horizontal)
        self.view_menu.addAction(self.asset_dock.toggleViewAction())

    def create_layers(self):
        self.layer_dock = QDockWidget("Layers", self)
        self.layer_dock.setObjectName("layers")
        self.layer_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 8, 10, 8)
        row = QHBoxLayout()
        layout.addLayout(row)
        for text, fn in (
            ("+", self.new_layer),
            ("↑", lambda: self.move_layer(1)),
            ("↓", lambda: self.move_layer(-1)),
            ("⧉", self.duplicate_layers),
            ("⌫", self.delete_layers),
        ):
            b = QPushButton(text)
            b.setFixedWidth(36)
            b.clicked.connect(fn)
            row.addWidget(b)
        self.layer_list = LayerList()
        self.layer_list.setIconSize(QSize(48, 48))
        self.layer_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.layer_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.layer_list.reordered.connect(self.reorder_layers)
        self.layer_list.itemSelectionChanged.connect(self.layer_selected)
        self.layer_list.itemChanged.connect(self.layer_visibility)
        self.layer_list.itemDoubleClicked.connect(lambda item: self.rename_layer())
        self.layer_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.layer_list.customContextMenuRequested.connect(self.layer_menu)
        layout.addWidget(self.layer_list, 1)
        row = QHBoxLayout()
        layout.addLayout(row)
        for text, fn in (
            ("Lock / Unlock", self.toggle_lock),
            ("Group", self.group_layers),
            ("Merge", self.merge_layers),
        ):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        b = QPushButton("Edit selected text…")
        b.clicked.connect(self.edit_text)
        layout.addWidget(b)
        label = QLabel("Tool shortcuts")
        label.setStyleSheet("font-size:15px;font-weight:600;margin-top:12px")
        layout.addWidget(label)
        self.shortcut_labels = {}
        for name, _, title, _ in TOOLS:
            label = QLabel()
            self.shortcut_labels[name] = label
            label.setStyleSheet(
                "background:#fff;border-bottom:1px solid #e0e5ec;padding:4px;"
            )
            layout.addWidget(label)
        b = QPushButton("Edit Shortcuts…")
        b.clicked.connect(self.shortcuts)
        layout.addWidget(b)
        self.layer_dock.setWidget(content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layer_dock)
        self.layer_dock.setMinimumWidth(265)
        self.resizeDocks([self.layer_dock], [285], Qt.Orientation.Horizontal)
        self.view_menu.addAction(self.layer_dock.toggleViewAction())

    def create_status(self):
        self.coords = QLabel("Ready")
        self.statusBar().addWidget(self.coords)
        self.dimensions = QLabel()
        self.statusBar().addWidget(self.dimensions)
        self.canvas.position.connect(self.coords.setText)
        self.canvas.zoom_requested.connect(
            lambda delta: self.set_zoom(
                max(10, min(400, round(self.canvas.zoom * 100) + delta))
            )
        )
        self.filename = QLineEdit(self.settings.value("quickName", "Untitled"))
        self.filename.setPlaceholderText("Filename")
        self.filename.setMaximumWidth(160)
        self.filename.setToolTip("Quick Save filename")
        self.output_folder = self.settings.value(
            "outputFolder", str(Path.home() / "Pictures")
        )
        self.folder_button = QPushButton("▣ Folder")
        self.folder_button.clicked.connect(self.choose_output)
        self.format = QComboBox()
        self.format.addItems(["PNG", "JPEG", "BMP", "TIFF", "WEBP"])
        self.format.setCurrentText(self.settings.value("quickFormat", "PNG"))
        self.save_button = QPushButton("▣ Quick Save")
        self.save_button.setStyleSheet(
            "background:#0078d4;color:white;border-color:#0078d4;font-weight:600;"
        )
        self.save_button.clicked.connect(self.quick_save)
        for widget in (
            self.folder_button,
            self.filename,
            self.format,
            self.save_button,
        ):
            self.statusBar().addPermanentWidget(widget)
        self.zoom_label = QLabel("100%")
        self.statusBar().addPermanentWidget(self.zoom_label)
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(110)
        self.zoom_slider.valueChanged.connect(self.set_zoom)
        self.statusBar().addPermanentWidget(self.zoom_slider)
        self.update_folder_label()

    def sync(self):
        self.sync_layers()
        self.actions["undo"].setEnabled(bool(self.doc.undo_stack))
        self.actions["redo"].setEnabled(bool(self.doc.redo_stack))
        self.dimensions.setText(f"  {self.doc.width} × {self.doc.height} px  ")
        title = Path(self.project_path).stem if self.project_path else "Untitled"
        self.setWindowTitle(
            f"{'* ' if self.doc.dirty else ''}{title} — GradeA PaintPlus"
        )

    def sync_layers(self):
        self.layer_list.blockSignals(True)
        self.layer_list.clear()
        for l in reversed(self.doc.layers):
            icon = QIcon(
                QPixmap.fromImage(qimage(l.image)).scaled(
                    48,
                    48,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            item = QListWidgetItem(
                icon, ("🔒 " if l.locked else "") + ("▣ " if l.group else "") + l.name
            )
            item.setData(Qt.ItemDataRole.UserRole, l.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if l.visible else Qt.CheckState.Unchecked
            )
            self.layer_list.addItem(item)
            item.setSelected(l.id in self.canvas.selection)
        self.layer_list.blockSignals(False)

    def layer_selected(self):
        self.canvas.selection = [
            i.data(Qt.ItemDataRole.UserRole) for i in self.layer_list.selectedItems()
        ]
        self.canvas.update()

    def layer_visibility(self, item):
        layer = next(
            l for l in self.doc.layers if l.id == item.data(Qt.ItemDataRole.UserRole)
        )
        self.doc.checkpoint()
        layer.visible = item.checkState() == Qt.CheckState.Checked
        self.canvas.refresh()

    def reorder_layers(self):
        order = [
            self.layer_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.layer_list.count())
        ]
        self.doc.checkpoint()
        lookup = {l.id: l for l in self.doc.layers}
        self.doc.layers = [lookup[i] for i in reversed(order)]
        self.canvas.refresh()

    def layer_menu(self, pos):
        menu = QMenu(self)
        for key in (
            "rename",
            "duplicate",
            "delete",
            "group",
            "ungroup",
            "merge",
            "edittext",
            "transform",
            "removebg",
        ):
            menu.addAction(self.actions[key])
        menu.addAction("Lock / Unlock", self.toggle_lock)
        menu.exec(self.layer_list.mapToGlobal(pos))

    def set_tool(self, name):
        self.canvas.tool = name
        self.actions[name].setChecked(True)
        cursors = {
            "pencil": Qt.CursorShape.CrossCursor,
            "brush": Qt.CursorShape.CrossCursor,
            "eraser": Qt.CursorShape.CrossCursor,
            "fill": Qt.CursorShape.CrossCursor,
            "text": Qt.CursorShape.IBeamCursor,
            "move": Qt.CursorShape.SizeAllCursor,
        }
        self.canvas.setCursor(cursors.get(name, Qt.CursorShape.ArrowCursor))
        self.canvas.update()
        if name == "crop":
            self.statusBar().showMessage(
                "Drag a rectangle on the canvas to crop. Undo restores the full scene.",
                6000,
            )

    def choose_brush(self, name):
        self.canvas.brush_style = name
        self.set_tool("brush")

    def choose_color(self, color):
        self.canvas.color = color
        self.primary.setStyleSheet(
            f"background:{color};color:{'#fff' if QColor(color).lightness() < 140 else '#222'};border:2px solid #0078d4;"
        )

    def choose_secondary(self, color):
        self.canvas.secondary = color
        self.secondary.setStyleSheet(
            f"background:{color};color:{'#fff' if QColor(color).lightness() < 140 else '#222'};"
        )

    def custom_color(self):
        c = QColorDialog.getColor(QColor(self.canvas.color), self, "Color 1")
        if c.isValid():
            self.choose_color(c.name())

    def custom_secondary(self):
        c = QColorDialog.getColor(QColor(self.canvas.secondary), self, "Color 2")
        if c.isValid():
            self.choose_secondary(c.name())

    def set_zoom(self, value):
        self.canvas.zoom = value / 100
        self.canvas.resize_canvas()
        self.zoom_label.setText(f"{value}%")
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(value)
        self.zoom_slider.blockSignals(False)

    def fit_canvas(self):
        if not hasattr(self, "zoom_slider"):
            return
        size = self.scroll.viewport().size()
        self.set_zoom(
            max(
                10,
                min(
                    100,
                    int(
                        min(
                            (size.width() - 40) / self.doc.width,
                            (size.height() - 40) / self.doc.height,
                        )
                        * 100
                    ),
                ),
            )
        )

    def confirm_discard(self):
        if not self.doc.dirty:
            return True
        result = QMessageBox.question(
            self,
            "Unsaved project",
            "Save your editable project before continuing?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if result == QMessageBox.StandardButton.Save:
            return self.save_project()
        return result == QMessageBox.StandardButton.Discard

    def replace_document(self, doc, path=None):
        self.doc = doc
        self.canvas.doc = doc
        self.project_path = path
        self.canvas.selection = []
        self.canvas.refresh()
        self.fit_canvas()

    def new_document(self):
        if not self.confirm_discard():
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("New canvas")
        form = QFormLayout(dialog)
        w = QSpinBox()
        h = QSpinBox()
        for spin, value in ((w, 1200), (h, 800)):
            spin.setRange(1, 16000)
            spin.setValue(value)
        form.addRow("Width (px):", w)
        form.addRow("Height (px):", h)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        form.addRow(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec() and w.value() * h.value() <= MAX_PIXELS:
            self.replace_document(Document(w.value(), h.value()))

    def canvas_size(self):
        width, ok = QInputDialog.getInt(
            self, "Canvas size", "Width in pixels:", self.doc.width, 1, 16000
        )
        if not ok:
            return
        height, ok = QInputDialog.getInt(
            self, "Canvas size", "Height in pixels:", self.doc.height, 1, 16000
        )
        if not ok:
            return
        if width * height > MAX_PIXELS:
            self.error("Canvas exceeds 64 million pixels.")
            return
        self.doc.checkpoint()
        self.doc.width = width
        self.doc.height = height
        self.canvas.refresh()
        self.fit_canvas()

    def open_document(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open image or editable project",
            filter="Images and projects (*.paintplus *.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff);;All files (*)",
        )
        if not path or not self.confirm_discard():
            return
        try:
            if Path(path).suffix.lower() == ".paintplus":
                self.replace_document(Document.load(path), path)
            else:
                image = self.read_image(path)
                doc = Document(*image.size)
                doc.layers = [Layer("Background", image)]
                self.replace_document(doc)
        except Exception as e:
            self.error(str(e))

    def save_project(self, save_as=False):
        path = self.project_path
        if not path or save_as:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save editable project",
                path or "Untitled.paintplus",
                "PaintPlus project (*.paintplus)",
            )
        if not path:
            return False
        if not path.lower().endswith(".paintplus"):
            path += ".paintplus"
        try:
            self.doc.save(path)
            self.project_path = path
            self.sync()
            self.statusBar().showMessage("Editable project saved", 4000)
            return True
        except Exception as e:
            self.error(str(e))
            return False

    def export_image(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export flattened image",
            "Untitled.png",
            "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;TIFF (*.tiff);;WebP (*.webp)",
        )
        if not path:
            return
        if not Path(path).suffix:
            path += ".png"
        try:
            self.doc.export(path)
            self.statusBar().showMessage(f"Exported {Path(path).name}", 5000)
        except Exception as e:
            self.error(str(e))

    def update_folder_label(self):
        self.folder_button.setToolTip("Output folder: " + self.output_folder)

    def choose_output(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Choose Quick Save output folder", self.output_folder
        )
        if folder:
            self.output_folder = folder
            self.settings.setValue("outputFolder", folder)
            self.update_folder_label()

    def quick_save(self):
        if not Path(self.output_folder).is_dir():
            self.choose_output()
            if not Path(self.output_folder).is_dir():
                return
        extension = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "BMP": ".bmp",
            "TIFF": ".tiff",
            "WEBP": ".webp",
        }[self.format.currentText()]
        try:
            path = unique_path(self.output_folder, self.filename.text(), extension)
            self.doc.export(path)
            self.settings.setValue("quickName", self.filename.text())
            self.settings.setValue("quickFormat", self.format.currentText())
            self.statusBar().showMessage(
                f"Saved: {path} — editable project is saved separately with Ctrl+S",
                8000,
            )
        except Exception as e:
            self.error(str(e))

    def read_image(self, path):
        from PIL import ImageOps

        with Image.open(path) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError("Image exceeds 64 million pixels.")
            return ImageOps.exif_transpose(image).convert("RGBA")

    def insert_dialog(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Insert images",
            filter="Images (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff)",
        )
        self.insert_images(paths)

    def insert_images(self, paths):
        if not paths:
            return
        try:
            images = [(self.read_image(p), Path(p).stem) for p in paths]
            self.doc.checkpoint()
            ids = []
            for i, (image, name) in enumerate(images):
                layer = Layer(name, image, 40 + i * 24, 40 + i * 24)
                scale = min(
                    1,
                    self.doc.width * 0.7 / image.width,
                    self.doc.height * 0.7 / image.height,
                )
                layer.width *= scale
                layer.height *= scale
                self.doc.layers.append(layer)
                ids.append(layer.id)
            self.canvas.selection = ids
            self.set_tool("select")
            self.canvas.refresh()
        except Exception as e:
            self.error(str(e))

    def new_layer(self):
        self.doc.checkpoint()
        layer = Layer("New layer", Image.new("RGBA", (self.doc.width, self.doc.height)))
        self.doc.layers.append(layer)
        self.canvas.selection = [layer.id]
        self.canvas.refresh()

    def selected_unlocked(self):
        layers = self.canvas.layers()
        if not layers:
            self.statusBar().showMessage("Select an object or layer first.", 4000)
            return []
        if any(l.locked for l in layers):
            self.statusBar().showMessage("Unlock selected layers first.", 4000)
            return []
        return layers

    def delete_layers(self):
        selected = self.selected_unlocked()
        if not selected:
            return
        self.doc.checkpoint()
        selected_ids = {l.id for l in selected}
        self.doc.layers = [l for l in self.doc.layers if l.id not in selected_ids]
        self.canvas.selection = []
        self.canvas.refresh()

    def duplicate_layers(self):
        selected = self.selected_unlocked()
        if not selected:
            return
        self.doc.checkpoint()
        ids = []
        groups = {}
        for layer in selected:
            new = copy.deepcopy(layer)
            new.id = uuid.uuid4().hex
            new.name += " copy"
            new.x += 20
            new.y += 20
            if new.group:
                new.group = groups.setdefault(new.group, uuid.uuid4().hex)
            self.doc.layers.append(new)
            ids.append(new.id)
        self.canvas.selection = ids
        self.canvas.refresh()

    def rename_layer(self):
        layers = self.canvas.layers()
        if len(layers) != 1:
            return
        name, ok = QInputDialog.getText(
            self, "Rename layer", "Name:", text=layers[0].name
        )
        if ok and name.strip():
            self.doc.checkpoint()
            layers[0].name = name.strip()
            self.canvas.refresh()

    def move_layer(self, direction):
        selected = self.canvas.layers()
        if not selected:
            return
        self.doc.checkpoint()
        for layer in sorted(selected, key=self.doc.layers.index, reverse=direction > 0):
            i = self.doc.layers.index(layer)
            target = i + direction
            if 0 <= target < len(self.doc.layers):
                self.doc.layers[i], self.doc.layers[target] = (
                    self.doc.layers[target],
                    self.doc.layers[i],
                )
        self.canvas.refresh()

    def toggle_lock(self):
        layers = self.canvas.layers()
        if not layers:
            return
        self.doc.checkpoint()
        value = not all(l.locked for l in layers)
        for l in layers:
            l.locked = value
        self.canvas.refresh()

    def lock_background(self):
        if not self.doc.layers:
            return
        self.doc.checkpoint()
        self.doc.layers[0].locked = not self.doc.layers[0].locked
        self.canvas.selection = [
            i for i in self.canvas.selection if i != self.doc.layers[0].id
        ]
        self.canvas.refresh()

    def group_layers(self):
        layers = self.selected_unlocked()
        if len(layers) < 2:
            return
        self.doc.checkpoint()
        group = uuid.uuid4().hex
        for l in layers:
            l.group = group
        self.canvas.refresh()

    def ungroup_layers(self):
        layers = self.selected_unlocked()
        if not layers:
            return
        self.doc.checkpoint()
        for l in layers:
            l.group = None
        self.canvas.refresh()

    def merge_layers(self):
        if len(self.selected_unlocked()) < 2:
            return
        try:
            merged = self.doc.merge(self.canvas.selection)
            self.canvas.selection = [merged.id]
            self.canvas.refresh()
        except ValueError as e:
            self.error(str(e))

    def select_all(self):
        self.canvas.selection = [
            l.id for l in self.doc.layers if not l.locked and l.visible
        ]
        self.set_tool("select")
        self.canvas.selected.emit()
        self.canvas.update()

    def transform_selected(self):
        layers = self.selected_unlocked()
        if not layers:
            return
        if len(layers) > 1:
            self.statusBar().showMessage(
                "Use canvas handles to transform a group. Exact values apply to one object at a time.",
                6000,
            )
            return
        dialog = TransformDialog(layers[0], self)
        if dialog.exec():
            self.doc.checkpoint()
            dialog.apply()
            self.canvas.refresh()

    def undo(self):
        if self.doc.undo():
            self.canvas.refresh()

    def redo(self):
        if self.doc.redo():
            self.canvas.refresh()

    def copy_selection(self):
        selected = self.canvas.layers()
        if selected:
            temporary = Document(self.doc.width, self.doc.height)
            temporary.layers = selected
            image = temporary.flatten()
            bbox = image.getbbox()
            image = image.crop(bbox) if bbox else image
        else:
            image = self.doc.flatten()
        QApplication.clipboard().setImage(qimage(image))
        self.statusBar().showMessage("Copied image to clipboard", 3000)

    def cut_selection(self):
        if self.selected_unlocked():
            self.copy_selection()
            self.delete_layers()

    def paste(self):
        clipboard = QApplication.clipboard()
        if clipboard.mimeData().hasUrls():
            self.insert_images(
                [
                    u.toLocalFile()
                    for u in clipboard.mimeData().urls()
                    if u.isLocalFile()
                ]
            )
            return
        image = clipboard.image()
        if image.isNull():
            self.statusBar().showMessage(
                "The clipboard does not contain an image.", 4000
            )
            return
        image = image.convertToFormat(QImage.Format.Format_RGBA8888)
        pil = Image.frombytes(
            "RGBA",
            (image.width(), image.height()),
            bytes(image.constBits()),
            "raw",
            "RGBA",
            image.bytesPerLine(),
        )
        layer = self.doc.add_image(pil, "Pasted image")
        self.canvas.selection = [layer.id]
        self.set_tool("select")
        self.canvas.refresh()

    def render_text(self, data):
        font = QFont(data["font"], data["size"])
        font.setBold(data["bold"])
        from PySide6.QtGui import QFontMetrics

        metrics = QFontMetrics(font)
        rect = metrics.boundingRect(data["content"] or " ")
        image = QImage(
            max(1, rect.width() + 12),
            max(1, metrics.height() + 12),
            QImage.Format.Format_RGBA8888,
        )
        image.fill(Qt.GlobalColor.transparent)
        p = QPainter(image)
        p.setFont(font)
        p.setPen(QColor(data.get("color", self.canvas.color)))
        p.drawText(6 - rect.left(), 6 + metrics.ascent(), data["content"])
        p.end()
        return Image.frombytes(
            "RGBA",
            (image.width(), image.height()),
            bytes(image.constBits()),
            "raw",
            "RGBA",
            image.bytesPerLine(),
        )

    def add_text(self, x, y):
        dialog = TextDialog(parent=self)
        if not dialog.exec() or not dialog.text.text():
            return
        data = dialog.data()
        data["color"] = self.canvas.color
        layer = self.doc.add_image(
            self.render_text(data), "Text: " + data["content"][:24], x, y
        )
        layer.text = data
        self.canvas.selection = [layer.id]
        self.set_tool("select")
        self.canvas.refresh()

    def edit_text(self):
        selected = self.selected_unlocked()
        if len(selected) != 1 or not selected[0].text:
            self.statusBar().showMessage("Select one editable text layer.", 4000)
            return
        layer = selected[0]
        dialog = TextDialog(layer.text, self)
        if dialog.exec():
            self.doc.checkpoint()
            data = dialog.data()
            data["color"] = layer.text.get("color", self.canvas.color)
            image = self.render_text(data)
            layer.width *= image.width / layer.image.width
            layer.height *= image.height / layer.image.height
            layer.image = image
            layer.text = data
            layer.name = "Text: " + data["content"][:24]
            self.canvas.refresh()

    def shortcuts(self):
        dialog = ShortcutDialog(self.actions, self)
        if dialog.exec():
            for name, edit in dialog.editors.items():
                self.actions[name].setShortcut(edit.keySequence())
            self.settings.setValue(
                "shortcuts",
                json.dumps(
                    {
                        name: action.shortcut().toString()
                        for name, action in self.actions.items()
                    }
                ),
            )
            self.update_shortcut_labels()

    def restore_shortcuts(self):
        data = json.loads(self.settings.value("shortcuts", "{}"))
        for name, key in data.items():
            if name in self.actions:
                self.actions[name].setShortcut(QKeySequence(key))
        self.update_shortcut_labels()

    def update_shortcut_labels(self):
        for name, label in self.shortcut_labels.items():
            label.setText(
                f"  {self.actions[name].shortcut().toString() or '—'}     {self.actions[name].text()}"
            )

    def background_settings(self):
        value, ok = QInputDialog.getDouble(
            self,
            "Background removal",
            "Edge smoothing radius (0 keeps crisp edges):",
            float(self.settings.value("aiFeather", 0)),
            0,
            5,
            1,
        )
        if ok:
            self.settings.setValue("aiFeather", value)

    def remove_background(self):
        selected = self.selected_unlocked()
        if len(selected) != 1:
            self.statusBar().showMessage(
                "Select one image for background removal.", 4000
            )
            return
        from .background import model_path, BackgroundWorker

        if not model_path().is_file():
            self.error(
                "The optional offline AI model is not installed. Use the full AI-enabled Windows build, or see docs/BACKGROUND_REMOVAL.md. No image is uploaded."
            )
            return
        if self.ai_worker:
            return
        layer = selected[0]
        self.actions["removebg"].setEnabled(False)
        self.statusBar().showMessage("Removing background locally…")
        self.ai_document = self.doc
        self.ai_original = layer.image.tobytes()
        self.ai_worker = BackgroundWorker(
            layer.image.copy(),
            layer.id,
            self,
            feather=float(self.settings.value("aiFeather", 0)),
        )
        self.ai_worker.result.connect(self.background_finished)
        self.ai_worker.failed.connect(self.background_failed)
        self.ai_worker.finished.connect(self.background_cleanup)
        self.ai_worker.start()

    def background_finished(self, id, image):
        layer = next((l for l in self.doc.layers if l.id == id), None)
        if (
            layer
            and self.doc is self.ai_document
            and layer.image.tobytes() == self.ai_original
            and not layer.locked
        ):
            self.doc.checkpoint()
            layer.image = image
            self.canvas.refresh()
            self.statusBar().showMessage(
                "Background removed locally. Undo is available.", 6000
            )
        else:
            self.statusBar().showMessage(
                "Image changed during inference; result discarded. Try again on the current image.",
                6000,
            )

    def background_failed(self, message):
        self.error(message)

    def background_cleanup(self):
        self.ai_worker.deleteLater()
        self.ai_worker = None
        self.actions["removebg"].setEnabled(True)

    def error(self, message):
        QMessageBox.warning(self, "PaintPlus", message)

    def open_demo(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "Woodland.paintplus"
        if path.is_file() and self.confirm_discard():
            self.replace_document(Document.load(path))

    def help(self):
        QMessageBox.information(
            self,
            "Getting started",
            "PaintPlus works entirely offline.\n\nDraw using the Home tools. Choose Color 1 for the left mouse button; Color 2 for the right.\n\nOpen a background, then Lock Background. Add PNG asset folders on the left; double-click to insert. Ctrl+click selects several assets or layers. Each inserted image stays editable.\n\nDrag objects to move. Drag the eight handles to resize; use the round handle to rotate. Shift snaps rotation to 15°. Resize / Rotate offers exact values and pixel-art mode.\n\nCtrl+S saves an editable .paintplus project. Quick Save exports an image to your chosen folder and gives duplicates a new number.\n\nUse View to hide Assets and Layers. Settings lets you change shortcuts, including number keys.",
        )

    def about(self):
        QMessageBox.information(
            self,
            "About GradeA PaintPlus",
            "GradeA PaintPlus 0.1.0\nAn independent, offline Paint-style image and scene editor.\nNot affiliated with Microsoft. No telemetry, accounts, or image uploads.\n\nBuilt with Python, Qt for Python and Pillow.\nSource and third-party notices are supplied with this project.",
        )

    def closeEvent(self, event):
        if self.ai_worker and self.ai_worker.isRunning():
            self.statusBar().showMessage(
                "Wait for background removal to finish before closing.", 5000
            )
            event.ignore()
            return
        if self.confirm_discard():
            self.settings.setValue("assetsVisible", self.asset_dock.isVisible())
            self.settings.setValue("layersVisible", self.layer_dock.isVisible())
            self._closing = True
            self.settings.sync()
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GradeA PaintPlus")
    app.setOrganizationName("GradeA")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    if len(sys.argv) > 1 and Path(sys.argv[1]).is_file():
        path = sys.argv[1]
        try:
            if Path(path).suffix.lower() == ".paintplus":
                window.replace_document(Document.load(path), path)
            else:
                image = window.read_image(path)
                doc = Document(*image.size)
                doc.layers = [Layer("Background", image)]
                window.replace_document(doc)
        except Exception as e:
            window.error(str(e))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
