// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment, useMutation } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// widgets
import { Range, SVG } from '~/widgets'

// local
// hooks
import { useSetVizSession } from '../../viz/useSetVizSession'


// amplitude controller
export const RangeController = props => {
    // ask the store for the current configuration
    const configuration = useFragment(graphql`
        fragment range_range on RangeController {
            id
            slot
            min
            max
            low
            high
        }
    `, props.configuration)
    // unpack
    const { slot, min, max, low, high } = configuration
    // initialize my local values of the range
    const [range, setRange] = React.useState([low, high])
    // make a handler that can update the session id of a view
    const setSession = useSetVizSession()
    // build the range mutator
    const [updateRange, isInFlight] = useMutation(updateRangeMutation)
    // set up the tick marks
    const major = [min, (max + min) / 2, max]

    // leave this here, for now
    // make some room for the performance stats
    const [served, setServed] = React.useState(0)
    const [dropped, setDropped] = React.useState(0)
    // show me
    console.log(`range: served: ${served}, dropped: ${dropped}, p: ${served / (served + dropped)}`)
    // make a handler that updates them
    const monitor = flag => {
        // pick an updater
        const update = flag ? setDropped : setServed
        // and invoke it
        update(old => old + 1)
        // all done
        return
    }

    // build the value updater to hand to the controller
    // this is built in the style of {react} state updates: the controller invokes this
    // and passes it as an argument a function that expects the current range and return
    // the updated value
    const setValue = f => {
        // invoke the controller's updater to get the new range
        const [newLow, newHigh] = f(range)
        // update my state
        setRange([newLow, newHigh])
        // update the stats
        monitor(isInFlight)
        // if there is a pending mutation
        if (isInFlight) {
            // skip the update
            return
        }
        // send it to the server
        updateRange({
            // input
            variables: {
                info: {
                    dataset: props.dataset,
                    channel: props.channel,
                    slot,
                    low: newLow,
                    high: newHigh,
                }
            },
            // when done
            onCompleted: data => {
                // get the session
                const session = data.updateRangeController.controller.session
                // and set it in the active view
                setSession(session)
                // all done
                return
            }
        })

        // all done
        return
    }
    // controller configuration
    const opt = {
        value: range,
        setValue,
        min, max, major,
        direction: "row", labels: "bottom", arrows: "top", markers: true,
        height: 100, width: 250,
    }

    // render
    return (
        <>
            <Header>
                <Title>{slot}</Title>
            </Header>
            <Housing height={opt.height} width={opt.width}>
                <Controller enabled={true} {...opt} />
            </Housing>
        </>
    )
}


// the range mutation
const updateRangeMutation = graphql`
mutation rangeMutation($info: RangeControllerInput!) {
    updateRangeController(range: $info) {
        controller {
            id
            # get my new session id
            session
            # refresh my parameters
            min
            max
            low
            high
        }
    }
}`


// styling
// the section header
const Header = styled.div`
    margin: 0.5rem 1.0rem 0.25rem 1.0rem;
`

// the title
const Title = styled.span`
    display: inline-block;
    font-family: rubik-light;
    width: 2.5rem;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    cursor: default;
    color: hsl(0deg, 0%, 75%);
`

// the controller housing
const Housing = styled(SVG)`
    margin: 0.25rem auto;
    /* border: 1px solid hsl(0deg, 0%, 10%); */
`

// the controller
const Controller = styled(Range)`
`


// end of file
