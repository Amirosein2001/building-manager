# Copyright (c) 2026 AmirEP
# All Rights Reserved.
# This source code is the confidential and proprietary information of AmirEP.
# Unauthorized copying of this file, via any medium, is strictly prohibited.

"""
سیستم System Tray برای مدیریت ساختمان
با پشتیبانی از آیکون پویا و مینیمایز به تسک‌بار
"""

import os
import threading
import time
import flet as ft

# ─── ایمپورت مستقل PIL ───
try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️ Pillow نصب نیست. آیکون Tray کار نخواهد کرد.")

# ─── ایمپورت مستقل pystray ───
try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False
    print("⚠️ pystray نصب نیست. System Tray غیرفعال است.")


class SystemTrayManager:
    """مدیریت آیکون تسک‌بار (System Tray) با پشتیبانی از آیکون پویا"""

    def __init__(self, page, app_name="مدیریت ساختمان"):
        self.page = page
        self.app_name = app_name
        self.icon = None
        self.running = False
        self.thread = None
        self.current_icon_path = None
        self.default_icon = None

        # ─── فقط اگه PIL در دسترس بود آیکون پیش‌فرض رو بساز ───
        if HAS_PIL:
            self._create_default_icon()
        else:
            print("⚠️ PIL موجود نیست. Tray غیرفعال می‌مونه.")
            # یه تصویر ساده خالی نداریم، پس نمیشه ادامه داد

    def _create_default_icon(self):
        """ساخت یک آیکون پیش‌فرض (در صورت نبود لوگو)"""
        if not HAS_PIL:
            return None

        try:
            size = 64
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # یک خانه ساده
            color = (21, 101, 192, 255)  # آبی
            draw.rectangle(
                [10, 25, 54, 55],
                fill=color, outline=(255, 255, 255, 255)
            )
            draw.polygon(
                [5, 25, 32, 10, 59, 25],
                fill=color, outline=(255, 255, 255, 255)
            )
            self.default_icon = img
            return img
        except Exception:
            try:
                img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.ellipse([8, 8, 56, 56], fill=(21, 101, 192, 255))
                self.default_icon = img
                return img
            except Exception:
                self.default_icon = None
                return None

    def _get_icon_image(self, image_path=None):
        """گرفتن تصویر آیکون از مسیر داده شده یا لوگوی پیش‌فرض"""
        if not HAS_PIL:
            return None

        if image_path and os.path.exists(image_path):
            try:
                return Image.open(image_path)
            except Exception as ex:
                print(f"⚠️ خطا در بارگذاری آیکون: {ex}")
        # اگر لوگو وجود نداشت، از پیش‌فرض استفاده کن
        return self.default_icon

    def _create_tray_icon(self, icon_path=None):
        """ساخت آیکون System Tray با منوی راست‌کلیک"""
        if not HAS_PYSTRAY or not HAS_PIL:
            return None

        image = self._get_icon_image(icon_path)
        if image is None:
            print("⚠️ تصویری برای آیکون Tray موجود نیست")
            return None

        def on_show(e):
            """نمایش پنجره برنامه"""
            if self.page:
                async def _do_show():
                    try:
                        self.page.window.visible = True
                        self.page.window.minimized = False
                        self.page.update()
                    except Exception as ex:
                        print(f"⚠️ خطا در نمایش پنجره: {ex}")
                try:
                    self.page.run_task(_do_show)
                except Exception as ex:
                    print(f"⚠️ خطا در زمان‌بندی نمایش پنجره: {ex}")

        def on_hide(e):
            """پنهان کردن پنجره (مینیمایز به Tray)"""
            if self.page:
                async def _do_hide():
                    try:
                        self.page.window.minimized = True
                        self.page.window.visible = False
                        self.page.update()
                    except Exception as ex:
                        print(f"⚠️ خطا در پنهان کردن پنجره: {ex}")
                try:
                    self.page.run_task(_do_hide)
                except Exception as ex:
                    print(f"⚠️ خطا در زمان‌بندی پنهان کردن پنجره: {ex}")

        def on_quit(e):
            """خروج کامل از برنامه"""
            print("🚪 درخواست خروج از منوی Tray دریافت شد")
            self.running = False

            if self.page:
                async def _do_close():
                    try:
                        self.page.window.visible = True
                        await self.page.window.destroy()
                    except Exception:
                        pass
                try:
                    self.page.run_task(_do_close)
                except Exception:
                    pass

            time.sleep(0.6)
            os._exit(0)

        # منوی کلیک راست
        menu = pystray.Menu(
            pystray.MenuItem("🪟 نمایش برنامه", on_show),
            pystray.MenuItem("📥 پنهان کردن", on_hide),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚪 خروج", on_quit),
        )

        # ساخت آیکون
        icon = pystray.Icon(
            self.app_name,
            image,
            self.app_name,
            menu,
        )
        return icon

    def start(self, icon_path=None):
        """شروع System Tray در یک ترد جداگانه"""
        if self.running:
            return

        if not HAS_PYSTRAY:
            print("⚠️ pystray نصب نیست. System Tray فعال نیست.")
            return

        if not HAS_PIL:
            print("⚠️ PIL نصب نیست. System Tray فعال نیست.")
            return

        self.current_icon_path = icon_path
        self.icon = self._create_tray_icon(icon_path)
        if not self.icon:
            return

        self.running = True

        def run_icon():
            try:
                self.icon.run()
            except Exception as ex:
                print(f"❌ خطای System Tray: {ex}")
            finally:
                self.running = False

        self.thread = threading.Thread(
            target=run_icon,
            daemon=True,
        )
        self.thread.start()
        print("✅ System Tray فعال شد")

    def stop(self):
        """توقف System Tray"""
        self.running = False
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
        print("❌ System Tray غیرفعال شد")

    def minimize_to_tray(self):
        """مینیمایز کردن پنجره به Tray (پنهان کردن)"""
        if self.icon and self.running:
            try:
                self.page.window.visible = False
                self.page.update()
                return True
            except Exception as ex:
                print(f"⚠️ خطا در مینیمایز به Tray: {ex}")
        # اگر Tray فعال نبود، مینیمایز معمولی
        try:
            self.page.window.minimized = True
            self.page.update()
            return True
        except Exception as ex:
            print(f"⚠️ خطا در مینیمایز معمولی: {ex}")
        return False

    def update_icon(self, image_path):
        """بروزرسانی آیکون Tray بدون نیاز به ری‌استارت"""
        if not self.running or not self.icon:
            print("⚠️ Tray در حال اجرا نیست یا آیکون وجود ندارد")
            return False

        if not HAS_PIL:
            print("⚠️ PIL نصب نیست")
            return False

        if not os.path.exists(image_path):
            print(f"⚠️ فایل تصویر وجود ندارد: {image_path}")
            return False

        try:
            new_image = Image.open(image_path)
            self.icon.icon = new_image
            self.icon.update_menu()
            self.current_icon_path = image_path
            print(f"✅ آیکون Tray به‌روز شد: {image_path}")
            return True
        except Exception as ex:
            print(f"❌ خطا در بروزرسانی آیکون Tray: {ex}")
            return False

    def is_running(self):
        """بررسی اینکه آیا Tray در حال اجراست"""
        return self.running

    def get_icon_path(self):
        """گرفتن مسیر آیکون فعلی"""
        return self.current_icon_path