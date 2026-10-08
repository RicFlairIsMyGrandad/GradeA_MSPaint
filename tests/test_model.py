import json
import zipfile
import pytest
from PIL import Image
from paintplus.model import Document, Layer, unique_path, SPECIAL_BLUE


def test_resizing_keeps_original_pixels():
    original = Image.new("RGBA", (100, 100))
    original.putpixel((50, 50), (255, 0, 0, 255))
    l = Layer("Subject", original)
    l.width = l.height = 5
    l.rendered()
    l.width = l.height = 100
    assert l.rendered().tobytes() == original.tobytes()
    assert l.image.size == (100, 100)


def test_transparency_and_stacking():
    d = Document(4, 4)
    d.layers.append(Layer("Overlay", Image.new("RGBA", (2, 2), (255, 0, 0, 128)), 1, 1))
    result = d.flatten()
    assert result.getpixel((0, 0)) == (255, 255, 255, 255)
    assert result.getpixel((1, 1)) == (255, 127, 127, 255)
    d.layers[-1].visible = False
    assert d.flatten().getpixel((1, 1)) == (255, 255, 255, 255)


def test_project_roundtrip(tmp_path):
    d = Document(60, 40)
    l = d.add_image(Image.new("RGBA", (12, 15), (24, 71, 241, 100)), "Character", -5, 9)
    l.width = 20
    l.height = 25
    l.angle = 33.5
    l.flip_h = True
    l.locked = True
    l.group = "group1"
    l.nearest = True
    l.text = {"content": "Hi", "font": "Arial", "size": 16, "bold": False}
    before = d.flatten().tobytes()
    path = tmp_path / "scene.paintplus"
    d.save(path)
    restored = Document.load(path)
    assert restored.flatten().tobytes() == before
    other = restored.layers[-1]
    assert other.id == l.id and other.image.tobytes() == l.image.tobytes()
    assert (
        other.text == l.text
        and other.group == "group1"
        and other.angle == 33.5
        and other.locked
    )
    assert not d.dirty


def test_undo_redo_and_new_branch():
    d = Document(10, 10)
    d.add_image(Image.new("RGBA", (2, 2)), "One")
    assert d.undo() and len(d.layers) == 1
    assert d.redo() and len(d.layers) == 2
    d.undo()
    d.add_image(Image.new("RGBA", (3, 3)), "Two")
    assert not d.redo()


def test_crop_is_reversible():
    d = Document(40, 40)
    d.add_image(Image.new("RGBA", (5, 5), "red"), "Thing", 12, 15)
    old = d.flatten().crop((10, 10, 30, 30)).tobytes()
    d.crop((10, 10, 30, 30))
    assert d.flatten().tobytes() == old and d.layers[-1].x == 2
    d.undo()
    assert (d.width, d.height) == (40, 40)


@pytest.mark.parametrize("extension", [".png", ".jpg", ".bmp", ".tiff", ".webp"])
def test_export_formats(tmp_path, extension):
    d = Document(16, 16)
    d.layers[0].visible = False
    d.add_image(Image.new("RGBA", (8, 8), SPECIAL_BLUE), "Blue", 0, 0)
    path = tmp_path / ("image" + extension)
    d.export(path)
    with Image.open(path) as result:
        assert result.size == (16, 16)
        if extension in (".jpg", ".bmp"):
            assert all(v >= 250 for v in result.convert("RGB").getpixel((15, 15)))
        if extension in (".png", ".tiff", ".webp"):
            assert result.convert("RGBA").getpixel((15, 15))[3] == 0


def test_merge_preserves_render_and_undo():
    d = Document(20, 20)
    a = d.add_image(Image.new("RGBA", (8, 8), "red"), "A", 2, 2)
    b = d.add_image(Image.new("RGBA", (8, 8), (0, 0, 255, 120)), "B", 6, 6)
    old = d.flatten().tobytes()
    d.merge([a.id, b.id])
    assert d.flatten().tobytes() == old
    assert len(d.layers) == 2
    d.undo()
    assert len(d.layers) == 3


def test_flip_and_rotation():
    image = Image.new("RGBA", (6, 4))
    image.putpixel((0, 0), (255, 0, 0, 255))
    l = Layer("Test", image)
    l.flip_h = True
    assert l.rendered().getpixel((5, 0)) == (255, 0, 0, 255)
    l.angle = 90
    assert l.rendered().size == (4, 6)
    assert l.image.getpixel((0, 0)) == (255, 0, 0, 255)


@pytest.mark.parametrize(
    "name", ["", "../oops", "a/b", "a\\b", "NUL", "con.txt", "image?", "COM1"]
)
def test_invalid_windows_filename(tmp_path, name):
    with pytest.raises(ValueError):
        unique_path(tmp_path, name, ".png")


def test_duplicate_names_never_overwrite(tmp_path):
    p = unique_path(tmp_path, "Scene", ".png")
    p.write_text("keep")
    assert unique_path(tmp_path, "Scene", ".png").name == "Scene (2).png"
    (tmp_path / "Scene (2).png").touch()
    assert unique_path(tmp_path, "Scene", ".png").name == "Scene (3).png"
    assert p.read_text() == "keep"


def test_invalid_project_version(tmp_path):
    p = tmp_path / "bad.paintplus"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("document.json", json.dumps({"version": 99}))
    with pytest.raises(ValueError, match="version"):
        Document.load(p)


def test_invalid_canvas_size(tmp_path):
    p = tmp_path / "bad.paintplus"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr(
            "document.json",
            json.dumps({"version": 1, "width": -10, "height": 20, "layers": []}),
        )
    with pytest.raises(ValueError, match="canvas"):
        Document.load(p)


def test_filename_extension_not_duplicated(tmp_path):
    assert unique_path(tmp_path, "Scene.png", ".png").name == "Scene.png"
