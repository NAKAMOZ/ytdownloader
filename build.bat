@echo off
echo YouTube Downloader - Kurulum Paketi Olusturucu

REM Gerekli paketleri yükle
echo Gerekli paketler yukleniyor...
pip install -r requirements.txt
pip install pyinstaller
pip install pywin32

REM Eski build ve dist klasörlerini temizle
echo Eski build klasorleri temizleniyor...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Uygulama simgesi için kontrol et
if not exist icon.ico (
    echo Uygulama simgesi (icon.ico) bulunamadı. Varsayılan simge kullanılacak.
)

REM LICENSE.txt dosyası için kontrol et
if not exist LICENSE.txt (
    echo LICENSE.txt dosyası bulunamadı. Basit bir lisans dosyası oluşturuluyor...
    echo YouTube Downloader - Lisans Sözleşmesi > LICENSE.txt
    echo. >> LICENSE.txt
    echo Bu yazılım, kullanıcıların YouTube'dan video ve ses indirmelerine olanak tanır. >> LICENSE.txt
    echo. >> LICENSE.txt
    echo Bu yazılımı kullanarak, telif hakkı yasalarına uygun şekilde kullanmayı kabul etmiş olursunuz. >> LICENSE.txt
    echo Telif hakkı ihlali yapan indirmelerden kullanıcı sorumludur. >> LICENSE.txt
)

REM PyInstaller ile exe dosyası oluştur
echo Uygulama exe dosyasi olusturuluyor...
pyinstaller --clean ^
  --onefile ^
  --windowed ^
  --noupx ^
  --exclude-module _bootlocale ^
  --name YouTubeDownloader ^
  --icon=icon.ico ^
  --add-binary "LICENSE.txt;." ^
  --add-binary "README.md;." ^
  main.py

REM Kurulum dosyası oluştur
echo NSIS ile kurulum dosyasi olusturuluyor...
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
    echo Kurulum dosyasi olusturuldu: YouTubeDownloader-Setup.exe
) else if exist "C:\Program Files\NSIS\makensis.exe" (
    "C:\Program Files\NSIS\makensis.exe" installer.nsi
    echo Kurulum dosyasi olusturuldu: YouTubeDownloader-Setup.exe
) else (
    echo NSIS bulunamadi! Kurulum dosyasi oluşturulamadı.
    echo NSIS'i buradan indirebilirsiniz: https://nsis.sourceforge.io/Download
)

echo Islem tamamlandi!
echo YouTubeDownloader-Setup.exe dosyasi olusturuldu.
echo Exe dosyası: dist\YouTubeDownloader.exe
if exist YouTubeDownloader-Setup.exe (
    echo Kurulum dosyası: YouTubeDownloader-Setup.exe
)
echo.
pause 