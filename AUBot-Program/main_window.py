import pymem
import win32gui
import time
import requests
from datetime import datetime, timedelta
import webbrowser
from tkinter import *
from tkinter import messagebox

from structs import *
from Offsets import *
# Note: The config is not on github on purpose
from config import *


# ----------------------------------------------------------------------------------------------------------------------
versionId = "13"
handle = None
module_addr = None
token = ""

# ----------------------------------------------------------------------------------------------------------------------
game = None
canvas = None
state = 0
state_ = False
label_among_init = None
label_token_init = None
label_version_init = None
label_check_for_game = None
canvas_elements = []
run_app = True
check_for_game_timer = datetime.now()
check_for_game_count = 0

# ----------------------------------------------------------------------------------------------------------------------
oldPlayers = []
Players = []
lobbycode = ""
region = 99
timer = datetime.now()
laststatus = datetime.now()
laststatus_cnt = 0
game_state = 0
sess_disconnected = []
sess_dead = []
sess_mute_state = 0
player_count = 0

# Offsets --------------------------------------------------------------------------------------------------------------
AmongUsClientOffset = all_offsets["AmongUsClientOffset"]
GameDataOffset = all_offsets["GameDataOffset"]
MeetingHudOffset = all_offsets["MeetingHudOffset"]
GameStartManagerOffset = all_offsets["GameStartManagerOffset"]
ServerManagerOffset = all_offsets["ServerManagerOffset"]
PlayerOffset = all_offsets["AllPlayerPtrOffsets"][0]

offsets_lobby_code = all_offsets["GameCodeOffsets"][1:]
offsets_meeting_hud_state_cache = all_offsets["MeetingHudPtr"][1:] + all_offsets["MeetingHudCachePtrOffsets"]
offsets_meeting_hud_state = all_offsets["MeetingHudPtr"][1:] + all_offsets["MeetingHudStateOffsets"]
offsets_all_players = all_offsets["AllPlayerPtrOffsets"][1:] + all_offsets["AllPlayersOffsets"]
offsets_player_count = all_offsets["AllPlayerPtrOffsets"][1:] + all_offsets["PlayerCountOffsets"]
offsets_game_state = all_offsets["GameStateOffsets"][1:]
offsets_region_id = all_offsets["PlayRegionOffsets"][1:]


# ----------------------------------------------------------------------------------------------------------------------
def on_close_window():
    global run_app
    run_app = False
    game.destroy()


def destroy_canvas_elements():
    for a in canvas_elements:
        a.destroy()


def command_tutorial():
    webbrowser.open_new("https://www.youtube.com/watch?v=YSLra9O-aFc")


def init_window():
    global canvas, game
    game = Tk()
    game.protocol("WM_DELETE_WINDOW", on_close_window)
    game.resizable(0, 0)
    game.wm_attributes("-topmost", 1)
    game.title("AUBot " + versionId)
    canvas = Canvas(game, width=200, height=200, bd=0, highlightthickness=0)
    canvas.pack()
    Button(game, text="Tutorial", command=command_tutorial).place(x=0, y=170, width=50, height=30)
    L1 = Label(game, text="AUBot by Jan", font=("Arial", 10), fg="black", anchor="w")
    L1.place(x=70, y=175, width=L1.winfo_reqwidth(), height=L1.winfo_reqheight())


# ----------------------------------------------------------------------------------------------------------------------
def among_init():
    global label_among_init, state_
    label_among_init = Label(game, text="Among Us not found", font=("Arial", 10), fg="red", anchor="w")
    label_among_init.place(x=0, y=0, width=label_among_init.winfo_reqwidth(), height=label_among_init.winfo_reqheight())
    state_ = True


def among_check():
    global label_among_init, state, state_, module_addr, handle
    if win32gui.FindWindow(0, "Among Us"):
        label_among_init.config(text="Among Us found", fg="green")
        handle = pymem.Pymem()
        handle.open_process_from_name("Among Us")
        list_of_modules = handle.list_modules()
        module_addr = None
        for module in list_of_modules:
            if module.name == "GameAssembly.dll":
                module_addr = int(module.lpBaseOfDll)
        if module_addr is None:
            exit()
        state = state + 1
        state_ = False


# ----------------------------------------------------------------------------------------------------------------------
def token_init():
    global canvas_elements, state_, label_token_init, state, token

    label_token_init = Label(game, text="Checking for token...", font=("Arial", 10), fg="red", anchor="w")
    label_token_init.place(x=0, y=20, width=label_token_init.winfo_reqwidth(), height=label_token_init.winfo_reqheight())

    token = token_checkFile()
    if token is not None:
        if token_check():
            return

    label_token_init.configure(text="Input token")

    entry1 = Entry(game)
    entry1.place(x=0, y=43, width=150, height=30)
    canvas_elements.append(entry1)

    button1 = Button(game, text="Enter", command=token_check)
    button1.place(x=0, y=75, width=50, height=30)
    canvas_elements.append(button1)
    state_ = True


def token_checkFile():
    token1 = None
    try:
        with open("AUBotToken.txt", 'r', encoding='utf-8') as file:
            token1 = file.readline()
    except FileNotFoundError:
        with open('AUBotToken.txt', 'w') as file2:
            file2.write("")
    return token1


def token_check():
    global state_, token, state, label_token_init, run_app
    if not state_:
        url3 = url + "?key=" + key + "&token=" + str(token)
    else:
        url3 = url + "?key=" + key + "&token=" + str(canvas_elements[0].get())
        token = canvas_elements[0].get()
    try:
        data2 = requests.get(url3)
    except:
        messagebox.showerror("Error", "Something went wrong when trying to connect to the database! Please try again.")
        if game:
            game.destroy()
        exit()
    if "tokenExists" in data2.text:
        data2 = data2.json()
        if data2["tokenExists"]:
            label_token_init.configure(text="Token found", fg="green")
            with open('AUBotToken.txt', 'w') as file2:
                file2.write(token)
            state = state + 1
            if state_:
                destroy_canvas_elements()
            state_ = False
            return True
    if state_:
        messagebox.showerror("Error", "Wrong token entered!")
    return False


# ----------------------------------------------------------------------------------------------------------------------
def version_init():
    global versionId, token, label_version_init, state
    label_version_init = Label(game, text="Checking for version...", font=("Arial", 10), fg="red", anchor="w")
    label_version_init.place(x=0, y=40, width=label_version_init.winfo_reqwidth(), height=label_version_init.winfo_reqheight())

    url2 = url + "?key=" + key + "&token=" + str(token)
    data = requests.get(url2).json()
    if data["version"] == versionId:
        label_version_init.configure(text="Program up to date", fg="green")
        state = state + 1
    else:
        label_version_init.configure(text="Wrong version!")
        messagebox.showerror("Error", "Please update the program!\nYour version: " + versionId + " | Required version: " + data["version"])
        if game:
            game.destroy()


# ----------------------------------------------------------------------------------------------------------------------
def check_for_game_init():
    global label_check_for_game, state_
    label_check_for_game = Label(game, text="Checking for game.", font=("Arial", 10), fg="red", anchor="w")
    label_check_for_game.place(x=0, y=60, width=200, height=label_check_for_game.winfo_reqheight())
    state_ = True


def check_for_game_check():
    global label_check_for_game, state_, check_for_game_timer, check_for_game_count, state
    if datetime.now() > check_for_game_timer:
        url2 = url + "?key=" + key + "&token=" + str(token)
        data = requests.get(url2).json()
        if data["gameExists"]:
            label_check_for_game.configure(text="Found game! Have fun!", fg="green")
            state_ = False
            state = state + 1
            destroy_canvas_elements()
        else:
            label_check_for_game.configure(text="Checking for game. Retries: " + str(check_for_game_count))
            label1 = Label(game, text="Please join a voice channel and", font=("Arial", 10), fg="red", anchor="w")
            label1.place(x=0, y=80, width=label1.winfo_reqwidth(), height=label1.winfo_reqheight())
            canvas_elements.append(label1)
            label2 = Label(game, text="write au!play into a text channel!", font=("Arial", 10), fg="red", anchor="w")
            label2.place(x=0, y=100, width=label2.winfo_reqwidth(), height=label2.winfo_reqheight())
            canvas_elements.append(label2)

            check_for_game_timer = datetime.now() + timedelta(seconds=10)
            check_for_game_count += 1
            if check_for_game_count >= 15:
                messagebox.showerror("Timeout", "Please dont leave the program in idle! Stopping...")
                if game:
                    game.destroy()


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
    meetingHud_cachePtr = get_ptr(MeetingHudOffset, offsets_meeting_hud_state_cache)
    if meetingHud_cachePtr is None:
        return 4
    meetingHud_cache = handle.read_int(meetingHud_cachePtr)
    if meetingHud_cache:
        meetingHudState_ptr = get_ptr(MeetingHudOffset, offsets_meeting_hud_state)
        meetingHudState = handle.read_int(int(meetingHudState_ptr))
    else:
        return 4
    return meetingHudState


def get_game_state():  # 0 = NotJoined, 1 = Joined, 2 = Started, 3 = Ended (during "defeat" or "victory" screen only)
    game_state_ptr = get_ptr(AmongUsClientOffset, offsets_game_state)
    game_state = handle.read_int(int(game_state_ptr))
    return game_state


def get_allPlayers():
    allP = []
    allPlayersPtr = get_ptr(PlayerOffset, offsets_all_players)
    if not allPlayersPtr:
        return
    allPlayers = handle.read_int(int(allPlayersPtr))
    playerAddrPtr = allPlayers + 0x10
    playerAddrPtr2 = ptr_calc(playerAddrPtr, [0])
    for i in range(get_player_count()):
        byte_arr = handle.read_bytes(int(playerAddrPtr2), 48)
        allP.append(PlayerInfo(byte_arr=byte_arr, handle=handle))
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


def get_player_count():
    player_count = 0
    player_countPtr = get_ptr(PlayerOffset, offsets_player_count)
    if player_countPtr:
        player_count = handle.read_int(int(player_countPtr))
    return player_count


def get_regionId():
    ptr = get_ptr(ServerManagerOffset, offsets_region_id)
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
    name_length = handle.read_int(int(ptr2 + 0x8))
    name = handle.read_bytes(int(ptr2 + 0xC), name_length << 1)
    if len(name) == 0 or len(name.decode("utf-8").split("\n")) != 2:
        return None
    data = name.decode("utf-8").replace("\x00", "").split("\n")[1]
    return data


# ----------------------------------------------------------------------------------------------------------------------
def check_leave(old_players, new_players):
    left = []
    for x in old_players:
        tmp = False
        for y in new_players:
            if x.PlayerName == y.PlayerName:
                tmp = True
        if not tmp:
            left.append(x)
    return left


def check_join(old_players, new_players):
    joined = []
    for x in new_players:
        tmp = False
        for y in old_players:
            if x.PlayerName == y.PlayerName:
                tmp = True
        if not tmp:
            joined.append(x)
    return joined


def check_colorChange(old_players, new_players):
    color_change = []
    if old_players is not None:
        for x in old_players:
            for y in new_players:
                if x.PlayerName == y.PlayerName:
                    if x.ColorId != y.ColorId:
                        color_change.append([x, y])
    return color_change


def check_disconnected(new_players):
    disconnect = []
    for x in new_players:
        if x.Disconnected == 1:
            disconnect.append(x)
    return disconnect


def check_dead(new_players):
    dead = []
    for x in new_players:
        if x.IsDead == 1:
            dead.append(x)
    return dead


# ----------------------------------------------------------------------------------------------------------------------
def arr_getter(data1):
    myArr = ""
    cnt = 1
    for x1 in data1:
        myArr = myArr + str(x1.ColorId)
        if cnt != len(data1):
            myArr = myArr + ","
        cnt = cnt + 1
    return myArr


# ----------------------------------------------------------------------------------------------------------------------
def main():
    global oldPlayers, Players, lobbycode, region, timer, laststatus, laststatus_cnt, game_state, sess_disconnected
    global sess_dead, sess_mute_state, player_count
    game_state = get_game_state()
    if game_state != 0 and datetime.now() > timer:
        oldPlayers = Players
        Players = get_allPlayers()

        if game_state == 1 or game_state == 3:  # if joined or ended
            sess_dead = []
            sess_disconnected = []
            colorchange = check_colorChange(oldPlayers, Players)
            if len(colorchange) != 0:
                for x in colorchange:
                    requests.post(url, data={"key": key, "token": token, "colorchange": str(x[0].ColorId) + "," + str(x[1].ColorId)})
            if player_count != get_player_count():
                player_count = get_player_count()
                requests.post(url, data={"key": key, "token": token, "playercount": str(player_count)})
            if lobbycode == "":
                time.sleep(2)
                region = get_regionId()
                requests.post(url, data={"key": key, "token": token, "regionId": str(region)})
                lobbycode = get_lobbyCode()
                if lobbycode is not None:
                    requests.post(url, data={"key": key, "token": token, "lobbycode": lobbycode})
        elif game_state == 2:  # if running
            disconnect = check_disconnected(Players)
            if len(disconnect) != 0:
                for x in disconnect:
                    if x.ColorId not in sess_disconnected:
                        sess_disconnected.append(x.ColorId)
                        requests.post(url, data={"key": key, "token": token, "leave": str(x.ColorId)})
            dead = check_dead(Players)
            if len(dead) != 0:
                for x in dead:
                    if x.ColorId not in sess_dead:
                        sess_dead.append(x.ColorId)
                        requests.post(url, data={"key": key, "token": token, "colorId": str(x.ColorId)})  # set dead and create if not existing

        if game_state == 2:  # if running
            if get_meetingHudState() == 4 and sess_mute_state != 1:  # mute
                requests.post(url, data={"key": key, "token": token, "mute": "1"})
                sess_mute_state = 1
            elif get_meetingHudState() != 4 and sess_mute_state != 2:  # unmute alive
                requests.post(url, data={"key": key, "token": token, "mute": "2"})
                sess_mute_state = 2
        elif sess_mute_state != 0:  # unmute all
            requests.post(url, data={"key": key, "token": token, "mute": "0"})
            sess_mute_state = 0

        game_state = get_game_state()
        timer = datetime.now() + timedelta(seconds=1)
    elif game_state == 0 and lobbycode != "":  # Not in a lobby
        requests.post(url, data={"key": key, "token": token, "mute": "0"})  # safety if player left lobby unmute all
        requests.post(url, data={"key": key, "token": token, "lobbycode": "NotSet"})
        requests.post(url, data={"key": key, "token": token, "playercount": "0"})
        # reset data
        player_count = 0
        oldPlayers = []
        Players = []
        lobbycode = ""
        sess_disconnected = []
        sess_dead = []
        sess_mute_state = 0
        laststatus_cnt = 0  # for idle after leaving a game

    if datetime.now() > laststatus:  # status update for timeout
        data = requests.post(url, data={"key": key, "token": token, "status": "1"}).json()
        newregion = get_regionId()
        if region != newregion or int(data["regionId"]) != newregion:
            requests.post(url, data={"key": key, "token": token, "regionId": str(newregion)})
        if game_state == 0:  # only when in idle
            if laststatus_cnt >= 30:
                messagebox.showerror("Timeout", "Please dont leave the program in idle! Stopping...")
                if game:
                    game.destroy()
                exit()
            laststatus_cnt = laststatus_cnt + 1
        laststatus = datetime.now() + timedelta(seconds=10)


# ----------------------------------------------------------------------------------------------------------------------
init_window()
while run_app:
    if state == 0:
        if not state_:
            among_init()
        else:
            among_check()
    elif state == 1 and not state_:
        token_init()
    elif state == 2:
        version_init()
    elif state == 3:
        if not state_:
            check_for_game_init()
        else:
            check_for_game_check()
    elif state == 4:
        main()

    if game is not None:
        game.update_idletasks()
        game.update()

    if state > 0 and not win32gui.FindWindow(0, "Among Us"):
        run_app = False
        game.destroy()
