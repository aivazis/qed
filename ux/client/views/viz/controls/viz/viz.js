// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Tray } from '~/widgets'

// local
// hooks
import { useGetVizPipeline } from './useGetVizPipeline'
// components
import { RangeController } from './range'
import { ValueController } from './value'


//  the tray with the visualization pipeline controls
export const Viz = () => {
    // get the pipeline
    const { dataset, channel, controllers } = useGetVizPipeline()
    // and render
    return (
        <Tray title="viz" state="enabled" initially={true} scale={0.5}>
            {controllers.map(configuration => {
                // unpack the controller configuration
                const { slot, __typename: typename } = configuration
                // look up the controller
                const Controller = registry[typename]
                // and render
                return (
                    <Controller key={slot}
                        dataset={dataset} channel={channel} configuration={configuration} />
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


// end of file
