// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"


// compute the spectrum of the rectangle the measure path spans, and show it
export const Spectrum = ({ viewport, view }) => {
    // unpack the view
    const { spectrum, dataset, measure } = useFragment(spectrumMeasureGetRegionFragment, view)
    // the address of the picture on display, which stays put until the user asks again
    const [picture, setPicture] = React.useState(null)
    // a dataset that has no spectrum, or no dataset at all
    if (spectrum === null || dataset === null) {
        // has nothing to offer
        return null
    }
    // the anchors of the path
    const { path } = measure
    // a rectangle needs two of them, at its opposite corners
    if (path.length < 2) {
        // so there is nothing to offer yet
        return null
    }
    // the lines and the samples of the anchors
    const lines = path.map(point => point.y)
    const samples = path.map(point => point.x)
    // the rectangle they span starts at the smallest of each
    const origin = [Math.min(...lines), Math.min(...samples)]
    // and reaches the largest of each, inclusive
    const shape = [Math.max(...lines) - origin[0] + 1, Math.max(...samples) - origin[1] + 1]
    // the server only transforms rectangles up to its limit along each side
    const fits = shape.every(extent => extent <= spectrum)
    // the address of the spectrum of the rectangle
    const address = [
        "spectrum", viewport, dataset.name, `${origin[0]}x${origin[1]}+${shape[0]}x${shape[1]}`
    ].join("/")
    // build the handler that asks for it
    const compute = () => {
        // a rectangle past the limit
        if (!fits) {
            // has no spectrum
            return
        }
        // otherwise, show the spectrum of the rectangle
        setPicture(address)
        // all done
        return
    }
    // let the keyboard press the control too
    const press = evt => {
        // only the keys that press a button
        if (evt.key !== "Enter" && evt.key !== " ") return
        // keep the space from scrolling the panel
        evt.preventDefault()
        // ask for the spectrum
        compute()
        // all done
        return
    }
    // pick the look of the control
    const Control = fits ? Enabled : Disabled
    // render
    return (
        <Box>
            <Action>
                spectrum of {shape[0]}x{shape[1]}:{" "}
                <Control role="button" tabIndex={fits ? 0 : -1}
                    aria-label="compute the spectrum of the region" aria-disabled={!fits}
                    title={fits ? "the spectrum of the rectangle the path spans"
                        : `the rectangle must be at most ${spectrum} on a side`}
                    onClick={compute} onKeyDown={press}>
                    fft
                </Control>
            </Action>
            {picture && <Picture src={picture} alt="the spectrum of the region" />}
        </Box>
    )
}


// the container
const Box = styled.div`
    color: ${() => theme.page.normal};
    margin: 0.0rem 1.0rem 0.5rem 1.0rem;
`

// the line with the control
const Action = styled.div`
    font-family: rubik-light;
    cursor: default;
`

// the control, when it can be pressed
const Enabled = styled.span`
    & {
        font-family: inconsolata;
        cursor: pointer;
        color: ${() => theme.page.bright};
    }

    &:hover, &:focus {
        outline: none;
        color: hsl(28deg, 90%, 55%);
    }
`

// and when it cannot
const Disabled = styled.span`
    font-family: inconsolata;
    cursor: default;
    color: ${() => theme.page.dim};
`

// the spectrum, fit into a box the size of the peek window
const Picture = styled.img`
    display: block;
    margin-top: 0.5rem;
    width: 256px;
    height: 256px;
    object-fit: contain;
    image-rendering: pixelated;
`


// the fragment
const spectrumMeasureGetRegionFragment = graphql`
    fragment spectrumMeasureGetRegionFragment on View {
        spectrum
        dataset {
            name
        }
        measure {
            path {
                x
                y
            }
        }
    }
`


// end of file
