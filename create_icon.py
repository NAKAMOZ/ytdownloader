import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    """YouTube Downloader için basit bir ikon oluşturur"""
    try:
        # Ikon boyutları
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Ana ikon dosyası
        icon_path = "icon.ico"
        
        # Geçici PNG dosyaları
        temp_pngs = []
        
        for size in sizes:
            # Yeni bir görüntü oluştur
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Arka plan daire
            circle_diameter = min(size)
            circle_radius = circle_diameter // 2
            circle_center = (size[0] // 2, size[1] // 2)
            
            # Kırmızı arka plan daire çiz
            draw.ellipse(
                (
                    circle_center[0] - circle_radius,
                    circle_center[1] - circle_radius,
                    circle_center[0] + circle_radius,
                    circle_center[1] + circle_radius
                ),
                fill=(255, 0, 0, 255)
            )
            
            # İndirme oku çiz
            arrow_width = circle_radius * 0.6
            arrow_height = circle_radius * 0.8
            
            # Ok başlangıç noktası (üst orta)
            arrow_top = (circle_center[0], circle_center[1] - arrow_height // 2)
            # Ok bitiş noktası (alt orta)
            arrow_bottom = (circle_center[0], circle_center[1] + arrow_height // 2)
            # Ok ucu sol köşesi
            arrow_left = (circle_center[0] - arrow_width // 2, arrow_bottom[1] - arrow_width // 2)
            # Ok ucu sağ köşesi
            arrow_right = (circle_center[0] + arrow_width // 2, arrow_bottom[1] - arrow_width // 2)
            
            # Ok çizgisi
            draw.line([arrow_top, arrow_bottom], fill=(255, 255, 255, 255), width=max(1, int(circle_radius * 0.2)))
            
            # Ok ucu
            draw.polygon([arrow_bottom, arrow_left, arrow_right], fill=(255, 255, 255, 255))
            
            # Geçici PNG dosyası oluştur
            temp_png = f"temp_icon_{size[0]}x{size[1]}.png"
            img.save(temp_png)
            temp_pngs.append(temp_png)
        
        # PNG dosyalarını ICO dosyasına dönüştür
        imgs = [Image.open(png) for png in temp_pngs]
        imgs[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in imgs])
        
        # Geçici dosyaları temizle
        for png in temp_pngs:
            os.remove(png)
        
        print(f"İkon başarıyla oluşturuldu: {icon_path}")
        return True
    
    except Exception as e:
        print(f"İkon oluşturulurken hata oluştu: {e}")
        return False

if __name__ == "__main__":
    create_icon() 