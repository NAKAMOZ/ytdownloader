import sys
import os
from PyQt6.QtWidgets import QApplication

# Modül yolunu düzenle
def setup_module_paths():
    """
    src klasörünü ve üst dizini Python yoluna ekler.
    Bu sayede core ve ui modüllerinin bulunması sağlanır.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Dizinler yola dahil değilse ekle
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Çalışma dizinini ve Python yolunu yazdır (hata ayıklama için)
    print(f"Çalışma dizini: {os.getcwd()}")
    print(f"Python modül yolu: {sys.path}")

# İlk olarak modül yollarını düzenle
setup_module_paths()

# Modülleri import et - her iki yolu da dene
try:
    # Direkt import (normal çalışma için)
    from core.downloader import YouTubeDownloader
    from ui.main_window import YouTubeDownloaderUI
    print("Modüller başarıyla import edildi (core.* yoluyla)")
except ImportError as e1:
    try:
        # Alternatif import (paketlenmiş uygulama için)
        from src.core.downloader import YouTubeDownloader
        from src.ui.main_window import YouTubeDownloaderUI
        print("Modüller başarıyla import edildi (src.core.* yoluyla)")
    except ImportError as e2:
        print(f"Birincil import hatası: {e1}")
        print(f"İkincil import hatası: {e2}")
        
        # Paketlenmiş uygulama durumunda son bir deneme
        try:
            # __file__ konumundan başlayarak manuel import
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.append(os.path.join(current_dir, "core"))
            sys.path.append(os.path.join(current_dir, "ui"))
            
            # Modülleri direkt olarak import et
            import downloader
            import main_window
            
            YouTubeDownloader = downloader.YouTubeDownloader
            YouTubeDownloaderUI = main_window.YouTubeDownloaderUI
            print("Modüller başarıyla import edildi (manuel yollarla)")
        except Exception as e3:
            print(f"Üçüncü import hatası: {e3}")
            # Hata mesajını göster
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Modül Bulunamadı", 
                f"Gerekli modüller yüklenemedi:\n{str(e2)}\n\nUygulama kapatılacak."
            )
            sys.exit(1)

def main():
    """
    Uygulamanın ana işlevi. QApplication oluşturur ve arayüzü gösterir.
    """
    app = QApplication(sys.argv)
    
    try:
        # Backend ve UI oluştur
        backend = YouTubeDownloader()
        window = YouTubeDownloaderUI(backend)
        
        # Arayüzü göster
        window.show()
        
        # Uygulamayı çalıştır
        sys.exit(app.exec())
    except Exception as e:
        # Herhangi bir hata olursa kullanıcıya bilgi ver
        print(f"Uygulama çalıştırılırken hata: {e}")
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Uygulama Hatası", 
            f"Uygulama başlatılırken bir hata oluştu:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main() 