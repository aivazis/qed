// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// widgets
import { Range, Spacer, SVG } from '~/widgets'
// colors
import { theme } from "~/palette"

// local
// hooks
import { useViewports } from '~/views/viz'
import { useResetRangeController } from './useResetRangeController'
import { useUpdateRangeController } from './useUpdateRangeController'
// components
import { Reset } from './reset'
import { Save } from './save'


// amplitude controller
export const RangeController = ({ channel, configuration }) => {
    // unpack the controller configuration
    const {
        slot, dirty, min, low, high, max,
    } = useFragment(rangeVizGetControllerStateFragment, configuration)
    // get the active viewport
    const { activeViewport } = useViewports()
    // initialize my range
    const [range, setRange] = React.useState({ low, high })
    // and my extent
    const [extent, setExtent] = React.useState({ min, max })

    // build the state reset handler
    const { reset: defaults } = useResetRangeController({ viewport: activeViewport, channel })
    // build the update handler
    const { update } = useUpdateRangeController({ viewport: activeViewport, channel })

    // the handler that sets the controller state
    // this is built in the style of {react} state updates: the controller invokes this
    // and passes it as an argument a function that expects the current range and returns
    // the updated value
    const set = callback => {
        // get the updated values
        const [newLow, newHigh] = callback([range.low, range.high])
        // make a new range
        const newRange = { low: newLow, high: newHigh }
        // store it
        setRange(newRange)
        // attempt to update the server side store
        update({ controller: slot, range: newRange, extent })
        // all done
        return
    }
    // the handler that resets the controller state
    const reset = () => {
        // reset the server side store
        defaults({ controller: slot, setRange, setExtent })
        // all done
        return
    }
    // the handler that saves the controller state
    const save = () => {
        console.log(`viz.range: saving`)
    }

    // set up the tick marks
    const major = [min, (max + min) / 2, max]
    // controller configuration
    const opt = {
        value: [range.low, range.high],
        setValue: set,
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
            <Housing height={opt.height} width={opt.width}>
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
    display: inline - block;
    font-family: rubik-light;
    width: 2.5rem;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    cursor: default ;
    color: ${() => theme.page.bright};
`

// the controller housing
const Housing = styled(SVG)`
    margin: 0.25rem auto;
`

// the controller
const Controller = styled(Range)`
`


// the fragment
const rangeVizGetControllerStateFragment = graphql`
    fragment rangeVizGetControllerStateFragment on RangeController {
        slot
        dirty
        min
        low
        high
        max
    }
 `


// end of file
