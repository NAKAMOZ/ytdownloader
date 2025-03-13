import sys
from PyQt6.QtWidgets import QApplication
from core.downloader import YouTubeDownloader
from ui.main_window import YouTubeDownloaderUI

def main():
    app = QApplication(sys.argv)
    
    backend = YouTubeDownloader()
    window = YouTubeDownloaderUI(backend)
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 