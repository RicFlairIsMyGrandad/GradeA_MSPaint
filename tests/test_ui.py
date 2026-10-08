from PIL import Image
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from paintplus.model import Document, Layer, SPECIAL_BLUE
from paintplus.dialogs import TransformDialog, ShortcutDialog
from paintplus.app import PALETTE


def canvas_point(w, x, y):
    return QPoint(round(20 + x * w.canvas.zoom), round(20 + y * w.canvas.zoom))


def drag(w, start, end):
    QTest.mousePress(w.canvas, Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(w.canvas, end, delay=20)
    QTest.mouseRelease(w.canvas, Qt.MouseButton.LeftButton, pos=end)


def test_special_color_and_defaults(window):
    assert window.canvas.color == SPECIAL_BLUE == PALETTE[-1]
    assert window.actions["brush"].shortcut().toString() == "2"
    assert len(window.doc.layers) == 1


def test_real_pencil_mouse_stroke(window):
    window.set_tool("pencil")
    drag(window, canvas_point(window, 50, 50), canvas_point(window, 130, 80))
    assert len(window.doc.layers) == 2
    assert window.doc.flatten().getpixel((50, 50))[:3] == (24, 71, 241)
    assert window.doc.layers[-1].image.width < window.doc.width
    window.undo()
    assert len(window.doc.layers) == 1
    window.redo()
    assert len(window.doc.layers) == 2


def test_shape_drag(window):
    window.set_tool("shape")
    window.canvas.shape = "Ellipse"
    window.canvas.shape_fill = True
    drag(window, canvas_point(window, 50, 50), canvas_point(window, 150, 150))
    assert window.doc.flatten().getpixel((100, 100))[:3] == (24, 71, 241)


def test_bucket_and_eraser(window):
    window.canvas.selection = [window.doc.layers[0].id]
    window.set_tool("fill")
    QTest.mouseClick(
        window.canvas, Qt.MouseButton.LeftButton, pos=canvas_point(window, 100, 100)
    )
    assert window.doc.layers[0].image.getpixel((100, 100))[:3] == (24, 71, 241)
    window.set_tool("eraser")
    window.canvas.brush_size = 20
    drag(window, canvas_point(window, 100, 100), canvas_point(window, 110, 100))
    assert window.doc.layers[0].image.getpixel((100, 100))[3] == 0


def test_insert_multiple_and_clipboard(window, tmp_path):
    paths = []
    for name in ("Character", "Prop"):
        p = tmp_path / (name + ".png")
        image = Image.new("RGBA", (24, 20), (255, 0, 0, 100))
        image.putpixel((0, 0), (0, 0, 0, 0))
        image.save(p)
        paths.append(str(p))
    window.insert_images(paths)
    assert len(window.canvas.selection) == 2
    assert window.doc.layers[-1].image.getpixel((0, 0))[3] == 0
    window.canvas.selection = [window.doc.layers[-1].id]
    window.copy_selection()
    window.paste()
    assert window.doc.layers[-1].name == "Pasted image"
    assert window.doc.layers[-1].image.getpixel((10, 10))[3] == 100


def test_move_resize_rotate_keep_source(window):
    l = window.doc.add_image(Image.new("RGBA", (100, 80), "red"), "Object", 100, 100)
    window.canvas.selection = [l.id]
    window.canvas.refresh()
    window.set_tool("select")
    before = l.image.tobytes()
    drag(window, canvas_point(window, 150, 140), canvas_point(window, 180, 170))
    assert abs(l.x - 130) < 2 and abs(l.y - 130) < 2
    h = window.canvas.handles()["se"]
    drag(
        window,
        canvas_point(window, h.x(), h.y()),
        canvas_point(window, h.x() + 100, h.y() + 80),
    )
    assert l.width > 190 and abs(l.width / l.height - 1.25) < 0.02
    h = window.canvas.handles()["rotate"]
    center = window.canvas.bounding().center()
    drag(
        window,
        canvas_point(window, h.x(), h.y()),
        canvas_point(window, center.x() + 120, center.y()),
    )
    assert abs(l.angle) > 50 and l.image.tobytes() == before


def test_locked_background_not_movable(window):
    window.lock_background()
    original = (window.doc.layers[0].x, window.doc.layers[0].y)
    drag(window, canvas_point(window, 100, 100), canvas_point(window, 200, 200))
    assert (window.doc.layers[0].x, window.doc.layers[0].y) == original
    assert window.doc.layers[0].locked


def test_group_duplicate_and_delete(window):
    a = window.doc.add_image(Image.new("RGBA", (10, 10), "red"), "A")
    b = window.doc.add_image(Image.new("RGBA", (10, 10), "blue"), "B")
    window.canvas.selection = [a.id, b.id]
    window.group_layers()
    assert a.group == b.group and a.group
    window.duplicate_layers()
    clones = window.canvas.layers()
    assert len(clones) == 2 and clones[0].group == clones[1].group != a.group
    window.delete_layers()
    assert len(window.doc.layers) == 3
    window.undo()
    assert len(window.doc.layers) == 5


def test_asset_reference_search_favorite_and_multi(window, tmp_path):
    for name in ("hero", "tree"):
        Image.new("RGBA", (12, 12), "red").save(tmp_path / (name + ".png"))
    assets = window.assets
    assets.folders = [{"name": "Characters", "path": str(tmp_path)}]
    assets.persist()
    assets.categories()
    assert assets.list.count() == 2
    assets.search.setText("hero")
    assert assets.list.count() == 1
    assets.list.item(0).setSelected(True)
    assets.favorite()
    assert len(assets.favorites) == 1
    assets.search.clear()
    for i in range(assets.list.count()):
        assets.list.item(i).setSelected(True)
    assets.insert_selected()
    assert len(window.canvas.selection) == 2 and len(assets.recent) == 2
    mime = assets.list.mimeData(assets.list.selectedItems())
    assert len(mime.urls()) == 2
    assert len(list(tmp_path.glob("*.png"))) == 2


def test_quick_save_duplicates(window, tmp_path):
    window.output_folder = str(tmp_path)
    window.filename.setText("Scene")
    window.quick_save()
    window.quick_save()
    assert (tmp_path / "Scene.png").is_file() and (tmp_path / "Scene (2).png").is_file()
    assert Image.open(tmp_path / "Scene.png").size == (1200, 800)


def test_transform_percent_and_pixel_art(window):
    l = Layer("Object", Image.new("RGBA", (100, 50), "red"))
    d = TransformDialog(l, window)
    d.units.setCurrentIndex(1)
    d.width.setValue(25)
    assert d.height.value() == 25
    d.angle.setValue(-15)
    d.nearest.setChecked(True)
    d.apply()
    assert (l.width, l.height, l.angle, l.nearest) == (25, 12.5, -15, True)
    assert l.image.size == (100, 50)


def test_rectangular_selection_detaches_pixels(window):
    window.canvas.selection = [window.doc.layers[0].id]
    window.set_tool("region")
    drag(window, canvas_point(window, 30, 30), canvas_point(window, 130, 100))
    assert len(window.doc.layers) == 2 and window.doc.layers[-1].name == "Selection"
    assert window.doc.layers[0].image.getpixel((50, 50))[3] == 0
    assert window.doc.flatten().getpixel((50, 50)) == (255, 255, 255, 255)


def test_crop_mouse_and_undo(window):
    window.set_tool("crop")
    drag(window, canvas_point(window, 20, 20), canvas_point(window, 220, 180))
    assert abs(window.doc.width - 200) <= 2 and abs(window.doc.height - 160) <= 2
    window.undo()
    assert window.doc.width == 1200


def test_shortcuts_edit_persistence(window):
    dialog = ShortcutDialog(window.actions, window)
    dialog.editors["brush"].setKeySequence("B")
    dialog.validate()
    assert dialog.result() == dialog.DialogCode.Accepted
    dialog.editors["eraser"].setKeySequence("B")
    dialog.validate()
    assert "share" in dialog.error.text()


def test_filename_typing_does_not_select_tools(window, app):
    window.filename.setFocus()
    window.filename.clear()
    QTest.keyClicks(window.filename, "1234567890")
    assert window.filename.text() == "1234567890" and window.canvas.tool == "select"


def test_editable_text_roundtrip(window, tmp_path):
    data = {
        "content": "Hello",
        "font": "DejaVu Sans",
        "size": 26,
        "bold": True,
        "color": "#1847F1",
    }
    image = window.render_text(data)
    assert image.getbbox()
    l = window.doc.add_image(image, "Text")
    l.text = data
    p = tmp_path / "text.paintplus"
    window.doc.save(p)
    assert Document.load(p).layers[-1].text == data


def test_merge_selects_result_when_upper_layer_exists(window):
    a = window.doc.add_image(Image.new("RGBA", (10, 10), "red"), "A")
    b = window.doc.add_image(Image.new("RGBA", (10, 10), "blue"), "B")
    top = window.doc.add_image(Image.new("RGBA", (10, 10), "green"), "Top")
    window.canvas.selection = [a.id, b.id]
    window.merge_layers()
    assert window.canvas.layers()[0].name == "Merged layers"
    assert window.doc.layers[-1].id == top.id


def test_arrow_nudge_and_escape(window):
    l = window.doc.add_image(Image.new("RGBA", (10, 10), "red"), "A", 50, 50)
    window.canvas.selection = [l.id]
    window.canvas.setFocus()
    QTest.keyClick(window.canvas, Qt.Key.Key_Right)
    assert l.x == 51
    QTest.keyClick(window.canvas, Qt.Key.Key_Down, Qt.KeyboardModifier.ShiftModifier)
    assert l.y == 60
    QTest.keyClick(window.canvas, Qt.Key.Key_Escape)
    assert not window.canvas.selection


def test_closing_does_not_hide_panels_next_launch(window, app):
    from paintplus.app import MainWindow

    window.asset_dock.show()
    window.layer_dock.show()
    app.processEvents()
    window.doc.dirty = False
    window.close()
    app.processEvents()
    assert window.settings.value("assetsVisible", type=bool)
    assert window.settings.value("layersVisible", type=bool)
    other = MainWindow()
    other.show()
    app.processEvents()
    assert other.asset_dock.isVisible() and other.layer_dock.isVisible()
    other.doc.dirty = False
    other.close()
    other.deleteLater()
    app.processEvents()
