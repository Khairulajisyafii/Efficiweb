import re
import colorsys
from typing import Dict, Tuple, Optional

class ColorConverter:
    """Utility helper untuk validasi dan konversi warna HEX, RGBA, dan HSL."""

    @staticmethod
    def parse_hex(hex_str: str) -> Optional[Tuple[int, int, int, float]]:
        h = hex_str.strip().lstrip('#')
        if len(h) == 3: 
            h = "".join(c*2 for c in h)
        try:
            if len(h) == 6: 
                return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0
            if len(h) == 8: 
                return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), round(int(h[6:8], 16)/255, 2)
        except ValueError: 
            pass
        return None

    @staticmethod
    def parse_rgba(rgba_str: str) -> Optional[Tuple[int, int, int, float]]:
        m = re.match(r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d\.]+)\s*)?\)", rgba_str.strip().lower())
        if m:
            try:
                r, g, b = map(int, m.groups()[:3])
                a = float(m.group(4)) if m.group(4) else 1.0
                if all(0 <= x <= 255 for x in (r, g, b)) and 0.0 <= a <= 1.0: 
                    return r, g, b, round(a, 2)
            except ValueError: 
                pass
        else:
            p = [x.strip() for x in rgba_str.split(',')]
            if len(p) in (3, 4):
                try:
                    r, g, b = map(int, p[:3])
                    a = float(p[3]) if len(p) == 4 else 1.0
                    if all(0 <= x <= 255 for x in (r, g, b)) and 0.0 <= a <= 1.0: 
                        return r, g, b, round(a, 2)
                except ValueError: 
                    pass
        return None

    @staticmethod
    def parse_hsl(hsl_str: str) -> Optional[Tuple[int, int, int, float]]:
        s_clean = hsl_str.strip().lower()
        m = re.match(r"hsla?\s*\(\s*(\d+)\s*,\s*([\d\.]+)%?\s*,\s*([\d\.]+)%?\s*(?:,\s*([\d\.]+)\s*)?\)", s_clean)
        if m:
            try:
                h = int(m.group(1))
                s, l = map(float, m.groups()[1:3])
                a = float(m.group(4)) if m.group(4) else 1.0
                if 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100 and 0.0 <= a <= 1.0:
                    r, g, b = ColorConverter.hsl_to_rgb_values(h, s, l)
                    return r, g, b, round(a, 2)
            except ValueError: 
                pass
        else:
            p = [x.strip().replace('%', '') for x in s_clean.split(',')]
            if len(p) in (3, 4):
                try:
                    h, s, l = int(p[0]), float(p[1]), float(p[2])
                    a = float(p[3]) if len(p) == 4 else 1.0
                    if 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100 and 0.0 <= a <= 1.0:
                        r, g, b = ColorConverter.hsl_to_rgb_values(h, s, l)
                        return r, g, b, round(a, 2)
                except ValueError: 
                    pass
        return None

    @staticmethod
    def hsl_to_rgb_values(h: int, s: float, l: float) -> Tuple[int, int, int]:
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
        return int(r * 255), int(g * 255), int(b * 255)

    @staticmethod
    def rgb_to_hsl_values(r: int, g: int, b: int) -> Tuple[int, int, int]:
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        return int(h * 360), int(s * 100), int(l * 100)

    @classmethod
    def convert_any_to_all(cls, val: str, fmt: str) -> Optional[Dict[str, str]]:
        rgb_data = cls.parse_hex(val) if fmt == "HEX" else cls.parse_rgba(val) if fmt == "RGBA" else cls.parse_hsl(val)
        if not rgb_data: 
            return None
        r, g, b, a = rgb_data
        h, s, l = cls.rgb_to_hsl_values(r, g, b)
        return {
            "hex": f"#{r:02X}{g:02X}{b:02X}",
            "rgba": f"rgba({r}, {g}, {b}, {a})" if a != 1.0 else f"rgb({r}, {g}, {b})",
            "hsl": f"hsla({h}, {s}%, {l}%, {a})" if a != 1.0 else f"hsl({h}, {s}%, {l}%)",
            "raw_rgb": (r, g, b, a)
        }