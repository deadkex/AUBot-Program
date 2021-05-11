class PlayerInfo:
    def __init__(self, byte_arr, handle):
        self.PlayerId = int.from_bytes(byte_arr[8:9], byteorder='little')
        self.PlayerNamePtr = int.from_bytes(byte_arr[12:20], byteorder='little')

        name_length = handle.read_int(int(self.PlayerNamePtr + 0x8))
        name = handle.read_bytes(int(self.PlayerNamePtr + 0xC), name_length << 1)

        encoding = ["utf-8", "ISO-8859-1", "latin1"]
        self.PlayerName = "User"
        for enc in encoding:
            try:
                self.PlayerName = name.decode(enc).replace("\x00", "")
                break
            except UnicodeDecodeError:
                pass
        if self.PlayerName == "User":
            pass
            # print("User with unsupported name in lobby, errors expected")

        self.ColorId = int.from_bytes(byte_arr[20:24], byteorder='little')
        self.HatId = int.from_bytes(byte_arr[24:28], byteorder='little')
        self.PetId = int.from_bytes(byte_arr[28:32], byteorder='little')
        self.SkinId = int.from_bytes(byte_arr[32:36], byteorder='little')
        self.Disconnected = int.from_bytes(byte_arr[36:40], byteorder='little')
        self.Tasks = int.from_bytes(byte_arr[40:44], byteorder='little')
        self.IsImposter = int.from_bytes(byte_arr[44:45], byteorder='little')
        self.IsDead = int.from_bytes(byte_arr[45:48], byteorder='little')
        self._object = int.from_bytes(byte_arr[48:52], byteorder='little')


PlayerColor = {
    "0": "Red",
    "1": "Blue",
    "2": "Green",
    "3": "Pink",
    "4": "Orange",
    "5": "Yellow",
    "6": "Black",
    "7": "White",
    "8": "Purple",
    "9": "Brown",
    "10": "Cyan",
    "11": "Lime"
}
PlayRegion = {
    "0": "NorthAmerica",
    "1": "Asia",
    "2": "Europe",
    "3": "Error"
}