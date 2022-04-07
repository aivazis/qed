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


//  display the demo control
export const Viz = () => {
    // get the pipeline
    const { dataset, channel } = useGetVizPipeline()

    // and render
    return (
        <Tray title="viz" state="enabled" initially={true}>
            <Dataset>{dataset}</Dataset>
            <Channel>{channel}</Channel>
        </Tray>
    )
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
