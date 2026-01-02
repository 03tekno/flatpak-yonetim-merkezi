import gi
import subprocess
import threading
import os
import shutil
from datetime import datetime

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio

class FlatpakPro(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.debian.flatpak_pro_final')
        self.home = os.path.expanduser("~")
        
    def do_activate(self):
        self.win = Adw.ApplicationWindow(application=self)
        self.win.set_title("Flatpak Yönetim Merkezi")
        self.win.set_default_size(550, 800)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.win.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        clamp = Adw.Clamp()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(clamp)
        main_box.append(scrolled)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        # Debian 13 uyumlu marjinler
        box.set_margin_top(20); box.set_margin_bottom(20)
        box.set_margin_start(20); box.set_margin_end(20)
        clamp.set_child(box)

        # --- 1. UYGULAMA KARTI ---
        card_group = Adw.PreferencesGroup(title="Seçili Uygulama")
        self.app_card = Adw.ActionRow(title="Seçim Yapın", subtitle="Boyut: -")
        self.app_icon = Gtk.Image(pixel_size=64)
        self.app_icon.set_from_icon_name("package-x-generic-symbolic")
        self.app_card.add_prefix(self.app_icon)
        card_group.add(self.app_card)
        box.append(card_group)

        # --- 2. LİSTE VE GİRİŞ ---
        list_group = Adw.PreferencesGroup(title="Yönetim", description="Kurulu olanlardan seçin veya yeni ID yazın")
        self.dropdown = Gtk.DropDown(enable_search=True)
        self.dropdown.connect("notify::selected-item", self.on_app_selected)
        list_group.add(self.dropdown)
        
        self.entry = Gtk.Entry(placeholder_text="Manuel ID Girişi (Örn: org.gimp.GIMP)")
        self.entry.set_margin_top(8)
        list_group.add(self.entry)
        box.append(list_group)

        # --- 3. ANA İŞLEMLER ---
        actions_group = Adw.PreferencesGroup(title="Uygulama İşlemleri")
        grid = Gtk.Grid(column_spacing=10, row_spacing=10, column_homogeneous=True)
        grid.attach(self.create_btn("Kur", "suggested-action", "install -y flathub"), 0, 0, 1, 1)
        grid.attach(self.create_btn("Güncelle", "", "update -y"), 1, 0, 1, 1)
        grid.attach(self.create_btn("Kaldır", "", "uninstall -y"), 0, 1, 1, 1)
        grid.attach(self.create_btn("Tamamen Sil", "destructive-action", "uninstall --delete-data -y"), 1, 1, 1, 1)
        actions_group.add(grid)
        box.append(actions_group)

        # --- 4. YEDEKLEME VE GERİ YÜKLEME ---
        backup_group = Adw.PreferencesGroup(title="Veri Yedekleme", description="Uygulama ayarlarını ve verilerini koruyun")
        b_grid = Gtk.Grid(column_spacing=10, row_spacing=10, column_homogeneous=True)
        
        btn_backup = Gtk.Button(label="Ayarları Yedekle")
        btn_backup.connect("clicked", self.backup_data)
        b_grid.attach(btn_backup, 0, 0, 1, 1)

        btn_restore = Gtk.Button(label="Yedeği Geri Yükle")
        btn_restore.connect("clicked", self.restore_data)
        b_grid.attach(btn_restore, 1, 0, 1, 1)
        
        backup_group.add(b_grid)
        box.append(backup_group)

        # --- 5. SİSTEM BAKIMI ---
        maint_group = Adw.PreferencesGroup(title="Sistem")
        super_btn = Gtk.Button(label="Süper Temizlik ve Onarım")
        super_btn.add_css_class("pill")
        super_btn.connect("clicked", self.run_cmd, "update -y && flatpak uninstall --unused -y && flatpak repair", True)
        maint_group.add(super_btn)
        box.append(maint_group)

        self.status_label = Gtk.Label(label="Hazır.")
        self.status_label.add_css_class("caption")
        box.append(self.status_label)

        self.app_data = {}
        self.refresh_installed_apps()
        self.win.present()

    def create_btn(self, label, css, cmd):
        btn = Gtk.Button(label=label)
        if css: btn.add_css_class(css)
        btn.add_css_class("pill")
        btn.connect("clicked", self.run_cmd, cmd)
        return btn

    def refresh_installed_apps(self):
        def fetch():
            res = subprocess.run(["flatpak", "list", "--app", "--columns=application,size"], capture_output=True, text=True)
            lines = res.stdout.strip().split('\n')
            self.app_data = {l.split("\t")[0]: l.split("\t")[1] for l in lines if "\t" in l}
            GLib.idle_add(self.update_ui_list)
        threading.Thread(target=fetch).start()

    def update_ui_list(self):
        self.dropdown.set_model(Gtk.StringList.new(sorted(self.app_data.keys())))
        self.status_label.set_text(f"Toplam {len(self.app_data)} uygulama kurulu.")

    def on_app_selected(self, dropdown, pspec):
        selected = dropdown.get_selected_item()
        if selected:
            appid = selected.get_string()
            self.entry.set_text(appid)
            self.app_card.set_title(appid)
            self.app_card.set_subtitle(f"Kurulu Boyut: {self.app_data.get(appid, '-')}")
            self.app_icon.set_from_icon_name(appid)

    def backup_data(self, btn):
        appid = self.entry.get_text().strip()
        source = os.path.join(self.home, ".var/app", appid)
        if not os.path.exists(source):
            self.status_label.set_text("❌ Hata: Uygulama veri klasörü bulunamadı!")
            return
        
        backup_path = os.path.join(self.home, "Desktop", f"{appid}_backup_{datetime.now().strftime('%Y%m%d')}.tar.gz")
        self.status_label.set_text("📦 Yedekleniyor...")
        
        def run():
            res = subprocess.run(["tar", "-czf", backup_path, "-C", os.path.dirname(source), appid])
            msg = f"✅ Yedek Masaüstüne kaydedildi: {appid}" if res.returncode == 0 else "❌ Yedekleme başarısız!"
            GLib.idle_add(self.status_label.set_text, msg)
        threading.Thread(target=run).start()

    def restore_data(self, btn):
        self.status_label.set_text("ℹ️ Masaüstündeki en güncel yedek aranıyor...")
        appid = self.entry.get_text().strip()
        # Basit geri yükleme mantığı: Masaüstündeki ilgili tar.gz'yi bul ve aç
        backup_file = None
        for f in os.listdir(os.path.join(self.home, "Desktop")):
            if f.startswith(appid) and f.endswith(".tar.gz"):
                backup_file = os.path.join(self.home, "Desktop", f)
                break
        
        if not backup_file:
            self.status_label.set_text("❌ Hata: Masaüstünde yedek dosyası bulunamadı!")
            return

        def run():
            res = subprocess.run(["tar", "-xzf", backup_file, "-C", os.path.join(self.home, ".var/app")])
            msg = "✅ Ayarlar geri yüklendi!" if res.returncode == 0 else "❌ Geri yükleme hatası!"
            GLib.idle_add(self.status_label.set_text, msg)
        threading.Thread(target=run).start()

    def run_cmd(self, button, action, is_complex=False):
        app_id = self.entry.get_text().strip()
        if not app_id and not is_complex: return
        cmd = f"flatpak {action}" if is_complex else f"flatpak {action} {app_id}"
        button.set_sensitive(False)
        self.status_label.set_text("İşlem yapılıyor...")
        
        def execute():
            res = subprocess.run(cmd, shell=True)
            GLib.idle_add(lambda: (button.set_sensitive(True), self.status_label.set_text("✅ Tamamlandı"), self.refresh_installed_apps()))
        threading.Thread(target=execute).start()

if __name__ == "__main__":
    app = FlatpakPro()
    app.run(None)