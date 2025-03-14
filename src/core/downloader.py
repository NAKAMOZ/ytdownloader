import os
import threading
import traceback
import urllib.request
import subprocess
from PyQt6.QtCore import pyqtSignal, QObject

try:
    import yt_dlp
except ImportError as e:
    print(f"Failed to import yt-dlp library: {e}")
    print("Please install it with 'pip install yt-dlp'")
    import sys
    sys.exit(1)

try:
    import ffmpeg
except ImportError as e:
    print(f"Failed to import ffmpeg-python library: {e}")
    print("Please install it with 'pip install ffmpeg-python'")
    import sys
    sys.exit(1)

class DownloadSignals(QObject):
    progress = pyqtSignal(float)
    finished = pyqtSignal(str, str, str)
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    playlist_progress = pyqtSignal(int, int)

class YouTubeDownloader:
    
    def __init__(self):
        self.signals = DownloadSignals()
        self.download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        self.downloaded_files = []
        self.skip_private = True  # Özel videoları atlama seçeneği (varsayılan olarak aktif)
        self.is_downloading = False  # İndirme durumunu takip etmek için değişken
        os.makedirs(self.download_directory, exist_ok=True)
    
    def set_download_directory(self, directory):
        self.download_directory = directory
        os.makedirs(self.download_directory, exist_ok=True)
    
    def set_skip_private(self, skip):
        """Özel videoları atlama seçeneğini ayarlar"""
        self.skip_private = skip
    
    def stop_download(self):
        """İndirme işlemini durdurur"""
        if self.is_downloading:
            self.is_downloading = False
            self.signals.status.emit("Download cancelled by user")
    
    def start_download(self, url, is_video, quality, is_playlist=False):
        # Aktif indirme varsa iptal et
        if self.is_downloading:
            self.signals.status.emit("Download already in progress")
            return
            
        self.is_downloading = True
        threading.Thread(
            target=self.download_thread,
            args=(url, is_video, quality, is_playlist),
            daemon=True
        ).start()
    
    def download_thread(self, url, is_video, quality, is_playlist=False):
        try:
            self.signals.status.emit("Getting information...")
            
            info_opts = {
                'quiet': True,
                'no_warnings': True, 
                'noplaylist': not is_playlist,
                'skip_download': True
            }
            
            # Özel videoları hata olmadan atlamak için ignoreerrors ekleyelim
            if self.skip_private:
                info_opts['ignoreerrors'] = True
            
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # İşlem iptal edildiyse çık
                if not self.is_downloading:
                    self.signals.status.emit("Download cancelled")
                    return
                
                if is_playlist and 'entries' in info:
                    entries = list(info['entries'])
                    # None değerleri filtreleme (atlanmış videolar)
                    entries = [entry for entry in entries if entry is not None]
                    
                    total_videos = len(entries)
                    self.signals.status.emit(f"Playlist found: {total_videos} videos")
                    
                    for i, entry in enumerate(entries):
                        # İşlem iptal edildiyse döngüden çık
                        if not self.is_downloading:
                            self.signals.status.emit("Download cancelled")
                            break
                            
                        self.signals.playlist_progress.emit(i+1, total_videos)
                        self.signals.status.emit(f"Downloading: Item {i+1}/{total_videos}")
                        
                        is_last_video = (i == len(entries) - 1)
                        success = self.download_single_video(entry, is_video, quality, notify_completion=is_last_video)
                        
                        # Video özel ise ve atlanması gerekiyorsa
                        if not success and self.skip_private:
                            self.signals.status.emit(f"Skipped private video: {entry.get('title', 'Unknown')}")
                else:
                    if info is not None:  # None olabilir (atlanmış video)
                        success = self.download_single_video(info, is_video, quality, notify_completion=True)
                        if not success and self.skip_private:
                            self.signals.status.emit(f"Skipped private video: {info.get('title', 'Unknown')}")
                    else:
                        self.signals.error.emit("Could not retrieve video information. It might be private or deleted.")
            
            # İndirme işlemi tamamlandı
            self.is_downloading = False
            
        except Exception as e:
            error_msg = str(e)
            print(f"Download error: {error_msg}")
            print("Error details:")
            traceback.print_exc()
            self.signals.error.emit(error_msg)
            self.signals.status.emit("Error occurred")
            self.is_downloading = False
    
    def download_single_video(self, info, is_video, quality, notify_completion=True):
        try:
            # İşlem iptal edildiyse çık
            if not self.is_downloading:
                return False
                
            video_title = info.get('title', 'video')
            video_id = info.get('id', '')
            video_url = info.get('webpage_url', '') or info.get('url', '')
            
            # Özel video kontrolü
            if 'private' in info.get('_type', '') or 'private' in info.get('availability', ''):
                if self.skip_private:
                    return False
            
            video_title = self.clean_filename(video_title)
            
            # Thumbnail kısmını kaldırıyoruz
            thumbnail_path = ""
            
            self.signals.status.emit("Starting download...")
            
            output_template = os.path.join(self.download_directory, f"{video_title}.%(ext)s")
            
            if not is_video:
                audio_quality_map = {
                    "320 kbps": "320",
                    "256 kbps": "256",
                    "192 kbps": "192",
                    "128 kbps": "128",
                    "96 kbps": "96"
                }
                audio_quality = audio_quality_map.get(quality, "192")
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                    'nopostoverwrites': False,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': audio_quality,
                    }]
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # İşlem iptal edildiyse çık
                        if not self.is_downloading:
                            return False
                            
                        ydl.download([video_url])
                except Exception as e:
                    error_msg = str(e)
                    if "Private video" in error_msg or "Sign in to confirm" in error_msg:
                        if self.skip_private:
                            return False
                    else:
                        raise e
                
                filepath = os.path.join(self.download_directory, f"{video_title}.mp3")
                file_ext = "mp3"
                
            else:
                self.signals.status.emit("Downloading...")
                video_path = os.path.join(self.download_directory, f"{video_title}.mp4")
                
                format_map = {
                    "Best Quality": "bestvideo[ext=mp4]/best[ext=mp4]",
                    "1080p": "bestvideo[height<=1080][ext=mp4]/best[height<=1080][ext=mp4]",
                    "720p": "bestvideo[height<=720][ext=mp4]/best[height<=720][ext=mp4]",
                    "480p": "bestvideo[height<=480][ext=mp4]/best[height<=480][ext=mp4]",
                    "360p": "bestvideo[height<=360][ext=mp4]/best[height<=360][ext=mp4]",
                    "240p": "bestvideo[height<=240][ext=mp4]/best[height<=240][ext=mp4]"
                }
                format_str = format_map.get(quality, "bestvideo[ext=mp4]/best[ext=mp4]")
                
                ydl_opts = {
                    'format': format_str,
                    'outtmpl': output_template,
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                    'nopostoverwrites': False,
                    'postprocessors': [],
                    'noplaylist': True,
                    'keepvideo': True
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # İşlem iptal edildiyse çık
                        if not self.is_downloading:
                            return False
                            
                        ydl.download([video_url])
                except Exception as e:
                    error_msg = str(e)
                    if "Private video" in error_msg or "Sign in to confirm" in error_msg:
                        if self.skip_private:
                            return False
                    else:
                        raise e
                
                # İşlem iptal edildiyse çık
                if not self.is_downloading:
                    return False
                
                self.signals.status.emit("Downloading audio component...")
                audio_format_map = {
                    "Best Quality": "bestaudio[ext=m4a]/best[ext=m4a]",
                    "1080p": "bestaudio[ext=m4a]/best[ext=m4a]",
                    "720p": "bestaudio[ext=m4a]/best[ext=m4a]",
                    "480p": "bestaudio[ext=m4a]/best[ext=m4a]",
                    "360p": "bestaudio[ext=m4a]/best[ext=m4a]",
                    "240p": "bestaudio[ext=m4a]/best[ext=m4a]"
                }
                audio_format_str = audio_format_map.get(quality, "bestaudio[ext=m4a]/best[ext=m4a]")
                
                audio_ydl_opts = {
                    'format': audio_format_str,
                    'outtmpl': output_template,
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                    'nopostoverwrites': False,
                    'postprocessors': [],
                    'noplaylist': True
                }
                
                try:
                    with yt_dlp.YoutubeDL(audio_ydl_opts) as ydl:
                        # İşlem iptal edildiyse çık
                        if not self.is_downloading:
                            return False
                            
                        ydl.download([video_url])
                except Exception as e:
                    error_msg = str(e)
                    if "Private video" in error_msg or "Sign in to confirm" in error_msg:
                        if self.skip_private:
                            return False
                    else:
                        raise e
                
                audio_path = os.path.join(self.download_directory, f"{video_title}.m4a")
                
                if os.path.exists(video_path) and os.path.exists(audio_path):
                    self.signals.status.emit("Merging files...")
                    merged_path = os.path.join(self.download_directory, f"{video_title}_merged.mp4")
                    
                    try:
                        cmd = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{merged_path}"'
                        result = subprocess.run(
                            cmd, 
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode != 0:
                            raise Exception(f"ffmpeg error: {result.stderr}")
                        
                        if os.path.exists(merged_path):
                            os.remove(video_path)
                            os.remove(audio_path)
                            os.rename(merged_path, video_path)
                    except Exception as e:
                        print(f"Video and audio merging error: {e}")
                        traceback.print_exc()
                        self.signals.error.emit(f"Video and audio merging error: {e}")
                
                filepath = video_path
                file_ext = "mp4"
            
            filename = os.path.basename(filepath)
            
            if notify_completion:
                self.signals.finished.emit(filename, filepath, thumbnail_path)
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"Video download error: {error_msg}")
            traceback.print_exc()
            self.signals.error.emit(error_msg)
            return False
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # İşlem iptal edildiyse çık
                if not self.is_downloading:
                    raise Exception("Download cancelled by user")
                    
                if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] > 0:
                    p = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed_str = self.format_size(speed) + "/s"
                        status_text = f"Downloading... {self.format_size(d['downloaded_bytes'])}/{self.format_size(d['total_bytes'])} ({speed_str})"
                        self.signals.status.emit(status_text)
                    self.signals.progress.emit(p)
                elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                    p = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed_str = self.format_size(speed) + "/s"
                        status_text = f"Downloading... {self.format_size(d['downloaded_bytes'])}/{self.format_size(d['total_bytes_estimate'])} ({speed_str})"
                        self.signals.status.emit(status_text)
                    self.signals.progress.emit(p)
                elif '_percent_str' in d:
                    percent_str = d.get('_percent_str', '0%')
                    status_text = f"Downloading... {percent_str} {d.get('_speed_str', '')}"
                    self.signals.status.emit(status_text)
                    
                    percent_str = percent_str.replace('%', '').strip()
                    try:
                        p = float(percent_str)
                        self.signals.progress.emit(p)
                    except (ValueError, TypeError):
                        pass
            except Exception as e:
                print(f"Error calculating progress: {e}")
        elif d['status'] == 'finished':
            self.signals.progress.emit(100)
            self.signals.status.emit("Processing... (Merging files)")
    
    def format_size(self, size_bytes):
        if size_bytes < 0:
            return "0B"
        
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
            
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def clean_filename(self, filename):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def merge_video_audio(self, video_path, audio_path, output_path):
        try:
            self.signals.status.emit("Merging files...")
            
            cmd = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{output_path}"'
            
            if not self._run_command(cmd):
                self.signals.status.emit("ffmpeg merge failed, trying yt-dlp...")
                cmd = f'yt-dlp -o "{output_path}" --audio-file "{audio_path}" "{video_path}"'
                if not self._run_command(cmd):
                    raise Exception("Both ffmpeg and yt-dlp merging failed")
            
            self.signals.status.emit("Merging completed.")
            return True
            
        except Exception as e:
            print(f"Video and audio merging error: {e}")
            traceback.print_exc()
            self.signals.error.emit(f"Video and audio merging error: {e}")
            return False
    
    def _run_command(self, cmd):
        try:
            result = subprocess.run(
                cmd, 
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Command error: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"Command execution error: {e}")
            return False 