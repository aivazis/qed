// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


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
import { LinearRangeController } from './linearrange'
import { LogRangeController } from './logrange'


//  the tray with the visualization pipeline controls
export const Viz = () => {
    // get the pipeline
    const { dataset, channel, controllers } = useGetVizPipeline()
    // and render
    return (
        <Tray title="viz" state="enabled" initially={true}>
            {controllers.map(configuration => {
                // unpack the controller configuration
                const { id, __typename: typename } = configuration
                // look up the controller
                const Controller = registry[typename]
                // and render
                return (
                    <Controller key={id}
                        dataset={dataset} channel={channel} configuration={configuration} />
                )
            })}
        </Tray>
    )
}


// the controller type registry
const registry = {
    LinearRangeController,
    LogRangeController,
}

// styling
const Dataset = styled.div`
    font-family: inconsolata;
    font-size: 75%;
    cursor: default;
    padding: 0.25rem;
`

const Channel = styled.div`
    font-family: inconsolata;
    font-size: 75%;
    cursor: default;
    padding: 0.25rem;
`


// end of file
