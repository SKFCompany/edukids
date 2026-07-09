"""
Векторные "живые" персонажи (аватары и питомцы), нарисованные примитивами
Kivy (Ellipse/Triangle/Line) - а не шрифтовыми иконками или PNG.

Почему так: юникод-эмодзи не рендерятся на Android (нет нужного шрифта),
а PNG-ассеты требуют возни с путями/кэшем (та же проблема, что была в FlowDo).
Векторная отрисовка через kivy.graphics не зависит ни от шрифтов, ни от
файловой системы - гарантированно рисуется одинаково везде.

Каждый вид (species) описан таблицей SPECIES: основной/дополнительный
цвет и набор "черт" (уши/клюв/рог/антенны и т.д.), плюс несколько видов
с уникальной отрисовкой (панда, пчела, рыбка, дракон), которые не
укладываются в общий шаблон.
"""

from kivy.uix.widget import Widget
from kivy.properties import StringProperty, NumericProperty
from kivy.graphics import Color, Ellipse, Triangle, Line, PushMatrix, PopMatrix, Rotate, Scale, Translate

BLACK = (0.15, 0.15, 0.18, 1)
WHITE = (1, 1, 1, 1)
PINK = (0.95, 0.55, 0.6, 1)

# primary / secondary (тело / живот-пятна), ear_style, snout_style
SPECIES = {
    "cat":            {"primary": (0.92, 0.58, 0.25, 1), "secondary": (1, 0.93, 0.85, 1), "ear": "triangle", "snout": "nose"},
    "dog":            {"primary": (0.72, 0.52, 0.32, 1), "secondary": (0.94, 0.86, 0.72, 1), "ear": "floppy", "snout": "nose"},
    "owl":            {"primary": (0.55, 0.4, 0.3, 1), "secondary": (0.88, 0.78, 0.6, 1), "ear": "tuft", "snout": "beak_small", "eye_scale": 1.35},
    "koala":          {"primary": (0.62, 0.62, 0.65, 1), "secondary": (0.85, 0.85, 0.87, 1), "ear": "round_big", "snout": "round_nose"},
    "panda":          {"primary": (1, 1, 1, 1), "secondary": (0.1, 0.1, 0.12, 1), "ear": "round_small_dark", "snout": "round_nose", "special": "panda"},
    "rabbit":         {"primary": (0.97, 0.93, 0.95, 1), "secondary": (0.95, 0.7, 0.78, 1), "ear": "long", "snout": "round_nose_pink"},
    "robot-happy":    {"primary": (0.55, 0.68, 0.82, 1), "secondary": (0.8, 0.88, 0.95, 1), "ear": "antenna", "snout": "none", "special": "robot"},
    "unicorn-variant": {"primary": (0.98, 0.97, 0.99, 1), "secondary": (1, 1, 1, 1), "ear": "triangle_small", "snout": "round_nose", "special": "unicorn"},
    "alien":          {"primary": (0.55, 0.85, 0.55, 1), "secondary": (0.75, 0.95, 0.7, 1), "ear": "antenna_ball", "snout": "none", "eye_scale": 1.5},
    "sword-cross":    {"primary": (0.55, 0.78, 0.5, 1), "secondary": (0.75, 0.9, 0.65, 1), "ear": "horn_small", "snout": "snout_long", "special": "dragon"},
    "duck":           {"primary": (0.98, 0.82, 0.25, 1), "secondary": (0.93, 0.6, 0.18, 1), "ear": "none", "snout": "beak_wide"},
    "fish":           {"primary": (0.4, 0.65, 0.92, 1), "secondary": (0.95, 0.65, 0.3, 1), "ear": "none", "snout": "none", "special": "fish"},
    "bee":            {"primary": (1, 0.85, 0.2, 1), "secondary": (0.15, 0.15, 0.18, 1), "ear": "antenna_thin", "snout": "none", "special": "bee"},
}

DEFAULT_SPECIES = {"primary": (0.6, 0.6, 0.9, 1), "secondary": (0.85, 0.85, 0.95, 1), "ear": "none", "snout": "round_nose"}


class CreatureWidget(Widget):
    species = StringProperty("cat")
    rotation = NumericProperty(0)
    scale_factor = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, species=self._redraw,
                  rotation=self._redraw, scale_factor=self._redraw)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        cfg = SPECIES.get(self.species, DEFAULT_SPECIES)
        x, y = self.pos
        w, h = self.size
        if w <= 0 or h <= 0:
            return
        cx, cy = x + w / 2, y + h / 2

        def rel(fx, fy):
            return (x + fx * w, y + fy * h)

        def rw(f):
            return f * w

        def rh(f):
            return f * h

        with self.canvas:
            PushMatrix()
            Rotate(angle=self.rotation, origin=(cx, cy))
            Scale(self.scale_factor, self.scale_factor, 1, origin=(cx, cy))

            self._draw_ears(cfg, rel, rw, rh)
            # Тело.
            Color(*cfg["primary"])
            Ellipse(pos=rel(0.10, 0.06), size=(rw(0.80), rh(0.78)))
            # Живот/пятно светлее по центру снизу.
            Color(*cfg["secondary"])
            Ellipse(pos=rel(0.28, 0.10), size=(rw(0.44), rh(0.40)))

            special = cfg.get("special")
            if special == "panda":
                self._panda_patches(rel, rw, rh)
            elif special == "bee":
                self._bee_stripes(cfg, rel, rw, rh)
            elif special == "fish":
                self._fish_extras(cfg, rel, rw, rh)
            elif special == "dragon":
                self._dragon_spikes(cfg, rel, rw, rh)
            elif special == "unicorn":
                self._unicorn_horn(rel, rw, rh)
            elif special == "robot":
                self._robot_face_plate(rel, rw, rh)

            self._draw_snout(cfg, rel, rw, rh)
            self._draw_eyes(cfg, rel, rw, rh)

            PopMatrix()

    # ---------- уши / антенны / рог ----------
    def _draw_ears(self, cfg, rel, rw, rh):
        style = cfg.get("ear", "none")
        color = cfg["primary"]
        if style == "triangle":
            Color(*color)
            Triangle(points=[*rel(0.14, 0.62), *rel(0.30, 0.62), *rel(0.16, 0.98)])
            Triangle(points=[*rel(0.86, 0.62), *rel(0.70, 0.62), *rel(0.84, 0.98)])
        elif style == "triangle_small":
            Color(*color)
            Triangle(points=[*rel(0.20, 0.66), *rel(0.32, 0.66), *rel(0.22, 0.94)])
            Triangle(points=[*rel(0.80, 0.66), *rel(0.68, 0.66), *rel(0.78, 0.94)])
        elif style == "floppy":
            Color(*color)
            Ellipse(pos=rel(0.02, 0.30), size=(rw(0.22), rh(0.38)))
            Ellipse(pos=rel(0.76, 0.30), size=(rw(0.22), rh(0.38)))
        elif style == "tuft":
            Color(*color)
            Triangle(points=[*rel(0.22, 0.72), *rel(0.32, 0.72), *rel(0.24, 0.92)])
            Triangle(points=[*rel(0.78, 0.72), *rel(0.68, 0.72), *rel(0.76, 0.92)])
        elif style == "round_big":
            Color(*color)
            Ellipse(pos=rel(0.00, 0.55), size=(rw(0.30), rh(0.42)))
            Ellipse(pos=rel(0.70, 0.55), size=(rw(0.30), rh(0.42)))
        elif style == "round_small_dark":
            Color(*(0.1, 0.1, 0.12, 1))
            Ellipse(pos=rel(0.06, 0.66), size=(rw(0.24), rh(0.30)))
            Ellipse(pos=rel(0.70, 0.66), size=(rw(0.24), rh(0.30)))
        elif style == "long":
            Color(*color)
            Ellipse(pos=rel(0.20, 0.78), size=(rw(0.16), rh(0.38)))
            Ellipse(pos=rel(0.64, 0.78), size=(rw(0.16), rh(0.38)))
            Color(*cfg["secondary"])
            Ellipse(pos=rel(0.235, 0.82), size=(rw(0.09), rh(0.26)))
            Ellipse(pos=rel(0.675, 0.82), size=(rw(0.09), rh(0.26)))
        elif style in ("antenna", "antenna_ball", "antenna_thin"):
            Color(*(0.35, 0.35, 0.4, 1))
            Line(points=[*rel(0.5, 0.80), *rel(0.5, 0.98)], width=rw(0.012))
            Color(*(0.9, 0.3, 0.3, 1) if style != "antenna_thin" else (0.15, 0.15, 0.18, 1))
            Ellipse(pos=rel(0.46, 0.94), size=(rw(0.08), rw(0.08)))
        elif style == "horn_small":
            Color(*(0.85, 0.4, 0.3, 1))
            Triangle(points=[*rel(0.30, 0.74), *rel(0.40, 0.74), *rel(0.33, 0.92)])
            Triangle(points=[*rel(0.70, 0.74), *rel(0.60, 0.74), *rel(0.67, 0.92)])

    def _unicorn_horn(self, rel, rw, rh):
        Color(1, 0.85, 0.4, 1)
        Triangle(points=[*rel(0.44, 0.80), *rel(0.56, 0.80), *rel(0.5, 1.05)])

    def _robot_face_plate(self, rel, rw, rh):
        Color(0.85, 0.9, 0.96, 1)
        Ellipse(pos=rel(0.22, 0.28), size=(rw(0.56), rh(0.46)))

    def _panda_patches(self, rel, rw, rh):
        Color(0.1, 0.1, 0.12, 1)
        Ellipse(pos=rel(0.20, 0.48), size=(rw(0.20), rh(0.24)))
        Ellipse(pos=rel(0.60, 0.48), size=(rw(0.20), rh(0.24)))

    def _bee_stripes(self, cfg, rel, rw, rh):
        Color(*cfg["secondary"])
        Ellipse(pos=rel(0.14, 0.30), size=(rw(0.16), rh(0.5)))
        Ellipse(pos=rel(0.42, 0.24), size=(rw(0.16), rh(0.58)))
        Ellipse(pos=rel(0.70, 0.30), size=(rw(0.16), rh(0.5)))
        # Крылышки.
        Color(0.9, 0.95, 1, 0.55)
        Ellipse(pos=rel(0.02, 0.60), size=(rw(0.30), rh(0.30)))
        Ellipse(pos=rel(0.68, 0.60), size=(rw(0.30), rh(0.30)))

    def _fish_extras(self, cfg, rel, rw, rh):
        Color(*cfg["secondary"])
        Triangle(points=[*rel(0.0, 0.30), *rel(0.16, 0.45), *rel(0.0, 0.65)])
        Triangle(points=[*rel(0.40, 0.80), *rel(0.55, 0.98), *rel(0.62, 0.78)])

    def _dragon_spikes(self, cfg, rel, rw, rh):
        Color(*cfg["secondary"])
        for fx in (0.30, 0.44, 0.58):
            Triangle(points=[*rel(fx, 0.68), *rel(fx + 0.08, 0.68), *rel(fx + 0.04, 0.86)])

    # ---------- морда/клюв/нос ----------
    def _draw_snout(self, cfg, rel, rw, rh):
        style = cfg.get("snout", "none")
        if style == "nose":
            Color(*PINK)
            Ellipse(pos=rel(0.45, 0.38), size=(rw(0.10), rh(0.08)))
        elif style == "round_nose":
            Color(*BLACK)
            Ellipse(pos=rel(0.44, 0.36), size=(rw(0.12), rh(0.10)))
        elif style == "round_nose_pink":
            Color(*PINK)
            Ellipse(pos=rel(0.44, 0.36), size=(rw(0.12), rh(0.10)))
        elif style == "beak_wide":
            Color(0.93, 0.55, 0.15, 1)
            Triangle(points=[*rel(0.62, 0.42), *rel(0.98, 0.46), *rel(0.62, 0.30)])
        elif style == "beak_small":
            Color(0.85, 0.5, 0.15, 1)
            Triangle(points=[*rel(0.44, 0.38), *rel(0.56, 0.38), *rel(0.5, 0.28)])
        elif style == "snout_long":
            Color(*cfg["secondary"])
            Ellipse(pos=rel(0.36, 0.28), size=(rw(0.28), rh(0.20)))

    # ---------- глаза ----------
    def _draw_eyes(self, cfg, rel, rw, rh):
        scale = cfg.get("eye_scale", 1.0)
        er = 0.11 * scale
        for cx in (0.35, 0.65):
            Color(*WHITE)
            Ellipse(pos=rel(cx - er, 0.56), size=(rw(er * 2), rh(er * 2)))
            Color(*BLACK)
            Ellipse(pos=rel(cx - er * 0.45, 0.56 + er * 0.55), size=(rw(er * 0.9), rh(er * 0.9)))


def creature_species_for(icon_or_item_id: str) -> str:
    """Совместимость со старыми данными: если пришёл icon-ключ (cat, duck, ...),
    просто возвращаем его - таблица SPECIES построена именно по этим ключам."""
    return icon_or_item_id if icon_or_item_id in SPECIES else "cat"
