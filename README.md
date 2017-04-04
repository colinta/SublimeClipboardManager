Clipboard Manager
=================

A version of the Sublime Text plugin at <http://www.sublimetext.com/forum/viewtopic.php?f=5&t=2260&start=0> that makes for TextMate-like clipboard history.

Originally written by AJ Palkovic ([ajpalkovic](https://github.com/ajpalkovic/SublimePlugins)), modified by Martin Aspeli ([optilude](https://gist.github.com/1132507)), and further (heavily) modified and packaged for `Package Control` by Colin T.A. Gray ([colinta](https://github.com/colinta/SublimeClipboardManager))

My (colinta) version of this plugin *does not use* `clipboard_history` as the prefix.  See the full command-list below.

Installation
------------

**Most importantly:** Clipboard Manager must be registered to receive the copy and cut commands, so be sure
to assign `clipboard_manager_copy` to `ctrl/super+c` and `clipboard_manager_cup` to `ctrl/super+x`. These
commands delegate to the sublime text built in commands, but also add the copied text to its internal history.

1. Using Package Control, install "Clipboard Manager"

Or:

1. Open the Sublime Text Packages folder
    - OS X: ~/Library/Application Support/Sublime Text 3/Packages/
    - Windows: %APPDATA%/Sublime Text 3/Packages/
    - Linux: ~/.Sublime Text 3/Packages/ or ~/.config/sublime-text-3/Packages

2. clone this repo
3. Install keymaps for the commands (see Example.sublime-keymap for my preferred keys)

Open `Preferences > Key Bindings` and copy the key bindings from `Example.sublime-keymap` that you want to use.  First you need to override the cut/copy/paste commands, so that the pasteboard entries can be stored in history:

``` json
    { "keys": ["super+x"], "command": "clipboard_manager_cut" },
    { "keys": ["super+c"], "command": "clipboard_manager_copy" },
    { "keys": ["super+v"], "command": "clipboard_manager_paste", "args": { "indent": true } },
```

Next you'll want to bind `next_and_paste` and `previous_and_paste`, these move forward and backward through history and paste the next/previous entry:

``` json
    { "keys": ["super+alt+v"], "command": "clipboard_manager_next_and_paste" },
    { "keys": ["super+shift+v"], "command": "clipboard_manager_previous_and_paste" },
```

The "choose and paste" command is super useful, and it uses the fuzzy finder so you can search your history:

```
    { "keys": ["super+alt+ctrl+v"], "command": "clipboard_manager_choose_and_paste" },
```

More commands are outlined below.


Commands
--------

**The basics**

`clipboard_manager_cut`: Self Explanatory

`clipboard_manager_copy`: Self Explanatory

`clipboard_manager_paste`: Self Explanatory.

*Options*: indent (default: False): Determines whether to use the `paste` or `paste_and_indent` built-in command.

- - - - - -

**Navigating clipboard history**

`clipboard_manager_next_and_paste` (`super+alt+v`)

Goes to the next entry in the history and pastes it.
*Options*: indent (default: `False`)

`clipboard_manager_previous_and_paste` (`super+shift+v`)

Goes to the previous entry in the history and pastes it.
*Options*: indent (default: `False`)

`clipboard_manager_next` (`super+pageup` aka `super+fn+up`)

Goes to the next entry in the history, but doesn't paste.  (the content will appear as a status message)

`clipboard_manager_previous` (`super+pagedown` aka `super+fn+down`)

Goes to the previous entry in the history, but doesn't paste.  (the content will appear as a status message)

`clipboard_manager_choose_and_paste` (`super+ctrl+alt+v`)

Shows the clipboard history in a "quick panel" so you can pick an entry from the history.

`clipboard_manager_show` (`super+ctrl+shift+v, /`)

Shows the clipboard history in an "output panel", and points to the current clipboard item.  This was mostly useful for development, but you might find it beneficial as well.

- - - - - -

**Registers**

Registers do not add/remove from the clipboard history, they are a place to store text that won't be affected by clipboard history.

`clipboard_manager_copy_to_register` (there are a ton, e.g. `super+ctrl+shift+c, 1`, `super+ctrl+shift+c, a`)

Puts the selection into a `register`.  The example keymap includes a register binding for every number and letter.

`clipboard_manager_paste_from_register` (`super+ctrl+shift+v, 1`, `super+ctrl+shift+v, a`)

Pastes the contents of a `register`.  Again, there are lots of example key bindings.

`clipboard_manager_show_registers` (`super+ctrl+shift+v, ?`)

Shows the clipboard registers in an "output panel", similar to `clipboard_manager_show`.

- - - - - -

**Helpful Tips**

There are two ways to find out what you've got hanging out in your clipboard history, you should use both.  The `clipboard_manager_choose_and_paste` command is your goto.  It uses the fuzzy finder input panel, so you can quickly find and paste the entry you want.

The other useful trick is to use `clipboard_manager_show` to show an output panel at the bottom of the screen.  As you scroll through history using `clipboard_manager_next` and `clipboard_manager_previous`, it will update that panel, with an arrow pointing to the current entry.  Then you can `clipboard_manager_next_and_paste`, and it will get updated then, too.  Keeps you sane if you're doing something crazy.

If you've got a repetive task to do, with lots of copy/pastes, use registers. They do not get affected by usual copy/pasting, so you can rest assured that your work flow will not get affected.  The keyboard shortcuts are unfortunately quite verbose (`super+ctrl+shift+c, letter/digit`), but look at Example.sublime-keymap and you'll see that it is easy to assign a quicker shortcut for registers you like to use.  Registers do not have to be one letter, any string can be used as the key.
