import pytest
from PIL import Image, ImageDraw
from paintplus.background import remove_background, model_path


def test_background_model_rejects_wrong_artifact(tmp_path):
    pytest.importorskip("onnxruntime")
    p = tmp_path / "model.onnx"
    p.write_bytes(b"wrong model")
    with pytest.raises(ValueError, match="checksum"):
        remove_background(Image.new("RGBA", (8, 8)), p)


@pytest.mark.skipif(not model_path().exists(), reason="Optional AI model not installed")
def test_real_local_cpu_inference_preserves_alpha():
    pytest.importorskip("onnxruntime")
    source = Image.new("RGBA", (160, 160), "white")
    draw = ImageDraw.Draw(source)
    draw.ellipse((40, 10, 120, 90), fill=(100, 50, 20, 255))
    draw.rectangle((50, 80, 110, 150), fill=(24, 71, 241, 255))
    source.putpixel((0, 0), (0, 0, 0, 0))
    result = remove_background(source)
    assert result.mode == "RGBA" and result.size == source.size
    assert result.getpixel((0, 0))[3] == 0
    alpha = result.getchannel("A")
    assert alpha.getextrema()[0] < alpha.getextrema()[1]
    assert result.getpixel((80, 60))[:3] == source.getpixel((80, 60))[:3]


@pytest.mark.skipif(not model_path().exists(), reason="Optional AI model not installed")
def test_example_subject_survives_and_white_background_is_removed():
    from pathlib import Path

    pytest.importorskip("onnxruntime")
    asset = Image.open(
        Path(__file__).resolve().parents[1]
        / "examples"
        / "Assets"
        / "Characters"
        / "Explorer.png"
    ).convert("RGBA")
    image = Image.new("RGBA", asset.size, "white")
    image.alpha_composite(asset)
    result = remove_background(image)
    assert result.getpixel((90, 70))[3] > 220
    assert result.getpixel((0, 0))[3] < 20
