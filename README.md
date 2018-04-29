LK2-gtx-tex-converter

- [x] Convert .gtx/.tex to .png (Almost, method "desaturation" needs to be tweaked?)
- [ ] Convert .png to .gtx/.tex

Data:
8 bytes fill 64 pixels.

Pixels are filled in this order:
 1  2  3  4  17 18 19 20  65 66 ...  
 5  6  7  8  21 22 23 24  
 9 10 11 12  25 26 27 28  
13 14 15 16  29 30 31 32  
33 34 35 36  49 50 51 52  
37 38 39 40  53 54 55 56  
41 42 43 44  57 58 59 60  
45 46 47 48  61 62 63 64  

example with FF 6D 37 E4 A8 2F F8 0F  
FF6D: first color: RGB565 (16-bit RGB)  
37E4: second color: RGB565 (16-bit RGB)  
A8 2F F8 0F needs to be converted to binary: 10 10 10 00 00 10 11 11 11 11 10 00 00 00 11 11 and represents the color of each pixels:  
00: first color  
01: second color  
10: second color desaturated?  
11: first color desaturated?  
