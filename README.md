Clipboard Manager plugin for Sublime Text 2
===========================================

A version of the Sublime Text 2 plugin at <http://www.sublimetext.com/forum/viewtopic.php?f=5&t=2260&start=0> that makes for TextMate-like clipboard history.

Originally written by AJ Palkovic ([ajpalkovic](https://github.com/ajpalkovic/SublimePlugins)), modified by Martin Aspeli ([optilude](https://gist.github.com/1132507)), and further modified and packaged for `Package Control` by Colin Thomas-Arnold ([colinta](https://github.com/colinta/SublimeClipboardManager))

Installation
------------

1. Using Package Control, install "Clipboard Manager"

Or:

1. Open the Sublime Text 2 Packages folder

    - OS X: ~/Library/Application Support/Sublime Text 2/Packages/
    - Windows: %APPDATA%/Sublime Text 2/Packages/
    - Linux: ~/.Sublime Text 2/Packages/

2. clone this repo

Commands
--------

`clipboard_manager_cut`: Self Explanatory

`clipboard_manager_copy`: Self Explanatory

`clipboard_manager_paste`: Self Explanatory. *Options*: indent (default: False): Determines whether to use `paste` or `paste_and_indent` built-in command.

`clipboard_manager_next_and_paste`: Goes to the next entry in the history and pastes it. *Options*: indent (default: False)

`clipboard_manager_previous_and_paste`:Goes to the previous entry in the history and pastes it. *Options*: indent (default: False)

`clipboard_manager_next`: Goes to the next entry in the history, but doesn't paste.  (the content will appear as a status message)

`clipboard_manager_previous`: Goes to the previous entry in the history, but doesn't paste.  (the content will appear as a status message)

`clipboard_manager_choose_and_paste`: Shows the clipboard history in a "quick panel".
