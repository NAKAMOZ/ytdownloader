import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QComboBox, 
                           QProgressBar, QFileDialog, QTabWidget, 
                           QListWidget, QListWidgetItem, QMessageBox,
                           QCheckBox, QGroupBox, QRadioButton, QButtonGroup,
                           QApplication, QSlider, QStyle, QFrame)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QFontDatabase, QCursor

class DarkPalette(QPalette):
    """Custom dark palette for Qt applications"""
    def __init__(self):
        super().__init__()
        
        # Main colors
        self.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        self.setColor(QPalette.ColorRole.WindowText, QColor(212, 212, 212))
        self.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        self.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        self.setColor(QPalette.ColorRole.Text, QColor(212, 212, 212))
        self.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        self.setColor(QPalette.ColorRole.ButtonText, QColor(212, 212, 212))
        self.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        self.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        self.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        # Disabled colors
        self.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
        self.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
        self.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
        self.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
        self.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))

class ModernButton(QPushButton):
    """Modern styled button with hover and click animations"""
    def __init__(self, text, parent=None, primary=False):
        super().__init__(text, parent)
        self.primary = primary
        self.setFixedHeight(40)
        
        # Default styles
        self.base_style = """
            QPushButton {{
                background-color: {bgcolor};
                color: {color};
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_bgcolor};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bgcolor};
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #888888;
            }}
        """
        
        if primary:
            self.setStyleSheet(self.base_style.format(
                bgcolor="#2979ff",
                color="#ffffff",
                hover_bgcolor="#2962ff",
                pressed_bgcolor="#1565c0"
            ))
        else:
            self.setStyleSheet(self.base_style.format(
                bgcolor="#454545",
                color="#e0e0e0",
                hover_bgcolor="#505050",
                pressed_bgcolor="#353535"
            ))
        
        # Cursor change on hover
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

class ModernLine(QFrame):
    """Modern horizontal line separator"""
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("border: 1px solid #3a3a3a;")

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
        
        # Apply dark theme
        self.set_dark_theme()
        
        # Load download history
        self.load_download_history()
    
    def set_dark_theme(self):
        """Applies dark theme to the application"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        app.setPalette(DarkPalette())
        
        # Set app-wide stylesheet
        app.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #1e1e1e;
            }
            QWidget {
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #2d2d2d;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #b0b0b0;
                padding: 8px 16px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2979ff;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #454545;
            }
            QLineEdit, QComboBox {
                background-color: #353535;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #e0e0e0;
                selection-background-color: #2979ff;
                selection-color: #ffffff;
                height: 30px;
            }
            QComboBox::drop-down {
                border: 0px;
                border-left: 1px solid #555555;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #353535;
                border: 1px solid #555555;
                color: #e0e0e0;
                selection-background-color: #2979ff;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #555555;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #2979ff;
                border: 1px solid #2979ff;
            }
            QRadioButton {
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid #555555;
                background-color: #353535;
            }
            QRadioButton::indicator:checked {
                background-color: #2979ff;
                border: 1px solid #2979ff;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2979ff;
                border-radius: 5px;
            }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 0.6em;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 2px;
                background-color: #2d2d2d;
                alternate-background-color: #353535;
            }
            QListWidget::item {
                padding: 3px;
                border-bottom: 1px solid #3a3a3a;
                min-height: 56px;
            }
            QListWidget::item:selected {
                background-color: #2979ff;
                color: #ffffff;
            }
            QListWidget::item:hover:!selected {
                background-color: #454545;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #787878;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #2d2d2d;
                height: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #5a5a5a;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #787878;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QToolTip {
                background-color: #353535;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 3px;
            }
        """)
    
    def init_ui(self):
        """Initialize the user interface"""
        # Basic window setup
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(900, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header with logo and title
        header_layout = QHBoxLayout()
        title_label = QLabel("YouTube Downloader")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2979ff;")
        
        # Version label
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("font-size: 16px; color: #888888;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(version_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Horizontal separator
        main_layout.addWidget(ModernLine())
        
        # Tab widget for different sections
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)
        main_layout.addWidget(tab_widget)
        
        # Download tab
        download_tab = QWidget()
        download_layout = QVBoxLayout(download_tab)
        download_layout.setContentsMargins(15, 15, 15, 15)
        download_layout.setSpacing(15)
        
        # URL input with label
        url_label = QLabel("YouTube URL")
        url_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        download_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube video or playlist URL")
        self.url_input.setStyleSheet("font-size: 15px; height: 40px; padding: 0 10px;")
        download_layout.addWidget(self.url_input)
        
        # Horizontal separator
        download_layout.addWidget(ModernLine())
        
        # Options section
        options_label = QLabel("Download Options")
        options_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        download_layout.addWidget(options_label)
        
        # Options layout
        options_layout = QHBoxLayout()
        options_layout.setSpacing(20)
        
        # Media type group
        media_group = QGroupBox("Media Type")
        media_group.setStyleSheet("font-size: 14px;")
        media_layout = QVBoxLayout(media_group)
        media_layout.setContentsMargins(15, 20, 15, 15)
        media_layout.setSpacing(10)
        
        self.video_radio = QRadioButton("Video")
        self.audio_radio = QRadioButton("Audio")
        self.video_radio.setStyleSheet("font-size: 14px;")
        self.audio_radio.setStyleSheet("font-size: 14px;")
        self.video_radio.setChecked(True)
        
        media_layout.addWidget(self.video_radio)
        media_layout.addWidget(self.audio_radio)
        options_layout.addWidget(media_group)
        
        # Quality selection
        quality_group = QGroupBox("Quality")
        quality_group.setStyleSheet("font-size: 14px;")
        quality_layout = QVBoxLayout(quality_group)
        quality_layout.setContentsMargins(15, 20, 15, 15)
        quality_layout.setSpacing(10)
        
        self.quality_combo = QComboBox()
        self.quality_combo.setStyleSheet("font-size: 14px;")
        
        # Video qualities
        self.video_qualities = ["Best Quality", "1080p", "720p", "480p", "360p", "240p"]
        # Audio qualities
        self.audio_qualities = ["320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps"]
        
        # Default to video qualities
        self.quality_combo.addItems(self.video_qualities)
        
        quality_layout.addWidget(self.quality_combo)
        options_layout.addWidget(quality_group)
        
        # Additional options group
        add_options_group = QGroupBox("Additional Options")
        add_options_group.setStyleSheet("font-size: 14px;")
        add_options_layout = QVBoxLayout(add_options_group)
        add_options_layout.setContentsMargins(15, 20, 15, 15)
        add_options_layout.setSpacing(10)
        
        # Playlist option
        self.playlist_check = QCheckBox("Download as playlist")
        self.playlist_check.setStyleSheet("font-size: 14px;")
        add_options_layout.addWidget(self.playlist_check)
        
        options_layout.addWidget(add_options_group)
        download_layout.addLayout(options_layout)
        
        # Output directory
        location_label = QLabel("Save Location")
        location_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        download_layout.addWidget(location_label)
        
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(10)
        
        self.dir_input = QLineEdit()
        self.dir_input.setText(self.backend.download_directory)
        self.dir_input.setReadOnly(True)
        self.dir_input.setStyleSheet("font-size: 14px; height: 40px; padding: 0 10px;")
        
        dir_button = ModernButton("Browse", primary=False)
        dir_button.clicked.connect(self.select_directory)
        
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        download_layout.addLayout(dir_layout)
        
        # Horizontal separator
        download_layout.addWidget(ModernLine())
        
        # Download button
        self.download_button = ModernButton("DOWNLOAD", primary=True)
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setFixedHeight(50)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #2979ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2962ff;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        download_layout.addWidget(self.download_button)
        
        # Progress section
        progress_group = QGroupBox("Download Progress")
        progress_group.setStyleSheet("font-size: 14px;")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(15, 20, 15, 15)
        progress_layout.setSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                height: 25px;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2979ff, stop:1 #7c4dff);
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 14px; color: #b0b0b0;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        # Playlist progress
        self.playlist_status = QLabel("")
        self.playlist_status.setStyleSheet("font-size: 14px; color: #7c4dff;")
        self.playlist_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.playlist_status)
        
        download_layout.addWidget(progress_group)
        
        # Add stretch to push everything up
        download_layout.addStretch()
        
        # Add download tab to tab widget
        tab_widget.addTab(download_tab, "Download")
        
        # History tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        history_layout.setContentsMargins(15, 15, 15, 15)
        history_layout.setSpacing(15)
        
        # History header
        history_header = QLabel("Downloaded Files")
        history_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        history_layout.addWidget(history_header)
        
        # List of downloaded files
        self.history_list = QListWidget()
        self.history_list.setIconSize(QSize(72, 48))
        self.history_list.setAlternatingRowColors(True)
        self.history_list.itemDoubleClicked.connect(self.open_file)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 2px;
                background-color: #2d2d2d;
                alternate-background-color: #353535;
            }
            QListWidget::item {
                padding: 3px;
                border-bottom: 1px solid #3a3a3a;
                min-height: 56px;
            }
            QListWidget::item:selected {
                background-color: #2979ff;
                color: #ffffff;
            }
            QListWidget::item:hover:!selected {
                background-color: #454545;
            }
        """)
        history_layout.addWidget(self.history_list)
        
        # History actions
        history_buttons = QHBoxLayout()
        history_buttons.setSpacing(10)
        
        open_button = ModernButton("Open Selected")
        open_button.clicked.connect(self.open_selected)
        
        open_folder_button = ModernButton("Open Folder")
        open_folder_button.clicked.connect(lambda: os.startfile(self.backend.download_directory))
        
        clear_history_button = ModernButton("Clear History")
        clear_history_button.clicked.connect(self.clear_history)
        
        history_buttons.addWidget(open_button)
        history_buttons.addWidget(open_folder_button)
        history_buttons.addWidget(clear_history_button)
        history_layout.addLayout(history_buttons)
        
        # Add history tab to tab widget
        tab_widget.addTab(history_tab, "History")
        
        # About tab
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(15, 15, 15, 15)
        about_layout.setSpacing(20)
        about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # App logo
        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap(os.path.join("assets", "icon.ico")).scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        except:
            logo_label.setText("YT")
            logo_label.setStyleSheet("font-size: 72px; font-weight: bold; color: #2979ff;")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(logo_label)
        
        # App title and version
        app_title = QLabel("YouTube Downloader")
        app_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(app_title)
        
        app_version = QLabel("Version 1.0.0")
        app_version.setStyleSheet("font-size: 16px; color: #b0b0b0;")
        app_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(app_version)
        
        # Horizontal separator
        about_layout.addWidget(ModernLine())
        
        # App description
        app_desc = QLabel("A modern application for downloading videos and audio from YouTube with a user-friendly interface.")
        app_desc.setWordWrap(True)
        app_desc.setStyleSheet("font-size: 14px; color: #e0e0e0;")
        app_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(app_desc)
        
        # Horizontal separator
        about_layout.addWidget(ModernLine())
        
        # Technologies used
        tech_label = QLabel("Powered by:")
        tech_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        tech_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(tech_label)
        
        tech_list = QLabel("PyQt6 | yt-dlp | FFmpeg")
        tech_list.setStyleSheet("font-size: 14px; color: #2979ff;")
        tech_list.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(tech_list)
        
        # Credits
        credits = QLabel("© 2023 YouTube Downloader. All rights reserved.")
        credits.setStyleSheet("font-size: 12px; color: #888888;")
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(credits)
        
        # Add about tab to tab widget
        tab_widget.addTab(about_tab, "About")
        
        # Connect media type radio buttons to update quality options
        self.video_radio.toggled.connect(self.update_quality_options)
        self.audio_radio.toggled.connect(self.update_quality_options)
    
    def update_quality_options(self):
        """Update quality options based on selected media type"""
        self.quality_combo.clear()
        if self.video_radio.isChecked():
            self.quality_combo.addItems(self.video_qualities)
        else:
            self.quality_combo.addItems(self.audio_qualities)
    
    def select_directory(self):
        """Open file dialog to select download directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Download Directory", 
            self.backend.download_directory
        )
        if dir_path:
            self.dir_input.setText(dir_path)
            self.backend.set_download_directory(dir_path)
    
    def start_download(self):
        """Start the download process"""
        url = self.url_input.text().strip()
        if not url:
            self.show_message("Input Error", "Please enter a YouTube URL.", QMessageBox.Icon.Warning)
            return
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting download...")
        self.playlist_status.setText("")
        
        # Get download options
        is_video = self.video_radio.isChecked()
        quality = self.quality_combo.currentText()
        is_playlist = self.playlist_check.isChecked()
        
        # Start download
        self.backend.start_download(url, is_video, quality, is_playlist)
        self.download_button.setEnabled(False)
        
        # Animate progress bar
        self.animate_progress_start()
    
    def animate_progress_start(self):
        """Add a subtle animation to progress bar"""
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(500)
        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(5)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.progress_animation.start()
    
    def update_progress(self, percentage):
        """Update progress bar with animation"""
        current = self.progress_bar.value()
        
        # Only animate if significant change
        if abs(percentage - current) > 1:
            self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
            self.progress_animation.setDuration(300)
            self.progress_animation.setStartValue(current)
            self.progress_animation.setEndValue(int(percentage))
            self.progress_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.progress_animation.start()
        else:
            self.progress_bar.setValue(int(percentage))
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
    
    def update_playlist_progress(self, current, total):
        """Update playlist progress status"""
        self.playlist_status.setText(f"Processing video {current} of {total}")
    
    def download_finished(self, filename, filepath, thumbnail_path):
        """Handle download completion"""
        self.status_label.setText(f"Download completed: {filename}")
        self.download_button.setEnabled(True)
        
        # Add to history UI 
        self.add_download_to_history(filename, filepath, thumbnail_path)
        
        # Show success animation
        self.animate_progress_complete()
        
        # Switch to history tab
        QTimer.singleShot(800, lambda: self.centralWidget().findChild(QTabWidget).setCurrentIndex(1))
    
    def animate_progress_complete(self):
        """Animate progress completion"""
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                height: 25px;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4caf50, stop:1 #8bc34a);
                border-radius: 5px;
            }
        """)
        
        # Reset style after delay
        QTimer.singleShot(2000, self.reset_progress_style)
    
    def reset_progress_style(self):
        """Reset progress bar style to default"""
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                height: 25px;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2979ff, stop:1 #7c4dff);
                border-radius: 5px;
            }
        """)
    
    def show_error(self, error_msg):
        """Show error message"""
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                height: 25px;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f44336, stop:1 #ff5722);
                border-radius: 5px;
            }
        """)
        
        # Reset style after delay
        QTimer.singleShot(2000, self.reset_progress_style)
        
        self.show_message("Download Error", error_msg, QMessageBox.Icon.Critical)
        self.download_button.setEnabled(True)
    
    def show_message(self, title, message, icon=QMessageBox.Icon.Information):
        """Show styled message box"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def add_download_to_history(self, filename, filepath, thumbnail_path):
        """Add downloaded file to history list with improved display"""
        print(f"Adding to history: {filename}, {filepath}, {thumbnail_path}")  # Debug için
        
        # Item ve widget oluşturma
        item = QListWidgetItem(self.history_list)
        
        # Widget oluştur
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(8, 8, 8, 8)
        item_layout.setSpacing(12)
        item_widget.setLayout(item_layout)
        
        # Küçük resim bölümü
        thumb_label = QLabel()
        thumb_label.setFixedSize(QSize(72, 48))
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Arkaplan rengi
        thumb_label.setStyleSheet("background-color: #444; border-radius: 3px;")
        
        # Küçük resimi yükle
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                pixmap = QPixmap(thumbnail_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(72, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    thumb_label.setPixmap(pixmap)
                else:
                    thumb_label.setText("No\nPreview")
                    thumb_label.setStyleSheet("background-color: #444; border-radius: 3px; color: #aaa; font-size: 11px;")
            except Exception as e:
                print(f"Thumbnail loading error: {e}")
                thumb_label.setText("No\nPreview")
                thumb_label.setStyleSheet("background-color: #444; border-radius: 3px; color: #aaa; font-size: 11px;")
        else:
            thumb_label.setText("No\nPreview")
            thumb_label.setStyleSheet("background-color: #444; border-radius: 3px; color: #aaa; font-size: 11px;")
        
        item_layout.addWidget(thumb_label)
        
        # Bilgi bölümü
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        info_widget.setLayout(info_layout)
        
        # Dosya adı etiketi
        file_name_label = QLabel(filename)
        file_name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        file_name_label.setWordWrap(True)
        
        # Dosya yolu etiketi
        file_path_label = QLabel(filepath)
        file_path_label.setStyleSheet("font-size: 12px; color: #bbbbbb;")
        file_path_label.setWordWrap(True)
        
        info_layout.addWidget(file_name_label)
        info_layout.addWidget(file_path_label)
        
        item_layout.addWidget(info_widget, 1)
        
        # Öğe için veri ayarla
        item.setData(Qt.ItemDataRole.UserRole, filepath)
        
        # Öğenin boyutunu ayarla
        item.setSizeHint(QSize(self.history_list.width() - 30, 70))
        
        # Widget'ı öğeye ekle
        self.history_list.setItemWidget(item, item_widget)
        
        # Yeni öğeyi listenin başına taşı
        self.history_list.insertItem(0, self.history_list.takeItem(self.history_list.count() - 1))
    
    def load_download_history(self):
        """Load download history from backend"""
        self.history_list.clear()  # Önce listeyi temizle
        
        try:
            downloaded_files = self.backend.load_downloaded_files()
            
            print(f"Loading history: Found {len(downloaded_files) if downloaded_files else 0} files")  # Debug için
            
            if downloaded_files and len(downloaded_files) > 0:
                for file_data in downloaded_files:
                    # 4 değer (URL dahil) veya 3 değer (eski format) olabilir
                    if len(file_data) >= 4:
                        filename, filepath, thumbnail_path, url = file_data
                    else:
                        filename, filepath, thumbnail_path = file_data
                        
                    print(f"Loading: {filename}")
                    print(f"  - File path: {filepath}, exists: {os.path.exists(filepath)}")
                    print(f"  - Thumbnail: {thumbnail_path}, exists: {os.path.exists(thumbnail_path) if thumbnail_path else False}")
                    self.add_download_to_history(filename, filepath, thumbnail_path)
            else:
                # Eğer hiç indirme yoksa bilgi mesajı göster
                item = QListWidgetItem(self.history_list)
                info_widget = QLabel("No downloads yet. Go to the 'Download' tab to start downloading.")
                info_widget.setStyleSheet("color: #888888; font-size: 14px; padding: 20px;")
                info_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setSizeHint(QSize(self.history_list.width() - 30, 60))
                self.history_list.setItemWidget(item, info_widget)
        except Exception as e:
            print(f"Error loading download history: {e}")
            # Hata durumunda bilgi mesajı göster
            item = QListWidgetItem(self.history_list)
            info_widget = QLabel(f"Error loading download history: {str(e)}")
            info_widget.setStyleSheet("color: #ff5555; font-size: 14px; padding: 20px;")
            info_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(QSize(self.history_list.width() - 30, 60))
            self.history_list.setItemWidget(item, info_widget)
    
    def open_file(self, item):
        """Open the downloaded file when double-clicked"""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        try:
            os.startfile(filepath)
        except Exception as e:
            self.show_message("Error", f"Could not open file: {e}", QMessageBox.Icon.Warning)
    
    def open_selected(self):
        """Open the selected file from history"""
        selected_items = self.history_list.selectedItems()
        if selected_items:
            self.open_file(selected_items[0])
        else:
            self.show_message("Selection Required", "Please select a file to open.", QMessageBox.Icon.Information)
    
    def clear_history(self):
        """Clear download history with confirmation"""
        reply = QMessageBox.question(
            self, "Clear History", 
            "Are you sure you want to clear the download history?\nThis will not delete the actual files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history_list.clear()
            self.backend.downloaded_files = []
            self.backend.save_downloaded_files()
            
            # Boş liste mesajını göster
            item = QListWidgetItem(self.history_list)
            info_widget = QLabel("No downloads yet. Go to the 'Download' tab to start downloading.")
            info_widget.setStyleSheet("color: #888888; font-size: 14px; padding: 20px;")
            info_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(QSize(self.history_list.width() - 30, 60))
            self.history_list.setItemWidget(item, info_widget) 