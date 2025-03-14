import os
import sys
import subprocess

def add_paths_to_environment():
    # Mevcut dizini al
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # FFmpeg dizinini PATH'e ekle
    ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        print(f"FFmpeg yolu: {ffmpeg_path}")
        os.environ["PATH"] = current_dir + os.pathsep + os.environ["PATH"]
    else:
        print("FFmpeg bulunamadı, sistem PATH'inde aranacak")
    
    # src dizinini Python path'ine ekle (modül import sorununu çözmek için)
    src_path = os.path.join(current_dir, "src")
    if src_path not in sys.path:
        sys.path.insert(0, current_dir)
        sys.path.insert(0, src_path)
        print(f"Python yolu eklendi: {current_dir}, {src_path}")

if __name__ == "__main__":
    add_paths_to_environment()
    
    # Ana uygulamayı başlat
    from src.main import main
    main() 