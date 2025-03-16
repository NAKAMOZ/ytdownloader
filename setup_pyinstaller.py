import sys
import os
import subprocess
import shutil
import urllib.request
import zipfile
import tempfile
import ctypes
import platform
from pathlib import Path
import PyInstaller.__main__

# FFmpeg kontrolünü geliştiren fonksiyon
def check_ffmpeg():
    """FFmpeg'in sistemde yüklü olup olmadığını kontrol eder ve gerekirse kurar."""
    print("FFmpeg kontrolü yapılıyor...")
    
    # FFmpeg'in mevcut olup olmadığını kontrol et
    ffmpeg_installed = False
    ffmpeg_path = None
    
    try:
        # Komut satırından çalıştırma deneyin
        result = subprocess.run(['ffmpeg', '-version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               timeout=5)
        if result.returncode == 0:
            ffmpeg_installed = True
            print("FFmpeg sistemde zaten yüklü.")
            
            # FFmpeg'in yolunu bulmaya çalış
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, "ffmpeg.exe")
                if os.path.isfile(exe_file):
                    ffmpeg_path = exe_file
                    print(f"FFmpeg yolu: {ffmpeg_path}")
                    break
    except (subprocess.SubprocessError, FileNotFoundError):
        ffmpeg_installed = False
        print("FFmpeg bulunamadı.")
    
    if not ffmpeg_installed:
        install_ffmpeg()
    
    return ffmpeg_path

def is_admin():
    """Programın yönetici olarak çalışıp çalışmadığını kontrol eder."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def install_ffmpeg():
    """FFmpeg'i indirir ve kurar."""
    print("FFmpeg kurulumu başlatılıyor...")
    
    # Önce winget ile kurulum deneyin
    try:
        print("FFmpeg winget ile kuruluyor...")
        subprocess.run(['winget', 'install', '--id', 'Gyan.FFmpeg'], check=False, timeout=120)
        
        # Kurulumun başarılı olup olmadığını kontrol et
        result = subprocess.run(['ffmpeg', '-version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               timeout=5)
        if result.returncode == 0:
            print("FFmpeg başarıyla kuruldu.")
            return
    except Exception as e:
        print(f"Winget ile kurulum sırasında hata: {e}")
    
    # Winget ile kurulamadıysa, manuel indirme ve kurma işlemi
    try:
        print("FFmpeg manuel olarak indiriliyor...")
        # Geçici klasör oluştur
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")
        
        # FFmpeg'i indir
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        print(f"FFmpeg indiriliyor: {ffmpeg_url}")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # Zip dosyasını çıkart
        print("Zip dosyası çıkartılıyor...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # ffmpeg.exe dosyasını bul
        ffmpeg_folder = None
        for root, dirs, _ in os.walk(temp_dir):
            for dir_name in dirs:
                if 'ffmpeg' in dir_name.lower():
                    ffmpeg_folder = os.path.join(root, dir_name)
                    break
            if ffmpeg_folder:
                break
        
        if not ffmpeg_folder:
            raise Exception("FFmpeg klasörü bulunamadı")
        
        # bin klasöründeki FFmpeg binary'sini bul
        ffmpeg_bin = None
        for root, _, files in os.walk(ffmpeg_folder):
            if 'bin' in root.lower():
                for file in files:
                    if file.lower() == 'ffmpeg.exe':
                        ffmpeg_bin = os.path.join(root, file)
                        break
                if ffmpeg_bin:
                    break
        
        if not ffmpeg_bin:
            raise Exception("ffmpeg.exe bulunamadı")
        
        # Program Files klasörüne kopyala veya uygulama klasörüne ekle
        if is_admin():
            ffmpeg_install_dir = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'FFmpeg', 'bin')
            os.makedirs(ffmpeg_install_dir, exist_ok=True)
            shutil.copy2(ffmpeg_bin, os.path.join(ffmpeg_install_dir, 'ffmpeg.exe'))
            
            # PATH'e ekle
            os.system(f'setx PATH "%PATH%;{ffmpeg_install_dir}" /M')
            print(f"FFmpeg {ffmpeg_install_dir} klasörüne kuruldu ve PATH'e eklendi.")
        else:
            # Uygulama klasörüne kopyala
            local_ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg.exe')
            shutil.copy2(ffmpeg_bin, local_ffmpeg)
            print(f"FFmpeg uygulama klasörüne kopyalandı: {local_ffmpeg}")
        
        # Geçici dosyaları temizle
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"FFmpeg manuel kurulumu sırasında hata: {e}")
        print("Lütfen FFmpeg'i manuel olarak kurun: https://ffmpeg.org/download.html")
        input("Devam etmek için ENTER tuşuna basın...")

# FFmpeg kontrolü
ffmpeg_path = check_ffmpeg()

# Gerekli paketlerin kontrolü
try:
    import ffmpeg
    print("ffmpeg-python kütüphanesi mevcut.")
except ImportError:
    print("ffmpeg-python kütüphanesi kuruluyor...")
    subprocess.run([sys.executable, "-m", "pip", "install", "ffmpeg-python"], check=True)
    try:
        import ffmpeg
        print("ffmpeg-python kütüphanesi başarıyla kuruldu.")
    except ImportError:
        print("UYARI: ffmpeg-python kütüphanesi kurulamadı.")

try:
    import PyQt6
    print("PyQt6 kütüphanesi mevcut.")
except ImportError:
    print("PyQt6 kütüphanesi kuruluyor...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6"], check=True)

try:
    import yt_dlp
    print("yt_dlp kütüphanesi mevcut.")
except ImportError:
    print("yt_dlp kütüphanesi kuruluyor...")
    subprocess.run([sys.executable, "-m", "pip", "install", "yt_dlp"], check=True)

# __init__.py dosyalarını oluştur
for path in ['src', 'src/core', 'src/ui']:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            pass
        print(f"Oluşturuldu: {init_file}")

# FFmpeg yolu varsa, PyInstaller'a ekle
data_files = [
    ('assets', 'assets'),
    ('src', 'src'),
    ('icon.ico', '.'),
]

if ffmpeg_path and os.path.exists(ffmpeg_path):
    ffmpeg_dest = '.'
    data_files.append((ffmpeg_path, ffmpeg_dest))
    print(f"FFmpeg ({ffmpeg_path}) derleme paketine dahil edilecek.")

# PyInstaller çağrısı için eklentileri hazırla
hidden_imports = [
    'PyQt6',
    'yt_dlp',
    'ffmpeg',
    'ffmpeg.audio',
    'ffmpeg.video',
    'src.core.downloader',
    'src.ui.main_window',
]

# Veri dosyalarını hazırla
add_data_args = []
for src, dest in data_files:
    if os.path.exists(src):
        add_data_args.append(f'--add-data={src};{dest}')
    else:
        print(f"UYARI: {src} bulunamadı, paketlemeye dahil edilemeyecek.")

# Hidden import argümanlarını hazırla
hidden_import_args = []
for imp in hidden_imports:
    hidden_import_args.append(f'--hidden-import={imp}')

# PyInstaller argümanları
pyinstaller_args = [
    'src/main.py',
    '--name=YTDownloader',
    '--icon=icon.ico',
    '--windowed',
    '--clean',
    '--noconfirm',
    *add_data_args,
    *hidden_import_args,
]

# Kullanıcıya bilgi
print("\n--- PyInstaller Derleme Yapılandırması ---")
print(f"Kaynak script: src/main.py")
print(f"Derleme adı: YTDownloader")
print(f"Eklenecek veri dosyaları: {', '.join(src for src, _ in data_files)}")
print(f"Gizli importlar: {', '.join(hidden_imports)}")
print("\nDerleme başlatılıyor...")

# PyInstaller çağrısı
try:
    PyInstaller.__main__.run(pyinstaller_args)
    print("\nDerleme tamamlandı. dist/YTDownloader klasöründe uygulamayı bulabilirsiniz.")
    
    # Derleme sonrası kontrol
    executable_path = os.path.join('dist', 'YTDownloader', 'YTDownloader.exe')
    if os.path.exists(executable_path):
        print(f"Çalıştırılabilir dosya başarıyla oluşturuldu: {os.path.abspath(executable_path)}")
        
        # FFmpeg dosyasını kontrol et
        dist_ffmpeg = os.path.join('dist', 'YTDownloader', 'ffmpeg.exe')
        if not os.path.exists(dist_ffmpeg) and ffmpeg_path:
            print("FFmpeg dosyası derleme klasörüne kopyalanıyor...")
            shutil.copy2(ffmpeg_path, dist_ffmpeg)
    else:
        print("UYARI: Çalıştırılabilir dosya bulunamadı. Derleme sırasında bir hata oluşmuş olabilir.")
except Exception as e:
    print(f"\nDerleme sırasında hata oluştu: {e}") 