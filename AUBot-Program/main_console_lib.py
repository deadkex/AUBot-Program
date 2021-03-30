import pymem
import win32gui
import os
import time
import requests
import json
from datetime import datetime, timedelta, date
from structs import *

versionId = "10"
lang = 0  # 0:de | 1:en
# ----------------------------------------------------------------------------------------------------------------------
print("          _    _ ____        _   ")
print("     /\\  | |  | |  _ \\      | |  ")
print("    /  \\ | |  | | |_) | ___ | |_ ")
print("   / /\\ \\| |  | |  _ < / _ \\| __|")
print("  / ____ \\ |__| | |_) | (_) | |_ ")
print(" /_/    \\_\\____/|____/ \\___/ \\__|")
print("Bot & program by Jan | API by Kim | Version " + versionId)
print("----------------------------------------------")
# ----------------------------------------------------------------------------------------------------------------------
with open("config.txt", 'r', encoding='utf-8') as keyFile:
    key = keyFile.readline().replace("\n", "")
    url = keyFile.readline()

# Offsets --------------------------------------------------------------------------------------------------------------
AmongUsClientOffset = 0x2C6C278
GameDataOffset = 0x2C6C07C
MeetingHudOffset = 0x2C6B78C
GameStartManagerOffset = 0x2B27F38
ServerManagerOffset = 0x2B206E8
# HudManagerOffset = 0x...


# ----------------------------------------------------------------------------------------------------------------------
def init():
    while not win32gui.FindWindow(0, "Among Us"):
        if lang == 0:
            print("Among Us nicht gefunden, versuche es in 5 Sekunden erneut...")
        elif lang == 1:
            print("Among Us was not found, retrying in 5 seconds...")
        time.sleep(5)
    if lang == 0:
        print("Among Us erkannt!")
    elif lang == 1:
        print("Found Among Us!")
    handle = pymem.Pymem()
    handle.open_process_from_name("Among Us")
    list_of_modules = handle.list_modules()
    module_addr = None
    for module in list_of_modules:
        if module.name == "GameAssembly.dll":
            module_addr = int(module.lpBaseOfDll)
    if module_addr is None:
        print("Something is wrong. ID:1")
        os.system("pause")
        exit()
    return handle, module_addr


handle, module_addr = init()


# ----------------------------------------------------------------------------------------------------------------------
def token_handle():
    token1 = token_checkFile()
    return token1
    while not token_check(token1):
        if lang == 0:
            print("Bitte gib den token vom Bot ein (bekommt man nach dem schreiben von au!play bzw au!token in irgendeinem channel)")
        elif lang == 1:
            print("Please input the token from the bot (which you get after writing au!play or au!token in any channel)")
        token1 = input()
        if token_check(token1):
            with open('AUBotToken.txt', 'w') as file2:
                file2.write(token1)
            break
        else:
            if lang == 0:
                print("Tokencheck ist fehlgeschlagen...")
            elif lang == 1:
                print("Tokencheck failed...")
    if lang == 0:
        print("Token gefunden!")
    elif lang == 1:
        print("Found token!")
    return token1


def token_checkFile():
    token1 = None
    try:
        with open('AUBotToken.txt', 'r', encoding='utf-8') as file:
            token1 = file.readline()
    except FileNotFoundError:
        with open('AUBotToken.txt', 'w') as file2:
            file2.write("")
    return token1


def token_check(token1):
    url3 = url + "?key=" + key + "&token=" + str(token1)
    data2 = requests.get(url3)
    if "tokenExists" in data2.text:
        data2 = data2.json()
        if data2["tokenExists"]:
            return True
    else:
        print(data2.text)
    return False


token = token_handle()

# ----------------------------------------------------------------------------------------------------------------------
# version check
url2 = url + "?key=" + key + "&token=" + str(token)
data = requests.get(url2).json()
if data["version"] == versionId:
    if lang == 0:
        print("Programm ist auf der neusten Version.")
    elif lang == 1:
        print("Program up to date!")
else:
    if lang == 0:
        print("Bitte update das Programm! Deine Version: " + versionId + " | Benötigte Version: " + data["version"])
    elif lang == 1:
        print("Please update the program! Your version: " + versionId + " | Required version: " + data["version"])
    os.system("pause")
    exit()


# ----------------------------------------------------------------------------------------------------------------------
def get_ptr(base, offsets):
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
    # meetingHud_ptr = get_ptr(hMeetingHudOffset, [0x5C])
    meetingHud_cachePtr = get_ptr(MeetingHudOffset, [0x5C, 0x0, 0x8])
    if meetingHud_cachePtr is None:
        return 4
    meetingHud_cache = handle.read_int(meetingHud_cachePtr)
    if meetingHud_cache:
        meetingHudState_ptr = get_ptr(MeetingHudOffset, [0x5C, 0x0, 0x84])
        meetingHudState = handle.read_int(int(meetingHudState_ptr))
    else:
        meetingHudState = 4
    return meetingHudState


def get_gameState():  # 0 = NotJoined, 1 = Joined, 2 = Started, 3 = Ended (during "defeat" or "victory" screen only)
    gameState_ptr = get_ptr(AmongUsClientOffset, [0x5c, 0, 0x64])
    gameState = handle.read_int(int(gameState_ptr))
    return gameState


def get_allPlayers():
    allP = []
    allPlayersPtr = get_ptr(GameDataOffset, [0x5C, 0, 0x24, 0x08])
    if not allPlayersPtr:
        return
    allPlayers = handle.read_int(int(allPlayersPtr))
    playerAddrPtr = allPlayers + 0x10
    playerAddrPtr2 = ptr_calc(playerAddrPtr, [0])
    for i in range(get_playerCount()):
        bytearr = handle.read_bytes(int(playerAddrPtr2), 48)
        allP.append(PlayerInfo(bytearr=bytearr, handle=handle))
        playerAddrPtr += 4
        playerAddrPtr2 = ptr_calc(playerAddrPtr, [0])
    return allP


def get_PlayerByColorId(ColorId):
    allP = get_allPlayers()
    player = None
    if allP:
        for x in allP:
            if x.ColorId == ColorId:
                player = x
    else:
        return
    return player


def get_exiledPlayer():
    exiledPlayerIdPtr = get_ptr(MeetingHudOffset, [0x5C, 0, 0x94, 0x08])
    if exiledPlayerIdPtr:
        exiledPlayerId = handle.read_int(int(exiledPlayerIdPtr))
        return exiledPlayerId


def get_playerCount():
    playerCount = 0
    playerCountPtr = get_ptr(GameDataOffset, [0x5C, 0, 0x24, 0x0C])
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
    ptr = get_ptr(GameStartManagerOffset, [0x5c, 0x0, 0x20, 0x28])
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


# ----------------------------------------------------------------------------------------------------------------------
def check_leave(oldPlayers, Players):
    left = []
    for x in oldPlayers:
        tmp = False
        for y in Players:
            if x.PlayerName == y.PlayerName:
                tmp = True
        if not tmp:
            left.append(x)
    return left


def check_join(oldPlayers, Players):
    joined = []
    for x in Players:
        tmp = False
        for y in oldPlayers:
            if x.PlayerName == y.PlayerName:
                tmp = True
        if not tmp:
            joined.append(x)
    return joined


def check_colorChange(oldPlayers, Players):
    colorchange = []
    if oldPlayers is not None:
        for x in oldPlayers:
            for y in Players:
                if x.PlayerName == y.PlayerName:
                    if x.ColorId != y.ColorId:
                        colorchange.append([x, y])
    return colorchange


def check_disconnected(Players):
    disconnect = []
    for x in Players:
        if x.Disconnected == 1:
            disconnect.append(x)
    return disconnect


def check_dead(Players):
    dead = []
    for x in Players:
        if x.IsDead == 1:
            dead.append(x)
    return dead


# ----------------------------------------------------------------------------------------------------------------------
def arrgetter(data1):
    myArr = ""
    cnt = 1
    for x1 in data1:
        myArr = myArr + str(x1.ColorId)
        if cnt != len(data1):
            myArr = myArr + ","
        cnt = cnt + 1
    return myArr
