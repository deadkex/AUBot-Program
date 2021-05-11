# These offsets have been taken from
# https://github.com/automuteus/amonguscapture/blob/master/Offsets.json

all_offsets = {
    "Description": "v2021.5.10s",
    "AmongUsClientOffset": 0x1E247C4,
    "GameDataOffset": 0x1E3F0F8,
    "MeetingHudOffset": 0x1E1CEEC,
    "GameStartManagerOffset": 0x1DF9080,
    "HudManagerOffset": 0x2821E20,
    "ServerManagerOffset": 0x1DF95F0,
    "TempDataOffset": 0x1E3BD8C,
    "GameOptionsOffset": 0x1E283AC,

    "MeetingHudPtr": [0x1E1CEEC, 92, 0],
    "MeetingHudCachePtrOffsets": [8],
    "MeetingHudStateOffsets": [132],
    "GameStateOffsets": [0x1E247C4, 92, 0, 112],
    "AllPlayerPtrOffsets": [0x1E3F0F8, 92, 0, 36],
    "AllPlayersOffsets": [8],
    "PlayerCountOffsets": [12],
    "ExiledPlayerIdOffsets": [0x1E1CEEC, 92, 0, 148, 8],
    "RawGameOverReasonOffsets": [0x1E3BD8C, 92, 4],
    "WinningPlayersPtrOffsets": [0x1E3BD8C, 92, 12],
    "WinningPlayersOffsets": [8],
    "WinningPlayerCountOffsets": [12],
    "GameCodeOffsets": [0x1DF9080, 92, 0, 0x20, 0x80],
    "PlayRegionOffsets": [0x1DF95F0, 92, 0, 16, 8, 8],
    "PlayMapOffsets": [0x1E283AC, 92, 4, 16],
    "StringOffsets": [8, 12],
    "isEpic": False,
    "AddPlayerPtr": 4,
    "PlayerListPtr": 16,
    "PlayerInfoStructOffsets": {
        "PlayerIDOffset": 8,
        "PlayerNameOffset": 12,
        "ColorIDOffset": 20,
        "HatIDOffset": 24,
        "PetIDOffset": 28,
        "SkinIDOffset": 32,
        "DisconnectedOffset": 36,
        "TasksOffset": 40,
        "ImposterOffset": 44,
        "DeadOffset": 45,
        "ObjectOffset": 48
    },
    "WinningPlayerDataStructOffsets": {
        "NameOffset": 8,
        "DeadOffset": 12,
        "ImposterOffset": 13,
        "ColorOffset": 16,
        "SkinOffset": 20,
        "HatOffset": 24,
        "PetOffset": 28,
        "IsYouOffset": 32
    }
}
