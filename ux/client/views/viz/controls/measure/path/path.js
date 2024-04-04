// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// local
// hooks
import { useViewports } from '~/views/viz'
// components
import { Profile } from './profile'
import { Point } from './point'
import { Title } from './title'


// a table of the points on the {measure} layer of the active viewport
export const Path = ({ view }) => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // unpack the view
    const { measure } = useFragment(pathMeasureGetMeasureLayerFragment, view)
    // get the path profile
    const { path } = measure
    // if the path is empty
    if (path.length === 0) {
        // bail
        return null
    }
    // otherwise, compute the id of the last point
    const last = path.length - 1
    // render the points
    return (
        <Box>
            {/* add a title to the table */}
            <Title />
            {/* render the points on the path */}
            {path.map((point, idx) =>
                <Point key={`p${idx}`}
                    viewport={activeViewport} view={view}
                    idx={idx} point={point} last={last} />
            )}
            {/* download the profile */}
            {<Profile view={view} />}
        </Box>
    )
}


// the container
const Box = styled.div`
    color: ${() => theme.page.normal};
    margin: 0.0rem 1.0rem 0.5rem 1.0rem;
`


// the fragment
const pathMeasureGetMeasureLayerFragment = graphql`
    fragment pathMeasureGetMeasureLayerFragment on View {
        measure {
            path {
                x
                y
            }
            selection
        }
    }
`


// end of file
