from main_console_lib import *
import time

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


# ----------------------------------------------------------------------------------------------------------------------
checkforgametimer = datetime.now()
checkforgamecount = 0
while True:
    if datetime.now() > checkforgametimer:
        url2 = url + "?key=" + key + "&token=" + str(token)
        data = requests.get(url2).json()
        if data["gameExists"]:
            if lang == 0:
                print("Spiel gefunden! Viel Spaß!")
            elif lang == 1:
                print("Found game! Have fun!")
            break
        else:
            if lang == 0:
                print("Bitte joine einem voice channel und schreibe au!play in einen Textchannel! Versuche es in 10 Sekunden erneut...")
            elif lang == 1:
                print("Please join a voice channel and write au!play into a text channel! Checking again in 10 seconds.")
            checkforgametimer = datetime.now() + timedelta(seconds=10)
            checkforgamecount += 1
            if checkforgamecount >= 15:
                if lang == 0:
                    print("Bitte lass das Programm nicht unnötig offen! Stoppe...")
                elif lang == 1:
                    print("Please dont leave the program in idle! Stopping...")
                os.system("pause")
                exit()

# ----------------------------------------------------------------------------------------------------------------------
while win32gui.FindWindow(0, "Among Us"):
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
                if lobbycode is None:
                    if lang == 0:
                        print("Lobbycode nicht erkannt")
                    elif lang == 1:
                        print("Lobbycode not recognized")
                else:
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
        if data["result"] != "success":
            if lang == 0:
                print("Token nicht gültig? Stoppe...")
            elif lang == 1:
                print("Token invalid? Stopping...")
            break
        newregion = get_regionId()
        if region != newregion or int(data["regionId"]) != newregion:
            requests.post(url, data={"key": key, "token": token, "regionId": str(newregion)})
        if gamestate == 0:  # only when in idle
            if laststatus_cnt >= 15:
                if lang == 0:
                    print("Bitte lass das Programm nicht unnötig offen! Stoppe...")
                elif lang == 1:
                    print("Please dont leave the program in idle! Stopping...")
                os.system("pause")
                exit()
            laststatus_cnt = laststatus_cnt + 1
        laststatus = datetime.now() + timedelta(seconds=10)
