import sys
import os
import subprocess
import PyInstaller.__main__

# FFmpeg kontrolü
subprocess.run(['winget', 'install', '--id', 'Gyan.FFmpeg'], check=False)

# __init__.py dosyalarını oluştur
for path in ['src', 'src/core', 'src/ui']:
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            pass

# PyInstaller çağrısı
PyInstaller.__main__.run([
    'src/main.py',
    '--name=YTDownloader',
    '--icon=icon.ico',
    '--windowed',
    '--add-data=assets;assets',
    '--add-data=src;src',
    '--add-data=icon.ico;.',
    '--hidden-import=PyQt6',
    '--hidden-import=yt_dlp',
    '--hidden-import=src.core.downloader',
    '--hidden-import=src.ui.main_window',
])

print("Derleme tamamlandı. dist/YTDownloader klasöründe bulabilirsiniz.") 