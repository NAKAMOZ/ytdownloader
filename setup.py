import sys
import os
import subprocess
from cx_Freeze import setup, Executable

# FFmpeg kontrolü
ffmpeg_path = None
try:
    subprocess.check_call(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("FFmpeg sistem üzerinde bulunuyor.")
    
    # FFmpeg'in yolunu bulmaya çalış
    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, "ffmpeg.exe")
        if os.path.isfile(exe_file):
            ffmpeg_path = exe_file
            print(f"FFmpeg yolu: {ffmpeg_path}")
            break
except:
    print("UYARI: FFmpeg bulunamadı!")
    print("FFmpeg'i yüklemek için: 'winget install ffmpeg' komutunu çalıştırın.")

# Uygulama bilgileri
APP_NAME = "YouTube Downloader"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "YouTube videoları ve ses dosyalarını indirmek için arayüz"
APP_AUTHOR = "YT Downloader Team"
APP_AUTHOR_EMAIL = "example@example.com"

# Ana Python dosyası
main_script = "src/main.py"

# Başlangıç betiği oluştur
with open("startup.py", "w") as f:
    f.write("""import os
import sys

# Modül yolu düzenleme
def setup_environment():
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # FFmpeg Path düzenleme
    os.environ["PATH"] = base_dir + os.pathsep + os.environ["PATH"]
    
    # Python modül yolu düzenleme
    sys.path.insert(0, base_dir)
    src_dir = os.path.join(base_dir, "src")
    if os.path.exists(src_dir):
        sys.path.insert(0, src_dir)
        
        # __init__.py dosyalarını kontrol et, yoksa oluştur
        core_dir = os.path.join(src_dir, "core")
        ui_dir = os.path.join(src_dir, "ui")
        
        for dir_path in [core_dir, ui_dir]:
            if os.path.exists(dir_path):
                init_file = os.path.join(dir_path, "__init__.py")
                if not os.path.exists(init_file):
                    open(init_file, 'w').close()
    
    print(f"Çalışma dizini: {base_dir}")
    print(f"Python yolu: {sys.path}")

if __name__ == "__main__":
    setup_environment()
    
    try:
        # Import doğru şekilde çalışmalı, aksi halde hata ver
        from src.main import main
        main()
    except ImportError as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Import Hatası", 
            f"Uygulama başlatılırken bir hata oluştu:\n{str(e)}\n\n"
            "Lütfen uygulama klasöründeki dosyaların tam olduğundan emin olun.")
""")

# Dahil edilecek dosyalar
include_files = [
    ("icon.ico", "icon.ico"),
    ("assets/", "assets/"),
    # Kaynak kodları doğrudan kopyala 
    ("src/", "src/"),
]

# FFmpeg varsa ekle
if ffmpeg_path:
    include_files.append((ffmpeg_path, "ffmpeg.exe"))

# Windows için base ayarları
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # GUI uygulaması, konsol gösterme

# cx_Freeze yapılandırması
build_exe_options = {
    # Temel Python paketleri
    "packages": [
        "os", 
        "sys",
        "PyQt6",
        "yt_dlp",
        "ffmpeg-python"
    ],
    
    # Dahil edilecek modüller
    "includes": [
        "src",
        "src.core",
        "src.ui",
        "src.core.downloader",
        "src.ui.main_window"
    ],
    
    # Hariç tutulacak modüller
    "excludes": [
        "unittest",
        "pydoc",
        "tkinter.test",
        "distutils"
    ],
    
    # Dosyalar
    "include_files": include_files,
    
    # ZIP paket yapılandırması
    "zip_include_packages": "*",  # Tüm paketleri zip içine al
    "zip_exclude_packages": None, # Hiçbir paketi hariç tutma
    
    # Ek ayarlar
    "include_msvcr": True,      # Windows için MSVC runtime
    "optimize": 0,              # Optimize etme (hata ayıklama için)
    "build_exe": "build/dist",  # Çıkış klasörü
}

# MSI kurulum paketi için seçenekler
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-5678-abcd-1234567890ab}",
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFilesFolder]\%s" % "YTDownloader",
}

# Executable oluşturma
executables = [
    Executable(
        script="startup.py",       # Kullanılacak başlangıç betiği
        base=base,
        target_name="YTDownloader.exe",
        icon="icon.ico",
        shortcut_name="YouTube Downloader",
        shortcut_dir="DesktopFolder",
        copyright="YT Downloader Team 2025"
    )
]

# Setup yapılandırması
setup(
    name="YTDownloader",
    version="1.0.0",
    description="YouTube videoları ve ses dosyalarını indirmek için arayüz",
    author="YT Downloader Team",
    author_email="example@example.com",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=executables
) 