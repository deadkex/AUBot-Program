import pymem
import win32gui
from structs import *
from Offsets import *

AmongUsClientOffset = all_offsets["AmongUsClientOffset"]
GameDataOffset = all_offsets["GameDataOffset"]
MeetingHudOffset = all_offsets["MeetingHudOffset"]
GameStartManagerOffset = all_offsets["GameStartManagerOffset"]
ServerManagerOffset = all_offsets["ServerManagerOffset"]
PlayerOffset = all_offsets["AllPlayerPtrOffsets"][0]

offsets_lobby_code = all_offsets["GameCodeOffsets"][1:]
offsets_meetinghud_state_cache = all_offsets["MeetingHudPtr"][1:] + all_offsets["MeetingHudCachePtrOffsets"]
offsets_meetinghud_state = all_offsets["MeetingHudPtr"][1:] + all_offsets["MeetingHudStateOffsets"]
offsets_all_players = all_offsets["AllPlayerPtrOffsets"][1:] + all_offsets["AllPlayersOffsets"]
offsets_playercount = all_offsets["AllPlayerPtrOffsets"][1:] + all_offsets["PlayerCountOffsets"]
offsets_game_state = all_offsets["GameStateOffsets"][1:]
offsets_region_id = all_offsets["PlayRegionOffsets"][1:]

if not win32gui.FindWindow(0, "Among Us"):
    exit()

handle = pymem.Pymem()
handle.open_process_from_name("Among Us")
list_of_modules = handle.list_modules()
module_addr = None
for module in list_of_modules:
    if module.name == "GameAssembly.dll":
        module_addr = int(module.lpBaseOfDll)


# ----------------------------------------------------------------------------------------------------------------------
def get_ptr(base, offsets):
    global module_addr
    ptr = module_addr + int(base)  # dll + base
    for offset in offsets:
        ptr = handle.read_int(int(ptr))  # read value -> new ptr
        if not ptr:
            return
        ptr = ptr + int(offset)  # calc new ptr with next offset
    return ptr  # return ptr not the value at the ptr


def ptr_calc(ptr, offsets):
    for offset in offsets:
        ptr = handle.read_int(int(ptr))
        if not ptr and len(offsets):
            return
        ptr = ptr + int(offset)  # calc new ptr with next offset
    return ptr  # return ptr not the value at the ptr


def get_meetingHudState():  # 0 = Discussion, 1 = NotVoted, 2 = Voted, 3 = Results, 4 = Proceeding
    meetingHud_cachePtr = get_ptr(MeetingHudOffset, offsets_meetinghud_state_cache)
    if meetingHud_cachePtr is None:
        return 4
    meetingHud_cache = handle.read_int(meetingHud_cachePtr)
    if meetingHud_cache:
        meetingHudState_ptr = get_ptr(MeetingHudOffset, offsets_meetinghud_state)
        meetingHudState = handle.read_int(int(meetingHudState_ptr))
    else:
        return 4
    return meetingHudState


def get_gameState():  # 0 = NotJoined, 1 = Joined, 2 = Started, 3 = Ended (during "defeat" or "victory" screen only)
    gameState_ptr = get_ptr(AmongUsClientOffset, offsets_game_state)
    gameState = handle.read_int(int(gameState_ptr))
    return gameState


def get_allPlayers():
    allP = []
    allPlayersPtr = get_ptr(PlayerOffset, offsets_all_players)
    if not allPlayersPtr:
        return
    allPlayers = handle.read_int(int(allPlayersPtr))
    playerAddrPtr = allPlayers + 0x10
    playerAddrPtr2 = ptr_calc(playerAddrPtr, [0])
    for i in range(get_playerCount()):
        bytearr = handle.read_bytes(int(playerAddrPtr2), 48)
        allP.append(PlayerInfo(byte_arr=bytearr, handle=handle))
        playerAddrPtr += 4
        playerAddrPtr2 = ptr_calc(playerAddrPtr, [0])
    return allP


def get_playerCount():
    playerCount = 0
    playerCountPtr = get_ptr(PlayerOffset, offsets_playercount)
    if playerCountPtr:
        playerCount = handle.read_int(int(playerCountPtr))
    return playerCount


def get_regionId():
    ptr = get_ptr(ServerManagerOffset, [0x5c, 0x0, 0x10, 0x8, 0x8])
    if not ptr:
        return 3
    data = (4 - (handle.read_int(int(ptr)) & 0b11)) % 3
    return data


def get_lobbyCode():
    ptr = get_ptr(GameStartManagerOffset, offsets_lobby_code)
    if not ptr:
        return None
    ptr2 = handle.read_int(int(ptr))
    if not ptr:
        return None
    nameleng = handle.read_int(int(ptr2 + 0x8))
    name = handle.read_bytes(int(ptr2 + 0xC), nameleng << 1)
    if len(name) == 0 or len(name.decode("utf-8").split("\n")) != 2:
        return None
    data = name.decode("utf-8").replace("\x00", "").split("\n")[1]
    return data


print("Lobbycode: " + str(get_lobbyCode()))
# print(get_gameState())
print("Region: " + PlayRegion[str(get_regionId())])
# print(get_meetingHudState())
print("Playercount: " + str(get_playerCount()))
print(get_allPlayers())
# print("meet" + str(get_meetingHudState()))
# print("state" + str(get_gameState()))
