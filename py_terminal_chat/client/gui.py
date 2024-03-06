import curses


class ChatWindow:
    def __init__(self, max_x: int, max_y: int, input_height: int = 3):
        self.height = max_y - (input_height + 1)
        self.window = curses.newwin(self.height, max_x, 0, 0)
        self.window.scrollok(True)

    def add_message(self, message: str):
        self.window.scroll()
        self.window.addstr(self.height - 1, 1, message)
        self.window.refresh()


class InputWindow:
    def __init__(self, max_x: int, max_y: int, prefix="> "):
        self.prefix = prefix
        self.max_x, self.max_y = max_x, max_y
        self.height = 3
        self.window = curses.newwin(
            self.height, self.max_x, self.max_y - self.height, 0
        )

    def refresh(self):
        self.window.clear()
        self.window.refresh()
        self.window.border()
        self.window.addstr(1, 1, self.prefix)

    def get_input_message(self) -> str:
        return self.window.getstr(1, len(self.prefix) + 1).decode("utf-8").strip()
