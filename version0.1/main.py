debug = 1
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
# pygame support text off
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
dprint("OS: OK")
from pygame import mixer
dprint("PYGAME.MIXER: OK")
import time
dprint("TIME: OK")
KWAUDIO = False
KWLOOP = False
KILL = False
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
def getNextSong(current_path):
    allfiles = os.listdir("songs")
    nexts =  allfiles[
        allfiles.index(current_path)+1
            ]
    current = nexts
    path = "songs/"+nexts
def drawsongs(win):
    maxy, maxx = win.getmaxyx()
    global minm, maxm, current, page, sel,current_page
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
            wp = current_page[i] if len(current_page[i]) < 30 else current_page[i][:30]
            wp = wp[:-6]+"...mp3" if len(wp) == 30 else wp
            if i == sel:
                win.addstr(i+1, 1, wp, curses.A_STANDOUT)
                win.addstr(i+1, len(wp)+1, " "*(50-len(wp)-1))
                if current_page[i] == current:
                    win.addstr(i+1, len(wp)+1, " *", curses.color_pair(2))
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
    red_color = "\033[31m"
    green_color = "\033[32m"
    reset_color = "\033[0m"

    drawsongs(win)
    maxy, maxx = win.getmaxyx()
    win.box()
    win.addstr(maxy-5, 0, "├"+("─"*(maxx-2))+("┤"))
    tx = {"1": "q: Quit, l: Loop, p: Play, s: Stop, u/d: pr/ne",
          "2": "Crystal+ TUI Music Player"}
    win.addstr(maxy-4, (maxx//2)-len(tx["2"])//2 , tx["2"])
    win.addstr(maxy-3, (maxx//2)-len(tx["1"])//2 , tx["1"])
    issig = sig.isSIGLOOP()
    # curses green
    if not curses.has_colors():
        curses.start_color()
    win.addstr(maxy-2, 2, "v0.1beta",curses.A_BOLD)
    win.addstr(maxy-2, 11, "{} ".format(issig), curses.color_pair(2) if issig else curses.color_pair(1))
    win.addstr(maxy-2, maxx-17, "daily ping sent", curses.color_pair(2))
    win.addstr(maxy-2, 21, "VOL {}".format(str(mixer.music.get_volume())[:4]), curses.A_BOLD)
dprint("DRAW: OK")
thread = None
def main(stdscr):
    global thread
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
def process(getc, win):
    global minm, maxm, current, page, sel, path
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
        current = current_page[sel]
        path = "songs/"+current

    if getc == "s":
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
dprint("PROCESS: OK")
def playAudio(win):
    global path
    # check if path instance of NULL
    prev = None
    while True:
        try:
            if path.endswith('.mp3'):
                if prev == path and not sig.isSIGLOOP():
                    continue
                prev = path
                mixer.music.load(path)
                while True:
                    mixer.music.play()
                    while mixer.music.get_busy():
                        if sig.isSIGTHKILL():
                            break
                        if sig.isSIGKILL():
                            mixer.music.stop()
                            break
                        if prev != path:
                            sig.SIGKILL()
                        time.sleep(0.1)
                    if sig.isSIGTHKILL():
                        break
                    if sig.isSIGKILL():
                        prev = None
                        sig.resetSIGKILL()
                        break
                    if not sig.isSIGLOOP():
                        mixer.music.stop()
                        break
                    else:
                        mixer.music.rewind()
                    time.sleep(0.1)
        except: pass
        if sig.isSIGTHKILL():
            break
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


