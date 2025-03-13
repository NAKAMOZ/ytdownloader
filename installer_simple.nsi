; YouTube Downloader için Basit NSIS Kurulum Dosyası
; Sorun Giderme Testi İçin

; Unicode desteği 
Unicode true

!define APP_NAME "YouTube Downloader"
!define APP_VERSION "1.0.0"
!define APP_EXE "YouTubeDownloader.exe"

; Modern UI tanımları
!include "MUI2.nsh"

; Genel ayarlar
Name "${APP_NAME}"
OutFile "YouTubeDownloader-Simple-Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"
RequestExecutionLevel admin

; Modern UI ayarları
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; Kurulum sayfaları
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Kaldırma sayfaları
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Dil dosyası
!insertmacro MUI_LANGUAGE "Turkish"

; Ana kurulum bölümü
Section "YouTube Downloader (Gerekli)" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"
  
  ; Dosyaları kopyala
  File "dist\${APP_EXE}"
  File "LICENSE.txt"
  File "README.md"
  File "icon.ico"
  
  ; Kısayollar oluştur
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Kaldır.lnk" "$INSTDIR\uninstall.exe"
  
  ; Kaldırma bilgilerini kaydet
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  
  ; Kaldırma programını oluştur
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Kaldırma bölümü
Section "Uninstall"
  ; Dosyaları sil
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\icon.ico"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Dizinleri sil
  RMDir "$INSTDIR"
  
  ; Kısayolları sil
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Kaldır.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  
  ; Kayıt defteri girdilerini sil
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd 