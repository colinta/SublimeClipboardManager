import sublime
import sublime_plugin


class HistoryList(list):
    """List type for storing the history - fairly
    inefficient, but useful.
    """

    SIZE = 256
    __index = 0

    def at(self, idx):
        self.__index = idx if idx < len(self) else 0

    def append(self, item):
        self.insert(0, item)
        self.__index = 0
        if len(self) > self.SIZE:
            del self[self.SIZE:]

    def current(self):
        if len(self) == 0:
            return None
        return self[self.__index]

    def next(self):
        if self.__index > 0:
            self.__index -= 1

    def previous(self):
        if self.__index < len(self) - 1:
            self.__index += 1

    def first(self):
        """"first" actually kind of means "last", since this is a FIFO stack"""
        self.__index = len(self) - 1

    def last(self):
        """"last" actually kind of means "first", since this is a FIFO stack"""
        self.__index = 0


HISTORY = HistoryList()


class ClipboardManagerBase(sublime_plugin.TextCommand):
    def update_clipboard(self, content):
        sublime.status_message('Set Clipboard to "' + content + '"')
        sublime.set_clipboard(content)

    def next(self):
        HISTORY.next()
        self.update_clipboard(HISTORY.current())

    def previous(self):
        HISTORY.previous()
        self.update_clipboard(HISTORY.current())

    def appendClipboard(self):
        # append the contents of the clipboard to the history
        if not HISTORY or HISTORY[0] != sublime.get_clipboard():
            HISTORY.append(sublime.get_clipboard())


class ClipboardManagerPaste(ClipboardManagerBase):
    def run(self, edit, indent=False):
        # If the user pastes something that was copied in a different program, it will not be in sublime's buffer, so we attempt to append every time
        self.appendClipboard()
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')


class ClipboardManagerCut(ClipboardManagerBase):
    def run(self, edit):
        # First run sublime's command to extract the selected text.
        # This will set the cut/copy'd data on the clipboard which we can easily steal without recreating the cut/copy logic.
        self.view.run_command('cut')
        self.appendClipboard()


class ClipboardManagerCopy(ClipboardManagerBase):
    def run(self, edit):
        self.view.run_command('copy')
        self.appendClipboard()


class ClipboardManagerNext(ClipboardManagerBase):
    def run(self, edit):
        self.next()


class ClipboardManagerNextAndPaste(ClipboardManagerBase):
    def run(self, edit, indent=False):
        self.next()
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')


class ClipboardManagerPrevious(ClipboardManagerBase):
    def run(self, edit):
        self.previous()


class ClipboardManagerPreviousAndPaste(ClipboardManagerBase):
    def run(self, edit, indent=False):
        self.previous()
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')


class ClipboardManagerChooseAndPaste(ClipboardManagerBase):
    def run(self, edit):
        def format(line):
            return line.replace('\n', '\\n')[:64]

        lines = []
        line_map = {}
        # filter out duplicates, keeping the first instance, and format
        for i, line in enumerate(HISTORY):
            if i == HISTORY.index(line):
                line_map[len(lines)] = i
                lines.append(format(line))

        def on_done(idx):
            if idx >= 0:
                idx = line_map[idx]
                HISTORY.at(idx)
                self.update_clipboard(HISTORY.current())
                self.view.run_command('paste')

        if lines:
            sublime.active_window().show_quick_panel(lines, on_done)
        else:
            sublime.status_message('Nothing in history')
