import sys
import numpy as np
from textwrap import wrap
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
        new_r = (self.r + other.r) // 2
        new_g = (self.g + other.g) // 2
        new_b = (self.b + other.b) // 2
        return Color(new_r, new_g, new_b)

    def __mul__(self, other):
        new_r = (2 * self.r + other.r) // 3
        new_g = (2 * self.g + other.g) // 3
        new_b = (2 * self.b + other.b) // 3
        return Color(new_r, new_g, new_b)

    def blend(color1, color2, mode):
        if mode == 0:
            color = color1
        elif mode == 1:
            color = color2
        elif mode == 2:
            if color1 < color2:
                color = color1 + color2
            else:
                color = color1 * color2
        elif mode == 3:
            color = color2 * color1
        return color.to_rgb()

    
    def __str__(self):
        return f'Color({self.r}, {self.g}, {self.b})'

    def to_rgb(self):
        return (self.r, self.g, self.b)

    def __lt__(self, other):
        return self.to_rgb() < other.to_rgb()



def main(files, shows=False, saves=True):
    for file in files:
        with open(file, 'rb') as f:
            addrs = []
            f.seek(0x4)
            while reader := hexlify(f.read(4)):    
                if reader == b'47545831': # == GTX1
                    addrs.append(f.tell())

            for addr in addrs:
                f.seek(addr)
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
                        coloration = wrap(f'{int(hexlify(f.read(4)), 16):032b}', 2)
                        for blend_mode in (int(c, 2) for c in coloration):
                            img[y][x] = Color.blend(back_color, front_color, blend_mode)
                                
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
                if saves:
                    if len(addrs) > 1:
                        png.save(f'{file}_{addr}.png')
                    else:
                        png.save(f'{file}.png')
                if shows:
                    png.show()


if __name__ == '__main__':
    main(sys.argv[1:])
