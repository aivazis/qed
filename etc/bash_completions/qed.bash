# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved

# bash completion script for qed
function _qed() {
    # get the partial command line
    local line=${COMP_LINE}
    local word=${COMP_WORDS[COMP_CWORD]}
    # ask qed to provide guesses
    COMPREPLY=($(qed complete --word="${word}" --line="${line}"))
}

# register the hook
complete -F _qed qed

# end of file
