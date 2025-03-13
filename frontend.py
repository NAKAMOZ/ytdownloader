import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QProgressBar,
                            QComboBox, QMessageBox, QFileDialog, QTabWidget, QListView,
                            QRadioButton, QButtonGroup, QStatusBar, QFrame, QCheckBox)
from PyQt6.QtCore import Qt, QSize, QAbstractListModel
from PyQt6.QtGui import QPixmap, QIcon, QColor, QPalette, QFont

class ThumbnailListModel(QAbstractListModel):
    """Thumbnail listesi için model sınıfı"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []  # (filename, filepath, thumbnail_path) tuples

    def rowCount(self, parent=None):
        return len(self.items)

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self.items):
            return None
        
        filename, filepath, thumbnail_path = self.items[index.row()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            return filename
        elif role == Qt.ItemDataRole.ToolTipRole:
            return filepath
        elif role == Qt.ItemDataRole.DecorationRole:
            if os.path.exists(thumbnail_path):
                pixmap = QPixmap(thumbnail_path)
                return pixmap.scaled(160, 90, Qt.AspectRatioMode.KeepAspectRatio)
            return None
        
        return None

    def add_item(self, filename, filepath, thumbnail_path):
        self.beginInsertRows(self.index(0, 0).parent(), len(self.items), len(self.items))
        self.items.append((filename, filepath, thumbnail_path))
        self.endInsertRows()

    def clear(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()

class StyledFrame(QFrame):
    """Özel stillendirilmiş çerçeve sınıfı"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("styledFrame")
        self.setStyleSheet("""
            #styledFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

class YouTubeDownloaderUI(QMainWindow):
    """YouTube indirici uygulamasının kullanıcı arayüzü"""
    
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setup_ui()
        self.connect_signals()
        self.load_downloaded_files()
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        self.setWindowTitle("YouTube İndirici")
        self.setGeometry(100, 100, 1000, 700)
        
        # UI stillerini ayarla
        self.setup_styles()
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_widget.setStyleSheet("background-color: #f5f5f5;")
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #505050;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 120px;
                padding: 8px 15px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1e88e5;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e3f2fd;
            }
        """)
        main_layout.addWidget(self.tab_widget)
        
        # İndirme sekmesi
        download_tab = QWidget()
        download_layout = QVBoxLayout(download_tab)
        download_layout.setContentsMargins(15, 15, 15, 15)
        download_layout.setSpacing(15)
        self.tab_widget.addTab(download_tab, "Video İndir")
        
        # Tarihçe sekmesi
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        history_layout.setContentsMargins(15, 15, 15, 15)
        history_layout.setSpacing(15)
        self.tab_widget.addTab(history_tab, "İndirme Geçmişi")
        
        # URL girişi
        url_frame = StyledFrame()
        url_layout = QVBoxLayout(url_frame)
        url_layout.setContentsMargins(15, 15, 15, 15)
        url_layout.setSpacing(10)
        url_layout_label = QLabel("Video URL")
        url_layout_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333; background-color: transparent;")
        url_layout.addWidget(url_layout_label)
        
        url_input_layout = QHBoxLayout()
        url_input_layout.setSpacing(10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube video URL'sini buraya yapıştırın")
        self.url_input.setMinimumHeight(40)
        self.url_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #f5f5f5;
                selection-background-color: #bbdefb;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #2196f3;
                background-color: #ffffff;
            }
        """)
        
        paste_button = QPushButton("Yapıştır")
        paste_button.setMinimumHeight(40)
        paste_button.setCursor(Qt.CursorShape.PointingHandCursor)
        paste_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px 15px;
                color: #333333;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 1px solid #bbdefb;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
        """)
        paste_button.clicked.connect(self.paste_url)
        
        url_input_layout.addWidget(self.url_input)
        url_input_layout.addWidget(paste_button)
        url_layout.addLayout(url_input_layout)
        
        # Playlist seçeneği
        self.playlist_checkbox = QCheckBox("Playlist olarak indir")
        self.playlist_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #333333;
                spacing: 8px;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #b0b0b0;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #2196f3;
                border: 2px solid #2196f3;
            }
            QCheckBox::indicator:unchecked:hover {
                border: 2px solid #2196f3;
            }
        """)
        url_layout.addWidget(self.playlist_checkbox)
        
        download_layout.addWidget(url_frame)
        
        # Seçenekler kısmı
        options_layout = QHBoxLayout()
        options_layout.setSpacing(15)
        
        # Format seçimi
        format_frame = StyledFrame()
        format_layout = QVBoxLayout(format_frame)
        format_layout.setContentsMargins(15, 15, 15, 15)
        format_layout.setSpacing(10)
        
        format_label = QLabel("Format")
        format_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333; background-color: transparent;")
        format_layout.addWidget(format_label)
        
        # Format radio butonları
        self.format_group = QButtonGroup(self)
        self.video_radio = QRadioButton("Video")
        self.audio_radio = QRadioButton("Ses")
        self.video_radio.setChecked(True)
        self.format_group.addButton(self.video_radio)
        self.format_group.addButton(self.audio_radio)
        
        self.video_radio.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                spacing: 8px;
                color: #333333;
                background-color: transparent;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #b0b0b0;
                background-color: #ffffff;
            }
            QRadioButton::indicator:checked {
                background-color: #2196f3;
                border: 2px solid #2196f3;
            }
            QRadioButton::indicator:unchecked:hover {
                border: 2px solid #2196f3;
            }
        """)
        self.audio_radio.setStyleSheet(self.video_radio.styleSheet())
        
        format_layout.addWidget(self.video_radio)
        format_layout.addWidget(self.audio_radio)
        
        # Kalite seçimi (Video için)
        quality_frame = StyledFrame()
        quality_layout = QVBoxLayout(quality_frame)
        quality_layout.setContentsMargins(15, 15, 15, 15)
        quality_layout.setSpacing(10)
        
        quality_label = QLabel("Video Kalitesi")
        quality_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333; background-color: transparent;")
        quality_layout.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["En İyi Kalite", "1080p", "720p", "480p", "360p", "240p"])
        self.quality_combo.setMinimumHeight(35)
        self.quality_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #f5f5f5;
                selection-background-color: #bbdefb;
                font-size: 14px;
                color: #333333;
            }
            QComboBox:hover {
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
            }
            QComboBox:focus {
                border: 1px solid #2196f3;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #e0e0e0;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                selection-background-color: #bbdefb;
                color: #333333;
            }
        """)
        quality_layout.addWidget(self.quality_combo)
        
        # Ses kalitesi seçimi (Ses için)
        audio_quality_frame = StyledFrame()
        audio_quality_layout = QVBoxLayout(audio_quality_frame)
        audio_quality_layout.setContentsMargins(15, 15, 15, 15)
        audio_quality_layout.setSpacing(10)
        
        audio_quality_label = QLabel("Ses Kalitesi")
        audio_quality_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333; background-color: transparent;")
        audio_quality_layout.addWidget(audio_quality_label)
        
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps"])
        self.audio_quality_combo.setMinimumHeight(35)
        self.audio_quality_combo.setStyleSheet(self.quality_combo.styleSheet())
        audio_quality_layout.addWidget(self.audio_quality_combo)
        
        # Formatları ekle
        options_layout.addWidget(format_frame, 1)
        options_layout.addWidget(quality_frame, 2)
        options_layout.addWidget(audio_quality_frame, 2)
        
        download_layout.addLayout(options_layout)
        
        # Format seçimine göre kalite seçeneklerini göster/gizle
        self.video_radio.toggled.connect(self.update_quality_options)
        self.audio_radio.toggled.connect(self.update_quality_options)
        self.update_quality_options()
        
        # İndirme dizini seçimi
        dir_frame = StyledFrame()
        dir_layout = QVBoxLayout(dir_frame)
        dir_layout.setContentsMargins(15, 15, 15, 15)
        dir_layout.setSpacing(10)
        
        dir_label_header = QLabel("İndirme Dizini")
        dir_label_header.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333; background-color: transparent;")
        dir_layout.addWidget(dir_label_header)
        
        dir_input_layout = QHBoxLayout()
        dir_input_layout.setSpacing(10)
        
        self.dir_label = QLabel(self.backend.download_directory)
        self.dir_label.setStyleSheet("""
            padding: 5px 10px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            font-size: 14px;
            color: #333333;
            background-color: #f5f5f5;
        """)
        
        dir_button = QPushButton("Dizin Seç")
        dir_button.setMinimumHeight(35)
        dir_button.setCursor(Qt.CursorShape.PointingHandCursor)
        dir_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px 15px;
                color: #333333;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 1px solid #bbdefb;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
        """)
        dir_button.clicked.connect(self.select_directory)
        
        dir_input_layout.addWidget(self.dir_label)
        dir_input_layout.addWidget(dir_button)
        dir_layout.addLayout(dir_input_layout)
        
        download_layout.addWidget(dir_frame)
        
        # İndirme butonu
        self.download_button = QPushButton("İNDİR")
        self.download_button.setMinimumHeight(50)
        self.download_button.setCursor(Qt.CursorShape.PointingHandCursor)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.download_button.setFont(font)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: 1px solid #1976d2;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
                border: 1px solid #0d47a1;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #bbdefb;
                color: #e1f5fe;
                border: 1px solid #90caf9;
            }
        """)
        self.download_button.clicked.connect(self.start_download)
        download_layout.addWidget(self.download_button)
        
        # İlerleme çubuğu
        progress_frame = StyledFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        progress_layout.setSpacing(10)
        
        progress_label = QLabel("İndirme Durumu")
        progress_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333; background-color: transparent;")
        progress_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: #f5f5f5;
                text-align: center;
                font-size: 12px;
                font-weight: bold;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #2196f3;
                border-radius: 4px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_status = QLabel("Hazır")
        self.progress_status.setStyleSheet("""
            font-size: 13px;
            color: #505050;
            padding: 5px;
            background-color: transparent;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        """)
        progress_layout.addWidget(self.progress_status)
        
        # Playlist ilerleme durumu
        self.playlist_progress_label = QLabel("")
        self.playlist_progress_label.setStyleSheet("""
            font-size: 13px;
            color: #505050;
            padding: 5px;
            background-color: transparent;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        """)
        self.playlist_progress_label.setVisible(False)
        progress_layout.addWidget(self.playlist_progress_label)
        
        download_layout.addWidget(progress_frame)
        
        # Thumbnail list view
        thumbnail_frame = StyledFrame()
        thumbnail_layout = QVBoxLayout(thumbnail_frame)
        thumbnail_layout.setContentsMargins(15, 15, 15, 15)
        thumbnail_layout.setSpacing(10)
        
        self.thumbnail_model = ThumbnailListModel()
        self.downloaded_list = QListView()
        self.downloaded_list.setModel(self.thumbnail_model)
        self.downloaded_list.setViewMode(QListView.ViewMode.IconMode)
        self.downloaded_list.setIconSize(QSize(180, 100))
        self.downloaded_list.setSpacing(15)
        self.downloaded_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.downloaded_list.setUniformItemSizes(True)
        self.downloaded_list.setWordWrap(True)
        self.downloaded_list.setStyleSheet("""
            QListView {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
            QListView::item {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
                margin: 5px;
                color: #333333;
            }
            QListView::item:selected {
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
            }
            QListView::item:hover:!selected {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
            }
        """)
        
        thumbnail_layout.addWidget(self.downloaded_list)
        history_layout.addWidget(thumbnail_frame)
        
        # Durum çubuğu
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f5f5f5;
                color: #505050;
                border-top: 1px solid #e0e0e0;
                padding: 5px;
                font-size: 13px;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
        # Genel buton stilleri için stil sayfası ayarla
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px 15px;
                color: #333333;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 1px solid #bbdefb;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
            QMessageBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
            }
            QMessageBox QLabel {
                color: #333333;
            }
        """)
    
    def setup_styles(self):
        """UI stillerini ayarlar"""
        # Ana renk teması
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(51, 51, 51))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(51, 51, 51))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(33, 150, 243))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(33, 150, 243))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
    
    def connect_signals(self):
        """Backend sinyallerini UI'a bağlar"""
        self.backend.signals.progress.connect(self.update_progress)
        self.backend.signals.finished.connect(self.download_finished)
        self.backend.signals.error.connect(self.show_error)
        self.backend.signals.status.connect(self.update_status)
        self.backend.signals.playlist_progress.connect(self.update_playlist_progress)
    
    def update_quality_options(self):
        """Format seçimine göre kalite seçeneklerini günceller"""
        is_video = self.video_radio.isChecked()
        if is_video:
            self.quality_combo.setEnabled(True)
            self.audio_quality_combo.setEnabled(False)
        else:
            self.quality_combo.setEnabled(False)
            self.audio_quality_combo.setEnabled(True)
    
    def paste_url(self):
        """Panodaki URL'yi giriş alanına yapıştırır"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())
    
    def select_directory(self):
        """İndirme dizinini seçmek için dosya gezgini açar"""
        new_dir = QFileDialog.getExistingDirectory(self, "İndirme Dizini Seç", self.backend.download_directory)
        if new_dir:
            self.backend.set_download_directory(new_dir)
            self.dir_label.setText(new_dir)
    
    def start_download(self):
        """İndirme işlemini başlatır"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Hata", "Lütfen bir URL girin.")
            return
        
        self.progress_bar.setValue(0)
        self.download_button.setEnabled(False)
        self.progress_status.setText("Hazırlanıyor...")
        self.status_bar.showMessage("İndirme başlatılıyor...")
        
        # Playlist seçeneği
        is_playlist = self.playlist_checkbox.isChecked()
        if is_playlist:
            self.playlist_progress_label.setText("Playlist hazırlanıyor...")
            self.playlist_progress_label.setVisible(True)
            self.playlist_progress_label.setStyleSheet("font-size: 13px; color: #505050; padding: 5px; background-color: transparent;")
        else:
            self.playlist_progress_label.setVisible(False)
        
        # Format ve kalite seçimi
        is_video = self.video_radio.isChecked()
        quality = self.quality_combo.currentText() if is_video else self.audio_quality_combo.currentText()
        
        # İndirme işlemini başlat
        self.backend.start_download(url, is_video, quality, is_playlist)
    
    def update_progress(self, percentage):
        """İlerleme çubuğunu günceller"""
        self.progress_bar.setValue(int(percentage))
    
    def update_status(self, status_text):
        """Durum metnini günceller"""
        self.progress_status.setText(status_text)
        self.status_bar.showMessage(status_text)
        self.progress_status.setStyleSheet("""
            font-size: 13px;
            color: #505050;
            padding: 5px;
            background-color: transparent;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        """)
    
    def update_playlist_progress(self, current, total):
        """Playlist ilerleme durumunu günceller"""
        self.playlist_progress_label.setText(f"Playlist İlerlemesi: {current}/{total} video")
        self.playlist_progress_label.setVisible(True)
        self.playlist_progress_label.setStyleSheet("""
            font-size: 13px;
            color: #505050;
            padding: 5px;
            background-color: transparent;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        """)

    def download_finished(self, filename, filepath, thumbnail_path):
        """İndirme tamamlandığında çağrılır"""
        self.progress_bar.setValue(100)
        self.download_button.setEnabled(True)
        self.progress_status.setText("İndirme tamamlandı")
        self.status_bar.showMessage(f"{filename} başarıyla indirildi.")
        self.progress_status.setStyleSheet("""
            font-size: 13px;
            color: #505050;
            padding: 5px;
            background-color: transparent;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        """)

        # Listeye ekle
        self.backend.downloaded_files.append((filename, filepath, thumbnail_path))
        self.thumbnail_model.add_item(filename, filepath, thumbnail_path)
        self.backend.save_downloaded_files()
    
    def show_error(self, error_message):
        """Hata mesajını gösterir"""
        self.download_button.setEnabled(True)
        self.progress_status.setText("Hata")
        self.status_bar.showMessage(f"Hata: {error_message}")
        self.progress_status.setStyleSheet("""
            font-size: 13px;
            color: #ff3d00;
            padding: 5px;
            background-color: transparent;
            border: 1px solid #ff8a65;
            border-radius: 5px;
        """)
        QMessageBox.critical(self, "Hata", f"İndirme başarısız: {error_message}")
    
    def load_downloaded_files(self):
        """İndirilen dosyaların listesini yükler"""
        downloaded_files = self.backend.load_downloaded_files()
        for filename, filepath, thumbnail_path in downloaded_files:
            self.thumbnail_model.add_item(filename, filepath, thumbnail_path) 