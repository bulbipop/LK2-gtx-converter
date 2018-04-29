import sys
import numpy as np
from PIL import Image
from binascii import hexlify

class Color:
    def __init__(self, r, g=None, b=None):
        """ Either a RGB 16bit int or 3 bytes R-G-B """
        if g is None:   # need to convert int16 to 3 bytes and adjust scales
            int16 = r
            r = ((((int16 >> 11) & 0x1F) * 255) // 31)
            g = ((((int16 >> 5) & 0x3F) * 255) // 63)
            b = (((int16 & 0x1F) * 255) // 31)
        self.r, self.g, self.b = r, g, b

    def __add__(self, other):
        """ Blend the two colors together """
        new_r = (self.r + other.r) // 2
        new_g = (self.g + other.g) // 2
        new_b = (self.b + other.b) // 2
        return Color(new_r, new_g, new_b)

    def __str__(self):
        return f'Color({self.r}, {self.g}, {self.b})'

    def to_rgb(self):
        return (self.r, self.g, self.b)

    def desaturation(self):
        """ TODO: find the right  """
        return Color(int(self.r * 0.8), int(self.g * 0.8), int(self.b * 0.8))


with open(sys.argv[1], 'rb') as f:
    f.seek(0x4)
    while hexlify(f.read(4)) != b'47545831':    # == GTX1
        f.seek(f.tell() + 0x0C)
    addr = f.tell()
    WIDTH = addr + 4
    HEIGHT = addr + 6
    DATA = addr + 0x18
    f.seek(WIDTH)
    width = int(hexlify(f.read(2)), 16)
    f.seek(HEIGHT)
    height = int(hexlify(f.read(2)), 16)
    f.seek(DATA)

    if width % 4 != 0:
        width += (width % 4) + 4

    x, y = 0, 0
    second_line = False
    img = np.zeros((height, width, 3), dtype=np.uint8)
    while True:
        try:
            back_color = Color(int(hexlify(f.read(2)), 16))
            front_color = Color(int(hexlify(f.read(2)), 16))
            coloration = f'{int(hexlify(f.read(4)), 16):032b}'
            for intensity, brush in zip(coloration[::2], coloration[1::2]):
                print('now in', x, y)
                if int(intensity):
                    if int(brush):
                        img[y][x] = back_color.desaturation().to_rgb()
                    else:
                        img[y][x] = front_color.desaturation().to_rgb()
                else:
                    if int(brush):
                        img[y][x] = front_color.to_rgb()
                    else:
                        img[y][x] = back_color.to_rgb()

                square_end_x = (x != 0 and (x+1) % 4 == 0)
                double_square_end_x = (x != 0 and (x+1) % 8 == 0)
                square_end_y = (y != 0 and (y+1) % 4 == 0)

                if x == width - 1 and square_end_y and second_line:
                    x = 0
                    y += 1
                    second_line = False
                elif double_square_end_x and square_end_y:
                    if second_line:
                        x += 1
                        y -= 7
                        second_line = False
                    else:
                        x -= 7
                        y += 1
                        second_line = True
                elif square_end_x and square_end_y:
                    x += 1
                    y -= 3
                elif square_end_x:
                    x -= 3
                    y += 1
                else:
                    x += 1
        except Exception as e:
            print(e)
            break
    png = Image.fromarray(img, 'RGB')
    png.save(f'{sys.argv[1]}.png')
    png.show()
