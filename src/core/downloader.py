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
    """Signals used during the download process"""
    progress = pyqtSignal(float)
    finished = pyqtSignal(str, str, str)  # filename, filepath, thumbnail_path
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    playlist_progress = pyqtSignal(int, int)  # current_index, total_count

class YouTubeDownloader:
    """Class managing YouTube download operations"""
    
    def __init__(self):
        self.signals = DownloadSignals()
        self.download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        self.thumbnail_directory = os.path.join(self.download_directory, "thumbnails")
        self.downloaded_files = []
        
        # Geçmiş dosyası yolunu kaldırıyoruz
        # script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # self.history_file_path = os.path.join(script_dir, "download_history.txt")
        # print(f"Download history file path: {self.history_file_path}")
        
        # Create thumbnail directory
        os.makedirs(self.thumbnail_directory, exist_ok=True)
    
    def set_download_directory(self, directory):
        """Sets the download directory"""
        self.download_directory = directory
        self.thumbnail_directory = os.path.join(self.download_directory, "thumbnails")
        os.makedirs(self.thumbnail_directory, exist_ok=True)
    
    def start_download(self, url, is_video, quality, is_playlist=False):
        """Starts the download process"""
        threading.Thread(
            target=self.download_thread,
            args=(url, is_video, quality, is_playlist),
            daemon=True
        ).start()
    
    def download_thread(self, url, is_video, quality, is_playlist=False):
        """Performs the download in the background"""
        try:
            self.signals.status.emit("Getting video information...")
            
            # Get video info
            info_opts = {
                'quiet': True,
                'no_warnings': True, 
                'noplaylist': not is_playlist,
                'skip_download': True
            }
            
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Playlist check
                if is_playlist and 'entries' in info:
                    entries = list(info['entries'])
                    total_videos = len(entries)
                    self.signals.status.emit(f"Playlist found: {total_videos} videos")
                    
                    for i, entry in enumerate(entries):
                        self.signals.playlist_progress.emit(i+1, total_videos)
                        self.signals.status.emit(f"Downloading: Video {i+1}/{total_videos}")
                        
                        # Download all videos in the playlist silently except for the last one
                        is_last_video = (i == len(entries) - 1)
                        self.download_single_video(entry, is_video, quality, notify_completion=is_last_video)
                else:
                    # Single video download
                    self.download_single_video(info, is_video, quality, notify_completion=True)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Download error: {error_msg}")
            print("Error details:")
            traceback.print_exc()
            self.signals.error.emit(error_msg)
            self.signals.status.emit("Error occurred")
    
    def download_single_video(self, info, is_video, quality, notify_completion=True):
        """Downloads a single video"""
        try:
            video_title = info.get('title', 'video')
            video_id = info.get('id', '')
            video_url = info.get('webpage_url', '') or info.get('url', '')
            
            # Clean invalid characters from filename
            video_title = self.clean_filename(video_title)
            
            # Get thumbnail URL
            thumbnails = info.get('thumbnails', [])
            thumbnail_url = None
            # Find the highest quality thumbnail
            if thumbnails:
                # Sort by size
                sorted_thumbnails = sorted(
                    [t for t in thumbnails if 'width' in t and 'height' in t],
                    key=lambda x: (x.get('width', 0) * x.get('height', 0)),
                    reverse=True
                )
                
                if sorted_thumbnails:
                    thumbnail_url = sorted_thumbnails[0].get('url')
                else:
                    # Alternative: get the first thumbnail
                    thumbnail_url = thumbnails[0].get('url') if thumbnails else None
        
            # Download thumbnail
            thumbnail_path = os.path.join(self.thumbnail_directory, f"{video_id}.jpg")
            if thumbnail_url:
                self.signals.status.emit("Downloading thumbnail...")
                try:
                    urllib.request.urlretrieve(thumbnail_url, thumbnail_path)
                except Exception as e:
                    print(f"Thumbnail download error: {e}")
                    thumbnail_path = ""
            
            # Download options
            self.signals.status.emit("Starting download...")
            
            # File path
            output_template = os.path.join(self.download_directory, f"{video_title}.%(ext)s")
            
            if not is_video:
                # Audio download - MP3 format
                # Audio quality settings
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
                    }],
                }
                
                # Download audio file
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Find downloaded file
                filepath = os.path.join(self.download_directory, f"{video_title}.mp3")
                file_ext = "mp3"
                
            else:
                # Video download
                # First download the video file
                self.signals.status.emit("Downloading video file...")
                video_path = os.path.join(self.download_directory, f"{video_title}.mp4")
                
                # Determine format based on quality selection
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
                    'keepvideo': True,
                }
                
                # Download video file
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Now download the audio file
                self.signals.status.emit("Downloading audio file...")
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
                    'noplaylist': True,
                }
                
                # Download audio file
                with yt_dlp.YoutubeDL(audio_ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Determine video and audio file paths
                audio_path = os.path.join(self.download_directory, f"{video_title}.m4a")
                
                # Merge with ffmpeg
                if os.path.exists(video_path) and os.path.exists(audio_path):
                    self.signals.status.emit("Merging video and audio...")
                    merged_path = os.path.join(self.download_directory, f"{video_title}_merged.mp4")
                    
                    try:
                        # Merge with ffmpeg command
                        cmd = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{merged_path}"'
                        result = subprocess.run(
                            cmd, 
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode != 0:
                            raise Exception(f"ffmpeg error: {result.stderr}")
                        
                        # Delete original files if merge successful
                        if os.path.exists(merged_path):
                            os.remove(video_path)
                            os.remove(audio_path)
                            # Rename merged file to original name
                            os.rename(merged_path, video_path)
                    except Exception as e:
                        print(f"Video and audio merging error: {e}")
                        traceback.print_exc()
                        self.signals.error.emit(f"Video and audio merging error: {e}")
                
                filepath = video_path
                file_ext = "mp4"
            
            # Finish the process
            filename = os.path.basename(filepath)
            
            # Send signal only if notification is required
            if notify_completion:
                self.signals.finished.emit(filename, filepath, thumbnail_path)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Video download error: {error_msg}")
            traceback.print_exc()
            self.signals.error.emit(error_msg)
    
    def progress_hook(self, d):
        """Tracks download progress"""
        if d['status'] == 'downloading':
            try:
                # Progress info can come in different forms, we check each one
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
            self.signals.status.emit("Processing video... (Merging video and audio)")
    
    def format_size(self, size_bytes):
        """Converts bytes to human-readable format"""
        if size_bytes < 0:
            return "0B"
        
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
            
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def save_downloaded_files(self):
        """Geçmiş kaydetme işlevi devre dışı bırakıldı"""
        pass
        # try:
        #     print(f"Saving download history: {len(self.downloaded_files)} items to {self.history_file_path}")
        #     with open(self.history_file_path, "w", encoding="utf-8") as f:
        #         for item in self.downloaded_files:
        #             if len(item) >= 4:  # New format with URL
        #                 filename, filepath, thumbnail_path, url = item
        #                 f.write(f"{filename}|{filepath}|{thumbnail_path}|{url}\n")
        #             else:  # Old format without URL
        #                 filename, filepath, thumbnail_path = item
        #                 f.write(f"{filename}|{filepath}|{thumbnail_path}|\n")
        #             print(f"  - Saved: {filename} | {filepath}")
        #     print(f"Download history saved successfully to {self.history_file_path}")
        # except Exception as e:
        #     print(f"Error saving download history: {e}")
    
    def load_downloaded_files(self):
        """Geçmiş yükleme işlevi devre dışı bırakıldı"""
        return []
        # try:
        #     if os.path.exists(self.history_file_path):
        #         print(f"Loading download history from {self.history_file_path}")
        #         self.downloaded_files = []
        #         with open(self.history_file_path, "r", encoding="utf-8") as f:
        #             for line in f:
        #                 try:
        #                     # Satırın boş olup olmadığını kontrol et
        #                     line = line.strip()
        #                     if not line:
        #                         continue
        #                     
        #                     # Verileri daha güvenli bir şekilde ayır
        #                     # Son parça video URL'si olduğundan, maksimum 3 ayrıştırma ile 4 parça elde et
        #                     parts = line.split("|", 3)
        #                     
        #                     if len(parts) >= 3:
        #                         filename = parts[0]
        #                         filepath = parts[1]
        #                         thumbnail_path = parts[2]
        #                         url = parts[3] if len(parts) >= 4 else ""
        #                         
        #                         # Gerçekten dosya mevcut mu kontrol et
        #                         file_exists = os.path.exists(filepath) if filepath else False
        #                         
        #                         # Thumbnail mevcut mu kontrol et - yoksa yalnızca hata mesajı yazdır
        #                         thumbnail_exists = os.path.exists(thumbnail_path) if thumbnail_path else False
        #                         if not thumbnail_exists and thumbnail_path:
        #                             print(f"  - Uyarı: Thumbnail bulunamadı: {thumbnail_path}")
        #                         
        #                         if file_exists:
        #                             print(f"  - Yüklendi: {filename}")
        #                             print(f"    Dosya: {filepath}")
        #                             print(f"    Thumbnail: {thumbnail_path} (Mevcut: {thumbnail_exists})")
        #                             print(f"    URL: {url if url else 'N/A'}")
        #                             self.downloaded_files.append((filename, filepath, thumbnail_path, url))
        #                         else:
        #                             print(f"  - Atlandı (dosya bulunamadı): {filename}")
        #                 except Exception as e:
        #                     print(f"Satır ayrıştırma hatası: {e}")
        #                     continue
        #             
        #         print(f"İndirme geçmişi yüklendi: {len(self.downloaded_files)} öğe")
        #     else:
        #         print("İndirme geçmişi dosyası bulunamadı:", self.history_file_path)
        #         self.downloaded_files = []
        #     return self.downloaded_files
        # except Exception as e:
        #     print(f"İndirme geçmişi yükleme hatası: {e}")
        #     import traceback
        #     traceback.print_exc()
        #     self.downloaded_files = []
        #     return []
    
    def clean_filename(self, filename):
        """Cleans invalid characters from filename"""
        # Characters that can't be used in Windows filenames
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def merge_video_audio(self, video_path, audio_path, output_path):
        """Merges video and audio files using subprocess"""
        try:
            self.signals.status.emit("Merging video and audio (ffmpeg)...")
            
            # Create ffmpeg command - using ffmpeg directly
            cmd = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{output_path}"'
            
            # Alternatively we could use yt-dlp's own merging feature
            if not self._run_command(cmd):
                # If ffmpeg fails, try with yt-dlp
                self.signals.status.emit("ffmpeg merge failed, trying yt-dlp...")
                cmd = f'yt-dlp -o "{output_path}" --audio-file "{audio_path}" "{video_path}"'
                if not self._run_command(cmd):
                    raise Exception("Both ffmpeg and yt-dlp merging failed")
            
            self.signals.status.emit("Video and audio merging completed.")
            return True
            
        except Exception as e:
            print(f"Video and audio merging error: {e}")
            traceback.print_exc()
            self.signals.error.emit(f"Video and audio merging error: {e}")
            return False
    
    def _run_command(self, cmd):
        """Runs a command and returns whether it was successful"""
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