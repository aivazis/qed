// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useReader } from './useReader'
// styles
import styles from './styles'


// display a single stack member as a participation toggle
export const Member = ({ index, active, locked, toggle }) => {
    // get my reader
    const reader = useReader()
    // park hover styling here, the way the coordinate selectors do
    const [polish, setPolish] = React.useState(false)

    // active members render as selected, the rest as enabled and available to add
    const state = active ? "selected" : "enabled"

    // make a click handler
    const onClick = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // a locked member is the last one standing; toggling it would empty the stack
        if (!locked) {
            // otherwise, flip my participation
            toggle(index)
        }
        // drop any hover polish
        setPolish(false)
        // all done
        return
    }
    // a locked member never changes, so it gets no hover affordance
    const behaviors = locked ? { onClick } : {
        onClick,
        onMouseEnter: () => setPolish(true),
        onMouseLeave: () => setPolish(false),
    }

    // mix my paint
    const paint = styles.coordinate(state, polish)
    // pick my tip
    const tip = active
        ? (locked
            ? `member ${index} is the only active member of '${reader.name}'`
            : `drop member ${index} from the aggregate of '${reader.name}'`)
        : `add member ${index} to the aggregate of '${reader.name}'`

    // and render; the client owns this control's identity -- the member {index} lives in {data-*},
    // while participation is state and lives in ARIA, never mirrored into {data-*}
    return (
        <div title={tip} style={paint}
            role="checkbox"
            aria-checked={active}
            aria-disabled={locked}
            data-qed-stack-member={index}
            {...behaviors}>
            {index}
        </div>
    )
}


/* end of file */
