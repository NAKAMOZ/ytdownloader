import os
import sys
import subprocess
import shutil
from pathlib import Path
from setuptools import setup, find_packages

# Uygulama bilgileri
APP_NAME = "YouTube Downloader"
APP_VERSION = "1.0.0"
AUTHOR = "YT Downloader"
DESCRIPTION = "YouTube'dan video ve ses dosyalarını indirmek için kullanılan bir uygulama"

def run_pre_install_commands():
    """Kurulum öncesi komutları çalıştırır"""
    print("Ön kurulum işlemleri yapılıyor...")
    
    # Gereksinimleri yükle
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # FFmpeg kontrolü ve kurulumu
    try:
        print("FFmpeg varlığı kontrol ediliyor...")
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print("FFmpeg yüklü değil. Winget ile kurulum deneniyor...")
            try:
                # Winget ile FFmpeg kurulumu
                subprocess.run(["winget", "install", "ffmpeg"], check=True)
                print("FFmpeg başarıyla yüklendi.")
            except FileNotFoundError:
                print("Winget bulunamadı. Manuel kurulum gerekiyor.")
                print("Lütfen FFmpeg'i https://ffmpeg.org/download.html adresinden indirin ve yükleyin.")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg kurulumu sırasında hata oluştu: {e}")
                print("Lütfen FFmpeg'i manuel olarak kurun: https://ffmpeg.org/download.html")
        else:
            print("FFmpeg zaten yüklü.")
    except Exception as e:
        print(f"FFmpeg kontrolü sırasında beklenmeyen bir hata oluştu: {e}")
    
    print("Ön kurulum işlemleri tamamlandı.")

def create_executable():
    """PyInstaller ile çalıştırılabilir dosya oluşturur"""
    print("Çalıştırılabilir dosya oluşturuluyor...")
    
    # Eski build ve dist dizinlerini temizle
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller parametreleri - Güvenlik uyarılarını azaltmak için ayarlar
    pyinstaller_cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--noupx",             # UPX sıkıştırması kullanma (bazı antivirüsler şüpheli görebilir)
        "--exclude-module", "_bootlocale",  # Gereksiz modülleri hariç tut
        "--key", "YTDownloader2024",  # Özel şifreleme anahtarı (antivirus yanlış pozitiflerini azaltabilir)
        "--name", "YouTubeDownloader",
        "--icon=icon.ico",
        "--add-binary", "LICENSE.txt;.",
        "--add-binary", "README.md;.",
        "main.py"
    ]
    
    subprocess.run(pyinstaller_cmd, check=True)
    print("Çalıştırılabilir dosya oluşturuldu: dist/YouTubeDownloader.exe")

def run_post_install_commands():
    """Kurulum sonrası komutları çalıştırır"""
    print("Son kurulum işlemleri yapılıyor...")
    
    # NSIS ile kurulum dosyası oluştur
    try:
        subprocess.run(["makensis", "installer.nsi"], check=True)
        print("Kurulum dosyası oluşturuldu: YouTubeDownloader-Setup.exe")
    except FileNotFoundError:
        print("NSIS bulunamadı. Kurulum dosyası oluşturulamadı.")
        print("NSIS'i indirmek için: https://nsis.sourceforge.io/Download")
    except subprocess.CalledProcessError as e:
        print(f"NSIS kurulum dosyası oluşturulurken hata: {e}")
    
    print("Son kurulum işlemleri tamamlandı.")

if __name__ == "__main__":
    # Kurulum öncesi komutları çalıştır
    run_pre_install_commands()
    
    # Setuptools yapılandırması
    setup(
        name=APP_NAME,
        version=APP_VERSION,
        author=AUTHOR,
        description=DESCRIPTION,
        packages=find_packages(),
        python_requires=">=3.8",
        install_requires=[
            "PyQt6>=6.5.0",
            "yt-dlp>=2023.12.0",
            "ffmpeg-python>=0.2.0",
        ],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
    
    # Çalıştırılabilir dosya oluştur
    create_executable()
    
    # Kurulum sonrası komutları çalıştır
    run_post_install_commands() 