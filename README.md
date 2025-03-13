# YouTube Downloader

YouTube'dan video ve ses indirmek için kullanılan basit bir uygulama.

## Özellikler

- YouTube videolarını MP4 formatında indirme
- YouTube ses dosyalarını MP3 formatında indirme
- Farklı video kalitesi seçenekleri (240p, 360p, 480p, 720p, 1080p)
- Farklı ses kalitesi seçenekleri (96kbps, 128kbps, 192kbps, 256kbps, 320kbps)
- Playlist indirme desteği
- İndirme ilerleme durumu gösterimi
- İndirilen dosyaların listesi

## Kurulum

### Kurulum Dosyası ile Kurulum

1. [Buradan](https://github.com/ytdownloader/releases) en son sürümü indirin.
2. İndirilen `YouTubeDownloader-Setup.exe` dosyasını çalıştırın.
3. Kurulum sihirbazını takip edin.

### Manuel Kurulum

1. Python 3.6 veya daha yeni bir sürümü yükleyin.
2. Gerekli paketleri yükleyin:
   ```
   pip install yt-dlp PyQt6 ffmpeg-python
   ```
3. FFmpeg'i yükleyin ve PATH'e ekleyin:
   - [FFmpeg İndirme Sayfası](https://ffmpeg.org/download.html)
4. Uygulamayı çalıştırın:
   ```
   python main.py
   ```

## Kullanım

1. Uygulamayı başlatın.
2. İndirmek istediğiniz YouTube video URL'sini girin.
3. Video veya ses indirme seçeneğini belirleyin.
4. Kalite seçeneğini belirleyin.
5. "İndir" düğmesine tıklayın.
6. İndirme tamamlandığında, dosya otomatik olarak açılacaktır.

## Geliştirme

### Gereksinimler

- Python 3.6+
- PyQt6
- yt-dlp
- ffmpeg-python

### Exe Dosyası Oluşturma

1. PyInstaller'ı yükleyin:
   ```
   pip install pyinstaller
   ```
2. Exe dosyasını oluşturun:
   ```
   pyinstaller --name YouTubeDownloader --onefile --windowed --icon=icon.ico --add-data "*.py;." --hidden-import PyQt6 --hidden-import yt_dlp --hidden-import ffmpeg main.py
   ```
   veya
   ```
   build.bat
   ```
   komutunu çalıştırın.

### Kurulum Dosyası Oluşturma

1. NSIS'i yükleyin: [NSIS İndirme Sayfası](https://nsis.sourceforge.io/Download)
2. `installer.nsi` dosyasını derleyin:
   ```
   "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
   ```
   veya
   ```
   build.bat
   ```
   komutunu çalıştırın.

## Güvenlik Uyarıları Hakkında

Bu uygulama, imzalanmamış bir uygulama olduğu için Windows Defender veya diğer antivirüs programları tarafından "güvenilir olmayan program" olarak işaretlenebilir. Bu durum, tüm PyInstaller ile paketlenmiş uygulamalar için yaygın bir sorundur ve uygulamanın zararlı olduğu anlamına gelmez.

### Uyarıyı Geçmek İçin

1. Dosyayı indirdiğinizde çıkan uyarıda "Daha fazla bilgi" seçeneğine tıklayın
2. Ardından "Yine de çalıştır" seçeneğini tıklayın
3. Yükleme sorunsuz bir şekilde devam edecektir

### Neden Bu Uyarı Çıkıyor?

Bu tür uyarılar, uygulamanın bir kod imzalama sertifikası ile imzalanmamış olmasından kaynaklanır. Kod imzalama sertifikaları, yazılımın güvenilir bir kaynaktan geldiğini doğrular ancak maliyetli olduklarından birçok ücretsiz ve açık kaynaklı projede kullanılmaz.

## Lisans

Bu proje [MIT Lisansı](LICENSE.txt) altında lisanslanmıştır.
