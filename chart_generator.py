# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

# -*- coding: utf-8 -*-
"""
chart_generator.py — نسخه‌ی نهایی (باگ badge میانگین رفع شد)
۳ نمودار: میله سه‌بعدی | ناحیه‌ای | حبابی
"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _RESH = True
except ImportError:
    _RESH = False


S = 2.5  # supersample factor

def _s(v): return int(v * S)


# ═══════════ Fonts ═══════════
def _fonts_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        p = os.path.join(sys._MEIPASS, "fonts")
        if os.path.isdir(p): return p
    return os.path.join(os.getcwd(), "fonts")

_fcache = {}
def _font(name, size):
    real = _s(size)
    k = (name, real)
    if k in _fcache: return _fcache[k]
    for p in [os.path.join(_fonts_dir(), name),
              os.path.join(_fonts_dir(), "Vazirmatn-Regular.ttf"),
              "arial.ttf", "tahoma.ttf"]:
        try:
            if os.path.exists(p) or p in ("arial.ttf", "tahoma.ttf"):
                _fcache[k] = ImageFont.truetype(p, real)
                return _fcache[k]
        except Exception: pass
    _fcache[k] = ImageFont.load_default()
    return _fcache[k]

def _fa(t):
    s = str(t or "")
    if not _RESH: return s
    try: return get_display(arabic_reshaper.reshape(s))
    except Exception: return s

def _fanum(v, d=0):
    try:
        s = f"{int(round(v)):,}" if d == 0 else f"{v:,.{d}f}"
    except Exception: s = str(v)
    return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

def _rgb(c):
    if isinstance(c, (tuple, list)): return tuple(int(x) for x in c[:3])
    s = str(c).lstrip("#")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)

def _mix(c1, c2, t):
    a, b = _rgb(c1), _rgb(c2)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def _shade(rgb, f):
    rgb = _rgb(rgb)
    if f >= 0: return tuple(int(c + (255 - c) * f) for c in rgb)
    return tuple(int(c * (1 + f)) for c in rgb)


BILL_THEMES = {
    "آب":  {"base": "#0EA5E9", "light": "#7DD3FC", "dark": "#0369A1"},
    "برق": {"base": "#F59E0B", "light": "#FCD34D", "dark": "#B45309"},
    "گاز": {"base": "#EF4444", "light": "#FCA5A5", "dark": "#991B1B"},
}


def _new_canvas(W, H, is_dark):
    WS, HS = _s(W), _s(H)
    if is_dark: top, bot = (15, 23, 42), (30, 41, 59)
    else:       top, bot = (255, 255, 255), (248, 250, 252)
    bg = Image.new("RGB", (WS, HS), top)
    d = ImageDraw.Draw(bg)
    for y in range(HS):
        t = y / (HS - 1)
        d.line([(0, y), (WS, y)],
               fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return bg.convert("RGBA")

def _theme_colors(is_dark):
    if is_dark:
        return {"text": (241, 245, 249), "sub": (148, 163, 184),
                "grid": (51, 65, 85, 100), "avg": (245, 158, 11),
                "panel": (30, 41, 59)}
    return {"text": (15, 23, 42), "sub": (100, 116, 139),
            "grid": (203, 213, 225, 130), "avg": (245, 158, 11),
            "panel": (255, 255, 255)}


def _draw_badge(canvas, text, x_center, y_center, color, font,
                pad_x=16, pad_y=9, radius=12):
    """badge نارنجی پُر رنگ با متن سفید و anchor دقیق"""
    d = ImageDraw.Draw(canvas)
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    px, py = _s(pad_x), _s(pad_y)
    bw = tw + px * 2
    bh = th + py * 2
    x0 = int(x_center - bw // 2)
    y0 = int(y_center - bh // 2)
    x1 = x0 + bw
    y1 = y0 + bh

    # ─── سایه‌ی نرم زیر badge ───
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [x0 + _s(2), y0 + _s(4), x1 + _s(2), y1 + _s(4)],
        radius=_s(radius), fill=(0, 0, 0, 80))
    sh = sh.filter(ImageFilter.GaussianBlur(_s(5)))
    canvas.alpha_composite(sh)

    # ─── پس‌زمینه‌ی گرادیان (روشن بالا → پر رنگ پایین) ───
    grad = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    light_c = _shade(color, 0.18)
    for row in range(bh):
        t = row / max(bh - 1, 1)
        col = _mix(light_c, color, t)
        gd.line([(0, row), (bw, row)], fill=col + (255,))
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, bw - 1, bh - 1], radius=_s(radius), fill=255)
    grad.putalpha(mask)
    canvas.paste(grad, (x0, y0), grad)

    # ─── هایلایت روشن بالای badge ───
    hl = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle(
        [x0, y0, x1, y0 + _s(4)],
        radius=_s(radius), fill=(255, 255, 255, 90))
    canvas.alpha_composite(hl)

    # ─── حاشیه‌ی تیره‌ی نازک ───
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x0, y0, x1, y1],
                        radius=_s(radius),
                        outline=_shade(color, -0.35) + (200,),
                        width=_s(1))

    # ─── متن سفید با anchor دقیق ───
    d.text((x_center, y_center), text, font=font,
           fill=(255, 255, 255), anchor="mm")


def _title(canvas, title, sub, accent, is_dark, W):
    d = ImageDraw.Draw(canvas)
    f_t = _font("Vazirmatn-Bold.ttf", 22)
    f_s = _font("Vazirmatn-Regular.ttf", 14)
    tc = _theme_colors(is_dark)
    b = d.textbbox((0, 0), _fa(title), font=f_t)
    tw = b[2] - b[0]
    tx = _s(W - 30) - tw
    ty = _s(20)
    d.text((tx, ty), _fa(title), font=f_t, fill=tc["text"])
    if sub:
        b2 = d.textbbox((0, 0), _fa(sub), font=f_s)
        tw2 = b2[2] - b2[0]
        d.text((_s(W - 30) - tw2, ty + _s(32)), _fa(sub),
               font=f_s, fill=tc["sub"])
    d.line([(tx, ty + _s(54)), (_s(W - 30), ty + _s(54))],
           fill=accent + (120,), width=_s(2))


def _draw_bar_3d(canvas, x_left, base_y, w, h, base, light, dark, dx, dy):
    xr, yt = x_left + w, base_y - h
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    pad = _s(8)
    ImageDraw.Draw(sh).ellipse(
        [x_left - pad, base_y - _s(5), xr + dx + pad, base_y + _s(10)],
        fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(_s(6)))
    canvas.alpha_composite(sh)
    d = ImageDraw.Draw(canvas)
    d.polygon([(x_left, yt), (xr, yt), (xr + dx, yt - dy), (x_left + dx, yt - dy)],
              fill=light + (255,))
    d.polygon([(xr, base_y), (xr, yt), (xr + dx, yt - dy), (xr + dx, base_y - dy)],
              fill=dark + (255,))
    if h > 0:
        fr = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fr)
        for row in range(h):
            t = row / max(h - 1, 1)
            col = _mix(light, base, t / 0.4) if t < 0.4 \
                  else _mix(base, dark, (t - 0.4) / 0.6 * 0.5)
            fd.line([(0, row), (w, row)], fill=col + (255,))
        canvas.alpha_composite(fr, (x_left, yt))
    hl = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).rectangle([x_left, yt, xr - 1, yt + _s(3)],
                                 fill=(255, 255, 255, 50))
    canvas.alpha_composite(hl)


# ═══════════ ۱. میله سه‌بعدی ═══════════
def chart_bar_3d(data, bill_type, unit_label, is_dark, mode="consumption"):
    vals = [float((d.get("consumption") if mode == "consumption"
                   else (d.get("amount") or 0) / 10) or 0) for d in data]
    if not vals or max(vals) <= 0: return None
    periods = [str(d.get("period", "-") or "-") for d in data]
    n = len(vals)
    th = BILL_THEMES.get(bill_type, BILL_THEMES["آب"])
    bc, lc, dc = _rgb(th["base"]), _rgb(th["light"]), _rgb(th["dark"])
    tc = _theme_colors(is_dark)

    W, H = max(720, n * 105 + 200), 420
    canvas = _new_canvas(W, H, is_dark)
    WS, HS = _s(W), _s(H)

    # ─── فضای‌ها: بالا زیاد برای badge میانگین ───
    pl = _s(95)     # چپ
    pr = _s(50)     # راست (کم چون badge بالاست)
    pt = _s(150)    # بالا (فضای کافی برای عنوان + badge میانگین)
    pb = _s(75)     # پایین برای برچسب دوره‌ها
    cl, cr = pl, WS - pr
    ctop, cbot = pt, HS - pb
    cw, ch = cr - cl, cbot - ctop

    # ymax با فضای اضافی بالا
    ymax_raw = max(vals)
    mag = 10 ** int(math.log10(max(ymax_raw, 1)))
    ymax = math.ceil(ymax_raw * 1.15 / (mag / 2)) * (mag / 2)
    y2p = lambda v: cbot - int((v / ymax) * ch)

    # ─── گرید ───
    g = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for i in range(5):
        yp = y2p(ymax * i / 4)
        gd.line([(cl, yp), (cr, yp)], fill=tc["grid"], width=_s(1))
    canvas.alpha_composite(g)

    # ─── خط میانگین (چین نازک) ───
    avg = sum(vals) / n
    d = ImageDraw.Draw(canvas)
    if avg > 0:
        ay = y2p(avg)
        x = cl
        while x < cr:
            xe = min(x + _s(8), cr)
            d.line([(x, ay), (xe, ay)], fill=tc["avg"], width=_s(2))
            x = xe + _s(6)

    # ─── میله‌ها ───
    slot = cw / n
    bw = int(slot * 0.42)
    dx, dy = _s(18), _s(10)
    mx = max(vals)
    for i, v in enumerate(vals):
        if v <= 0: continue
        cx = cl + slot * i + slot / 2
        xl = int(cx - (bw + dx) / 2)
        hp = int((v / ymax) * ch)
        sat = 0.68 + 0.32 * (v / mx)
        _draw_bar_3d(canvas, xl, cbot, bw, hp,
                     tuple(int(c * sat) for c in bc),
                     tuple(int(c * sat) for c in lc),
                     tuple(int(c * sat * 0.9) for c in dc), dx, dy)

    # ─── برچسب مقدار بالای میله ───
    d = ImageDraw.Draw(canvas)
    f_v = _font("Vazirmatn-Bold.ttf", 15)
    for i, v in enumerate(vals):
        if v <= 0: continue
        cx = cl + slot * i + slot / 2
        hp = int((v / ymax) * ch)
        ty = cbot - hp - dy - _s(24)
        lbl = _fanum(v, 0)
        b = d.textbbox((0, 0), lbl, font=f_v)
        tw = b[2] - b[0]
        d.text((int(cx - tw / 2), ty), lbl, font=f_v, fill=tc["text"])

    # ─── برچسب دوره‌ها ───
    f_p = _font("Vazirmatn-Bold.ttf", 15)
    for i, p in enumerate(periods):
        cx = cl + slot * i + slot / 2
        lbl = _fa(p)
        b = d.textbbox((0, 0), lbl, font=f_p)
        tw = b[2] - b[0]
        d.text((int(cx - tw / 2), cbot + _s(18)), lbl, font=f_p, fill=tc["text"])

    # ─── محور Y ───
    f_y = _font("Vazirmatn-Regular.ttf", 12)
    for i in range(5):
        yp = y2p(ymax * i / 4)
        lbl = _fanum(ymax * i / 4, 0)
        b = d.textbbox((0, 0), lbl, font=f_y)
        tw = b[2] - b[0]
        d.text((cl - _s(10) - tw, yp - _s(7)), lbl, font=f_y, fill=tc["sub"])

    # ─── badge میانگین — بالای ناحیه‌ی نمودار، سمت راست ───
    if avg > 0:
        f_badge = _font("Vazirmatn-Bold.ttf", 14)
        lbl = _fa(f"میانگین: {_fanum(avg, 0)}")
        b = d.textbbox((0, 0), lbl, font=f_badge)
        bw_text = b[2] - b[0]
        # فاصله از لبه‌ی راست نمودار
        x_c = cr - bw_text // 2 - _s(30)
        # در بالای ناحیه‌ی نمودار (بین عنوان و کوتاه‌ترین میله)
        y_c = ctop - _s(40)
        _draw_badge(canvas, lbl, x_c, y_c, tc["avg"], f_badge,
                    pad_x=16, pad_y=9, radius=12)

    # ─── خط تزئینی زیر badge ───
    # (خط کوتاه به سمت خط میانگین)
    if avg > 0:
        y_c_end = y_c + _s(20)  # پایین badge
        ay = y2p(avg)
        # خط راهنما از badge تا خط میانگین
        # (به صورت نقطه‌چین با شفافیت کم)
        # خیلی ساده: یک خط کوتاه عمودی از زیر badge به سمت خط میانگین
        guide = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        gd2 = ImageDraw.Draw(guide)
        gx = int(x_c)
        gy1 = int(y_c_end)
        gy2 = int(ay)
        # فقط نیمه‌ی راه (برای ظرافت)
        gy_mid = (gy1 + gy2) // 2
        for yy in range(gy1, gy_mid, _s(6)):
            gd2.line([(gx, yy), (gx, yy + _s(3))],
                     fill=tc["avg"] + (120,), width=_s(1))
        canvas.alpha_composite(guide)

    # ─── عنوان ───
    ttl = f"{'مصرف' if mode == 'consumption' else 'مبلغ'} {bill_type}"
    if unit_label: ttl += f" ({unit_label})"
    _title(canvas, ttl, "مقایسه در طول دوره", bc, is_dark, W)

    # ─── downscale با LANCZOS برای کیفیت بالا ───
    out = canvas.convert("RGB").resize((W * 2, H * 2), Image.LANCZOS)
    return out


# ═══════════ ۲. ناحیه‌ای ═══════════
def chart_area(data, bill_type, unit_label, is_dark, mode="consumption"):
    vals = [float((d.get("consumption") if mode == "consumption"
                   else (d.get("amount") or 0) / 10) or 0) for d in data]
    if not vals or max(vals) <= 0: return None
    periods = [str(d.get("period", "-") or "-") for d in data]
    n = len(vals)
    th = BILL_THEMES.get(bill_type, BILL_THEMES["آب"])
    bc, lc = _rgb(th["base"]), _rgb(th["light"])
    tc = _theme_colors(is_dark)

    W, H = max(720, n * 105 + 200), 420
    canvas = _new_canvas(W, H, is_dark)
    WS, HS = _s(W), _s(H)

    pl, pr = _s(95), _s(50)
    pt, pb = _s(150), _s(75)
    cl, cr = pl, WS - pr
    ctop, cbot = pt, HS - pb
    cw, ch = cr - cl, cbot - ctop

    ymax_raw = max(vals)
    mag = 10 ** int(math.log10(max(ymax_raw, 1)))
    ymax = math.ceil(ymax_raw * 1.15 / (mag / 2)) * (mag / 2)
    y2p = lambda v: cbot - int((v / ymax) * ch)

    # گرید
    g = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for i in range(5):
        yp = y2p(ymax * i / 4)
        gd.line([(cl, yp), (cr, yp)], fill=tc["grid"], width=_s(1))
    canvas.alpha_composite(g)

    xs = [cl + (cw * i / max(n - 1, 1)) for i in range(n)]
    ys = [y2p(v) for v in vals]

    # ناحیه‌ی گرادیانی
    area = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ad = ImageDraw.Draw(area)
    for i in range(n - 1):
        x1, x2 = int(xs[i]), int(xs[i + 1])
        y1, y2 = ys[i], ys[i + 1]
        for x in range(x1, x2 + 1):
            t = (x - x1) / max(x2 - x1, 1)
            ytop = int(y1 + (y2 - y1) * t)
            for y in range(ytop, cbot):
                tt = (y - ytop) / max(cbot - ytop, 1)
                alpha = int(200 * (1 - tt * 0.9))
                col = _mix(lc, bc, tt * 0.5)
                ad.point((x, y), fill=col + (alpha,))
    canvas.alpha_composite(area)

    d = ImageDraw.Draw(canvas)
    for i in range(n - 1):
        d.line([(xs[i], ys[i]), (xs[i + 1], ys[i + 1])],
               fill=bc + (255,), width=_s(3))
    r = _s(5)
    for x, y in zip(xs, ys):
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=bc + (255,), outline=(255, 255, 255, 255), width=_s(2))

    f_v = _font("Vazirmatn-Bold.ttf", 14)
    for x, y, v in zip(xs, ys, vals):
        lbl = _fanum(v, 0)
        b = d.textbbox((0, 0), lbl, font=f_v)
        tw = b[2] - b[0]
        d.text((int(x - tw / 2), int(y - _s(26))), lbl, font=f_v, fill=tc["text"])

    f_p = _font("Vazirmatn-Bold.ttf", 15)
    for x, p in zip(xs, periods):
        lbl = _fa(p)
        b = d.textbbox((0, 0), lbl, font=f_p)
        tw = b[2] - b[0]
        d.text((int(x - tw / 2), cbot + _s(18)), lbl, font=f_p, fill=tc["text"])

    f_y = _font("Vazirmatn-Regular.ttf", 12)
    for i in range(5):
        yp = y2p(ymax * i / 4)
        lbl = _fanum(ymax * i / 4, 0)
        b = d.textbbox((0, 0), lbl, font=f_y)
        tw = b[2] - b[0]
        d.text((cl - _s(10) - tw, yp - _s(7)), lbl, font=f_y, fill=tc["sub"])

    # badge میانگین
    avg = sum(vals) / n
    if avg > 0:
        f_badge = _font("Vazirmatn-Bold.ttf", 14)
        lbl = _fa(f"میانگین: {_fanum(avg, 0)}")
        b = d.textbbox((0, 0), lbl, font=f_badge)
        bw_text = b[2] - b[0]
        x_c = cr - bw_text // 2 - _s(30)
        y_c = ctop - _s(40)
        _draw_badge(canvas, lbl, x_c, y_c, tc["avg"], f_badge,
                    pad_x=16, pad_y=9, radius=12)

    ttl = f"{'مصرف' if mode == 'consumption' else 'مبلغ'} {bill_type}"
    if unit_label: ttl += f" ({unit_label})"
    _title(canvas, ttl, "حجم مصرف با گرادیان", bc, is_dark, W)

    out = canvas.convert("RGB").resize((W * 2, H * 2), Image.LANCZOS)
    return out


# ═══════════ ۳. حبابی ═══════════
def chart_bubble(data, bill_type, unit_label, is_dark, mode=None):
    if not data: return None
    th = BILL_THEMES.get(bill_type, BILL_THEMES["آب"])
    bc = _rgb(th["base"])
    tc = _theme_colors(is_dark)

    xs, ys, sizes, labels = [], [], [], []
    for d in data:
        c = float(d.get("consumption") or 0)
        a = float(d.get("amount") or 0) / 10
        if c <= 0 or a <= 0: continue
        xs.append(c); ys.append(a)
        sizes.append(max(8, min(28, (d.get("daily_avg") or 1) * 1.5)))
        labels.append(d.get("period", "-") or "-")
    if not xs: return None

    W, H = 720, 480
    canvas = _new_canvas(W, H, is_dark)
    WS, HS = _s(W), _s(H)
    pl, pr, pt, pb = _s(95), _s(50), _s(120), _s(75)
    cl, cr = pl, WS - pr
    ctop, cbot = pt, HS - pb
    cw, ch = cr - cl, cbot - ctop

    xmax, ymax = max(xs) * 1.15, max(ys) * 1.15
    x2p = lambda v: cl + int((v / xmax) * cw)
    y2p = lambda v: cbot - int((v / ymax) * ch)

    g = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for i in range(5):
        yp = y2p(ymax * i / 4)
        gd.line([(cl, yp), (cr, yp)], fill=tc["grid"], width=_s(1))
        xp = x2p(xmax * i / 4)
        gd.line([(xp, ctop), (xp, cbot)], fill=tc["grid"], width=_s(1))
    canvas.alpha_composite(g)

    d = ImageDraw.Draw(canvas)
    for x, y, s in zip(xs, ys, sizes):
        px, py = x2p(x), y2p(y)
        rr = _s(s)
        d.ellipse([px - rr - _s(4), py - rr - _s(4),
                   px + rr + _s(4), py + rr + _s(4)], fill=bc + (35,))
        d.ellipse([px - rr, py - rr, px + rr, py + rr],
                  fill=bc + (200,), outline=(255, 255, 255, 220), width=_s(2))

    for x, y, s, lb in zip(xs, ys, sizes, labels):
        px, py = x2p(x), y2p(y)
        f_lbl = _font("Vazirmatn-Bold.ttf", 12)
        l = _fa(lb)
        b = d.textbbox((0, 0), l, font=f_lbl)
        tw = b[2] - b[0]
        d.text((int(px - tw / 2), int(py + _s(s) + _s(6))), l,
               font=f_lbl, fill=tc["text"])

    f_a = _font("Vazirmatn-Regular.ttf", 12)
    for i in range(5):
        xp = x2p(xmax * i / 4)
        lbl = _fanum(xmax * i / 4, 0)
        b = d.textbbox((0, 0), lbl, font=f_a)
        tw = b[2] - b[0]
        d.text((int(xp - tw / 2), cbot + _s(18)), lbl, font=f_a, fill=tc["sub"])
        yp = y2p(ymax * i / 4)
        lbl = _fanum(ymax * i / 4, 0)
        b = d.textbbox((0, 0), lbl, font=f_a)
        tw = b[2] - b[0]
        d.text((cl - _s(10) - tw, yp - _s(7)), lbl, font=f_a, fill=tc["sub"])

    ttl = f"حباب {bill_type}"
    _title(canvas, ttl,
           "مصرف در برابر مبلغ (اندازه = میانگین روزانه)",
           bc, is_dark, W)

    out = canvas.convert("RGB").resize((W * 2, H * 2), Image.LANCZOS)
    return out


# ═══════════ فقط ۳ نمودار ═══════════
CHART_TYPES = [
    ("bar_3d",  "میله سه‌بعدی", chart_bar_3d),
    ("area",    "ناحیه‌ای",     chart_area),
    ("bubble",  "حبابی",        chart_bubble),
]


def _get_output_dir():
    """پوشه‌ی temp_charts — سازگار با exe و حالت توسعه"""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(base, "temp_charts")
    os.makedirs(p, exist_ok=True)
    return p


def generate_chart(chart_type, data, bill_type, unit_label="",
                   is_dark=False, mode="consumption"):
    if not data:
        return {"success": False, "path": None, "message": "داده نیست"}
    handler = None
    for ct, _, fn in CHART_TYPES:
        if ct == chart_type:
            handler = fn
            break
    if handler is None:
        return {"success": False, "path": None,
                "message": f"نوع نامعتبر: {chart_type}"}
    try:
        img = handler(data, bill_type, unit_label, is_dark, mode=mode)
        if img is None:
            return {"success": False, "path": None,
                    "message": "نمودار قابل رسم نیست"}
        d = _get_output_dir()
        safe = "".join(c for c in f"{chart_type}_{mode}_{bill_type}"
                       if c.isalnum() or c in "._-")
        p = os.path.join(d, f"{safe}.png")
        img.save(p, "PNG", optimize=True)
        return {"success": True, "path": p, "message": ""}
    except Exception as ex:
        import traceback
        traceback.print_exc()
        return {"success": False, "path": None, "message": str(ex)}