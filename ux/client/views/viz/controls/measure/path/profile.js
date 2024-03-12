// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
// hooks
import { useGetView } from '../../../../main/useGetView'
import { usePixelPath } from '../../../../main/usePixelPath'


// the container of the {measure} actions
export const Profile = () => {
    // get the {dataset} in the active view; one is guaranteed to exist because
    // we wouldn't be here otherwise
    const { dataset } = useGetView()
    // get the set of pixels on the profile path
    const pixelPath = usePixelPath()

    // if the path is empty
    if (pixelPath.points.length === 0) {
        // bail
        return null
    }

    // the profile uri
    const url = encoding => {
        // encode the points
        const points = pixelPath.points.map(p => `${p[0]},${p[1]}`).join("&")
        // form the url and return it
        return (
            ["profile", encoding, dataset.name].join("/")
            + '?'
            + `closed=${pixelPath.closed}&`
            + points
        )
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
    color: hsl(0deg, 0%, 50%);
    padding: 0.5rem 0.0rem 0.0rem 0.0rem;
`

// an action
const Action = styled.span`
    & {
        font-family: rubik-light;
        cursor: default;
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
