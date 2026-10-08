"""Original sample art, drawn from primitives. No external artwork or downloads."""

import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from paintplus.model import Document, Layer

OUT = ROOT / "examples" / "Assets"
S = 3


def asset(name, folder, size, draw_fn):
    image = Image.new("RGBA", (size[0] * S, size[1] * S))
    draw = ImageDraw.Draw(image)

    class Scaled:
        def __getattr__(self, key):
            fn = getattr(draw, key)

            def call(points, *args, **kwargs):
                def scale(value):
                    if isinstance(value, (tuple, list)):
                        return tuple(scale(v) for v in value)
                    return value * S

                if "width" in kwargs:
                    kwargs["width"] *= S
                if "radius" in kwargs:
                    kwargs["radius"] *= S
                return fn(scale(points), *args, **kwargs)

            return call

    draw_fn(Scaled())
    image = image.resize(size, Image.Resampling.LANCZOS)
    path = OUT / folder / (name + ".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return image


def hero(d):
    edge = "#253547"
    d.polygon(
        [(52, 100), (26, 233), (111, 214), (149, 126)],
        fill="#d24f45",
        outline=edge,
        width=3,
    )
    d.rounded_rectangle(
        (64, 205, 85, 281), radius=9, fill="#385e87", outline=edge, width=3
    )
    d.rounded_rectangle(
        (100, 205, 124, 281), radius=9, fill="#385e87", outline=edge, width=3
    )
    d.rounded_rectangle(
        (54, 271, 89, 291), radius=7, fill="#5e392c", outline=edge, width=3
    )
    d.rounded_rectangle(
        (99, 271, 139, 291), radius=7, fill="#5e392c", outline=edge, width=3
    )
    d.rounded_rectangle(
        (48, 108, 138, 216), radius=21, fill="#3987ba", outline=edge, width=3
    )
    d.line([(61, 115), (49, 166), (39, 204)], fill="#edbe91", width=22)
    d.line([(128, 118), (143, 166), (146, 197)], fill="#edbe91", width=22)
    d.ellipse((52, 23, 139, 111), fill="#f1c69a", outline=edge, width=3)
    d.polygon(
        [
            (45, 65),
            (44, 37),
            (62, 41),
            (60, 14),
            (79, 28),
            (92, 6),
            (100, 26),
            (131, 12),
            (124, 33),
            (145, 31),
            (143, 69),
            (126, 52),
            (115, 42),
            (87, 57),
            (65, 54),
        ],
        fill="#724633",
        outline=edge,
        width=3,
    )
    d.ellipse((73, 65, 82, 77), fill=edge)
    d.ellipse((111, 65, 120, 77), fill=edge)
    d.arc((83, 73, 111, 96), 0, 180, fill="#875647", width=2)
    d.polygon(
        [(50, 105), (94, 127), (138, 102), (126, 133), (96, 145), (60, 126)],
        fill="#efb947",
        outline=edge,
        width=2,
    )
    d.rectangle((49, 177, 138, 189), fill="#734b37", outline=edge, width=2)
    d.rectangle((88, 174, 102, 192), fill="#e8c463", outline=edge, width=2)


def fox(d):
    edge = "#6c432c"
    d.polygon(
        [(125, 111), (167, 95), (178, 50), (153, 35), (149, 75), (109, 84)],
        fill="#ed9642",
        outline=edge,
        width=3,
    )
    d.polygon([(160, 72), (178, 50), (153, 35), (149, 59)], fill="#fff1dc")
    d.ellipse((40, 66, 139, 139), fill="#ed9642", outline=edge, width=3)
    d.polygon(
        [(36, 57), (28, 7), (64, 35), (106, 34), (140, 6), (133, 67)],
        fill="#ed9642",
        outline=edge,
        width=3,
    )
    d.polygon([(36, 19), (43, 45), (57, 38)], fill="#de8284")
    d.polygon([(130, 19), (119, 39), (132, 47)], fill="#de8284")
    d.ellipse((28, 34, 141, 104), fill="#ed9642", outline=edge, width=3)
    d.polygon(
        [(33, 64), (77, 75), (137, 64), (125, 92), (85, 108), (43, 91)], fill="#fff1dc"
    )
    d.ellipse((51, 56, 61, 68), fill=edge)
    d.ellipse((108, 56, 118, 68), fill=edge)
    d.polygon([(78, 76), (93, 76), (85, 84)], fill=edge)
    d.ellipse((65, 101, 109, 137), fill="#fff1dc")
    d.ellipse((45, 125, 80, 147), fill="#ed9642", outline=edge, width=2)
    d.ellipse((105, 125, 140, 147), fill="#ed9642", outline=edge, width=2)


def tree(d):
    d.polygon(
        [(65, 204), (75, 88), (91, 80), (100, 204)],
        fill="#8c6044",
        outline="#574631",
        width=3,
    )
    for box, color in [
        ((5, 37, 98, 131), "#467a4b"),
        ((55, 24, 146, 125), "#4e8b51"),
        ((23, 0, 124, 99), "#679d56"),
        ((34, 38, 127, 136), "#679d56"),
    ]:
        d.ellipse(box, fill=color, outline="#395d3c", width=2)
    d.ellipse((51, 16, 103, 59), fill="#86b46b")


def chest(d):
    d.rounded_rectangle(
        (12, 25, 136, 95), radius=12, fill="#b77d3e", outline="#67452e", width=4
    )
    d.rounded_rectangle(
        (12, 5, 136, 58), radius=16, fill="#ce9952", outline="#67452e", width=4
    )
    d.rectangle((33, 8, 44, 93), fill="#e5c765", outline="#67452e", width=2)
    d.rectangle((104, 8, 115, 93), fill="#e5c765", outline="#67452e", width=2)
    d.rectangle((12, 47, 136, 57), fill="#e5c765", outline="#67452e", width=2)
    d.rounded_rectangle(
        (64, 42, 84, 70), radius=3, fill="#e5c765", outline="#67452e", width=2
    )
    d.ellipse((71, 50, 78, 58), fill="#67452e")


def cloud(d):
    for box in [
        (4, 32, 76, 84),
        (32, 8, 100, 79),
        (66, 23, 126, 84),
        (91, 40, 151, 83),
    ]:
        d.ellipse(box, fill="#fffdf6", outline="#c5dcec", width=2)
    d.rectangle((24, 54, 130, 81), fill="#fffdf6")


def rock(d):
    d.polygon(
        [(4, 65), (24, 20), (65, 5), (111, 28), (128, 67), (107, 93), (26, 92)],
        fill="#87939d",
        outline="#546373",
        width=3,
    )
    d.polygon([(24, 20), (65, 5), (83, 51), (4, 65)], fill="#b6c1c8")
    d.polygon([(83, 51), (111, 28), (128, 67), (107, 93)], fill="#697683")


def meadow(d):
    d.rectangle((0, 0, 1200, 800), fill="#a9d6e7")
    d.ellipse((936, 49, 1033, 146), fill="#ffdf9a")
    d.polygon(
        [
            (0, 360),
            (183, 157),
            (346, 347),
            (519, 112),
            (750, 350),
            (909, 189),
            (1200, 369),
            (1200, 800),
            (0, 800),
        ],
        fill="#7ea8b0",
    )
    d.polygon(
        [(96, 250), (183, 157), (267, 260), (189, 231), (170, 238)], fill="#d7e7e5"
    )
    d.polygon(
        [(411, 239), (519, 112), (643, 258), (524, 213), (491, 227)], fill="#d7e7e5"
    )
    d.polygon(
        [
            (0, 404),
            (190, 348),
            (397, 406),
            (642, 320),
            (847, 408),
            (1030, 340),
            (1200, 407),
            (1200, 800),
            (0, 800),
        ],
        fill="#65967f",
    )
    d.polygon(
        [
            (0, 551),
            (194, 458),
            (367, 515),
            (578, 429),
            (790, 494),
            (992, 437),
            (1200, 491),
            (1200, 800),
            (0, 800),
        ],
        fill="#78a263",
    )
    d.polygon(
        [
            (744, 462),
            (849, 442),
            (844, 491),
            (980, 517),
            (786, 568),
            (788, 617),
            (558, 685),
            (596, 800),
            (235, 800),
            (507, 634),
            (674, 568),
            (839, 534),
            (746, 507),
        ],
        fill="#75c0d2",
    )
    d.polygon(
        [
            (0, 648),
            (214, 565),
            (403, 587),
            (498, 659),
            (437, 744),
            (373, 800),
            (0, 800),
        ],
        fill="#9db46d",
    )
    d.polygon(
        [(781, 658), (958, 590), (1200, 594), (1200, 800), (638, 800)], fill="#9db46d"
    )
    random.seed(17)
    for _ in range(100):
        x = random.randint(15, 1190)
        y = random.randint(650, 795)
        if 435 < x < 785:
            continue
        d.line([(x, y), (x - 3, y - 12)], fill="#638e54", width=2)
        d.ellipse(
            (x - 6, y - 18, x + 2, y - 10),
            fill=random.choice(["#fff2b8", "#f0cd7f", "#e5998b"]),
        )


if __name__ == "__main__":
    background = asset("Meadow", "Backgrounds", (1200, 800), meadow)
    character = asset("Explorer", "Characters", (190, 300), hero)
    cat = asset("Fox", "Characters", (190, 160), fox)
    oak = asset("Oak", "Props", (150, 210), tree)
    treasure = asset("Treasure", "Props", (150, 105), chest)
    sky = asset("Cloud", "Effects", (160, 90), cloud)
    stone = asset("Rock", "Props", (140, 100), rock)
    doc = Document()
    doc.layers = [Layer("Background", background, locked=True)]
    doc.layers.extend(
        [
            Layer("Cloud", sky, 210, 80),
            Layer("Oak", oak, 74, 379, width=210, height=294),
            Layer("Rock", stone, 970, 697),
            Layer("Treasure", treasure, 900, 580),
            Layer("Explorer", character, 335, 398),
            Layer("Fox", cat, 771, 638, angle=8),
        ]
    )
    doc.save(ROOT / "examples" / "Woodland.paintplus")
