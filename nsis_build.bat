@echo off
echo YouTube Downloader - NSIS Kurulum Olusturucu
echo =============================================

REM NSIS'in kurulu olduğu olası dizinleri kontrol et
set NSIS_FOUND=0

REM 64-bit yüklemeler için kontrol
if exist "C:\Program Files\NSIS\makensis.exe" (
    set NSIS_EXE="C:\Program Files\NSIS\makensis.exe"
    set NSIS_FOUND=1
    echo NSIS 64-bit surumu bulundu.
    goto MAKE_INSTALLER
)

REM 32-bit yüklemeler için kontrol
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    set NSIS_EXE="C:\Program Files (x86)\NSIS\makensis.exe"
    set NSIS_FOUND=1
    echo NSIS 32-bit surumu bulundu.
    goto MAKE_INSTALLER
)

REM NSIS bulunmadı
if %NSIS_FOUND%==0 (
    echo HATA: NSIS bulunamadi!
    echo NSIS'i buradan indirip kurun: https://nsis.sourceforge.io/Download
    echo Sonra bu batch dosyasini tekrar calistirin.
    goto END
)

:MAKE_INSTALLER
echo.
echo installer.nsi dosyasi isleniyor...
echo.

REM NSIS'i verbose modda çalıştır (hataların görünmesi için)
%NSIS_EXE% /V4 installer.nsi

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo HATA: NSIS kurulum dosyasi olusturulamadi!
    echo Hata kodu: %ERRORLEVEL%
    echo.
    echo Olası sorunlar:
    echo 1. installer.nsi dosyasinda sentaks hatasi olabilir
    echo 2. Gerekli eklentiler eksik olabilir
    echo 3. Dosya izinleri yetersiz olabilir
    echo.
    echo Ayrintili NSIS hatalarini gormek icin yukaridaki ciktiyi inceleyin.
) else (
    echo.
    echo BASARILI: YouTubeDownloader-Setup.exe dosyasi olusturuldu!
    echo.
)

:END
echo.
echo Islemi sonlandirmak icin herhangi bir tusa basin...
pause > nul 