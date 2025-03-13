import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QComboBox, 
                           QProgressBar, QFileDialog, QTabWidget, 
                           QListWidget, QListWidgetItem, QMessageBox,
                           QCheckBox, QGroupBox, QRadioButton, QButtonGroup,
                           QApplication, QFrame)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette

class YouTubeDownloaderUI(QMainWindow):
    """Main UI class for YouTube Downloader application"""
    
    def __init__(self, backend):
        super().__init__()
        
        self.backend = backend
        self.init_ui()
        
        # Connect signals from backend
        self.backend.signals.progress.connect(self.update_progress)
        self.backend.signals.status.connect(self.update_status)
        self.backend.signals.finished.connect(self.download_finished)
        self.backend.signals.error.connect(self.show_error)
        self.backend.signals.playlist_progress.connect(self.update_playlist_progress)
        
        # Temel karanlık tema uygula
        self.set_basic_theme()
    
    def set_basic_theme(self):
        """Temel karanlık tema uygular"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        # Karanlık tema için temel renkler
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        app.setPalette(dark_palette)
    
    def init_ui(self):
        """Ana arayüzü başlatır"""
        # Temel pencere ayarları
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(800, 600)
        
        # Ana widget ve layout oluşturma
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Başlık ekle
        title_label = QLabel("YouTube Downloader")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Versiyon etiketi
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("font-size: 12px;")
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label)
        header_layout.addWidget(version_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Yatay ayraç
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # Sekme widgeti oluştur
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # İndirme sekmesi
        download_tab = QWidget()
        download_layout = QVBoxLayout(download_tab)
        download_layout.setContentsMargins(10, 10, 10, 10)
        download_layout.setSpacing(10)
        
        # URL girişi
        url_label = QLabel("YouTube URL")
        url_label.setStyleSheet("font-weight: bold;")
        download_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube video or playlist URL")
        download_layout.addWidget(self.url_input)
        
        # Ayraç
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        download_layout.addWidget(separator2)
        
        # İndirme seçenekleri
        options_label = QLabel("Download Options")
        options_label.setStyleSheet("font-weight: bold;")
        download_layout.addWidget(options_label)
        
        # Seçenekler düzeni
        options_layout = QHBoxLayout()
        
        # Medya türü seçimi
        media_group = QGroupBox("Media Type")
        media_layout = QVBoxLayout(media_group)
        
        self.video_radio = QRadioButton("Video")
        self.audio_radio = QRadioButton("Audio")
        self.video_radio.setChecked(True)
        
        media_layout.addWidget(self.video_radio)
        media_layout.addWidget(self.audio_radio)
        options_layout.addWidget(media_group)
        
        # Kalite seçimi
        quality_group = QGroupBox("Quality")
        quality_layout = QVBoxLayout(quality_group)
        
        self.quality_combo = QComboBox()
        
        # Video kaliteleri
        self.video_qualities = ["Best Quality", "1080p", "720p", "480p", "360p", "240p"]
        # Ses kaliteleri
        self.audio_qualities = ["320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps"]
        
        # Varsayılan olarak video kalitelerini ayarla
        self.quality_combo.addItems(self.video_qualities)
        
        quality_layout.addWidget(self.quality_combo)
        options_layout.addWidget(quality_group)
        
        # Ek seçenekler
        add_options_group = QGroupBox("Additional Options")
        add_options_layout = QVBoxLayout(add_options_group)
        
        # Oynatma listesi seçeneği
        self.playlist_check = QCheckBox("Download as playlist")
        add_options_layout.addWidget(self.playlist_check)
        
        options_layout.addWidget(add_options_group)
        download_layout.addLayout(options_layout)
        
        # Çıktı dizini
        location_label = QLabel("Save Location")
        location_label.setStyleSheet("font-weight: bold;")
        download_layout.addWidget(location_label)
        
        dir_layout = QHBoxLayout()
        
        self.dir_input = QLineEdit()
        self.dir_input.setText(self.backend.download_directory)
        self.dir_input.setReadOnly(True)
        
        dir_button = QPushButton("Browse")
        dir_button.clicked.connect(self.select_directory)
        
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        download_layout.addLayout(dir_layout)
        
        # Ayraç
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        download_layout.addWidget(separator3)
        
        # İndirme butonu
        self.download_button = QPushButton("DOWNLOAD")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setMinimumHeight(40)
        download_layout.addWidget(self.download_button)
        
        # İlerleme bölümü
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # Durum etiketi
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        # Oynatma listesi ilerleme durumu
        self.playlist_status = QLabel("")
        self.playlist_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.playlist_status)
        
        download_layout.addWidget(progress_group)
        
        # Boşluğu yukarı it
        download_layout.addStretch()
        
        # İndirme sekmesini ekle
        tab_widget.addTab(download_tab, "Download")
        
        # Hakkında sekmesi
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(10, 10, 10, 10)
        about_layout.setSpacing(10)
        about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Uygulama logosu
        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap(os.path.join("assets", "icon.ico")).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        except:
            logo_label.setText("YT")
            logo_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(logo_label)
        
        # Uygulama başlığı ve versiyon
        app_title = QLabel("YouTube Downloader")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(app_title)
        
        app_version = QLabel("Version 1.0.0")
        app_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(app_version)
        
        # Ayraç
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.Shape.HLine)
        separator4.setFrameShadow(QFrame.Shadow.Sunken)
        about_layout.addWidget(separator4)
        
        # Uygulama açıklaması
        app_desc = QLabel("An application for downloading videos and audio from YouTube.")
        app_desc.setWordWrap(True)
        app_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(app_desc)
        
        # Ayraç
        separator5 = QFrame()
        separator5.setFrameShape(QFrame.Shape.HLine)
        separator5.setFrameShadow(QFrame.Shadow.Sunken)
        about_layout.addWidget(separator5)
        
        # Kullanılan teknolojiler
        tech_label = QLabel("Powered by:")
        tech_label.setStyleSheet("font-weight: bold;")
        tech_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(tech_label)
        
        tech_list = QLabel("PyQt6 | yt-dlp | FFmpeg")
        tech_list.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(tech_list)
        
        # Hakkında sekmesini ekle
        tab_widget.addTab(about_tab, "About")
        
        # Medya türü radio butonlarını kalite seçeneklerini güncellemek için bağlantıla
        self.video_radio.toggled.connect(self.update_quality_options)
        self.audio_radio.toggled.connect(self.update_quality_options)
    
    def update_quality_options(self):
        """Seçilen medya türüne göre kalite seçeneklerini günceller"""
        self.quality_combo.clear()
        if self.video_radio.isChecked():
            self.quality_combo.addItems(self.video_qualities)
        else:
            self.quality_combo.addItems(self.audio_qualities)
    
    def select_directory(self):
        """İndirme dizinini seçmek için dosya iletişim kutusunu açar"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Download Directory", 
            self.backend.download_directory
        )
        if dir_path:
            self.dir_input.setText(dir_path)
            self.backend.set_download_directory(dir_path)
    
    def start_download(self):
        """İndirme işlemini başlatır"""
        url = self.url_input.text().strip()
        if not url:
            self.show_message("Input Error", "Please enter a YouTube URL.", QMessageBox.Icon.Warning)
            return
        
        # İlerlemeyi sıfırla
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting download...")
        self.playlist_status.setText("")
        
        # İndirme seçeneklerini al
        is_video = self.video_radio.isChecked()
        quality = self.quality_combo.currentText()
        is_playlist = self.playlist_check.isChecked()
        
        # İndirmeyi başlat
        self.backend.start_download(url, is_video, quality, is_playlist)
        self.download_button.setEnabled(False)
    
    def update_progress(self, percentage):
        """İlerleme çubuğunu güncelle"""
        self.progress_bar.setValue(int(percentage))
    
    def update_status(self, status):
        """Durum etiketini güncelle"""
        self.status_label.setText(status)
    
    def update_playlist_progress(self, current, total):
        """Oynatma listesi ilerleme durumunu güncelle"""
        self.playlist_status.setText(f"Processing video {current} of {total}")
    
    def download_finished(self, filename, filepath, thumbnail_path):
        """İndirme tamamlandığında işlemleri yap"""
        self.status_label.setText(f"Download completed: {filename}")
        self.download_button.setEnabled(True)
    
    def show_error(self, error_msg):
        """Hata mesajı göster"""
        self.show_message("Download Error", error_msg, QMessageBox.Icon.Critical)
        self.download_button.setEnabled(True)
    
    def show_message(self, title, message, icon=QMessageBox.Icon.Information):
        """Mesaj kutusu göster"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec() 