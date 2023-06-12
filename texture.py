from PIL import Image
import numpy as np

class Texture:
    def __init__(self, data):
        self.pixelIndicesSize = int.from_bytes(data.read(4), "little")
        self.width = int.from_bytes(data.read(2), "little")
        self.height = int.from_bytes(data.read(2), "little")
        self.bppMode = {b"\x07":8, b"\x08":4, b"\x05":None}[data.read(1)]
        self.hasPredefinedPalette = {b"\x0D":True, b"\x0C":False}[data.read(1)]
        self.null = data.read(2)
        self.paletteSize = int.from_bytes(data.read(2), "little")
        self.paletteFormat = {b"\x0E":"ABGR8888", b"\x01":"BGR565", b"\x00":"ABGR4444"}[data.read(1)]
        self.null1 = data.read(1)

        self.image = self.getArray(data)

    def getArray(self, data):
        temp = [[0 for x in range(self.width)] for y in range(self.height)]

        if self.paletteFormat == "ABGR4444":
            for yblock in range(0, self.height, 8):
                for xblock in range(0, self.width, 8):
                    for y in range(8):
                        for x in range(8):
                            temp[-1-(yblock + y)][xblock + x] = self.getPalette(data.read(2))

        else:
            if self.paletteFormat == "BGR565":
                palette = [self.getPalette(data.read(2)) for x in range(self.paletteSize//2)]
            else:
                palette = [self.getPalette(data.read(4)) for x in range(self.paletteSize//4)]

            if self.bppMode == 4:
                for yblock in range(0, self.height, 8):
                    for xblock in range(0, self.width, 32):
                        for y in range(8):
                            for x in range(16):
                                index = int.from_bytes(data.read(1), "little")
                                for xx in range(2):
                                    if self.paletteFormat == "BGR565":
                                        temp[-1-(yblock + y)][xblock + x*2 + xx] = palette[index >> xx*4 & 15]
                                    else:
                                        temp[-1-(yblock + y)][xblock + x*2 + xx] = palette[index >> (4-xx*4) & 15]
            
            elif self.bppMode == 8:
                for yblock in range(0, self.height, 8):
                    for xblock in range(0, self.width, 16):
                        for y in range(8):
                            for x in range(16):
                                temp[-1-(yblock + y)][xblock + x] = palette[int.from_bytes(data.read(1), "little")]

        return Image.fromarray(np.array([np.array([rgba for rgba in img], np.uint8) for img in temp], np.uint8), {"BGR565":"RGB"}.get(self.paletteFormat, "RGBA"))

    def getPalette(self, color):
        color = int.from_bytes(color, "little")
        match(self.paletteFormat):
            case "ABGR4444":
                return (color << 4 & 0xff, color >> 4 << 4 & 0xff, color >> 8 << 4 & 0xff, color >> 12 << 4 & 0xff)
            case "BGR565":
                return (color << 3 & 0xff, color >> 5 << 2 & 0xff, color >> 11 << 3 & 0xff)
            case "ABGR8888":
                return (color & 0xff, color >> 8 & 0xff, color >> 16 & 0xff, color >> 24 & 0xff)

    def exportTexture(self, path):
        if path == "": return
        self.image.save(path)