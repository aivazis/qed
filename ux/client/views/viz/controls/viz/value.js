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
import { Slider, Spacer, SVG } from '~/widgets'
// colors
import { theme } from "~/palette"

// local
// hooks
import { useSetVizSession } from '../../../main/useSetVizSession'
// components
import { Reset } from './reset'
import { Save } from './save'


// amplitude controller
export const ValueController = props => {
    // ask the store for the current configuration
    const configuration = useFragment(graphql`
        fragment value_value on ValueController {
            id
            slot
            min
            max
            value
        }
    `, props.configuration)
    // unpack
    const { slot, min, max, value } = configuration
    // initialize my local value
    const [marker, setMarker] = React.useState(value)
    // and my extent
    const [extent, setExtent] = React.useState([min, max])
    // my state
    const [modified, setModified] = React.useState(false)
    // make a handler that can update the session id of a view
    const setSession = useSetVizSession()
    // build the value mutator
    const [updateValue, updateIsInFlight] = useMutation(updateValueMutation)
    // and the state reset
    const [resetValue, resetIsInFlight] = useMutation(resetValueMutation)
    // set up the tick marks
    const major = [min, (min + max) / 2, max]

    // leave this here, for now
    // make some room for the performance stats
    const [served, setServed] = React.useState(0)
    const [dropped, setDropped] = React.useState(0)
    // show me
    console.log(`value: served: ${served}, dropped: ${dropped}, p: ${served / (served + dropped)}`)
    // make a handler that updates them
    const monitor = flag => {
        // pick an updater
        const update = flag ? setDropped : setServed
        // and invoke it
        update(old => old + 1)
        // all done
        return
    }

    // build the state reset
    const reset = () => {
        // if there is a pending reset
        if (resetIsInFlight) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        resetValue({
            // input
            variables: {
                controller: {
                    dataset: props.dataset,
                    channel: props.channel,
                    slot,
                }
            },
            // when done
            onCompleted: data => {
                // unpack
                const { min, value, max, session } = data.resetValueController.controller
                // set my value
                setMarker(value)
                // and my limits
                setExtent([min, max])
                // indicate i'm at my defaults
                setModified(false)
                // and set the session in the active view
                setSession(session)
                // all done
                return
            }
        })
    }

    // build the value updater to hand to the controller
    // this is built in the style of {react} state updates: the controller invokes this
    // and passes it a function that expects the current value and returns the updated value
    const setValue = newValue => {
        // update my state
        setMarker(newValue)
        // update the delivery stats
        monitor(updateIsInFlight)
        // if there is a pending mutation
        if (updateIsInFlight) {
            // skip the update
            return
        }
        // otherwise, send the new value to the server
        updateValue({
            // input
            variables: {
                info: {
                    dataset: props.dataset,
                    channel: props.channel,
                    slot,
                    value: newValue,
                }
            },
            // when done
            onCompleted: data => {
                // indicate i'm at modified away from my defaults
                setModified(true)
                // get the session
                const session = data.updateValueController.controller.session
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
        value: marker
        , setValue,
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
                <Save save={reset} enabled={modified} />
                <Reset reset={reset} enabled={modified} />
            </Header>
            <Housing height={opt.height} width={opt.width}>
                <Controller enabled={true} {...opt} />
            </Housing>
        </>
    )
}

// the mutation that reset the controller state
const resetValueMutation = graphql`
mutation valueResetControllerMutation($controller: ValueControllerInput!) {
    resetValueController(controller: $controller) {
        controller {
            id
            # get my new session id
            session
            # refresh my parameters
            min
            max
            value
        }
    }
}`

// the mutation that updates the controller state
const updateValueMutation = graphql`
mutation valueUpdateControllerMutation($info: ValueControllerValueInput!) {
    updateValueController(value: $info) {
        controller {
            id
            # get my new session id
            session
            # refresh my parameters
            min
            max
            value
        }
    }
}`


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


// end of file
