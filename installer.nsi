; YouTube Downloader Kurulum Betiği
; NSIS (Nullsoft Scriptable Install System) kullanılarak oluşturulmuştur

; Unicode desteği
Unicode true

; Uygulama bilgileri
!define APP_NAME "YouTube Downloader"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "YT Downloader"
!define APP_WEBSITE "https://github.com/ytdownloader"
!define APP_ICON "icon.ico"
!define APP_EXE "YouTubeDownloader.exe"

; Modern UI tanımlamaları
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

; Genel ayarlar
Name "${APP_NAME}"
OutFile "YouTubeDownloader-Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"
RequestExecutionLevel admin

; MUI ayarları
!define MUI_ABORTWARNING
!define MUI_ICON "${APP_ICON}"
!define MUI_UNICON "${APP_ICON}"
!define MUI_WELCOMEFINISHPAGE_BITMAP "welcome.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp"
!define MUI_HEADERIMAGE_RIGHT

; Kurulum sayfaları
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Programi simdi calistir"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.md"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Beni Oku dosyasini goster"
!insertmacro MUI_PAGE_FINISH

; Kaldırma sayfaları
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Dil dosyası - ÖNEMLİ: Dil tanımı sayfa tanımlarından sonra olmalı
!insertmacro MUI_LANGUAGE "Turkish"

; Kurulum bölümleri
Section "YouTube Downloader (Gerekli)" SecMain
  SectionIn RO ; Bu bölüm zorunlu
  SetOutPath "$INSTDIR"
  
  ; Uygulama dosyalarını kopyala
  File "dist\${APP_EXE}"
  File /r "dist\*.*"
  File "LICENSE.txt"
  File "README.md"
  File "icon.ico"
  
  ; FFmpeg'i kontrol et ve gerekirse indir
  Call CheckFFmpeg
  
  ; Başlat menüsü kısayolları oluştur
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Kaldir.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  
  ; Kaldırma bilgilerini kaydet
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_WEBSITE}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
  
  ; Kurulum boyutunu hesapla
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "EstimatedSize" "$0"
  
  ; Kaldırma programını oluştur
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Masaustu Kisayolu" SecDesktop
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
SectionEnd

Section "Baslangicta Calistir" SecStartup
  CreateShortcut "$SMSTARTUP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
SectionEnd

; Bölüm açıklamaları
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "YouTube Downloader uygulamasinin temel bilesenleri."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Masaustune bir kisayol ekler."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartup} "Windows baslangicinda uygulamayi otomatik olarak baslatir."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; FFmpeg'i kontrol et ve gerekirse indir
Function CheckFFmpeg
  ; FFmpeg'in yüklü olup olmadığını kontrol et
  nsExec::ExecToStack 'cmd.exe /c "where ffmpeg"'
  Pop $0
  Pop $1
  
  ${If} $0 != 0
    MessageBox MB_YESNO "FFmpeg bulunamadi. FFmpeg, video ve ses isleme icin gereklidir. Winget ile yuklemek ister misiniz?" IDYES winget_install IDNO manual_install
    
    winget_install:
      ; Winget ile FFmpeg'i yükle
      DetailPrint "Winget ile FFmpeg yukleniyor..."
      nsExec::ExecToStack 'cmd.exe /c "winget install ffmpeg"'
      Pop $0
      Pop $1
      
      ${If} $0 == 0
        DetailPrint "FFmpeg basariyla yuklendi."
      ${Else}
        DetailPrint "Winget ile FFmpeg yuklenirken hata olustu: $1"
        MessageBox MB_YESNO "Winget ile FFmpeg yuklenemedi. Manuel olarak indirmek ister misiniz?" IDYES manual_install IDNO skip
      ${EndIf}
      Goto skip
    
    manual_install:
      MessageBox MB_OK "Lutfen kurulumdan sonra FFmpeg'i manuel olarak indirip kurun: https://ffmpeg.org/download.html"
      Goto skip
    
    skip:
  ${EndIf}
FunctionEnd

; Kaldırma bölümü
Section "Uninstall"
  ; Uygulama dosyalarını kaldır
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\ffmpeg.exe"
  Delete "$INSTDIR\ffprobe.exe"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\icon.ico"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR"
  
  ; Kısayolları kaldır
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Kaldir.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMSTARTUP\${APP_NAME}.lnk"
  
  ; Kayıt defteri girdilerini kaldır
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  DeleteRegKey HKLM "Software\${APP_NAME}"
SectionEnd 