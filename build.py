#!/usr/bin/env python3
"""
Build script for YouTube Downloader
Creates executable and installer
"""

import os
import sys
import shutil
import subprocess
import platform

def setup_environment():
    """Setup build environment and install dependencies"""
    print("Setting up build environment...")
    
    # Install dependencies
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    if platform.system() == "Windows":
        subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=True)
    
    # Clean previous build artifacts
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Create necessary directories
    os.makedirs("assets", exist_ok=True)

def build_executable():
    """Build executable with PyInstaller"""
    print("Building executable...")
    
    icon_path = os.path.join("assets", "icon.ico")
    if not os.path.exists(icon_path):
        print("Warning: Icon file not found, using default icon")
        icon_path = ""
    
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--noupx",
        "--name", "YouTubeDownloader",
    ]
    
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # Add main file
    cmd.append(os.path.join("src", "main.py"))
    
    subprocess.run(cmd, check=True)
    
    print("Executable created successfully!")

def build_installer():
    """Build installer with NSIS (Windows only)"""
    if platform.system() != "Windows":
        print("Installer creation is only supported on Windows")
        return
    
    print("Building installer...")
    
    # Check if NSIS is installed
    nsis_paths = [
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\Program Files (x86)\NSIS\makensis.exe"
    ]
    
    nsis_exe = None
    for path in nsis_paths:
        if os.path.exists(path):
            nsis_exe = path
            break
    
    if not nsis_exe:
        print("NSIS not found. Please install NSIS from https://nsis.sourceforge.io/Download")
        print("Skipping installer creation")
        return
    
    # Copy necessary files for installer
    if not os.path.exists("installer"):
        os.makedirs("installer")
    
    # Create simple NSIS script if not exists
    nsis_script = "installer.nsi"
    if not os.path.exists(nsis_script):
        create_nsis_script(nsis_script)
    
    # Run NSIS
    subprocess.run([nsis_exe, nsis_script], check=True)
    print("Installer created successfully!")

def create_nsis_script(filename):
    """Create a basic NSIS script"""
    print("Creating NSIS script...")
    
    script = """
; YouTube Downloader Installer Script
Unicode true

!define APP_NAME "YouTube Downloader"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "YouTube Downloader"
!define APP_EXE "YouTubeDownloader.exe"

!include "MUI2.nsh"

Name "${APP_NAME}"
OutFile "YouTubeDownloader-Setup.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icon.ico"
!define MUI_UNICON "assets\\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "YouTube Downloader (Required)" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"
  
  ; Copy files
  File "dist\\${APP_EXE}"
  File "LICENSE"
  File "README.md"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
  
  ; Create desktop shortcut
  CreateShortcut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
  
  ; Write registry keys for uninstaller
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayIcon" "$INSTDIR\\${APP_EXE}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\\${APP_EXE}"
  Delete "$INSTDIR\\LICENSE"
  Delete "$INSTDIR\\README.md"
  Delete "$INSTDIR\\uninstall.exe"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk"
  Delete "$DESKTOP\\${APP_NAME}.lnk"
  
  ; Remove directories
  RMDir "$SMPROGRAMS\\${APP_NAME}"
  RMDir "$INSTDIR"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}"
SectionEnd
"""
    
    with open(filename, "w") as f:
        f.write(script)

def main():
    """Main function"""
    try:
        setup_environment()
        build_executable()
        build_installer()
        print("Build completed successfully!")
    except Exception as e:
        print(f"Error during build: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main()) 