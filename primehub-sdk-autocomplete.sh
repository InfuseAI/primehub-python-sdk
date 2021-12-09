#!/usr/bin/env bash
autoload -U bashcompinit

_primehub() {
  COMPREPLY=($(cur="${COMP_WORDS[COMP_CWORD]}" prev="${COMP_WORDS[COMP_CWORD-1]}" auto-primehub))
}

complete -F _primehub primehub
