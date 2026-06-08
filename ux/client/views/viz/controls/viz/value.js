// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// widgets
import { Slider, Spacer, SVG } from '~/widgets'
// colors
import { theme } from "~/palette"

// local
// hooks
import { useViewports } from '~/views/viz'
import { useResetValueController } from './useResetValueController'
import { useUpdateValueController } from './useUpdateValueController'
// components
import { Reset } from './reset'
import { Save } from './save'


// amplitude controller
export const ValueController = ({ channel, configuration }) => {
    // unpack the controller configuration
    const {
        slot, dirty, min, value, max,
    } = useFragment(valueVizGetControllerStateFragment, configuration)
    // get the active viewport
    const { activeViewport } = useViewports()
    // the slider is fully controlled, so local state drives the marker and lets it track the
    // pointer smoothly during a drag; it is reconciled with the server below
    const [marker, setMarker] = React.useState(value)
    // and my extent
    const [extent, setExtent] = React.useState({ min, max })
    // true while the user is dragging THIS control; server updates are throttled, so the store
    // trails the pointer and we must not let an in-flight echo of our own edit yank the marker back
    const interacting = React.useRef(false)

    // adopt server-side values that arrive while we are not dragging: a reset, or -- the point of
    // live sync -- a change another client made that the server pushed to us over the event stream
    React.useEffect(() => {
        // do not fight the pointer
        if (interacting.current) {
            return
        }
        // adopt the server value
        setMarker(value)
    }, [value])
    React.useEffect(() => {
        // do not fight the pointer
        if (interacting.current) {
            return
        }
        // adopt the server extent
        setExtent({ min, max })
    }, [min, max])
    // a drag ends when the pointer is released anywhere; clear the flag so the next server value
    // is reconciled. listen in the capture phase so a child that stops propagation cannot hide it
    React.useEffect(() => {
        const release = () => { interacting.current = false }
        window.addEventListener("pointerup", release, true)
        window.addEventListener("pointercancel", release, true)
        return () => {
            window.removeEventListener("pointerup", release, true)
            window.removeEventListener("pointercancel", release, true)
        }
    }, [])

    // build the state reset handler
    const { reset: defaults } = useResetValueController({ viewport: activeViewport, channel })
    // build the update handler
    const { update } = useUpdateValueController({ viewport: activeViewport, channel })

    // the handler that sets the controller state
    // this is built in the style of {react} state updates: the controller invokes this
    // and passes it as an argument a function that expects the current value and returns
    // the updated value
    const set = value => {
        // we are driving this control; suppress server reconciliation until the drag ends
        interacting.current = true
        // store it
        setMarker(value)
        // attempt to update the server side store
        update({ controller: slot, value, extent })
        // all done
        return
    }
    // the handler that resets the controller state
    const reset = () => {
        // reset the server side store
        defaults({ controller: slot, setMarker, setExtent })
        // all done
        return
    }
    // the handler that saves the controller state
    const save = () => {
        console.log(`viz.value: saving`)
    }

    // set up the tick marks
    const major = [min, (min + max) / 2, max]
    // controller configuration
    const opt = {
        value: marker,
        setValue: set,
        // name the single thumb after the server controller {slot}, so it is uniquely addressable
        label: slot,
        min, max, major,
        direction: "row", labels: "bottom", arrows: "top", markers: true,
        height: 100, width: 250,
    }

    // render
    return (
        <>
            <Header>
                <Title>{slot}</Title>
                <Spacer />
                <Save save={save} enabled={false} />
                <Reset reset={reset} enabled={dirty} />
            </Header>
            <Housing height={opt.height} width={opt.width} data-qed-control={slot}>
                <Controller enabled={true} {...opt} />
            </Housing>
        </>
    )
}


// styling
// the section header
const Header = styled.div`
    height: 1.5rem;
    margin: 0.5rem 0.0rem 0.25rem 1.0rem;
    // for my children
    display: flex;
    flex-direction: row;
    align-items: center;
`

// the title
const Title = styled.span`
    display: inline-block;
    font-family: rubik-light;
    width: 2.5rem;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    cursor: default;
    color: ${() => theme.page.bright};
`

// the controller housing
const Housing = styled(SVG)`
    margin: 0.25rem auto;
`

// the controller
const Controller = styled(Slider)`
`


// the fragment
const valueVizGetControllerStateFragment = graphql`
    fragment valueVizGetControllerStateFragment on Controller {
        slot
        dirty
        min
        max
        ... on ValueController {
            value
        }
    }
`


// end of file
