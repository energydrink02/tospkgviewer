import struct


class BMS_Header:
    def __init__(self, file):
        self.unk1 = int.from_bytes(file.read(4), "little")
        self.bmsName = file.read(0x10).decode("ANSI").rstrip("\0")
        self.amountEntries = int.from_bytes(file.read(4), "little")

        self.entries = [BMS_Entry(file) for x in range(self.amountEntries)]

    def ToString(self):
        return self.bmsName + "\n" + "\n".join(entry.ToString() for entry in self.entries)


class BMS_Entry:
    def __init__(self, file):
        self.unk1 = int.from_bytes(file.read(4), "little")
        self.unk2 = int.from_bytes(file.read(4), "little")
        self.position = [round(struct.unpack("<f", file.read(4))[0], 4) for x in range(3)]
        self.unk3 = file.read(0x38)
        self.objName = file.read(0x20).decode("ANSI").rstrip("\0")
        self.mshName = file.read(0x20).decode("ANSI").rstrip("\0")
        self.unk4 = file.read(0x28)

    def ToString(self):
        return self.objName + " " + self.mshName + " " + " ".join(str(f) for f in self.position)
    
