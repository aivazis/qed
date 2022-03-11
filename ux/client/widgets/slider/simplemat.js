// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// hooks
import { useEvent } from '~/hooks'

// locals
// hooks
import { useClient } from './useClient'
import { useConfig } from './useConfig'
import { useMine } from './useMine'
import { useNames } from './useNames'
import { useSliding } from './useSliding'
import { useStopSliding } from './useStopSliding'
import { useUser } from './useUser'


// a workaround for capturing events in the controller client area
// needed only because {pointer-events: bounding-box} doesn't work yet
export const Simplemat = ({ setValue, children, ...rest }) => {
    // make a ref to attach to the placemat so we can measure its extent
    const placemat = React.useRef(null)
    // get the {sliding} indicator
    const sliding = useSliding()
    // make a handler that clears the {sliding} flag
    const stopSliding = useStopSliding()
    // get names
    const { mainMovementName, mainOffsetName } = useNames()

    // unpack my state
    const { enabled } = useConfig()
    // unpack the geometry
    const { emplace } = useClient()
    const { bboxMine } = useMine()
    const { mouseToUser } = useUser()

    // handler that converts mouse coordinates to user space and invokes {setValue} to inform
    // the client
    const pick = evt => {
        // get the position of the mouse relative to the main edge
        const pixels = evt[mainOffsetName]
        // transform the mouse coordinates into a user value
        const value = mouseToUser(pixels)
        // notify the client
        setValue(value)
        // and done
        return
    }

    // handler that checks whether the marker is being dragged before converting
    // mouse coordinates to user space
    const drag = evt => {
        // if the indicator is not being dragged
        if (sliding === null) {
            // do nothing
            return
        }
        // get the mouse movement along my main axis
        const dMain = evt[mainMovementName]
        // if there is no change
        if (Math.trunc(dMain) === 0) {
            // bail
            return
        }
        // otherwise, {pick} a value
        pick(evt)
        // all done
        return
    }

    // install the mouse event listeners
    // when the use clicks anywhere inside the {placemat}
    useEvent({
        name: "click", listener: enabled ? pick : null, client: placemat,
        triggers: [setValue]
    })

    // the mouse down is attached to the indicator
    // when the mouse drags
    useEvent({
        name: "mousemove", listener: enabled ? drag : null, client: placemat,
        triggers: [sliding, setValue]
    })

    // dragging ends when the user lets go of the mouse button
    useEvent({
        name: "mouseup", listener: enabled ? stopSliding : null, client: placemat,
        triggers: []
    })
    // or when the mouse leaves the placemat
    useEvent({
        name: "mouseleave", listener: enabled ? stopSliding : null, client: placemat,
        triggers: []
    })

    // render
    // N.B.: attach the {ref} to the group and not the {rect} that fills the bounding box;
    // otherwise, the {mouseleave} will trigger when the mouse enters any of the other
    // {children} of the slider
    return (
        <g ref={placemat} transform={emplace} >
            <Rect {...bboxMine} {...rest} />
            {children}
        </g>
    )
}


// styling
const Rect = styled.rect`
    fill: hsl(0deg, 0%, 7%);

    &:active {
        stroke: hsl(0deg, 0%, 20%);
        stroke-width: 1;
        vector-effect: non-scaling-stroke;
    }
`

// end of file
