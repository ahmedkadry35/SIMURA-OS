# SIMURA OS — default zsh config copied to every new user via /etc/skel.
# Designed for an immediately useful, modern shell experience.

# History
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY HIST_IGNORE_DUPS HIST_IGNORE_SPACE

# Completion
autoload -Uz compinit
compinit -d ~/.cache/zcompdump
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' '+l:|=* r:|=*'

# Prompt: starship if available, otherwise a tasteful fallback.
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init zsh)"
else
    PROMPT='%F{cyan}%n@%m%f:%F{blue}%~%f %# '
fi

# Plugins
[ -f /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ] && \
    source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
[ -f /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ] && \
    source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# Aliases
alias ls='eza --group-directories-first --icons'
alias ll='eza -l --group-directories-first --icons --git'
alias la='eza -la --group-directories-first --icons --git'
alias cat='bat --paging=never --style=plain'
alias grep='grep --color=auto'
alias ip='ip --color=auto'
alias diff='diff --color=auto'
alias ai='simura-assistant'

# Path
typeset -U path
path=(~/.local/bin /usr/local/bin $path)
export PATH

# Fancy welcome banner shown on interactive shells.
if [[ -o interactive ]] && [[ -z "$SIMURA_BANNER_SHOWN" ]]; then
    export SIMURA_BANNER_SHOWN=1
    if command -v fastfetch >/dev/null 2>&1; then
        fastfetch 2>/dev/null
    elif command -v neofetch >/dev/null 2>&1; then
        neofetch 2>/dev/null
    fi
fi
