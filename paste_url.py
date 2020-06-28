import os
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

class PasteURL():
    def __init__(self, img, url):
        self.img_name, self.ext = os.path.splitext(os.path.basename(img))
        self.img = Image.open(img)
        self.url = url
        self.width, self.height = self.img.size
        self.rectangle_width = round(self.width / 3, 1)
        self.rectangle_height = round(self.height * 0.03448, 1)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 100)
        self.d = ImageDraw.Draw(self.img)
        print(self.img, self.url)
    
    def rectangle_draw(self):
        d = self.d
        width = self.width
        height = self.height
        d.rectangle([(width - self.rectangle_width, height - self.rectangle_height), (width, height)], fill=(237, 100, 51))
        self.d = d
    
    def url_draw(self):
        d = self.d
        url = self.url
        rectangle_width = self.rectangle_width
        rectangle_height = self.rectangle_height
        url_width, url_height = d.textsize(self.url, self.font)
        url_position_x = rectangle_width - round(rectangle_height * 0.2, 1)
        url_position_y = rectangle_height - round(rectangle_height * 0.2, 1)
        font_size = 100
        i = 1
        while  url_width > url_position_x or url_height > url_position_y:
            font_size = 100 - i
            font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', font_size)
            url_width, url_height = d.textsize(url, font)
            i += 1

        d.text((self.width - url_position_x, self.height - url_position_y), url, fill=(255, 255, 255), font=font)
        self.img.save(self.img_name + 'url_pasted' + self.ext, quality=95)
    
    def url_paste_img(self):
        self.rectangle_draw()
        self.url_draw()

# PasteURL = PasteURL('img/drink/1.jpg', 'https://qiita.com/FGtatsuro/items/cf178bc44ce7b068d2355')
# PasteURL.url_paste_img()

