// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// widgets
import { Tray } from '~/widgets'

// local
// components
import { RangeController } from './range'
import { ValueController } from './value'


//  the tray with the visualization pipeline controls
export const Viz = ({ view }) => {
    // unpack the view
    const { dataset, channel } = useFragment(vizControlsGetViewFragment, view)
    // and render
    return (
        <Tray title="viz" state="enabled" initially={true} scale={0.5}>
            {channel.controllers.map(configuration => {
                // unpack the controller configuration
                const { slot, __typename: typename } = configuration
                // look up the controller
                const Controller = registry[typename]
                // and render
                return (
                    <Controller key={slot}
                        dataset={dataset.name} channel={channel.tag}
                        configuration={configuration} />
                )
            })}
        </Tray>
    )
}


// the controller type registry
const registry = {
    RangeController,
    ValueController,
}


// the fragment
const vizControlsGetViewFragment = graphql`
    fragment vizControlsGetViewFragment on View {
        dataset {
            name
        }
        channel {
            tag
            controllers {
                __typename
                ... on Node {
                   id
                }
                ... on RangeController {
                    slot
                    ...range_range
                }
                ... on ValueController {
                    slot
                    ...value_value
                }
            }
        }
    }
`


// end of file
