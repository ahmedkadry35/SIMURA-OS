# SIMURA OS — root user zsh config, mirrors /etc/skel/.zshrc.
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY HIST_IGNORE_DUPS HIST_IGNORE_SPACE

autoload -Uz compinit
compinit -d ~/.cache/zcompdump
zstyle ':completion:*' menu select

if command -v starship >/dev/null 2>&1; then
    eval "$(starship init zsh)"
else
    PROMPT='%F{red}%n@%m%f:%F{blue}%~%f # '
fi

[ -f /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ] && \
    source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
[ -f /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ] && \
    source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

alias ls='eza --group-directories-first --icons'
alias ll='eza -l --group-directories-first --icons --git'
alias la='eza -la --group-directories-first --icons --git'

if [[ -o interactive ]] && [[ -z "$SIMURA_BANNER_SHOWN" ]]; then
    export SIMURA_BANNER_SHOWN=1
    fastfetch 2>/dev/null || neofetch 2>/dev/null || true
fi
