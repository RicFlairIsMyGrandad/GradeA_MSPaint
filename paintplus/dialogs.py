from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QDialogButtonBox,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QKeySequenceEdit,
    QSpinBox,
    QLineEdit,
    QFontComboBox,
)


class TransformDialog(QDialog):
    def __init__(self, layer, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resize & Rotate")
        self.setMinimumWidth(360)
        self.layer = layer
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.units = QComboBox()
        self.units.addItems(["Pixels", "Percent"])
        form.addRow("Units:", self.units)
        self.width = QDoubleSpinBox()
        self.height = QDoubleSpinBox()
        for spin, value in ((self.width, layer.width), (self.height, layer.height)):
            spin.setRange(1, 16000)
            spin.setValue(value)
            spin.setDecimals(1)
        form.addRow("Width:", self.width)
        form.addRow("Height:", self.height)
        self.lock = QCheckBox("Maintain aspect ratio")
        self.lock.setChecked(True)
        form.addRow(self.lock)
        self.angle = QDoubleSpinBox()
        self.angle.setRange(-3600, 3600)
        self.angle.setValue(layer.angle)
        self.angle.setSuffix(" °")
        form.addRow("Rotate:", self.angle)
        row = QHBoxLayout()
        layout.addLayout(row)
        for text, delta in (("↶ 90°", -90), ("↷ 90°", 90), ("180°", 180)):
            button = QPushButton(text)
            button.clicked.connect(
                lambda checked=False, n=delta: self.angle.setValue(
                    self.angle.value() + n
                )
            )
            row.addWidget(button)
        self.h = QCheckBox("Flip horizontal")
        self.h.setChecked(layer.flip_h)
        self.v = QCheckBox("Flip vertical")
        self.v.setChecked(layer.flip_v)
        layout.addWidget(self.h)
        layout.addWidget(self.v)
        self.nearest = QCheckBox("Nearest neighbour (pixel art)")
        self.nearest.setChecked(layer.nearest)
        layout.addWidget(self.nearest)
        layout.addWidget(
            QLabel(
                "Original pixels are retained. Export uses Lanczos resizing\nand bicubic rotation unless pixel-art mode is enabled."
            )
        )
        self.width.valueChanged.connect(lambda: self.sync(True))
        self.height.valueChanged.connect(lambda: self.sync(False))
        self.units.currentIndexChanged.connect(self.change_units)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def sync(self, from_width):
        if not self.lock.isChecked():
            return
        other = self.height if from_width else self.width
        other.blockSignals(True)
        ratio = (
            1
            if self.units.currentIndex() == 1
            else self.layer.height / self.layer.width
        )
        other.setValue(
            self.width.value() * ratio if from_width else self.height.value() / ratio
        )
        other.blockSignals(False)

    def change_units(self):
        for s, value in (
            (self.width, 100 if self.units.currentIndex() else self.layer.width),
            (self.height, 100 if self.units.currentIndex() else self.layer.height),
        ):
            s.blockSignals(True)
            s.setValue(value)
            s.blockSignals(False)

    def apply(self):
        l = self.layer
        percent = self.units.currentIndex() == 1
        l.width = self.width.value() * l.width / 100 if percent else self.width.value()
        l.height = (
            self.height.value() * l.height / 100 if percent else self.height.value()
        )
        l.angle = self.angle.value()
        l.flip_h = self.h.isChecked()
        l.flip_v = self.v.isChecked()
        l.nearest = self.nearest.isChecked()


class ShortcutDialog(QDialog):
    def __init__(self, actions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard shortcuts")
        self.resize(510, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Click a shortcut and press your preferred key combination.\nNumber keys 0–9 can select tools. Clear a field to unassign it."
            )
        )
        self.table = QTableWidget(len(actions), 2)
        self.table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.editors = {}
        for row, (name, action) in enumerate(actions.items()):
            item = QTableWidgetItem(action.text())
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, item)
            edit = QKeySequenceEdit(action.shortcut())
            edit.setMaximumSequenceLength(1)
            self.table.setCellWidget(row, 1, edit)
            self.editors[name] = edit
        layout.addWidget(self.table)
        self.error = QLabel()
        self.error.setStyleSheet("color:#b42318")
        layout.addWidget(self.error)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)

    def validate(self):
        keys = [
            e.keySequence().toString()
            for e in self.editors.values()
            if not e.keySequence().isEmpty()
        ]
        if len(keys) != len(set(keys)):
            self.error.setText(
                "Two actions share a shortcut. Please choose different keys."
            )
            return
        self.accept()


class TextDialog(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Text")
        layout = QFormLayout(self)
        data = data or {}
        self.text = QLineEdit(data.get("content", ""))
        self.font = QFontComboBox()
        self.font.setCurrentText(data.get("font", "Segoe UI"))
        self.size = QSpinBox()
        self.size.setRange(6, 300)
        self.size.setValue(data.get("size", 28))
        self.bold = QCheckBox("Bold")
        self.bold.setChecked(data.get("bold", False))
        layout.addRow("Text:", self.text)
        layout.addRow("Font:", self.font)
        layout.addRow("Size:", self.size)
        layout.addRow(self.bold)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def data(self):
        return {
            "content": self.text.text(),
            "font": self.font.currentText(),
            "size": self.size.value(),
            "bold": self.bold.isChecked(),
        }
