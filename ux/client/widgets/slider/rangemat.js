// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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
export const Rangemat = ({ setValue, children, ...rest }) => {
    // make a ref to attach to the placemat so we can measure its extent
    const placemat = React.useRef(null)
    // get the {sliding} indicator
    const { cursor, sliding } = useSliding()
    // make a handler that clears the {sliding} flag
    const stopSliding = useStopSliding()
    // get names
    const { mainCoordinateName, mainNearEdgeName, mainPositionName } = useNames()
    // get my state
    const { enabled, min, max } = useConfig()
    // unpack the geometry
    const { emplace } = useClient()
    const { bboxMine } = useMine()
    const { mouseDeltaToUser, mouseToUser } = useUser()

    // handler that converts mouse coordinates to user space and invokes {setValue} to inform
    // the client
    const pick = evt => {
        // get the current cursor position
        const mouseMain = evt[mainPositionName]
        // notify the client
        setValue(old => {
            // make a copy
            const range = [...old]
            // if both are sliding
            if (sliding < 0) {
                // get the position of the mouse relative to the main edge
                const dCursor = mouseMain - cursor.current[mainCoordinateName]
                // transform the mouse coordinates into a user value
                const delta = mouseDeltaToUser(dCursor)
                // adjust both entries
                range[0] += delta
                range[1] += delta
            } else {
                // measure the {target} box
                const box = evt.currentTarget.getBoundingClientRect()
                // get the position of the mouse relative to the main edge
                const pixels = mouseMain - box[mainNearEdgeName]
                // compute the new value
                const newValue = mouseToUser(pixels)
                // use the selector id to modify to correct entry
                range[sliding] = newValue
            }

            // clip
            range[0] = Math.max(range[0], min)
            range[1] = Math.max(Math.min(range[1], max), range[0])
            // and return the new range
            return range
        })
        // update the cursor location
        cursor.current = { ...cursor.current, [mainCoordinateName]: mouseMain }
        // and done
        return
    }

    // handler that checks whether the marker is being dragged before converting
    // mouse coordinates to user space
    const drag = evt => {
        // if no indicator is being dragged
        if (sliding === null) {
            // do nothing
            return
        }
        // otherwise, {pick} a value
        pick(evt)
        // all done
        return
    }

    // install the mouse event listeners
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
