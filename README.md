# dot-config

The contents of ~/.config I am using to install a new (Apple Silicon) Mac.
The environment is set up so that settings are stored according to the XDG
standard.

## Updating configurations

Some configurations are only used for installing, and must be updated manually.

* `brew/Brewfile`: `brew bundle dump --describe --force --file ~/.config/brew/Brewfile`
* `python/default-python-packages`: `pip list`, then check for packages you want to include
* `ruby/Gemfile`: `bundle list`, then check for gems you want to include

# Updating installed files

If you want to update xonsh to the latest version, the update it using `pipupgrade`, then use `~/.local/bin/link-xonsh`.