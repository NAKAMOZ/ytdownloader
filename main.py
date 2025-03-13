import sys
from PyQt6.QtWidgets import QApplication
from backend import YouTubeDownloader
from frontend import YouTubeDownloaderUI

def main():
    """Ana uygulama fonksiyonu"""
    app = QApplication(sys.argv)
    
    # Backend ve frontend oluştur
    backend = YouTubeDownloader()
    window = YouTubeDownloaderUI(backend)
    
    # Uygulamayı gösterböyle 
    window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 