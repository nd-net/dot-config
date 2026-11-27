# Keep history in the XDG state directory (not exported: bash must not inherit it)
HISTFILE="$HOME/.local/state/zsh/history"
mkdir -p "${HISTFILE:h}"
