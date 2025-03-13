import sys
from PyQt6.QtWidgets import QApplication
from core.downloader import YouTubeDownloader
from ui.main_window import YouTubeDownloaderUI

def main():
    """Main application function"""
    app = QApplication(sys.argv)
    
    # Create backend and frontend
    backend = YouTubeDownloader()
    window = YouTubeDownloaderUI(backend)
    
    # Show the application
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 