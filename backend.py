import os
import threading
import traceback
import urllib.request
import subprocess
from PyQt6.QtCore import pyqtSignal, QObject

try:
    import yt_dlp
except ImportError as e:
    print(f"yt-dlp kütüphanesi yüklenemedi: {e}")
    print("Lütfen 'pip install yt-dlp' komutu ile yükleyin.")
    import sys
    sys.exit(1)

try:
    import ffmpeg
except ImportError as e:
    print(f"ffmpeg-python kütüphanesi yüklenemedi: {e}")
    print("Lütfen 'pip install ffmpeg-python' komutu ile yükleyin.")
    import sys
    sys.exit(1)

class DownloadSignals(QObject):
    """İndirme işlemi sırasında kullanılacak sinyaller"""
    progress = pyqtSignal(float)
    finished = pyqtSignal(str, str, str)  # filename, filepath, thumbnail_path
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    playlist_progress = pyqtSignal(int, int)  # current_index, total_count

class YouTubeDownloader:
    """YouTube indirme işlemlerini yöneten sınıf"""
    
    def __init__(self):
        self.signals = DownloadSignals()
        self.download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        self.thumbnail_directory = os.path.join(self.download_directory, "thumbnails")
        self.downloaded_files = []
        
        # Thumbnail dizinini oluştur
        os.makedirs(self.thumbnail_directory, exist_ok=True)
    
    def set_download_directory(self, directory):
        """İndirme dizinini ayarlar"""
        self.download_directory = directory
        self.thumbnail_directory = os.path.join(self.download_directory, "thumbnails")
        os.makedirs(self.thumbnail_directory, exist_ok=True)
    
    def start_download(self, url, is_video, quality, is_playlist=False):
        """İndirme işlemini başlatır"""
        threading.Thread(
            target=self.download_thread,
            args=(url, is_video, quality, is_playlist),
            daemon=True
        ).start()
    
    def download_thread(self, url, is_video, quality, is_playlist=False):
        """İndirme işlemini arka planda gerçekleştirir"""
        try:
            self.signals.status.emit("Video bilgileri alınıyor...")
            
            # Video bilgisini al
            info_opts = {
                'quiet': True,
                'no_warnings': True, 
                'noplaylist': not is_playlist,
                'skip_download': True
            }
            
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Playlist kontrolü
                if is_playlist and 'entries' in info:
                    entries = list(info['entries'])
                    total_videos = len(entries)
                    self.signals.status.emit(f"Playlist bulundu: {total_videos} video")
                    
                    for i, entry in enumerate(entries):
                        self.signals.playlist_progress.emit(i+1, total_videos)
                        self.signals.status.emit(f"İndiriliyor: Video {i+1}/{total_videos}")
                        
                        # Playlist içindeki son video dışındakileri sessizce indir
                        is_last_video = (i == len(entries) - 1)
                        self.download_single_video(entry, is_video, quality, notify_completion=is_last_video)
                else:
                    # Tek video indirme
                    self.download_single_video(info, is_video, quality, notify_completion=True)
            
        except Exception as e:
            error_msg = str(e)
            print(f"İndirme hatası: {error_msg}")
            print("Hata detayları:")
            traceback.print_exc()
            self.signals.error.emit(error_msg)
            self.signals.status.emit("Hata oluştu")
    
    def download_single_video(self, info, is_video, quality, notify_completion=True):
        """Tek bir videoyu indirir"""
        try:
            video_title = info.get('title', 'video')
            video_id = info.get('id', '')
            
            # Dosya adında geçersiz karakterleri temizle
            video_title = self.clean_filename(video_title)
            
            # Thumbnail URL'i al
            thumbnails = info.get('thumbnails', [])
            thumbnail_url = None
            # En kaliteli thumbnaili bul
            if thumbnails:
                # Boyuta göre sırala
                sorted_thumbnails = sorted(
                    [t for t in thumbnails if 'width' in t and 'height' in t],
                    key=lambda x: (x.get('width', 0) * x.get('height', 0)),
                    reverse=True
                )
                
                if sorted_thumbnails:
                    thumbnail_url = sorted_thumbnails[0].get('url')
                else:
                    # Alternatif: ilk thumbnaili al
                    thumbnail_url = thumbnails[0].get('url') if thumbnails else None
        
            # Thumbnail indir
            thumbnail_path = os.path.join(self.thumbnail_directory, f"{video_id}.jpg")
            if thumbnail_url:
                self.signals.status.emit("Küçük resim indiriliyor...")
                try:
                    urllib.request.urlretrieve(thumbnail_url, thumbnail_path)
                except Exception as e:
                    print(f"Thumbnail indirme hatası: {e}")
                    thumbnail_path = ""
            
            # İndirme seçenekleri
            self.signals.status.emit("İndirme başlıyor...")
            
            # Dosya yolu
            output_template = os.path.join(self.download_directory, f"{video_title}.%(ext)s")
            
            if not is_video:
                # Ses indirme - MP3 formatında
                # Ses kalitesi ayarı
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
                
                # Ses dosyasını indir
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([info['webpage_url'] if 'webpage_url' in info else info['url']])
                
                # İndirilen dosyayı bul
                filepath = os.path.join(self.download_directory, f"{video_title}.mp3")
                file_ext = "mp3"
                
            else:
                # Video indirme
                # Önce video dosyasını indir
                self.signals.status.emit("Video dosyası indiriliyor...")
                video_path = os.path.join(self.download_directory, f"{video_title}.mp4")
                
                # Kalite seçimine göre format belirle
                format_map = {
                    "En İyi Kalite": "bestvideo[ext=mp4]/best[ext=mp4]",
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
                
                # Video dosyasını indir
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([info['webpage_url'] if 'webpage_url' in info else info['url']])
                
                # Şimdi ses dosyasını indir
                self.signals.status.emit("Ses dosyası indiriliyor...")
                audio_format_map = {
                    "En İyi Kalite": "bestaudio[ext=m4a]/best[ext=m4a]",
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
                
                # Ses dosyasını indir
                with yt_dlp.YoutubeDL(audio_ydl_opts) as ydl:
                    ydl.download([info['webpage_url'] if 'webpage_url' in info else info['url']])
                
                # Video ve ses dosyalarının yollarını belirle
                audio_path = os.path.join(self.download_directory, f"{video_title}.m4a")
                
                # ffmpeg ile birleştirme işlemi
                if os.path.exists(video_path) and os.path.exists(audio_path):
                    self.signals.status.emit("Video ve ses birleştiriliyor...")
                    merged_path = os.path.join(self.download_directory, f"{video_title}_merged.mp4")
                    
                    try:
                        # ffmpeg komutu ile birleştir
                        cmd = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{merged_path}"'
                        result = subprocess.run(
                            cmd, 
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode != 0:
                            raise Exception(f"ffmpeg hatası: {result.stderr}")
                        
                        # Birleştirme başarılı olduysa orijinal dosyaları sil
                        if os.path.exists(merged_path):
                            os.remove(video_path)
                            os.remove(audio_path)
                            # Birleştirilmiş dosyayı orijinal isimle yeniden adlandır
                            os.rename(merged_path, video_path)
                    except Exception as e:
                        print(f"Video ve ses birleştirme hatası: {e}")
                        traceback.print_exc()
                        self.signals.error.emit(f"Video ve ses birleştirme hatası: {e}")
                
                filepath = video_path
                file_ext = "mp4"
            
            # İşlemi bitir
            filename = os.path.basename(filepath)
            
            # Sadece bildirim gönderilmesi gerekiyorsa sinyal gönder
            if notify_completion:
                self.signals.finished.emit(filename, filepath, thumbnail_path)
            else:
                # Bildirim gönderilmeyecekse sadece listeye ekle
                self.downloaded_files.append((filename, filepath, thumbnail_path))
                self.save_downloaded_files()
            
        except Exception as e:
            error_msg = str(e)
            print(f"Video indirme hatası: {error_msg}")
            traceback.print_exc()
            self.signals.error.emit(error_msg)
    
    def progress_hook(self, d):
        """İndirme ilerleme durumunu takip eder"""
        if d['status'] == 'downloading':
            try:
                # İlerleme bilgisi farklı şekillerde gelebilir, her birini kontrol ediyoruz
                if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] > 0:
                    p = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed_str = self.format_size(speed) + "/s"
                        status_text = f"İndiriliyor... {self.format_size(d['downloaded_bytes'])}/{self.format_size(d['total_bytes'])} ({speed_str})"
                        self.signals.status.emit(status_text)
                    self.signals.progress.emit(p)
                elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                    p = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed_str = self.format_size(speed) + "/s"
                        status_text = f"İndiriliyor... {self.format_size(d['downloaded_bytes'])}/{self.format_size(d['total_bytes_estimate'])} ({speed_str})"
                        self.signals.status.emit(status_text)
                    self.signals.progress.emit(p)
                elif '_percent_str' in d:
                    percent_str = d.get('_percent_str', '0%')
                    status_text = f"İndiriliyor... {percent_str} {d.get('_speed_str', '')}"
                    self.signals.status.emit(status_text)
                    
                    percent_str = percent_str.replace('%', '').strip()
                    try:
                        p = float(percent_str)
                        self.signals.progress.emit(p)
                    except (ValueError, TypeError):
                        pass
            except Exception as e:
                print(f"İlerleme hesaplanırken hata: {e}")
        elif d['status'] == 'finished':
            self.signals.progress.emit(100)
            self.signals.status.emit("Video işleniyor... (Video ve ses birleştiriliyor)")
    
    def format_size(self, size_bytes):
        """Bayt cinsinden boyutu insan okunabilir biçime dönüştürür"""
        if size_bytes < 0:
            return "0B"
        
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
            
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def save_downloaded_files(self):
        """İndirilen dosyaların listesini kaydeder"""
        try:
            with open("download_history.txt", "w", encoding="utf-8") as f:
                for filename, filepath, thumbnail_path in self.downloaded_files:
                    f.write(f"{filename}|{filepath}|{thumbnail_path}\n")
        except Exception as e:
            print(f"İndirme geçmişi kaydedilirken hata: {e}")
    
    def load_downloaded_files(self):
        """İndirilen dosyaların listesini yükler"""
        try:
            if os.path.exists("download_history.txt"):
                with open("download_history.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("|")
                        if len(parts) >= 3:
                            filename = parts[0]
                            filepath = parts[1]
                            thumbnail_path = parts[2]
                            self.downloaded_files.append((filename, filepath, thumbnail_path))
            return self.downloaded_files
        except Exception as e:
            print(f"İndirme geçmişi yüklenirken hata: {e}")
            return []
    
    def clean_filename(self, filename):
        """Dosya adındaki geçersiz karakterleri temizler"""
        # Windows'da dosya adında kullanılamayan karakterler
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def merge_video_audio(self, video_path, audio_path, output_path):
        """Subprocess kullanarak video ve ses dosyalarını birleştirir"""
        try:
            self.signals.status.emit("Video ve ses birleştiriliyor (ffmpeg)...")
            
            # ffmpeg komutunu oluştur - doğrudan ffmpeg kullanarak
            cmd = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{output_path}"'
            
            # Alternatif olarak yt-dlp'nin kendi birleştirme özelliğini kullanabiliriz
            if not self._run_command(cmd):
                # ffmpeg başarısız olursa yt-dlp ile deneyelim
                self.signals.status.emit("ffmpeg ile birleştirme başarısız oldu, yt-dlp deneniyor...")
                cmd = f'yt-dlp -o "{output_path}" --audio-file "{audio_path}" "{video_path}"'
                if not self._run_command(cmd):
                    raise Exception("Hem ffmpeg hem de yt-dlp ile birleştirme başarısız oldu")
            
            self.signals.status.emit("Video ve ses birleştirme tamamlandı.")
            return True
            
        except Exception as e:
            print(f"Video ve ses birleştirme hatası: {e}")
            traceback.print_exc()
            self.signals.error.emit(f"Video ve ses birleştirme hatası: {e}")
            return False
    
    def _run_command(self, cmd):
        """Komutu çalıştırır ve başarılı olup olmadığını döndürür"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Komut hatası: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"Komut çalıştırma hatası: {e}")
            return False 