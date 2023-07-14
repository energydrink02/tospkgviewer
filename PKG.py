import gzip
import struct
from Helpers.Helper import Padding

assettype = {
    "rtf": "Texture",
    "msh": "Mesh",
    "wav": "Audio",
    "ent": "Entity",
    "cmh": "Collision",
    "mnf": "Manifest",
    "bms": "BMS"
}


class PKGHeader:
    def __init__(self, file):
        self.path = file.name
        
        self.magic = file.read(4).decode("ANSI")
        self.null0 = file.read(4)
        self.amountAssets = int.from_bytes(file.read(4), "little")
        self.unknown0 = int.from_bytes(file.read(4), "little") # Always 1
        self.totalSizeUncompressed = int.from_bytes(file.read(4), "little")
        self.totalSizeCompressed = int.from_bytes(file.read(4), "little")
        self.maxUncompressedAsset = int.from_bytes(file.read(4), "little")
        self.maxCompressedAsset = int.from_bytes(file.read(4), "little")
        self.unknown1 = int.from_bytes(file.read(4), "little") # Always 3
        self.null1 = file.read(12)

        if self.amountAssets == 0: raise Exception("PKG archive is empty")
    
        self.assets = [PKGEntry(file) for x in range(self.amountAssets)] 

    def Update(self):
        self.amountAssets = len(self.assets)

        self.totalSizeCompressed,self.maxCompressedAsset,self.totalSizeUncompressed,self.maxUncompressedAsset = sum([[sum(a), max(a)] for a in zip(*[(x.compressedSize, x.uncompressedSize) for x in self.assets])], [])

        startoffset = 0x30 + (0x34*self.amountAssets)
        for index, asset in enumerate(self.assets):
            asset.num = index

            asset.offset = startoffset
            asset.Update()
            startoffset += len(asset.data)

            

    def Serialize(self):
        bytecode = b""
        bytecode += self.magic.encode("ANSI")
        bytecode += self.null0
        bytecode += struct.pack("<IIIIIII", self.amountAssets, self.unknown0, self.totalSizeUncompressed, self.totalSizeCompressed, self.maxUncompressedAsset, self.maxCompressedAsset, self.unknown1)
        bytecode += self.null1     
        bytecode += b"".join(asset.SerializeHeader() for asset in self.assets)
        bytecode += b"".join(asset.data for asset in self.assets)
        return bytecode

    def save(self):
        with open(self.path, "wb+") as file:
            file.truncate(0)
            file.seek(0)
            file.write(self.Serialize())
    
    def save_as(self, wrapper):
        wrapper.write(self.Serialize())


class PKGEntry:
    def __init__(self, file):
        self.name = file.read(0x20).decode("ANSI").rstrip("\x00")
        self.num = int.from_bytes(file.read(2), "little")
        self.isCompressed = int.from_bytes(file.read(2), "little")
        self.uncompressedSize = int.from_bytes(file.read(4), "little")
        self.compressedSize = int.from_bytes(file.read(4), "little")
        self.offset = int.from_bytes(file.read(4), "little")
        self.null = file.read(4)

        self.endAsset = file.tell()
        file.seek(self.offset)

        self.data = file.read(self.compressedSize)

        file.seek(self.endAsset)

    def Update(self):
        self.data += bytes(Padding(len(self.data), 4))

    def Import(self, data, compress):
        if compress:
            self.isCompressed = 1
            self.uncompressedSize = len(data)
            self.data = gzip.compress(data)
            self.compressedSize = len(self.data)
        else:
            self.isCompressed = 0
            self.data = data
            self.compressedSize = self.uncompressedSize = len(self.data)

    def getType(self):
        return assettype.get(self.name[-3:], "")

    def getData(self):
        if self.isCompressed:
            return gzip.decompress(self.data)
        return self.data

    def SerializeHeader(self):
        bytecode = b""
        bytecode += self.name.ljust(32, "\0").encode("ANSI")
        bytecode += struct.pack("<HHIII", self.num, self.isCompressed, self.uncompressedSize, self.compressedSize, self.offset)
        bytecode += bytes(4)
        return bytecode
