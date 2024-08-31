from colorama import Fore, Style, Back, init
from threading import Lock
from datetime import datetime
import ctypes
lock = Lock()

bright = Style.BRIGHT
reset = Style.RESET_ALL
green = Fore.GREEN
red = Fore.RED
yellow = Fore.YELLOW
blue = Fore.BLUE
cyan = Fore.CYAN
magenta = Fore.MAGENTA
white = Fore.WHITE
black = Fore.BLACK

valid,invalid=0,0
class TL:
    def timestamp():
        return datetime.now().strftime("%H:%M:%S")

    def log(tag:str, content, color):
        ts = TL.timestamp()
        with lock:
            init()
            return print(
                f"{bright}{white}[{blue}{ts}{white}][{color}{tag.upper()[:4]}{white}] {green}- {white}{content}{reset}"
            )
    def remove_content(filename: str, delete_line: str) -> None:
        with open(filename, "r+") as io:
            content = io.readlines()
            io.seek(0)
            for line in content:
                if not (delete_line in line):
                    io.write(line)
            io.truncate()
    
    def add_content(file:str,content:str)->None:
      with open(file,'a') as f:
        f.write(content+'\n')
    
    def update_console_title(new_title):
      hwnd = ctypes.windll.kernel32.GetConsoleWindow()
      ctypes.windll.kernel32.SetConsoleTitleW(new_title)