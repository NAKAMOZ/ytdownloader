import os
from PIL import Image, ImageDraw, ImageFont

def create_welcome_banner():
    """NSIS kurulumu için hoşgeldiniz banner'ı oluşturur"""
    try:
        # Banner boyutları (NSIS standart boyutları)
        width, height = 164, 314
        
        # Yeni bir görüntü oluştur
        img = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Kırmızı gradient arka plan
        for y in range(height):
            # Yukarıdan aşağıya kırmızı tonunu azalt
            red_value = max(180, 255 - int(y / height * 100))
            draw.line([(0, y), (width, y)], fill=(red_value, 0, 0))
        
        # Daire ve ok çiz (logo benzeri)
        circle_center = (width // 2, height // 3)
        circle_radius = width // 3
        
        # Beyaz daire
        draw.ellipse(
            (
                circle_center[0] - circle_radius,
                circle_center[1] - circle_radius,
                circle_center[0] + circle_radius,
                circle_center[1] + circle_radius
            ),
            fill=(255, 255, 255)
        )
        
        # İndirme oku
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
        draw.line([arrow_top, arrow_bottom], fill=(200, 0, 0), width=max(1, int(circle_radius * 0.2)))
        
        # Ok ucu
        draw.polygon([arrow_bottom, arrow_left, arrow_right], fill=(200, 0, 0))
        
        # Metin ekle
        try:
            # Yazı tipi yükle (varsayılan sistem yazı tipi)
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            # Yazı tipi yüklenemezse varsayılan yazı tipini kullan
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Başlık
        text = "YouTube"
        text_width = draw.textlength(text, font=font_large)
        draw.text(
            (width // 2 - text_width // 2, height // 2 + 20),
            text,
            fill=(255, 255, 255),
            font=font_large
        )
        
        # Alt başlık
        text = "Downloader"
        text_width = draw.textlength(text, font=font_large)
        draw.text(
            (width // 2 - text_width // 2, height // 2 + 50),
            text,
            fill=(255, 255, 255),
            font=font_large
        )
        
        # Sürüm
        text = "v1.0.0"
        text_width = draw.textlength(text, font=font_small)
        draw.text(
            (width // 2 - text_width // 2, height // 2 + 80),
            text,
            fill=(255, 255, 255),
            font=font_small
        )
        
        # Banner'ı kaydet
        img.save("welcome.bmp")
        print("Hoşgeldiniz banner'ı oluşturuldu: welcome.bmp")
        
        # Header görselini oluştur
        header_width, header_height = 150, 57
        header_img = Image.new('RGB', (header_width, header_height), color=(240, 240, 240))
        header_draw = ImageDraw.Draw(header_img)
        
        # Kırmızı gradient arka plan
        for y in range(header_height):
            # Soldan sağa kırmızı tonunu azalt
            red_value = max(180, 255 - int(y / header_height * 100))
            header_draw.line([(0, y), (header_width, y)], fill=(red_value, 0, 0))
        
        # Metin ekle
        try:
            header_font = ImageFont.truetype("arial.ttf", 16)
        except:
            header_font = ImageFont.load_default()
        
        text = "YouTube Downloader"
        text_width = header_draw.textlength(text, font=header_font)
        header_draw.text(
            (header_width // 2 - text_width // 2, header_height // 2 - 8),
            text,
            fill=(255, 255, 255),
            font=header_font
        )
        
        # Header'ı kaydet
        header_img.save("header.bmp")
        print("Header görseli oluşturuldu: header.bmp")
        
        return True
    
    except Exception as e:
        print(f"Banner oluşturulurken hata oluştu: {e}")
        return False

if __name__ == "__main__":
    create_welcome_banner() 