debug = 1
BLOUT = 0
version = "v0.2-bl"
daily = True
# import module for pinging
import requests
import time
BLACKLIST = []
snt = 0
unavb = 0
msg = ""
def unavbsig(mg):
    global unavb, msg
    unavb = 1
    msg = mg
def runavb():
    global unavb
    unavb = 0
def dailyping():
    global daily,snt
    if daily:
        with open("dly", "r") as f:
            # read 1| and day of month
            dly = f.read()
        if dly == "0|{}".format(time.localtime().tm_mday):
            snt = 1
            return
        try:
            requests.get("https://google.com")
            with open("dly", "w") as f:
                f.write("0|{}".format(time.localtime().tm_mday))
            snt = 1
        except:
            with open("dly", "w") as f:
                # write 1| and day of month
                f.write("1|{}".format(time.localtime().tm_mday))
            snt = 0
dailyping()
def dprint(x):
    global debug
    if debug: print(x)
import threading
dprint("THREADING: OK")
import curses
# colors
dprint("CURSES: OK")
# tui local music player | mp3
import os
if os.path.exists("blacklist"):
    BLACKLIST = open(
            "blacklist",
            "r"
            ).read().split("\n")
# pygame support text off
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
dprint("OS: OK")
from pygame import mixer
dprint("PYGAME.MIXER: OK")
import DiscordRPC
try:

    rpc = DiscordRPC.RPC.Set_ID(app_id=1003981361079668829)
    act = 1
except:
    act = 0
dprint("DISCORD_RPC: OK")
KWAUDIO = False
KWLOOP = False
KILL = False
DESEL = False
class signals:
    def SIGTHKILL(a=None):
        global KILL
        KILL = True
    def isSIGTHKILL(a=None):
        global KILL
        return KILL
    def resetSIGKILL(a=None):
        global KWAUDIO
        KWAUDIO = False
    def SIGKILL(a=None):
        global KWAUDIO,path, current
        KWAUDIO = True
        path = None
        current = None
    def isSIGKILL(a=None):
        global KWAUDIO
        return KWAUDIO
    def SIGLOOP(a=None):
        global KWLOOP
        KWLOOP = True
    def isSIGLOOP(a=None):
        global KWLOOP
        return KWLOOP
    def resetSIGLOOP(a=None):
        global KWLOOP
        KWLOOP = False
dprint("SIGNALS: OK")
sig = signals()
path= "No mp3s found"
minm = 0
maxm = 14
current = "No mp3s found"
page = 0
sel = 0
current_page=[]
dprint("CONSTANTS: OK")
def getNewSongs(current_path):
    global current, path, BLOUT
    start = current_path
    allfiles = os.listdir("songs")
    while 1:
        try:
            nexts =  allfiles[
                allfiles.index(current_path)+1
                    ]
        except:
            nexts = allfiles[0]
        if nexts in BLACKLIST:
            BLOUT = 1
            current_path = nexts
            if current_path == start:
                unavbsig("unavailable")
                return
            continue
        else: break
    current = nexts
    path = "songs/"+nexts
pathverb = "Nothing"
def drawsongs(win):
    maxy, maxx = win.getmaxyx()
    global minm, maxm, current, page, sel,current_page, DESEL, pathverb
    allfiles = os.listdir("songs")
    mp3s = []
    for i in allfiles:
        if i.endswith('.mp3'):
            mp3s.append(i)
    current_page = mp3s[page*14:page*14+14]
    if len(current_page) == 0:
        current_page = ["No mp3s found"]
    try:
        for i in range(len(current_page)):
            wp = current_page[i] if len(current_page[i]) < 33 else current_page[i][:33]
            wp = wp[:-6]+"..." if len(wp) == 33 else wp
            wp = wp.replace(".mp3", "")
            if current_page[i] == current:
                pathverb = wp
            if i == sel and not DESEL:
                win.addstr(i+1, 1, wp, curses.A_STANDOUT)
                win.addstr(i+1, len(wp)+1, " "*(50-len(wp)-1))
                if current_page[i] == current:
                    win.addstr(i+1, len(wp)+1, " *", curses.color_pair(2))
                elif current_page[i] in BLACKLIST:
                    win.addstr(i+1, len(wp)+1, " BL", curses.color_pair(1))
            elif current_page[i] in BLACKLIST:
                win.addstr(i+1, 1, wp)
                win.addstr(i+1, len(wp)+1, " "*(50-len(wp)-1))
                win.addstr(i+1, len(wp)+1, " BL", curses.color_pair(1))
            elif current_page[i] == current:
                win.addstr(i+1, 1, wp, curses.A_BOLD)
                win.addstr(i+1, len(wp)+1, " "*(50-len(wp)-1))
                win.addstr(i+1, len(wp)+1, " *", curses.color_pair(2))
            else:
                win.addstr(i+1, 1, wp)
                win.addstr(i+1, len(wp)+1, " "*(50-len(wp)-1))
            if i == 0:
                win.addstr(1, maxx-6, "P:"+(" "+str(page+1) if page < 10 else str(page)), curses.A_BOLD)
    except Exception as e:
        print(e)

    if len(current_page) < 14:
        for i in range(len(current_page), 14):
            win.addstr(i+1, 1, " "*(50-1))
dprint("DRAWSONGS: OK")
def draw(win):
    global version, snt, pathverb, unavb, msg
    red_color = "\033[31m"
    green_color = "\033[32m"
    reset_color = "\033[0m"

    drawsongs(win)
    maxy, maxx = win.getmaxyx()
    win.box()
    win.addstr(maxy-5, 0, "├"+("─"*(maxx-2))+("┤"))  #  #
    tx = {"1": "Version  Loop       Crystal            Volume",
          "2": pathverb}
    if pathverb != "Nothing":
        win.addstr(maxy-4, 2, tx["2"], curses.color_pair(2))
    else:
        win.addstr(maxy-4, 2, "Select something", curses.color_pair(2))
    win.addstr(maxy-4, len(pathverb if pathverb != "Nothing" else "Select something")+2, " "*(48-len(pathverb if pathverb != "Nothing" else "Select something")-1))
    if unavb:
        win.addstr(maxy-4, maxx-(len(msg)+2), msg, curses.color_pair(1))
    win.addstr(maxy-3, 2 , tx["1"])
    issig = sig.isSIGLOOP()
    # curses green
    if not curses.has_colors():
        curses.start_color()
    dlyy = "ping sent" if snt else "offline w"
    win.addstr(maxy-2, 2, "{}".format(version),curses.A_BOLD)
    win.addstr(maxy-2, 11, "{} ".format(issig), curses.color_pair(2) if issig else curses.color_pair(1))
    win.addstr(maxy-2, maxx//2-4, dlyy, curses.color_pair(2 if dlyy == "ping sent" else 1))
    mx = str(mixer.music.get_volume())[:4]
    mx += "0" if mx == "0.5" else ""
    win.addstr(maxy-2, maxx-(len("VOL {}".format(mx))+2), "VOL {}".format(mx), curses.A_BOLD)
dprint("DRAW: OK")
thread = None
callbacks = {'ready': lambda: print('ready'),
             'disconnected': lambda: print('disconnected'),
             'error': lambda: print('error')}

def main(stdscr):
    global thread, callbacks
    curses.curs_set(0)
    # enable colors
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    win = curses.newwin(20, 50, 0, 1)
    thread = threading.Thread(target=playAudio, args=(win,))
    thread.start()
    stdscr.refresh()
    while True:
        draw(win)
        win.refresh()
        getc = stdscr.getkey()
        process(getc, win)
dprint("MAIN: OK")
def blacklist(select):
    global BLACKLIST, current
    if select in BLACKLIST:
        BLACKLIST.remove(select)
    else:
        if select == current:
            unavbsig("is current")
            return
        BLACKLIST.append(select)
def process(getc, win):
    runavb()
    global minm, maxm, current, page, sel, path, DESEL, current_page, pathverb
    if getc == 'q':
        # kill thread
        sig.SIGTHKILL()
        exit()

    if getc == "KEY_DOWN":
        if sel >= 13:
            sel = 0
            page += 1
        else:
            if not sel == len(current_page)-1:
                sel+=1
    if getc == "KEY_UP":
        if sel <= 0 and not page == 0:
            sel = maxm-1
            page -= 1
        else:
            if not sel == 0:
                sel -= 1
    if getc == "KEY_ENTER" or getc == "KEY_RIGHT" or getc == "p":
        sig.SIGKILL()
        getNewSongs(current_page[current_page.index(current_page[sel])-1])
    if getc == "b":
        blacklist(current_page[sel])
    if getc == "s":
        pathverb = "Nothing"
        sig.SIGKILL()
    if getc == "l":
        if sig.isSIGLOOP():
            sig.resetSIGLOOP()
        else:
            sig.SIGLOOP()
    if getc == "kUP5":
        mixer.music.set_volume(mixer.music.get_volume()+0.05)
    if getc == "kDN5":
        mixer.music.set_volume(mixer.music.get_volume()-0.05)
    if getc == "d":
        DESEL = not DESEL

dprint("PROCESS: OK")
def playAudio(win):
    global path,current, rpc,act, BLOUT
    # check if path instance of NULL
    prev = None
    newly = 0
    while True:
        try:
            if path.endswith('.mp3'):
                if prev == path and not sig.isSIGLOOP():
                    if not BLOUT:
                        continue
                    BLOUT = 0
                prev = path
                mixer.music.load(path)
                while True:
                    mixer.music.play()
                    newly = 0
                    xx = current[:-4]
                    if act:
                        rpc.set_activity(details="Enjoying Crystal+", state="Playing: {}".format(xx), 
                                     large_image="defau", small_image="plus",
                                     timestamp=time.time())
                    while mixer.music.get_busy():
                        if sig.isSIGTHKILL():
                            break
                        if sig.isSIGKILL():
                            mixer.music.stop()
                            break
                        if prev != path:
                            sig.SIGKILL()
                        time.sleep(0.1)
                    if sig.isSIGKILL():
                        prev = None
                        mixer.music.stop()
                        sig.resetSIGKILL()
                        break
                    if sig.isSIGTHKILL():
                        break
                    if not sig.isSIGLOOP():
                        mixer.music.stop()
                        break
                    else:
                        mixer.music.rewind()
                    time.sleep(0.1)
                time.sleep(0.1)
        except: pass
        if sig.isSIGTHKILL():
            break
        if prev != None and not sig.isSIGKILL() and not sig.isSIGTHKILL():
            newly += 1
            getNewSongs(current)
            draw(win)
            win.refresh()
        if sig.isSIGKILL():
            sig.resetSIGKILL()
        time.sleep(0.1)
dprint("PLAYAUDIO: OK")
        
if __name__ == '__main__':
    mixer.init()
    mixer.music.set_volume(0.5)
    curses.wrapper(main)
    # init pygame
    #mixer.music.load("test.mp3")
    #mixer.music.play()
    #while True:
    #   time.sleep(1)


