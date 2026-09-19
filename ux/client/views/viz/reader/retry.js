// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'

// project
// shapes
import { Refresh as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// hooks
import { useStageReader } from './useStageReader'
// styles
import { retry as paintRetry } from './styles'


// control that asks for another attempt at first contact with the product of a reader
export const Retry = ({ name }) => {
    // get the handler that asks the server to survey the product again
    const { stage, isInFlight } = useStageReader(name)
    // build the handler that asks for another attempt
    const retry = evt => {
        // this control lives in the header of a tray, so keep the click from toggling it
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // if there is already an attempt under way
        if (isInFlight) {
            // there is nothing to ask for
            return
        }
        // otherwise, ask the server to survey the product again
        stage()
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: retry,
    }
    // the glyph draws its ring well inside its box, while the x of the control next to me runs
    // nearly corner to corner; size my box so that the two marks come out the same
    const size = 20
    // render
    return (
        <Badge size={size} state="enabled" behaviors={behaviors} style={paintRetry}
            aria-label={`retry first contact with '${name}'`}>
            <Icon />
        </Badge>
    )
}


// end of file
