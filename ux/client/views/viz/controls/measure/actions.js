// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
// hooks
import { useGetView } from '../../viz/useGetView'
import { usePixelPath } from '../../viz/usePixelPath'


// the container of the {measure} actions
export const Actions = () => {
    // get the {dataset} in the active view; one is guaranteed to exist because
    // we wouldn't be here otherwise
    const { dataset } = useGetView()
    // get the set of pixels on the profile path
    const pixelPath = usePixelPath()

    // if the path is empty
    if (pixelPath.length === 0) {
        // bail
        return null
    }

    // the profile uri
    const url = encoding => {
        // encode the points
        const points = pixelPath.map(p => `${p[0]},${p[1]}`).join("&")
        // form the url and return it
        return ["/profile", encoding, dataset.uuid].join("/") + '?' + points
    }

    // render the points
    return (
        <Box>
            <Action>
                profile: <a download href={url("CSV")} value="profile.csv">CSV</a>
            </Action>
        </Box>
    )
}


// the container
const Box = styled.div`
    font-size: 75%;
    color: hsl(0deg, 0%, 40%);
    margin: 0.0rem 1.0rem 1.0rem 1.0rem;
`

// an action
const Action = styled.span`
    & {
        font-family: rubik-light;
    }

    & a {
        font-family: inconsolata;
        color: hsl(0deg, 0%, 60%);
    }

    & a:active {
        color: hsl(28deg, 90%, 55%);

    }

    & a:hover {
        color: hsl(28deg, 90%, 55%);

    }
`


// end of file
