import sublime, sublime_plugin
import math, time

# two globals store the complete clipboard history and position so that it is shared between all the various actions
_clipboardHistory = ['']
_clipboardIndex = 0

class ClipboardHistoryBase(sublime_plugin.TextCommand):
  # gets/sets the sublime clipboard
  def clipboard(self, content=None):
    if content == None:
      return sublime.get_clipboard()
    else:
      sublime.set_clipboard(content)

  # gets the clipboard history clipboard
  def top(self):
    return _clipboardHistory[_clipboardIndex]

  def next(self):
    global _clipboardIndex
    if _clipboardIndex < len(_clipboardHistory)-1:
      _clipboardIndex += 1
    self.clipboard(self.top())

  def previous(self):
    global _clipboardIndex
    if _clipboardIndex > 0:
      _clipboardIndex -= 1
    self.clipboard(self.top())

  def appendClipboard(self):
    global _clipboardIndex

    # append the contents of the clipboard to the history if it is unique
    if not self.onTop():
      _clipboardHistory.append(sublime.get_clipboard())
      _clipboardIndex = len(_clipboardHistory)-1

  def onTop(self):
    return self.clipboard() == self.top()

  def run_command(self, command):
    self.view.run_command(command)
    # I know this is hideous, and I sincerely apologize, but it works
    # I was getting non deterministic behavior in which the clipboard seemingly randomly returned stale data.
    time.sleep(0.1)


class ClipboardHistoryPaste(ClipboardHistoryBase):
  def run(self, edit):
    # If the user pastes something that was copied in a different program, it will not be in sublime's buffer, so we attempt to append every time
    self.appendClipboard()
    self.run_command('paste')

class ClipboardHistoryPasteAndIndent(ClipboardHistoryBase):
  def run(self, edit):
    self.appendClipboard()
    self.run_command('paste_and_indent')

class ClipboardHistoryCut(ClipboardHistoryBase):
  def run(self, edit):
    # First run sublime's command to extract the selected text.
    # This will set the cut/copy'd data on the clipboard which we can easily steal without recreating the cut/copy logic.
    self.run_command('cut')
    self.appendClipboard()

class ClipboardHistoryCopy(ClipboardHistoryBase):
  def run(self, edit):
    self.run_command('copy')
    self.appendClipboard()

class ClipboardHistoryNext(ClipboardHistoryBase):
  def run(self, edit):
    self.next()

class ClipboardHistoryPrevious(ClipboardHistoryBase):
  def run(self, edit):
    self.previous()

class ClipboardHistoryPasteAndPrevious(ClipboardHistoryBase):
  def run(self, edit):
    self.previous()
    self.run_command('paste')

class ClipboardHistoryVisualize(ClipboardHistoryBase):
  def run(self, edit):
    def escapeLine(line):
      return ' ' + line.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')

    # All newlines need to be escaped so they can each fit on one line in the editor
    # This means we also need to escape backslashes so that they can be properly unescaped later.
    lines = map(escapeLine, _clipboardHistory)
    lines[_clipboardIndex] = lines[_clipboardIndex].replace(' ', '*', 1)

    view = sublime.active_window().new_file()
    view.set_scratch(True)
    view.set_name('Clipboard History')
    edit = view.begin_edit()
    view.insert(edit, 0, '\n'.join(lines))
    view.end_edit(edit)

class ClipboardHistorySave(sublime_plugin.EventListener):
  def on_close(self, view):
    if view.name() != 'Clipboard History':
      return

    global _clipboardHistory, _clipboardIndex
    _clipboardHistory = []
    _clipboardIndex = 0

    lineRegions = view.lines(sublime.Region(0, view.size()))
    if len(lineRegions) == 0:
      _clipboardHistory = ['']
      return

    for c in range(0, len(lineRegions)):
      line = view.substr(lineRegions[c])

      if line[0] == '*':
        _clipboardIndex = c

      content = line[1:len(line)]
      content = content.replace('\\n', '\n').replace('\\r', '\r').replace('\\\\', '\\')
      _clipboardHistory.append(content)

    sublime.set_clipboard(_clipboardHistory[_clipboardIndex])
