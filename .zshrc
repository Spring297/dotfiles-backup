# Created by newuser for 5.9.1
autoload -Uz compinit
compinit

source /usr/share/zsh/site-functions/zsh-autosuggestions.zsh

source /usr/share/zsh/site-functions/zsh-syntax-highlighting.zsh

ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=8'

HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

setopt APPEND_HISTORY
setopt INC_APPEND_HISTORY
setopt SHARE_HISTORY

fastfetch
