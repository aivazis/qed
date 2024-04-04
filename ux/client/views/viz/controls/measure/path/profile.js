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


// download the signal profile along the path
export const Profile = ({ view }) => {
    // unpack the view
    const { dataset, measure } = useFragment(profileMeasureGetMeasureLayerFragment, view)
    // get the name of the dataset
    const { name } = dataset
    // unpack the measure layer info
    const { closed, path } = measure
    // if the path is empty
    if (path.length === 0) {
        // bail
        return null
    }
    // the profile uri
    const url = encoding => {
        // encode the points
        const points = path.map(p => `${p.y},${p.x}`).join("&")
        // form the url and return it
        return (
            ["profile", encoding, name].join("/")
            + '?'
            + `closed=${closed}&`
            + points
        )
    }

    // render the points
    return (
        <Box>
            <Action>
                profile: <a download href={url("CSV")} value={`${name}.csv`}>CSV</a>
            </Action>
        </Box>
    )
}


// the container
const Box = styled.div`
    color: ${() => theme.page.normal};
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
        color: ${() => theme.page.bright};
    }

    & a:active {
        color: ${() => theme.page.highlight};

    }

    & a:hover {
        color: ${() => theme.page.highlight};

    }
`


// the fragment
const profileMeasureGetMeasureLayerFragment = graphql`
    fragment profileMeasureGetMeasureLayerFragment on View {
        dataset {
            name
        }
        measure {
            closed
            path {
                x
                y
            }
        }
    }
`


// end of file
