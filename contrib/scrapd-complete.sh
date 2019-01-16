_scrapd_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _SCRAPD_COMPLETE=complete $1 ) )
    return 0
}

complete -F _scrapd_completion -o default scrapd;
