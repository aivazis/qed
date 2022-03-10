// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// shapes
import { Target } from '~/shapes'
// widgets
import { SVG } from '~/widgets'

// local
// hooks
import { useFocus } from './useFocus'
import { useViews } from '../../viz/useViews'


// a table of the points on the {measure} layer of the active viewport
export const Minimap = ({ path }) => {
    // get the node in focus
    const focus = useFocus()
    // get the {activeViewport} and the set of {views} from {viz}
    const { views, activeViewport } = useViews()

    // if it's still uninitialized
    if (focus === null) {
        // bail
        return null
    }
    // compute the origin of our tile
    const [x, y] = path[focus].map(p => p - 64)
    // and derive the tile rep
    const rep = `${y}x${x}+128x128`

    // unpack the view associated with the active viewport
    const { reader, dataset, channel } = views[activeViewport]
    // check for the trivial cases
    if (!reader || !dataset || !channel) {
        // bail
        return null
    }
    // otherwise, unpack the view
    const { uuid: readerUUID, api } = reader
    const { uuid: datasetUUID } = dataset
    // assemble the data request URI
    const base = [api, readerUUID, datasetUUID, channel, 0, rep].join("/")

    const style = {
        icon: {
            stroke: "hsl(0deg, 0%, 60%)",
            strokeWidth: "3",
        }
    }

    // render
    return (
        <Box>
            <Data src={base} />
            <Map>
                <g transform={`scale(${256 / 1000})`}>
                    <Target style={style} />
                </g>
            </Map>
        </Box>
    )
}


// the container
const Box = styled.div`
    position: relative;
    width: 256px;
    height: 256px;
    background-color: hsl(0deg, 0%, 10%);
    margin: 0.0rem 1.0rem 1.0rem 1.0rem;
    border: 2px solid hsl(28deg, 30%, 25%);
`

const Data = styled.img`
    width: 256px;
    height: 256px;
`

const Map = styled(SVG)`
    position: absolute;
    top: 0px;
    left: 0px;
    width: 256px;
    height: 256px;
`


// end of file
