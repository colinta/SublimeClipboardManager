import sublime
import sublime_plugin


class HistoryList(list):
    """
    List type for storing the history.
    Maintains a "pointer" to the current clipboard item
    """

    SIZE = 256
    __index = 0

    def show(self):
        ret = ""
        ret += " CLIPBOARD HISTORY (%d)\n" % len(self)
        ret += "====================%s==\n" % ("=" * len(str(len(self))))
        for i, item in enumerate(self):
            if i == self.__index:
                ret += '--> '
            else:
                ret += '    '
            item = item.replace("\t", "\\t")
            item = item.replace("\n", "\\n")
            item = item.replace("\r", "\\r")
            ret += str(i + 1) + '. ' + item + "\n"
        return ret

    def append(self, item):
        """
        Appends to the history only if it isn't the current
        item.
        """
        if not self or self[self.__index] != item:
            self.insert(0, item)
            self.__index = 0
            if len(self) > self.SIZE:
                del self[self.SIZE:]

    def current(self):
        if len(self) == 0:
            return None
        return self[self.__index]

    def at(self, idx):
        self.__index = (idx if idx < len(self) else 0)
        self.status()

    def next(self):
        if self.__index > 0:
            self.__index -= 1
        self.status()

    def previous(self):
        if self.__index < len(self) - 1:
            self.__index += 1
        self.status()

    def first(self):
        """"first" actually kind of means "last", since this is a FIFO stack"""
        self.__index = len(self) - 1
        self.status()

    def last(self):
        """"last" actually kind of means "first", since this is a FIFO stack"""
        self.__index = 0
        self.status()

    def status(self):
        sublime.status_message('Set Clipboard to "' + self.current() + '"')
        sublime.set_clipboard(self.current())


HISTORY = HistoryList([sublime.get_clipboard()])


def append_clipboard():
    # append the contents of the clipboard to the history
    HISTORY.append(sublime.get_clipboard())


class ClipboardManagerPaste(sublime_plugin.TextCommand):
    def run(self, edit, indent=False):
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')


class ClipboardManagerCut(sublime_plugin.TextCommand):
    def run(self, edit):
        # First run sublime's command to extract the selected text.
        # This will set the cut/copy'd data on the clipboard which we can easily steal without recreating the cut/copy logic.
        self.view.run_command('cut')
        append_clipboard()


class ClipboardManagerCopy(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command('copy')
        append_clipboard()


class ClipboardManagerNext(sublime_plugin.TextCommand):
    def run(self, edit):
        HISTORY.next()


class ClipboardManagerNextAndPaste(sublime_plugin.TextCommand):
    def run(self, edit, indent=False):
        HISTORY.next()
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')


class ClipboardManagerPrevious(sublime_plugin.TextCommand):
    def run(self, edit):
        HISTORY.previous()


class ClipboardManagerPreviousAndPaste(sublime_plugin.TextCommand):
    def run(self, edit, indent=False):
        HISTORY.previous()
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')


class ClipboardManagerShow(sublime_plugin.WindowCommand):
    def run(self):
        v = self.window.get_output_panel('clipboard_manager')
        e = v.begin_edit('clipboard_manager')
        v.replace(e, sublime.Region(0, v.size()), '')
        v.insert(e, 0, HISTORY.show())
        v.end_edit(e)
        self.window.run_command('show_panel', {'panel': 'output.clipboard_manager'})


class ClipboardManagerChooseAndPaste(sublime_plugin.TextCommand):
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
                self.view.run_command('paste')

        if lines:
            sublime.active_window().show_quick_panel(lines, on_done)
        else:
            sublime.status_message('Nothing in history')


class ClipboardManagerEventListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        append_clipboard()
