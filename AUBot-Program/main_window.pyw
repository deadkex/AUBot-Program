import pymem
import win32gui
import time
import requests
from datetime import datetime, timedelta
from structs import *
import webbrowser
from tkinter import *
from tkinter import messagebox

# ----------------------------------------------------------------------------------------------------------------------
versionId = "10"
with open("config.txt", 'r', encoding='utf-8') as keyFile:
    key = keyFile.readline().replace("\n", "")
    url = keyFile.readline()
handle = None
module_addr = None
token = ""

# ----------------------------------------------------------------------------------------------------------------------
game = None
canvas = None
state = 0
state_ = False
label_amonginit = None
label_tokeninit = None
label_versioninit = None
label_checkforgame = None
canvas_elements = []
run_app = True
checkforgametimer = datetime.now()
checkforgamecount = 0

# ----------------------------------------------------------------------------------------------------------------------
oldPlayers = []
Players = []
lobbycode = ""
region = 99
timer = datetime.now()
laststatus = datetime.now()
laststatus_cnt = 0
gamestate = 0
sess_disconnected = []
sess_dead = []
sess_mute_state = 0
playercount = 0

# Offsets --------------------------------------------------------------------------------------------------------------
AmongUsClientOffset = 46580344
GameDataOffset = 46580344
MeetingHudOffset = 46577548
GameStartManagerOffset = 45252408
ServerManagerOffset = 45221608
PlayerOffset = 46579836

offsets_lobby_code = [92, 0, 32, 40]
offsets_meetinghud_state_cache = [92, 0, 8]
offsets_meetinghud_state = [92, 0, 132]
offsets_all_players = [92, 0, 36, 8]
offsets_playercount = [92, 0, 36, 12]
offsets_game_state = [92, 0, 108]
offsets_region_id = [92, 0, 16, 8, 8]


# ----------------------------------------------------------------------------------------------------------------------
def on_close_window():
    global run_app
    run_app = False
    game.destroy()


def destroy_canvaselements():
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
    global label_amonginit, state_
    label_amonginit = Label(game, text="Among Us not found", font=("Arial", 10), fg="red", anchor="w")
    label_amonginit.place(x=0, y=0, width=label_amonginit.winfo_reqwidth(), height=label_amonginit.winfo_reqheight())
    state_ = True


def among_check():
    global label_amonginit, state, state_, module_addr, handle
    if win32gui.FindWindow(0, "Among Us"):
        label_amonginit.config(text="Among Us found", fg="green")
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
    global canvas_elements, state_, label_tokeninit, state, token

    label_tokeninit = Label(game, text="Checking for token...", font=("Arial", 10), fg="red", anchor="w")
    label_tokeninit.place(x=0, y=20, width=label_tokeninit.winfo_reqwidth(), height=label_tokeninit.winfo_reqheight())

    token = token_checkFile()
    if token is not None:
        if token_check():
            return

    label_tokeninit.configure(text="Input token")

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
    global state_, token, state, label_tokeninit
    if not state_:
        url3 = url + "?key=" + key + "&token=" + str(token)
    else:
        url3 = url + "?key=" + key + "&token=" + str(canvas_elements[0].get())
        token = canvas_elements[0].get()
    data2 = requests.get(url3)
    if "tokenExists" in data2.text:
        data2 = data2.json()
        if data2["tokenExists"]:
            label_tokeninit.configure(text="Token found", fg="green")
            with open('AUBotToken.txt', 'w') as file2:
                file2.write(token)
            state = state + 1
            if state_:
                destroy_canvaselements()
            state_ = False
            return True
    if state_:
        messagebox.showerror("Error", "Wrong token entered!")
    return False


# ----------------------------------------------------------------------------------------------------------------------
def version_init():
    global versionId, token, label_versioninit, state
    label_versioninit = Label(game, text="Checking for version...", font=("Arial", 10), fg="red", anchor="w")
    label_versioninit.place(x=0, y=40, width=label_versioninit.winfo_reqwidth(), height=label_versioninit.winfo_reqheight())

    url2 = url + "?key=" + key + "&token=" + str(token)
    data = requests.get(url2).json()
    if data["version"] == versionId:
        label_versioninit.configure(text="Program up to date", fg="green")
        state = state + 1
    else:
        label_versioninit.configure(text="Wrong version!")
        messagebox.showerror("Error", "Please update the program!\nYour version: " + versionId + " | Required version: " + data["version"])
        exit()


# ----------------------------------------------------------------------------------------------------------------------
def checkforgame_init():
    global label_checkforgame, state_
    label_checkforgame = Label(game, text="Checking for game.", font=("Arial", 10), fg="red", anchor="w")
    label_checkforgame.place(x=0, y=60, width=200, height=label_checkforgame.winfo_reqheight())
    state_ = True


def checkforgame_check():
    global label_checkforgame, state_, checkforgametimer, checkforgamecount, state
    if datetime.now() > checkforgametimer:
        url2 = url + "?key=" + key + "&token=" + str(token)
        data = requests.get(url2).json()
        if data["gameExists"]:
            label_checkforgame.configure(text="Found game! Have fun!", fg="green")
            state_ = False
            state = state + 1
            destroy_canvaselements()
        else:
            label_checkforgame.configure(text="Checking for game. Retries: " + str(checkforgamecount))
            label1 = Label(game, text="Please join a voice channel and", font=("Arial", 10), fg="red", anchor="w")
            label1.place(x=0, y=80, width=label1.winfo_reqwidth(), height=label1.winfo_reqheight())
            canvas_elements.append(label1)
            label2 = Label(game, text="write au!play into a text channel!", font=("Arial", 10), fg="red", anchor="w")
            label2.place(x=0, y=100, width=label2.winfo_reqwidth(), height=label2.winfo_reqheight())
            canvas_elements.append(label2)

            checkforgametimer = datetime.now() + timedelta(seconds=10)
            checkforgamecount += 1
            if checkforgamecount >= 15:
                messagebox.showerror("Timeout", "Please dont leave the program in idle! Stopping...")
                exit()


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
    playerCountPtr = get_ptr(PlayerOffset, offsets_playercount)
    if playerCountPtr:
        playerCount = handle.read_int(int(playerCountPtr))
    return playerCount


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


# ----------------------------------------------------------------------------------------------------------------------
def main():
    global oldPlayers, Players, lobbycode, region, timer, laststatus, laststatus_cnt, gamestate, sess_disconnected
    global sess_dead, sess_mute_state, playercount
    gamestate = get_gameState()
    if gamestate != 0 and datetime.now() > timer:
        oldPlayers = Players
        Players = get_allPlayers()

        if gamestate == 1 or gamestate == 3:  # if joined or ended
            sess_dead = []
            sess_disconnected = []
            colorchange = check_colorChange(oldPlayers, Players)
            if len(colorchange) != 0:
                for x in colorchange:
                    requests.post(url, data={"key": key, "token": token, "colorchange": str(x[0].ColorId) + "," + str(x[1].ColorId)})
            if playercount != get_playerCount():
                playercount = get_playerCount()
                requests.post(url, data={"key": key, "token": token, "playercount": str(playercount)})
            if lobbycode == "":
                time.sleep(2)
                region = get_regionId()
                requests.post(url, data={"key": key, "token": token, "regionId": str(region)})
                lobbycode = get_lobbyCode()
                if lobbycode is not None:
                    requests.post(url, data={"key": key, "token": token, "lobbycode": lobbycode})
        elif gamestate == 2:  # if running
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

        if gamestate == 2:  # if running
            if get_meetingHudState() == 4 and sess_mute_state != 1:  # mute
                requests.post(url, data={"key": key, "token": token, "mute": "1"})
                sess_mute_state = 1
            elif get_meetingHudState() != 4 and sess_mute_state != 2:  # unmute alive
                requests.post(url, data={"key": key, "token": token, "mute": "2"})
                sess_mute_state = 2
        elif sess_mute_state != 0:  # unmute all
            requests.post(url, data={"key": key, "token": token, "mute": "0"})
            sess_mute_state = 0

        gamestate = get_gameState()
        timer = datetime.now() + timedelta(seconds=1)
    elif gamestate == 0 and lobbycode != "":  # Not in a lobby
        requests.post(url, data={"key": key, "token": token, "mute": "0"})  # safety if player left lobby unmute all
        requests.post(url, data={"key": key, "token": token, "lobbycode": "NotSet"})
        requests.post(url, data={"key": key, "token": token, "playercount": "0"})
        # reset data
        playercount = 0
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
        if gamestate == 0:  # only when in idle
            if laststatus_cnt >= 15:
                messagebox.showerror("Timeout", "Please dont leave the program in idle! Stopping...")
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
            checkforgame_init()
        else:
            checkforgame_check()
    elif state == 4:
        main()

    if game is not None:
        game.update_idletasks()
        game.update()

    if state > 0 and not win32gui.FindWindow(0, "Among Us"):
        run_app = False
        game.destroy()
