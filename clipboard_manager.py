import re

import sublime
import sublime_plugin


HISTORY = None
PANEL_SHOWING = None


def plugin_loaded():
    global HISTORY

    HISTORY = HistoryList([HistoryEntry(sublime.get_clipboard(), None)])


class HistoryEntry(object):
    def __init__(self, item, syntax):
        self.item = item
        self.syntax = syntax


class HistoryList(list):
    """
    List type for storing the history.
    Maintains a "pointer" to the current clipboard item
    """
    registers = {}
    SIZE = 256
    __index = 0

    def show_current(self, panel):
        entry = self[self.__index]
        return self.show(entry, panel)

    def show(self, entry, panel):
        syntax = entry.syntax or 'Packages/Text/Plain text.tmLanguage'
        panel.set_syntax_file(syntax)
        ret = entry.item
        return ret

    def show_all(self, panel):
        syntax = 'Packages/Text/Plain text.tmLanguage'
        panel.set_syntax_file(syntax)

        ret = ""
        ret += " CLIPBOARD HISTORY (%d)\n" % len(self)
        ret += "====================%s==\n" % ("=" * len(str(len(self))))
        for i, entry in enumerate(self):
            item = entry.item
            if i == self.__index:
                ret += '--> '
            else:
                ret += '    '
            item = item.replace("\t", '\\t')
            item = item.replace("\r\n", "\n")
            item = item.replace("\r", "\n")
            item = item.replace("\n", "\n" + '       > ')
            ret += u'{i:>3}. {item}\n'.format(i=str(i + 1)[-3:], item=item)
        return ret

    def show_all(self, panel):
        syntax = 'Packages/Text/Plain text.tmLanguage'
        panel.set_syntax_file(syntax)

        ret = ""
        ret += " CLIPBOARD HISTORY (%d)\n" % len(self)
        ret += "====================%s==\n" % ("=" * len(str(len(self))))
        for i, entry in enumerate(self):
            item = entry.item
            if i == self.__index:
                ret += '--> '
            else:
                ret += '    '
            item = item.replace("\t", '\\t')
            item = item.replace("\r\n", "\n")
            item = item.replace("\r", "\n")
            item = item.replace("\n", "\n" + '       > ')
            ret += u'{i:>3}. {item}\n'.format(i=str(i + 1)[-3:], item=item)
        return ret

    def show_registers(self, panel):
        ret = ""
        ret += " CLIPBOARD REGISTERS (%d)\n" % len(self.registers.items())
        ret += "=====================%s==\n" % ("=" * len(str(len(self.registers.items()))))
        for key, item in self.registers.items():
            item = item.replace("\t", '\\t')
            item = item.replace("\r\n", "\n")
            item = item.replace("\r", "\n")
            item = item.replace("\n", "\n" + ' > ')
            ret += u'{key:<1}: {item}\n'.format(key=key, item=item)
        return ret

    def register(self, register, *args):
        if args:
            if len(args) == 1:
                copy = args[0]
            else:
                copy = "\n".join(args)
            self.registers[register] = copy
            copy = copy.replace("\t", "\\t")
            copy = copy.replace("\n", "\\n")
            copy = copy.replace("\r", "\\r")
            sublime.status_message('Set Clipboard Register "{0}" to "{1}"'.format(register, copy))
        else:
            return self.registers[register]

    def append(self, item, syntax=None):
        """
        Appends to the history only if it isn't the current item.
        """
        if not self or self[self.__index].item != item:
            self.insert(0, HistoryEntry(item, syntax))
            self.__index = 0
            if len(self) > self.SIZE:
                del self[self.SIZE:]

    def current(self):
        if len(self) == 0:
            return None
        return self[self.__index]

    def at(self, idx):
        self.__index = (idx if idx < len(self) else 0)
        self.update_status()

    def get_next(self):
        if len(self) == 0:
            return None

        if self.__index == 0:
            return self.current()

        try:
            return self[self.__index - 1]
        except IndexError:
            return self[0]

    def goto_next(self):
        if self.__index > 0:
            self.__index -= 1
        self.update_status()

    def get_previous(self):
        if len(self) == 0:
            return None

        if self.__index == len(self) - 1:
            return self.current()

        try:
            return self[self.__index + 1]
        except IndexError:
            return self[self.__index]

    def goto_previous(self):
        if self.__index < len(self) - 1:
            self.__index += 1
        self.update_status()

    def update_status(self):
        copy = self.current().item
        copy = copy.replace("\t", "\\t")
        copy = copy.replace("\n", "\\n")
        copy = copy.replace("\r", "\\r")
        sublime.status_message(u'Set Clipboard to "{copy}"'.format(copy=copy))
        sublime.set_clipboard(self.current().item)


def clipboard_without_ibooks_quotes():
    clipboard = sublime.get_clipboard()
    quotes_re = re.compile(r'^“(.*?)”\s+Excerpt From:.*$', re.DOTALL)
    match = quotes_re.search(clipboard)
    if match:
        clipboard = match.group(1)
        sublime.set_clipboard(clipboard)
    return clipboard


def append_clipboard(syntax=None):
    '''
    Append the contents of the clipboard to the HISTORY global.
    '''
    HISTORY.append(clipboard_without_ibooks_quotes(), syntax)


def update_output_panel(window, show=None, make_visible=False):
    '''
    Update output panel with latest history if it is visible
    '''
    panel = window.get_output_panel('clipboard_manager')

    if make_visible:
        window.run_command('show_panel', {'panel': 'output.clipboard_manager'})

    if not panel.window():
        return

    global PANEL_SHOWING
    show = show or PANEL_SHOWING
    if show == 'registers':
        PANEL_SHOWING = 'registers'
        content = HISTORY.show_registers(panel)
    elif show == 'all':
        PANEL_SHOWING = 'all'
        content = HISTORY.show_all(panel)
    elif isinstance(show, HistoryEntry):
        content = HISTORY.show(show, panel)
    else:
        PANEL_SHOWING = 'current'
        content = HISTORY.show_current(panel)

    panel.run_command('clipboard_manager_dummy', {'content': content })


class ClipboardManagerPaste(sublime_plugin.TextCommand):
    def run(self, edit, indent=False):
        clipboard_without_ibooks_quotes()
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')


class ClipboardManagerCut(sublime_plugin.TextCommand):
    def run(self, edit):
        '''
        First run sublime's command to extract the selected text. This will set
        the cut/copy'd data on the clipboard which we can easily steal without
        recreating the cut/copy logic.
        '''
        self.view.run_command('cut')
        append_clipboard(self.view.settings().get('syntax'))
        update_output_panel(self.view.window())


class ClipboardManagerCopy(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command('copy')
        append_clipboard(self.view.settings().get('syntax'))
        update_output_panel(self.view.window())


class ClipboardManagerCopyToRegister(sublime_plugin.TextCommand):
    def run(self, edit, register=None, content=None):
        if register:
            self.view.run_command('copy')
            if content is None:
                content = sublime.get_clipboard()
            HISTORY.register(register, content)
            update_output_panel(self.view.window(), show='registers')
        else:
            self.view.run_command('copy')
            content = sublime.get_clipboard()
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
            lines = list(chars)
            def on_done(idx):
                self.view.window().run_command('clipboard_manager_copy_to_register', {'register': lines[idx], 'content': content})
            sublime.active_window().show_quick_panel(lines, on_done)


class ClipboardManagerPasteFromRegister(sublime_plugin.TextCommand):
    def run(self, edit, register):
        sublime.set_clipboard(HISTORY.register(register))
        self.view.run_command('paste')


class ClipboardManagerNext(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()
        panel = window.find_output_panel('clipboard_manager')
        panel_visible = panel and panel.window() is not None
        if PANEL_SHOWING == 'all' and panel_visible:
            show = 'all'
        else:
            show = 'current'
        HISTORY.goto_next()
        update_output_panel(window, show=show, make_visible=True)


class ClipboardManagerNextAndPaste(sublime_plugin.TextCommand):
    def run(self, edit, indent=False):
        HISTORY.goto_next()
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')
        update_output_panel(self.view.window(), show=HISTORY.get_next())


class ClipboardManagerPrevious(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()
        panel = window.find_output_panel('clipboard_manager')
        panel_visible = panel and panel.window() is not None
        if PANEL_SHOWING == 'all' and panel_visible:
            show = 'all'
        else:
            show = 'current'
        HISTORY.goto_previous()
        update_output_panel(window, show=show, make_visible=True)


class ClipboardManagerPreviousAndPaste(sublime_plugin.TextCommand):
    def run(self, edit, indent=False):
        HISTORY.goto_previous()
        if indent:
            self.view.run_command('paste_and_indent')
        else:
            self.view.run_command('paste')
        update_output_panel(self.view.window(), show=HISTORY.get_previous())


class ClipboardManagerShow(sublime_plugin.WindowCommand):
    def run(self):
        update_output_panel(self.window, show='all', make_visible=True)


class ClipboardManagerShowRegisters(sublime_plugin.WindowCommand):
    def run(self):
        update_output_panel(self.window, show='registers', make_visible=True)


class ClipboardManagerChooseAndPaste(sublime_plugin.TextCommand):
    def run(self, edit):
        def format(line):
            return line.replace('\n', '\\n')[:64]

        lines = []
        line_map = {}
        # filter out duplicates, keeping the first instance, and format
        for i, entry in enumerate(HISTORY):
            line = entry.item
            if i == HISTORY.index(entry):
                line_map[len(lines)] = i
                lines.append(format(line))

        def on_highlighted(idx):
            window = sublime.active_window()
            update_output_panel(window, show=HISTORY[idx], make_visible=True)
            return

        def on_done(idx):
            sublime.active_window().destroy_output_panel('clipboard_manager')
            if idx == -1:
                return
            idx = line_map[idx]
            HISTORY.at(idx)
            self.view.run_command('paste')

        if lines:
            on_highlighted(0)
            sublime.active_window().show_quick_panel(lines, on_done, 0, 0, on_highlighted)
        else:
            sublime.status_message('Nothing in history')


class ClipboardManagerEventListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        append_clipboard(view.settings().get('syntax'))


class ClipboardManagerDummy(sublime_plugin.TextCommand):
    def run(self, edit, content):
        region = sublime.Region(0, self.view.size())
        self.view.replace(edit, region, '')
        self.view.insert(edit, 0, content)
