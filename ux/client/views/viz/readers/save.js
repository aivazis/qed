// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// project
// shapes
import { Download as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// styles
import styles from './styles'


// save the state of a controller
export const Save = ({ enabled = true }) => {
    // saving te state invokes a mutation
    const [request, pending] = useMutation(persistReadersMutation)

    // make a handler that invokes the mutation
    const persist = () => {
        // if it's already in progress
        if (pending) {
            // bail
            return
        }
        // otherwise, post the request
        request({
            // input
            variables: {
                // the payload
                dummy: null
            }
        })
        // all done
        return
    }

    // build the handler
    const click = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // save the state
        persist()
        // all done
        return
    }
    // assemble the controllers to hand my {badge}
    const behaviors = {
        onClick: click,
    }

    // deduce my state
    const state = enabled ? "enabled" : "disabled"

    // mix my paint
    const paint = styles.save
    // and render
    return (
        <Badge size={12} state={state} behaviors={behaviors} style={paint}
            title="save the current configuration"
        >
            <Icon />
        </Badge>
    )
}

// the mutation that persists the current readers
const persistReadersMutation = graphql`
    mutation saveCurrentReaderMutation($dummy: ID) {
        viewPersist(dummy: $dummy) {
            id
        }
    }
`


// end of file