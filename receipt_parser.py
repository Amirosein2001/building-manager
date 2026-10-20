# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.


"""
Parser فیش‌های بانکی ایرانی — Universal v31.1
Fix: 5→0 variants for year-prefixed tracking codes
"""

import os
import sys
import re
from itertools import combinations
from collections import Counter, defaultdict
from PIL import Image, ImageOps


def _get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = _get_app_dir()


def _load_image_rgb(image_path):
    import numpy as np
    return np.array(Image.open(image_path).convert('RGB'))


def _load_image_gray(image_path):
    import numpy as np
    return np.array(Image.open(image_path).convert('L'))


# ═══════════════════════════════════════════════════════════
# ═══  Tesseract  ═══
# ═══════════════════════════════════════════════════════════

TESSERACT_PATHS = [
    os.path.join(APP_DIR, "Tesseract-OCR", "tesseract.exe"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "Tesseract-OCR", "tesseract.exe"),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(
        r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    ),
]

_tess_ready = None


def _setup_tesseract():
    global _tess_ready
    if _tess_ready is not None:
        return _tess_ready
    try:
        import pytesseract
    except ImportError:
        _tess_ready = False
        return False
    for path in TESSERACT_PATHS:
        if path and os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            _tess_ready = True
            print(f"✅ Tesseract: {path}")
            return True
    _tess_ready = False
    return False


# ═══════════════════════════════════════════════════════════
# ═══  EasyOCR  ═══
# ═══════════════════════════════════════════════════════════

_ocr_reader = None


def _get_easyocr_model_dir():
    bundled = os.path.join(APP_DIR, "EasyOCR_models")
    if os.path.exists(bundled):
        return bundled
    return None


def _get_ocr():
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr
            print("🔄 لود EasyOCR...")
            model_dir = _get_easyocr_model_dir()

            # ⭐ چک فایل‌های موردنیاز
            if model_dir:
                import glob
                files = os.listdir(model_dir)
                print(f"📁 فایل‌های موجود در {model_dir}: {files}")

                required = ['craft_mlt_25k.pth', 'english_g2.pth', 'farsi_g2.pth']
                missing = [f for f in required if f not in files]
                if missing:
                    print(f"⚠️⚠️⚠️ فایل‌های گم‌شده: {missing}")
                    _ocr_reader = False
                    return False

            _ocr_reader = easyocr.Reader(
                ['fa', 'en'], gpu=False, verbose=False,
                model_storage_directory=model_dir,
                download_enabled=False,  # ⭐ جلوگیری از دانلود
            )
            print("✅ EasyOCR آماده")
        except Exception as ex:
            print(f"❌ EasyOCR خطا: {ex}")
            import traceback
            traceback.print_exc()
            _ocr_reader = False
    return _ocr_reader


def _easyocr_raw(image_path):
    reader = _get_ocr()
    if not reader:
        return []
    try:
        return reader.readtext(_load_image_rgb(image_path))
    except Exception as ex:
        print(f"❌ EasyOCR: {ex}")
        return []


def _group_lines(boxes):
    if not boxes:
        return []
    boxes = sorted(boxes, key=lambda b: b['y'])
    avg_h = sum(b['h'] for b in boxes) / len(boxes)
    y_th = max(avg_h * 0.6, 8)
    rows, cur = [], [boxes[0]]
    for b in boxes[1:]:
        if abs(b['y'] - cur[-1]['y']) <= y_th:
            cur.append(b)
        else:
            rows.append(cur);
            cur = [b]
    rows.append(cur)
    return rows


def _boxes_to_text(raw):
    if not raw:
        return ""
    boxes = []
    for bbox, text, conf in raw:
        if not text or not text.strip() or conf < 0.2:
            continue
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        boxes.append({
            'text': text.strip(),
            'x_center': sum(xs) / len(xs),
            'y': sum(ys) / len(ys),
            'h': max(ys) - min(ys),
        })
    rows = _group_lines(boxes)
    lines = []
    for row in rows:
        row.sort(key=lambda b: -b['x_center'])
        lines.append(' '.join(b['text'] for b in row))
    return '\n'.join(lines)


def _easyocr_crop_digits(image_path, bbox, pad=15, debug=False, tag=""):
    reader = _get_ocr()
    if not reader:
        return ""
    try:
        import numpy as np
        orig = Image.open(image_path)
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        x1 = max(0, int(min(xs)) - pad)
        y1 = max(0, int(min(ys)) - pad)
        x2 = min(orig.width, int(max(xs)) + pad)
        y2 = min(orig.height, int(max(ys)) + pad)
        crop = orig.crop((x1, y1, x2, y2))
        crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)

        allowlist = '۰۱۲۳۴۵۶۷۸۹0123456789٠١٢٣٤٥٦٧٨٩'
        result = reader.readtext(np.array(crop), allowlist=allowlist)
        txt = ' '.join(t for _, t, _ in result)
        if debug:
            print(f"\n🔎 [{tag} easyocr-digits]: {txt!r}")
        return txt
    except Exception as ex:
        if debug:
            print(f"❌ [{tag}]: {ex}")
        return ""


def _tesseract_full_text(image_path, debug=False):
    if not _setup_tesseract():
        return ""
    try:
        import pytesseract
        img = Image.open(image_path)
        w, h = img.size
        img = img.resize((int(w * 2.5), int(h * 2.5)), Image.LANCZOS)
        img = img.convert('L')
        img = ImageOps.autocontrast(img, cutoff=1)
        txt = pytesseract.image_to_string(
            img, config='--oem 3 --psm 4 -l fas+eng'
        )
        if debug:
            print(f"\n📄 Tesseract full:")
            for line in txt.split('\n')[:20]:
                if line.strip():
                    print(f"   {line!r}")
        return txt
    except Exception as ex:
        print(f"❌ Tesseract full: {ex}")
        return ""


# ═══════════════════════════════════════════════════════════
# ═══  نرمال‌سازی  ═══
# ═══════════════════════════════════════════════════════════

PD = "۰۱۲۳۴۵۶۷۸۹"
AD = "٠١٢٣٤٥٦٧٨٩"
ED = "0123456789"


def to_english_digits(text):
    if not text:
        return ""
    for i in range(10):
        text = text.replace(PD[i], ED[i]).replace(AD[i], ED[i])
    return text


def normalize_text(text):
    if not text:
        return ""
    t = to_english_digits(text)
    t = t.replace("٬", ",").replace("،", ",")
    t = t.replace("|", " ")
    t = t.replace("\u200c", " ")
    t = t.replace("\u200f", "").replace("\u200e", "")
    t = t.replace("ي", "ی").replace("ك", "ک")
    t = t.replace("ربال", "ریال")
    t = re.sub(r'[^\S\n]+', ' ', t)
    return t


PERSIAN_MONTHS = {
    'فروردین': 1, 'فرودین': 1, 'اردیبهشت': 2, 'خرداد': 3, 'تیر': 4,
    'مرداد': 5, 'امرداد': 5, 'شهریور': 6, 'مهر': 7, 'آبان': 8,
    'ابان': 8, 'آذر': 9, 'اذر': 9, 'دی': 10, 'بهمن': 11, 'اسفند': 12,
}


def _find_persian_month_date(text):
    for name, mnum in PERSIAN_MONTHS.items():
        if name not in text:
            continue
        for pat in [
            rf'(\d{{1,2}})\s+{name}\s+(\d{{4}})',
            rf'(\d{{4}})\s+{name}\s+(\d{{1,2}})',
            rf'{name}\s+(\d{{1,2}})\s+(\d{{4}})',
        ]:
            for m in re.finditer(pat, text):
                nums = m.groups()
                if len(nums) != 2:
                    continue
                a, b = int(nums[0]), int(nums[1])
                if 1300 <= a <= 1500:
                    y, d = a, b
                elif 1300 <= b <= 1500:
                    d, y = a, b
                else:
                    continue
                if 1 <= d <= 31:
                    return f"{y}/{mnum:02d}/{d:02d}"
    return ""


def _find_persian_month_day_fallback(text):
    for name, mnum in PERSIAN_MONTHS.items():
        if name not in text:
            continue
        m = re.search(rf'(\d{{1,2}})\s+{name}', text)
        if m:
            day = int(m.group(1))
            if 1 <= day <= 31:
                return f"1405/{mnum:02d}/{day:02d}"
    return ""


def _fix_chars(text):
    if not text:
        return ""
    c = to_english_digits(text)
    c = c.replace("\u200f", "").replace("\u200e", "")
    c = c.replace("|", " ")
    reps = {
        'Y': '2', 'y': '2', 'A': '4', 'a': '4', 'V': '7', 'v': '7',
        'T': '7', 't': '7', 'H': '4', 'h': '4', 'B': '8', 'b': '6',
        'Z': '2', 'z': '2', 'S': '5', 's': '5', 'g': '9', 'q': '9',
        '}': '1', ']': '1', '\\': '1', '!': '1',
        'o': '0', 'O': '0', 'D': '0', 'Q': '0', 'l': '1', 'I': '1',
    }
    for k, v in reps.items():
        c = c.replace(k, v)
    for w in ['ریال', 'ربال', 'کارمزد', 'مبلغ', 'انتقال']:
        c = c.replace(w, ' ')
    return c


def _strip_spaces_in_numbers(text):
    if not text:
        return text
    parts = re.split(r'\s{2,}', text)
    cleaned = []
    for p in parts:
        prev = None
        while prev != p:
            prev = p
            p = re.sub(r'(\d)\s+(\d)', r'\1\2', p)
            p = re.sub(r'(\d)\s+([,\.])', r'\1\2', p)
            p = re.sub(r'([,\.])\s+(\d)', r'\1\2', p)
        cleaned.append(p)
    return '  '.join(cleaned)


# ═══════════════════════════════════════════════════════════
# ⭐ NEW: 5→0 variant generator for year-prefixed codes
# ═══════════════════════════════════════════════════════════

YEAR_PREFIXES = ['1405', '1404', '1403', '1402', '1401', '1400',
                 '1399', '1398', '1397', '1396', '1395']


def _5_to_0_variants(code, max_swaps=3):
    """
    برای کدهایی که با سال شمسی شروع می‌شن (140x)،
    نسخه‌هایی تولید کن که بعضی ۵های tail رو با ۰ عوض می‌کنه.

    منطق: در فیش‌های بانکی، ۰ و ۵ در بعضی فونت‌ها شبیه‌ن
    و OCR اشتباه می‌کنه.
    """
    if not code or len(code) < 8:
        return [code]

    # چک کردن year prefix
    year_prefix = None
    for p in YEAR_PREFIXES:
        if code.startswith(p):
            year_prefix = p
            break

    if year_prefix is None:
        return [code]

    tail = code[len(year_prefix):]

    # فقط ۵هایی که کنارشون ۵ نیست (isolated 5s)
    isolated_positions = []
    for i, c in enumerate(tail):
        if c != '5':
            continue
        prev_is_5 = (i > 0 and tail[i - 1] == '5')
        next_is_5 = (i < len(tail) - 1 and tail[i + 1] == '5')
        if not prev_is_5 and not next_is_5:
            isolated_positions.append(i)

    if not isolated_positions:
        return [code]

    variants = [code]
    n_isolated = len(isolated_positions)
    max_n = min(max_swaps, n_isolated)

    for n in range(1, max_n + 1):
        for combo in combinations(isolated_positions, n):
            new_tail = list(tail)
            for pos in combo:
                new_tail[pos] = '0'
            variants.append(year_prefix + ''.join(new_tail))

    return variants


# ═══════════════════════════════════════════════════════════
# ═══  ⭐ Repair: پیگیری (v31)  ═══
# ═══════════════════════════════════════════════════════════

def _repair_tracking(code):
    if not code or len(code) < 4:
        return code

    # Saman: 12-digit `1355...` → `1300...`
    if len(code) == 12 and code.startswith('13') and code[2:4] == '55':
        return code[:2] + '00' + code[4:]

    # Sepino: 12-digit `4555...` → `14050...`
    if len(code) == 12 and code.startswith('4555'):
        return '14050' + code[4:]



    # Refah: 6-digit `39XXXX5` → `39XXXX0`
    if len(code) == 6 and code.startswith('39') and code.endswith('5'):
        return code[:5] + '0'

    # صادرات: 12-digit `15...`
    if len(code) == 12 and code.startswith('15'):
        chars = list(code)
        chars[0] = '4'
        for i in (1, 3, 6):
            if i < len(chars) and chars[i] == '5':
                chars[i] = '0'
        return ''.join(chars)

    # ملل: 6-digit `15...`
    if len(code) == 6 and code.startswith('15'):
        code = re.sub(r'5{2,}',
                      lambda m: '0' * len(m.group()),
                      code)
        return code

    # سال شمسی
    if code.startswith('14') and len(code) >= 3:
        third = code[2]
        if third in '56789':
            code = code[:2] + '0' + code[3:]

    return code


# ═══════════════════════════════════════════════════════════
# ═══  Repair: مبلغ  ═══
# ═══════════════════════════════════════════════════════════

def _is_year_like(n):
    return 1385 <= n <= 1425


def _max_reasonable_amount():
    return 99_999_999_999


def _repair_amount(amount):
    if amount <= 0:
        return amount
    s = str(amount)
    if len(s) >= 11:
        best_candidate = None
        best_score = -1
        for split in range(6, len(s) - 5):
            for sub in (s[:split], s[split:]):
                try:
                    v = int(sub)
                except Exception:
                    continue
                if 100_000 <= v <= _max_reasonable_amount():
                    trailing = len(sub) - len(sub.rstrip('0'))
                    if trailing > best_score:
                        best_score = trailing
                        best_candidate = v
        return best_candidate if best_candidate else 0
    candidates = [(s, amount)]
    n5 = s.count('5')
    ratio_5 = n5 / len(s)
    if ratio_5 >= 0.4:
        s2 = s.replace('5', '0')
        if s2.startswith('0'):
            s2 = '1' + s2
        try:
            v = int(s2)
            if 100_000 <= v <= _max_reasonable_amount():
                candidates.append((s2, v))
        except Exception:
            pass
    if s.startswith('11') and len(s) >= 9:
        s4 = s[1:]
        try:
            v = int(s4)
            if 100_000 <= v <= _max_reasonable_amount():
                candidates.append((s4, v))
        except Exception:
            pass

    def _score(s_val, v):
        if v < 100_000 or v > _max_reasonable_amount():
            return -1e9
        if 1385 <= v <= 1425:
            return -1e8
        trailing_zeros = len(s_val) - len(s_val.rstrip('0'))
        n5_c = s_val.count('5')
        n0_c = s_val.count('0')
        score = 0
        score += trailing_zeros * 300
        score += n0_c * 15
        score -= n5_c * 50
        if s_val.endswith('0000000'):
            score += 500
        elif s_val.endswith('000000'):
            score += 300
        elif s_val.endswith('00000'):
            score += 100
        if s_val and s_val[0] in '123456789':
            score += 40
        if s_val.startswith('11') and len(s_val) > 8:
            score -= 80
        return score

    best = max(candidates, key=lambda c: _score(c[0], c[1]))
    return best[1]


# ═══════════════════════════════════════════════════════════
# ═══  Scattered Amount Collector  ═══
# ═══════════════════════════════════════════════════════════

def _collect_scattered_amounts(text):
    amounts = []
    for line in text.split('\n'):
        if 'ریال' not in line and 'ريال' not in line:
            continue
        tokens = re.findall(r'\d[\d,]*', line)
        if not tokens:
            continue
        cleaned_tokens = []
        for t in tokens:
            t2 = re.sub(r'[^\d]', '', t)
            if t2:
                cleaned_tokens.append(t2)
        if not cleaned_tokens:
            continue
        joined = ''.join(cleaned_tokens)
        if joined:
            try:
                v = int(joined)
                if 100_000 <= v <= _max_reasonable_amount():
                    amounts.append(v)
            except Exception:
                pass
        joined_rev = ''.join(reversed(cleaned_tokens))
        if joined_rev and joined_rev != joined:
            try:
                v = int(joined_rev)
                if 100_000 <= v <= _max_reasonable_amount():
                    amounts.append(v)
            except Exception:
                pass
        for t in cleaned_tokens:
            try:
                v = int(t)
                if 100_000 <= v <= _max_reasonable_amount():
                    amounts.append(v)
            except Exception:
                pass
        if len(cleaned_tokens) >= 2:
            for i in range(len(cleaned_tokens) - 1):
                for j in range(i + 1, len(cleaned_tokens)):
                    for combo in [
                        cleaned_tokens[i] + cleaned_tokens[j],
                        cleaned_tokens[j] + cleaned_tokens[i],
                    ]:
                        try:
                            v = int(combo)
                            if 100_000 <= v <= _max_reasonable_amount():
                                amounts.append(v)
                        except Exception:
                            pass
    return amounts


# ═══════════════════════════════════════════════════════════
# ═══  Smart Amount Merge  ═══
# ═══════════════════════════════════════════════════════════

def _smart_amount_from_sources(all_amounts):
    if not all_amounts:
        return 0
    seen = set()
    unique_amounts = []
    for a in all_amounts:
        if a not in seen:
            seen.add(a)
            unique_amounts.append(a)
    filtered = [
        a for a in unique_amounts
        if 100_000 <= a <= _max_reasonable_amount()
           and not (1385 <= a <= 1425)
    ]
    if not filtered:
        return 0
    repaired = []
    for a in filtered:
        r = _repair_amount(a)
        if 100_000 <= r <= _max_reasonable_amount():
            repaired.append(r)
    if not repaired:
        return 0
    seen2 = set()
    unique_repaired = []
    for r in repaired:
        if r not in seen2:
            seen2.add(r)
            unique_repaired.append(r)
    repaired = unique_repaired
    counts = Counter(repaired)
    max_count = max(counts.values())
    top = [v for v, c in counts.items() if c == max_count]

    def _score(v):
        s = str(v)
        trailing = len(s) - len(s.rstrip('0'))
        n5 = s.count('5')
        score = trailing * 100 - n5 * 30
        if s.endswith('0000000'):
            score += 400
        elif s.endswith('000000'):
            score += 200
        if 7 <= len(s) <= 9:
            score += 50
        elif len(s) >= 11:
            score -= 200
        return score

    return max(top, key=_score)


# ═══════════════════════════════════════════════════════════
# ═══  Repair: تاریخ  ═══
# ═══════════════════════════════════════════════════════════

CURRENT_YEAR = 1405


def _repair_year(date_str):
    if not date_str:
        return date_str
    m = re.match(r'(\d{4})/(\d{2})/(\d{2})', date_str)
    if not m:
        return date_str
    y, mo, d = int(m.group(1)), m.group(2), m.group(3)
    y_str = str(y)
    candidates = [y]
    if '5' in y_str:
        c1 = int(y_str.replace('5', '0'))
        if 1300 <= c1 <= 1500:
            candidates.append(c1)
    if len(y_str) == 4 and y_str[2] == '5':
        c2 = int(y_str[:2] + '0' + y_str[3])
        if 1300 <= c2 <= 1500:
            candidates.append(c2)
    if len(y_str) == 4 and y_str[3] == '5':
        c3 = int(y_str[:3] + '0')
        if 1300 <= c3 <= 1500:
            candidates.append(c3)
    good = [c for c in candidates if 1400 <= c <= 1410]
    if good:
        best = min(good, key=lambda c: abs(c - CURRENT_YEAR))
    else:
        best = min(candidates, key=lambda c: abs(c - CURRENT_YEAR))
    return f"{best}/{mo}/{d}"


def _repair_date_day(day):
    if 1 <= day <= 31:
        return day
    s = str(day)
    if len(s) == 2 and s[0] == '5':
        nd = int(s[1])
        if 1 <= nd <= 31:
            return nd
    if len(s) == 2 and s[0] in ('7', '8', '9'):
        nd = int('1' + s[1])
        if 1 <= nd <= 31:
            return nd
    if len(s) == 3:
        for cand in (int(s[1:]), int(s[:2])):
            if 1 <= cand <= 31:
                return cand
    return day


def _repair_date_month(mo):
    if 1 <= mo <= 12:
        return mo
    s = str(mo)
    if len(s) == 2 and s[0] == '5':
        nm = int(s[1])
        if 1 <= nm <= 12:
            return nm
    if len(s) == 2 and s[0] in ('1', '2', '3', '7', '8', '9'):
        nm = int(s[1])
        if 1 <= nm <= 12:
            return nm
    return mo


def _crop_region_tesseract(region, thresholds=(100, 128, 160, 190),
                           psms=(7, 8, 6)):
    if not _setup_tesseract():
        return []
    try:
        import pytesseract
        import numpy as np
        results = []
        for th in thresholds:
            arr = np.array(region.convert('L'))
            bin_arr = np.where(arr > th, 255, 0).astype(np.uint8)
            img_bin = Image.fromarray(bin_arr)
            for psm in psms:
                try:
                    txt = pytesseract.image_to_string(
                        img_bin,
                        config=f'--oem 3 --psm {psm} -l fas+eng'
                    ).strip()
                    if txt:
                        results.append((th, psm, txt))
                except Exception:
                    pass
        return results
    except Exception:
        return []


def _crop_left_of_label(image_path, label_bbox, pad=15):
    if not _setup_tesseract():
        return []
    try:
        orig = Image.open(image_path)
        xs = [p[0] for p in label_bbox]
        ys = [p[1] for p in label_bbox]
        x_label_min = int(min(xs))
        y1 = max(0, int(min(ys)) - pad)
        y2 = min(orig.height, int(max(ys)) + pad)
        x2 = x_label_min - 5
        if x2 <= 5:
            return []
        region = orig.crop((0, y1, x2, y2))
        region = region.resize(
            (region.width * 5, region.height * 5), Image.LANCZOS
        )
        return _crop_region_tesseract(region)
    except Exception:
        return []


def _crop_above_label(image_path, label_bbox):
    if not _setup_tesseract():
        return []
    try:
        orig = Image.open(image_path)
        xs = [p[0] for p in label_bbox]
        ys = [p[1] for p in label_bbox]
        y_label_top = int(min(ys))
        h_label = max(ys) - min(ys)
        y_top = max(0, y_label_top - 4 * h_label)
        x_min = max(0, int(min(xs)) - 50)
        x_max = min(orig.width, int(max(xs)) + 50)
        region = orig.crop((x_min, y_top, x_max, y_label_top))
        region = region.resize(
            (region.width * 5, region.height * 5), Image.LANCZOS
        )
        return _crop_region_tesseract(region, psms=(6, 7, 8, 13))
    except Exception:
        return []


AMOUNT_LABEL_PATTERNS = [
    r'مبلغ\s*(?:کل|انتقال|تراکنش|برداشت|واریز|انتقال\s*وجه)?\s*[:：]?\s*([0-9][0-9,\.\s]{2,})',
    r'مبلغ\s*(?:کل|انتقال|تراکنش|برداشت|واریز)?\s+([0-9][0-9,\.\s]{2,})',
]


def _extract_amounts_from_text(text):
    amounts = []
    for line in text.split('\n'):
        if ('مبلغ' not in line and 'مبلع' not in line
                and 'ميلغ' not in line):
            continue
        fixed_line = _strip_spaces_in_numbers(line)
        for pat in AMOUNT_LABEL_PATTERNS:
            for m in re.finditer(pat, fixed_line):
                token = m.group(1)
                digits = re.sub(r'[^\d]', '', token)
                if not digits:
                    continue
                try:
                    v = int(digits)
                    if (100_000 <= v <= _max_reasonable_amount()
                            and not _is_year_like(v)):
                        amounts.append(v)
                except Exception:
                    pass
    fixed_text = _strip_spaces_in_numbers(text)
    for m in re.finditer(
            r'([0-9][0-9,\.]{3,})\s*(?:ریال|ريال)', fixed_text
    ):
        v = int(re.sub(r'[^\d]', '', m.group(1)) or 0)
        if (100_000 <= v <= _max_reasonable_amount()
                and not _is_year_like(v)):
            amounts.append(v)
    for m in re.finditer(r'\b(\d{1,3}(?:,\d{3}){2,})\b', text):
        v = int(re.sub(r'[^\d]', '', m.group(1)) or 0)
        if (100_000 <= v <= _max_reasonable_amount()
                and not _is_year_like(v)):
            amounts.append(v)
    return amounts


def _is_valid_tracking(code):
    if not code or len(code) < 5:
        return False
    if len(set(code)) == 1:
        return False
    if max(code.count(d) for d in set(code)) > len(code) * 0.6:
        return False
    return True


def _is_card_like(code):
    if not code:
        return False
    if len(code) == 16:
        return True
    if code.upper().startswith('IR') and len(code) >= 24:
        return True
    if len(code) == 8 and code.startswith('0'):
        return True
    return False


TRACKING_PATTERNS = [
    (r'شماره\s*[پیب]یگیری\s*[:：]?\s*(\d{5,25})', 100),
    (r'کد\s*[پیب]یگیری\s*[:：]?\s*(\d{5,25})', 100),
    (r'کد\s*رهگیری\s*[:：]?\s*(\d{5,25})', 100),
    (r'[پیب]یگیری\s*[:：]?\s*(\d{5,25})', 95),
    (r'شماره\s*سند\s*[:：]?\s*(\d{5,25})', 80),
    (r'سند\s*[:：]?\s*(\d{8,25})', 70),
    (r'شماره\s*ارجاع\s*[:：]?\s*(\d{5,25})', 50),
    (r'شماره\s*مرجع\s*[:：]?\s*(\d{5,25})', 40),
    (r'شماره\s*بازیابی\s*[:：]?\s*(\d{5,25})', 40),
    (r'شماره\s*پایانه\s*[:：]?\s*(\d{5,25})', 20),
]


def _extract_trackings_with_prio(text):
    results = []
    for pat, prio in TRACKING_PATTERNS:
        for m in re.finditer(pat, text):
            code = m.group(1)
            if _is_valid_tracking(code):
                results.append((code, prio))
    return results


def _cross_check_55_with_tesseract(easy_codes, tess_codes):
    corrections = {}
    for ec in easy_codes:
        pairs_55 = [i for i in range(len(ec) - 1)
                    if ec[i] == '5' and ec[i + 1] == '5']
        if not pairs_55:
            continue
        for tc in tess_codes:
            if len(tc) != len(ec):
                continue
            for pos in pairs_55:
                if pos < 1:
                    continue
                matches_before = sum(
                    1 for i in range(pos) if ec[i] == tc[i]
                )
                required = min(pos, 3)
                if matches_before < required:
                    continue
                if tc[pos] == '0':
                    corrections[ec] = ec[:pos] + '0' + ec[pos + 1:]
                    break
                elif tc[pos + 1] == '0':
                    corrections[ec] = ec[:pos + 1] + '0' + ec[pos + 2:]
                    break
            if ec in corrections:
                break
    return corrections


# ═══════════════════════════════════════════════════════════
# ⭐ UPDATED: _pick_best_tracking with 5→0 variants
# ═══════════════════════════════════════════════════════════

def _pick_best_tracking(easy_full, easy_crop, tess_full, tess_crop):
    # ⭐ اول variants رو از کد خام بساز، بعد repair
    easy_full_pre = []
    for c, p in easy_full:
        easy_full_pre.append((c, p))  # خام
        for v in _5_to_0_variants(c):
            if v != c:
                easy_full_pre.append((v, p - 5))

    easy_crop_pre = []
    for c, p in easy_crop:
        easy_crop_pre.append((c, p))
        for v in _5_to_0_variants(c):
            if v != c:
                easy_crop_pre.append((v, p - 5))

    all_tess_codes = [c for c, _ in tess_full] + [c for c, _ in tess_crop]

    corrections_full = _cross_check_55_with_tesseract(
        [c for c, _ in easy_full_pre], all_tess_codes
    )
    easy_full_fixed = [
        (corrections_full.get(c, c), p) for c, p in easy_full_pre
    ]

    corrections_crop = _cross_check_55_with_tesseract(
        [c for c, _ in easy_crop_pre], all_tess_codes
    )
    easy_crop_fixed = [
        (corrections_crop.get(c, c), p) for c, p in easy_crop_pre
    ]

    all_items = []
    for code, prio in easy_full_fixed:
        all_items.append((code, prio, 200))
    for code, prio in tess_full:
        all_items.append((code, prio, 80))
    for code, prio in easy_crop_fixed:
        all_items.append((code, prio, 40))
    for code, prio in tess_crop:
        all_items.append((code, prio, 0))

    # ⭐ NEW: اضافه کردن variant‌های 5→0
    base_items = list(all_items)
    for code, prio, boost in base_items:
        for variant in _5_to_0_variants(code):
            if variant != code:
                # boost کمتر چون مشتق شده
                all_items.append((variant, prio, boost - 20))

    if not all_items:
        return "", ""

    def _score(item):
        code, prio, boost = item
        if not _is_valid_tracking(code):
            return -1e9
        if _is_card_like(code):
            return -1e8
        s = prio * 5 + boost

        # طول مناسب
        if 10 <= len(code) <= 13:
            s += 40
        elif 5 <= len(code) <= 12:
            s += 30
        elif len(code) > 13:
            s -= 30  # ⭐ طول‌های >13 مشکوک
        else:
            s += 10

        # ⭐ NEW: کدهای 140x با طول > 12 = مشکوک
        if code.startswith('1405') and len(code) >= 13:
            s -= 200  # penalty سنگین
        elif code.startswith('140') and len(code) >= 13:
            s -= 100

        s += min(len(code), 12) * 2
        return s
    best = max(all_items, key=_score)
    best_code = best[0]

    if any(c == best_code for c, _ in easy_full_fixed):
        source = "easy_full"
    elif any(c == best_code for c, _ in tess_full):
        source = "tess_full"
    elif any(c == best_code for c, _ in easy_crop_fixed):
        source = "easy_crop"
    elif any(c == best_code for c, _ in tess_crop):
        source = "tess_crop"
    else:
        source = "5to0_variant"

    return best_code, source


def _extract_dates_from_text(text):
    dates = []
    for m in re.finditer(r'(\d{4})[/\-](\d{1,3})[/\-](\d{1,3})', text):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1300 <= y <= 1500:
            mo = _repair_date_month(mo)
            d = _repair_date_day(d)
            if 1 <= mo <= 12 and 1 <= d <= 31:
                dates.append(f"{y}/{mo:02d}/{d:02d}")
    for m in re.finditer(
            r'\b(\d{1,2})\s*[/]\s*(\d{4})\s*[/]\s*(\d{1,2})\b', text
    ):
        d, y, mo = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1300 <= y <= 1500:
            mo = _repair_date_month(mo)
            d = _repair_date_day(d)
            if 1 <= mo <= 12 and 1 <= d <= 31:
                dates.append(f"{y}/{mo:02d}/{d:02d}")
    pd = _find_persian_month_date(text)
    if pd:
        dates.append(pd)
    return dates


def _date_score(d):
    if not d:
        return -1
    try:
        y = int(d[:4])
        m = int(d[5:7])
        day = int(d[8:10])
    except Exception:
        return -1
    score = 0
    if 1400 <= y <= 1410:
        score += 200
    elif 1390 <= y <= 1420:
        score += 100
    if 1 <= m <= 12:
        score += 20
    if 1 <= day <= 31:
        score += 20
    return score


def parse_receipt_text(text):
    result = {
        "success": False, "tracking_code": "", "amount_rial": 0,
        "amount_toman": 0, "date": "", "raw_text": text or "",
    }
    if not text or len(str(text).strip()) < 10:
        return result
    t = normalize_text(text)
    trks = _extract_trackings_with_prio(t)
    if trks:
        code, _ = _pick_best_tracking(trks, [], [], [])
        result["tracking_code"] = _repair_tracking(code)
    amts = _extract_amounts_from_text(t)
    if not amts:
        amts = _collect_scattered_amounts(t)
    if amts:
        result["amount_rial"] = _smart_amount_from_sources(amts)
        result["amount_toman"] = result["amount_rial"] // 10
    dts = _extract_dates_from_text(t)
    if dts:
        repaired = [_repair_year(d) for d in dts]
        best = max(repaired, key=_date_score)
        result["date"] = best
    result["success"] = bool(
        result["amount_rial"] or result["tracking_code"] or result["date"]
    )
    return result


TRACKING_LABELS = [
    ('پیگیری', 100), ('بیگیری', 100), ('پیگیر', 95),
    ('کد پیگیری', 100), ('کد رهگیری', 100),
    ('سند', 80), ('مرجع', 40), ('بازیابی', 40), ('ارجاع', 50),
]

DATE_LABELS = ['تاریخ', 'زمان', 'تاريخ', 'تاریخ و زمان']


def parse_receipt(image_path, debug=False):
    result = {
        "success": False, "tracking_code": "", "amount_rial": 0,
        "amount_toman": 0, "date": "", "raw_text": "", "error": "",
        "source_amount": "", "source_tracking": "", "source_date": "",
    }
    if not image_path or not os.path.exists(image_path):
        result["error"] = "فایل تصویر پیدا نشد."
        return result

    raw_boxes = _easyocr_raw(image_path)
    easy_text = _boxes_to_text(raw_boxes)
    result["raw_text"] = easy_text

    easy_norm = normalize_text(easy_text)
    easy_amts = _extract_amounts_from_text(easy_norm)
    if not easy_amts:
        easy_amts = _collect_scattered_amounts(easy_norm)
    easy_trks_full = _extract_trackings_with_prio(easy_norm)
    easy_dates = _extract_dates_from_text(easy_norm)

    if debug:
        print(f"\n📊 EasyOCR full: trk={easy_trks_full}")
        print(f"   amt={easy_amts} dt={easy_dates}")

    tess_text = _tesseract_full_text(image_path, debug=False)
    tess_fixed = _fix_chars(tess_text)
    tess_fixed = _strip_spaces_in_numbers(tess_fixed)
    tess_norm = normalize_text(tess_fixed)
    tess_amts = _extract_amounts_from_text(tess_norm)
    if not tess_amts:
        tess_amts = _collect_scattered_amounts(tess_norm)
    tess_trks_full = _extract_trackings_with_prio(tess_norm)
    tess_dates = _extract_dates_from_text(tess_norm)

    if debug:
        print(f"📊 Tesseract full: trk={tess_trks_full}")
        print(f"   amt={tess_amts} dt={tess_dates}")

    easy_trks_crop = []
    tess_trks_crop = []

    for bbox, text, conf in raw_boxes:
        if 'مبلغ' in text and 'کارمزد' not in text:
            for crop_result in [
                _crop_left_of_label(image_path, bbox),
                _crop_above_label(image_path, bbox),
            ]:
                for th, psm, txt in crop_result:
                    c = _fix_chars(txt)
                    c = _strip_spaces_in_numbers(c)
                    for m in re.finditer(r'\d[\d,\.]{3,}', c):
                        v = int(re.sub(r'[^\d]', '', m.group(0)) or 0)
                        if (100_000 <= v <= _max_reasonable_amount()
                                and not _is_year_like(v)):
                            tess_amts.append(v)
            break

    for bbox, text, conf in raw_boxes:
        for label, prio in TRACKING_LABELS:
            if label in text:
                for crop_result in [
                    _crop_left_of_label(image_path, bbox),
                    _crop_above_label(image_path, bbox),
                ]:
                    for th, psm, txt in crop_result:
                        c = _fix_chars(txt)
                        c = _strip_spaces_in_numbers(c)
                        for m in re.finditer(r'\d{5,25}', c):
                            code = m.group(0)
                            if _is_valid_tracking(code):
                                tess_trks_crop.append((code, prio))
                easy_crop = _easyocr_crop_digits(
                    image_path, bbox, tag="پیگیری"
                )
                if easy_crop:
                    c = _strip_spaces_in_numbers(easy_crop)
                    for m in re.finditer(r'\d{5,25}', c):
                        code = m.group(0)
                        if _is_valid_tracking(code):
                            easy_trks_crop.append((code, prio))
                break

    for bbox, text, conf in raw_boxes:
        if any(lbl in text for lbl in DATE_LABELS):
            for crop_result in [
                _crop_left_of_label(image_path, bbox),
                _crop_above_label(image_path, bbox),
            ]:
                for th, psm, txt in crop_result:
                    c = _fix_chars(txt)
                    c = _strip_spaces_in_numbers(c)
                    for d in _extract_dates_from_text(c):
                        tess_dates.append(d)
            easy_crop = _easyocr_crop_digits(
                image_path, bbox, tag="تاریخ"
            )
            if easy_crop:
                c = _strip_spaces_in_numbers(easy_crop)
                for d in _extract_dates_from_text(c):
                    tess_dates.append(d)
            break

    all_amts = list(easy_amts) + list(tess_amts)
    best = _smart_amount_from_sources(all_amts)
    if best > 0:
        result["amount_rial"] = best
        result["amount_toman"] = best // 10
        if best in easy_amts and best in tess_amts:
            result["source_amount"] = "both"
        elif best in tess_amts:
            result["source_amount"] = "tesseract"
        else:
            result["source_amount"] = "easyocr"

    best_code, best_source = _pick_best_tracking(
        easy_trks_full, easy_trks_crop,
        tess_trks_full, tess_trks_crop,
    )
    if best_code:
        repaired = _repair_tracking(best_code)
        result["tracking_code"] = repaired
        result["source_tracking"] = best_source or ""

    easy_dates_rep = [_repair_year(d) for d in easy_dates]
    tess_dates_rep = [_repair_year(d) for d in tess_dates]
    all_dates = list(set(easy_dates_rep + tess_dates_rep))
    if all_dates:
        def _date_rank(d):
            return (_date_score(d), 1 if d in easy_dates_rep else 0)

        best_date = max(all_dates, key=_date_rank)
        result["date"] = best_date
        if (best_date in tess_dates_rep
                and best_date in easy_dates_rep):
            result["source_date"] = "both"
        elif best_date in easy_dates_rep:
            result["source_date"] = "easyocr"
        else:
            result["source_date"] = "tesseract"

    if not result["date"]:
        combined = easy_norm + "\n" + tess_norm
        fallback = _find_persian_month_day_fallback(combined)
        if fallback:
            result["date"] = fallback
            result["source_date"] = "fallback"

    result["success"] = bool(
        result["amount_rial"] or result["tracking_code"] or result["date"]
    )
    if not result["success"]:
        result["error"] = "اطلاعات استخراج نشد."
    return result


if __name__ == "__main__":
    import glob

    print("=" * 60)
    print("🧪 receipt_parser (Universal v31.1)")
    print("=" * 60)

    RECEIPTS_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "simplerec",
    )

    IMAGE_PATHS = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp",
                "*.JPG", "*.JPEG", "*.PNG"):
        IMAGE_PATHS.extend(glob.glob(os.path.join(RECEIPTS_DIR, ext)))
    IMAGE_PATHS = sorted(set(IMAGE_PATHS))

    print(f"\n📁 پوشه: {RECEIPTS_DIR}")
    print(f"✅ {len(IMAGE_PATHS)} عکس")

    summary = []

    for idx, IMAGE_PATH in enumerate(IMAGE_PATHS, 1):
        print("\n" + "═" * 60)
        print(f"🖼️  {idx}/{len(IMAGE_PATHS)}: {os.path.basename(IMAGE_PATH)}")
        print("═" * 60)

        try:
            result = parse_receipt(IMAGE_PATH, debug=(idx == 15))
        except Exception as ex:
            print(f"❌ خطای کلی: {ex}")
            continue

        print(f"  ✅ موفق: {result['success']}")
        print(f"  📌 پیگیری: {result['tracking_code'] or '-'}  "
              f"({result['source_tracking']})")
        if result['amount_rial']:
            print(f"  💰 ریال: {result['amount_rial']:,}  "
                  f"({result['source_amount']})")
        else:
            print(f"  💰 مبلغ: -")
        print(f"  📅 تاریخ: {result['date'] or '-'}  "
              f"({result['source_date']})")

        summary.append({
            "file": os.path.basename(IMAGE_PATH),
            "success": result['success'],
            "tracking": result['tracking_code'],
            "amount": result['amount_rial'],
            "date": result['date'],
        })

    print("\n\n" + "=" * 60)
    print("📊 خلاصه نهایی")
    print("=" * 60)

    complete = 0
    partial = 0
    failed = 0

    for s in summary:
        has_all = s["tracking"] and s["amount"] and s["date"]
        has_any = s["tracking"] or s["amount"] or s["date"]

        if has_all:
            marker = "✅"
            complete += 1
        elif has_any:
            marker = "⚠️"
            partial += 1
        else:
            marker = "❌"
            failed += 1

        amt_str = f"{s['amount']:,}" if s['amount'] else "-"
        print(f"  {marker} {s['file'][:45]}")
        print(f"     trk: {s['tracking'] or '-'} | "
              f"amt: {amt_str} | "
              f"dt: {s['date'] or '-'}")

    print(f"\n  ✅ کامل: {complete}/{len(summary)}")
    print(f"  ⚠️ نصفه: {partial}/{len(summary)}")
    print(f"  ❌ خرابی: {failed}/{len(summary)}")

    print("\n" + "=" * 60)
    print("🏁 پایان")
    print("=" * 60)