import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QWidget, QLabel, 
                             QMessageBox, QHBoxLayout, QTabWidget, QLineEdit, 
                             QHeaderView, QStatusBar, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class FlatpakWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            # Komutu çalıştır ve çıktıyı al
            result = subprocess.check_output(self.command, text=True, stderr=subprocess.STDOUT)
            self.finished.emit(result.strip().split('\n'))
        except subprocess.CalledProcessError as e:
            self.error.emit(e.output)
        except Exception as e:
            self.error.emit(str(e))

class DebianFlatpakManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flatpak Paket Yöneticisi")
        self.resize(1000, 650)

        # Ana Widget yapısı
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Sekme yapısı
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Durum çubuğu
        self.setStatusBar(QStatusBar())

        # Sekmeleri Başlat
        self.init_installed_tab()
        self.init_search_tab()

        # İlk açılışta yüklüleri getir
        self.refresh_installed()

    def create_styled_table(self, headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def init_installed_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.inst_table = self.create_styled_table(["Uygulama Adı", "Uygulama ID", "Sürüm", "Boyut"])
        
        # Butonlar
        controls = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Yenile")
        update_btn = QPushButton("🚀 Tümünü Güncelle")
        backup_btn = QPushButton("📦 Veri Yedekle")
        remove_btn = QPushButton("🗑️ Kaldır")
        purge_btn = QPushButton("🔥 Tamamen Sil")
        
        # Stil ayarları
        purge_btn.setStyleSheet("color: #cc0000; font-weight: bold;")
        backup_btn.setStyleSheet("color: #2e7d32; font-weight: bold;")

        # Bağlantılar
        refresh_btn.clicked.connect(self.refresh_installed)
        update_btn.clicked.connect(self.update_all_apps)
        backup_btn.clicked.connect(self.backup_app_data)
        remove_btn.clicked.connect(lambda: self.remove_app(purge=False))
        purge_btn.clicked.connect(lambda: self.remove_app(purge=True))
        
        controls.addWidget(refresh_btn)
        controls.addWidget(update_btn)
        controls.addWidget(backup_btn)
        controls.addStretch()
        controls.addWidget(remove_btn)
        controls.addWidget(purge_btn)
        
        layout.addWidget(self.inst_table)
        layout.addLayout(controls)
        self.tabs.addTab(tab, "Yüklü Uygulamalar")

    def init_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Uygulama adı yazın ve Enter'a basın...")
        self.search_input.returnPressed.connect(self.search_apps)
        
        search_btn = QPushButton("🔍 Mağazada Ara")
        search_btn.clicked.connect(self.search_apps)
        
        search_bar.addWidget(self.search_input)
        search_bar.addWidget(search_btn)
        
        self.search_table = self.create_styled_table(["Uygulama", "ID", "Açıklama"])
        
        install_btn = QPushButton("📥 Seçilen Uygulamayı Kur")
        install_btn.clicked.connect(self.install_app)
        
        layout.addLayout(search_bar)
        layout.addWidget(self.search_table)
        layout.addWidget(install_btn)
        self.tabs.addTab(tab, "Yeni Uygulama Kur")

    # --- MANTIK VE İŞLEMLER ---

    def refresh_installed(self):
        self.statusBar().showMessage("Yüklü paketler listeleniyor...")
        cmd = ["flatpak", "list", "--app", "--columns=name,application,version,size"]
        self.run_worker(cmd, self.fill_installed)

    def fill_installed(self, data):
        self.inst_table.setRowCount(0)
        for line in data:
            if not line: continue
            row = self.inst_table.rowCount()
            self.inst_table.insertRow(row)
            for i, text in enumerate(line.split('\t')):
                if i < 4:
                    self.inst_table.setItem(row, i, QTableWidgetItem(text))
        self.statusBar().showMessage(f"{len(data)} paket bulundu.", 3000)

    def update_all_apps(self):
        self.execute_action(["flatpak", "update", "-y"], "Tüm uygulamalar güncelleniyor...")

    def remove_app(self, purge=False):
        row = self.inst_table.currentRow()
        if row < 0: return
        app_id = self.inst_table.item(row, 1).text()
        
        msg = f"{app_id} kaldırılsın mı?"
        if purge:
            msg = f"DİKKAT: {app_id} ve tüm kullanıcı verileri tamamen silinecek! Onaylıyor musunuz?"
            
        if QMessageBox.question(self, "Onay", msg) == QMessageBox.StandardButton.Yes:
            cmd = ["flatpak", "uninstall", "-y"]
            if purge: cmd.append("--delete-data")
            cmd.append(app_id)
            self.execute_action(cmd, f"{app_id} kaldırılıyor...")

    def backup_app_data(self):
        row = self.inst_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen yedeklemek için bir uygulama seçin.")
            return

        app_id = self.inst_table.item(row, 1).text()
        home = os.path.expanduser("~")
        source_dir = os.path.join(home, ".var/app", app_id)

        if not os.path.exists(source_dir):
            QMessageBox.warning(self, "Hata", "Bu uygulamaya ait bir veri klasörü bulunamadı.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Yedeği Kaydet", 
                                                 f"{home}/{app_id}_data_backup.tar.gz", 
                                                 "Arşiv Dosyası (*.tar.gz)")
        if save_path:
            # tar -czf [hedef] -C [dizin] [klasör]
            cmd = ["tar", "-czf", save_path, "-C", os.path.join(home, ".var/app"), app_id]
            self.execute_action(cmd, f"{app_id} verileri yedekleniyor...")

    def search_apps(self):
        query = self.search_input.text().strip()
        if not query: return
        self.statusBar().showMessage(f"'{query}' aranıyor...")
        cmd = ["flatpak", "search", "--columns=name,application,description", query]
        self.run_worker(cmd, self.fill_search)

    def fill_search(self, data):
        self.search_table.setRowCount(0)
        for line in data:
            if not line or "No results" in line: continue
            row = self.search_table.rowCount()
            self.search_table.insertRow(row)
            for i, text in enumerate(line.split('\t')[:3]):
                self.search_table.setItem(row, i, QTableWidgetItem(text))
        self.statusBar().showMessage("Arama sonuçları listelendi.", 3000)

    def install_app(self):
        row = self.search_table.currentRow()
        if row < 0: return
        app_id = self.search_table.item(row, 1).text()
        self.execute_action(["flatpak", "install", "-y", "flathub", app_id], f"{app_id} kuruluyor...")

    def run_worker(self, cmd, callback):
        self.worker = FlatpakWorker(cmd)
        self.worker.finished.connect(callback)
        self.worker.error.connect(lambda e: QMessageBox.warning(self, "Hata", e))
        self.worker.start()

    def execute_action(self, cmd, msg):
        self.statusBar().showMessage(msg)
        self.action_worker = FlatpakWorker(cmd)
        self.action_worker.finished.connect(lambda: [self.refresh_installed(), 
                                                   self.statusBar().showMessage("İşlem Başarılı", 5000),
                                                   QMessageBox.information(self, "Bilgi", "İşlem başarıyla tamamlandı.")])
        self.action_worker.error.connect(lambda e: QMessageBox.critical(self, "Hata", e))
        self.action_worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebianFlatpakManager()
    window.show()
    sys.exit(app.exec())