import curses
import sys

import mainytVLC

class YTVLCPrinter:
    def __init__(self, stdscr, **kwargs):
        self.stdscr = stdscr
        self.input_title = kwargs.get("input_title", "INPUT")
        self.list_title = kwargs.get("list_title", "LIST")
        self.prompt_msg = kwargs.get("prompt_msg", "Enter input: ")
        self.transition_msg = kwargs.get("transition_msg", "Please wait...")

        self.query = None
        self.current_results = None # list -> [title 1, title 2, ...]
        self.vid_infos = None # dict -> {"title":"link", ...}
        self.current_results_page = None # youtubesearchpython object
        self.go_to_next_page = False

        self.option = None
        self.quality = None

        self.handler()

    def handler(self):
        while True:
            if not self.go_to_next_page:
                self.curses_input_printer(self.stdscr, self.input_title, self.prompt_msg)
            self.curses_transition_printer(self.stdscr, self.transition_msg)
            self.curses_list_printer(self.stdscr, self.list_title, self.current_results)

            if isinstance(self.option, int) and self.quality:
                self.quality = self.quality.replace("p", "")
                url = list(self.vid_infos.values())[int(self.option)]
                vid_info = mainytVLC.get_video_info(url, self.quality)
                video, audio = vid_info["requested_formats"]
                mainytVLC.play_media(video["url"], audio["url"])
                self.option = None
                self.quality = None

    def curses_input_printer(self, stdscr, title, prompt_msg):
        inpt = ""

        while True:
            stdscr.erase()
            stdscr.addstr(0, 0, f"{title}")
            stdscr.addstr(1, 0, f"{prompt_msg}")
            curses.curs_set(1)
            stdscr.clrtobot()
            stdscr.addstr(inpt)

            char = stdscr.getch()
            if isinstance(char, int) and 31 < char < 127:
                inpt += chr(char)
            elif char == 8: # Backspace
                inpt = inpt[:-1]
            elif char == 127: # Ctrl + Backspace
                inpt = ""
            elif char == 10: # Enter
                break
            elif char == 17 or char == 27: # Ctrl + q or Esc
                sys.exit()
            else:
                raise AssertionError(repr(char))

        self.query = inpt

    def curses_transition_printer(self, stdscr, transition_msg):
        stdscr.addstr(0, 0, f"{transition_msg}")
        curses.curs_set(0)
        stdscr.clrtobot()
        stdscr.refresh()

        if not self.go_to_next_page:
            self.vid_infos, self.current_results_page = mainytVLC.search_youtube(self.query, 20)
        else:
            search_result = mainytVLC.get_next_results(self.current_results_page)
            self.vid_infos, self.current_results_page = mainytVLC.search_youtube(search_result=search_result)
            self.go_to_next_page = False
        self.current_results = list(self.vid_infos.keys())

    def curses_list_printer(self, stdscr, title, obj_to_be_printed, multiple_instance=True):
        attributes = {}
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        attributes['normal'] = curses.color_pair(1)

        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        attributes['highlighted'] = curses.color_pair(2)

        char = 0  # last character read
        option = 0  # the current option that is marked
        while char != 10:  # Enter in ascii
            stdscr.erase()
            stdscr.addstr(f"{title}\n")
            curses.curs_set(0)

            for i in range(len(obj_to_be_printed)):
                if i == option:
                    attr = attributes['highlighted']
                else:
                    attr = attributes['normal']
                stdscr.addstr(f"{2*' '}[{i+1}] ")
                stdscr.addstr(obj_to_be_printed[i] + '\n', attr)

            char = stdscr.getch()
            if char == 444: # Ctrl + Right Arrow
                break
            elif char == 17 or char == 27: # Ctrl + q or Esc
                sys.exit()
            elif char == curses.KEY_UP and option > 0:
                option -= 1
            elif char == curses.KEY_DOWN and option < len(obj_to_be_printed) - 1:
                option += 1

        if char == 10:
            if multiple_instance:
                qual_list = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
                quality = self.curses_list_printer(self.stdscr, "CHOOSE QUALITY", qual_list, False)
                self.option = option
                self.quality = quality
            else:
                return obj_to_be_printed[option]
        else:
            self.go_to_next_page = True

if __name__ == "__main__":
    opts = {"input_title":"YOUTUBE VLC", "list_title":"CHOOSE VIDEO - SHORTCUT KEYS: <Ctrl + Right Arrow> To go to next page",
            "prompt_msg":"Search Youtube: ", "transition_msg":"Searching..."}
    curses.wrapper(YTVLCPrinter, **opts)
