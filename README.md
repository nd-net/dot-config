# dot-config

The contents of ~/.config I am using to install a new (Apple Silicon) Mac.
The environment is set up so that settings are stored according to the XDG
standard.

## Updating configurations

Some configurations are only used for installing, and must be updated manually.

* `homebrew/Brewfile`: `brew bundle dump --describe --force --file ~/.config/brew/Brewfile`
* `python/default-python-packages`: `pip list`, then check for packages you want to include
* `ruby/Gemfile`: `bundle list`, then check for gems you want to include


## Symlinking configurations

Tools that do not read their configuration from `~/.config` get an executable
`symlink` script in their subdirectory, which links the configuration to where
the tool expects it with `../xdg/link SOURCE TARGET`. `xdg/link` never replaces
an existing file, and does nothing if the link is already in place.

Run `xdg/symlink` to run all of these scripts, or `xdg/symlink NAME...` for
selected subdirectories only. It can be run again at any time.
