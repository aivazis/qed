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
    // whether to taper the region towards its edges before transforming it; almost always
    // what one wants when reading a spectrum, so it starts out on
    const [taper, setTaper] = React.useState(true)
    // the picture on display, if any: its address, how it was made, and whether it has arrived
    const [picture, setPicture] = React.useState(null)
    // the region the picture belongs to; any change to it makes the picture meaningless
    const scene = JSON.stringify({ viewport, dataset: dataset?.name, path: measure.path })
    // so whenever it changes
    React.useEffect(() => {
        // the picture goes
        setPicture(null)
        // all done
        return
    }, [scene])
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
    // the request for the spectrum of the rectangle, tapered or not
    const request = tapered => ({
        // where to get it
        address: [
            "spectrum", viewport, dataset.name,
            `${origin[0]}x${origin[1]}+${shape[0]}x${shape[1]}`,
        ].join("/") + (tapered ? "?taper=hann" : ""),
        // how it is made, for the caption
        shape, tapered,
        // and that it is on its way
        status: "computing",
    })
    // build the handler that asks for it
    const compute = () => {
        // a rectangle past the limit
        if (!fits) {
            // has no spectrum
            return
        }
        // otherwise, ask for the spectrum of the rectangle
        setPicture(request(taper))
        // all done
        return
    }
    // build the handler that removes the picture
    const clear = () => {
        // forget it
        setPicture(null)
        // all done
        return
    }
    // build the handler that flips the taper
    const flip = () => {
        // the new setting
        const tapered = !taper
        // remember it
        setTaper(tapered)
        // a picture on display is remade the new way, so the two can be compared
        if (picture !== null) {
            // by asking for it again
            setPicture(request(tapered))
        }
        // all done
        return
    }
    // record how the picture at {address} fared, unless it was cleared or replaced since
    const settle = (address, status) => () => {
        // update the picture it belongs to
        setPicture(old => old?.address === address ? { ...old, status } : old)
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
                <Control {...pressable(compute, fits)}
                    aria-label="compute the spectrum of the region"
                    title={fits ? "the spectrum of the rectangle the path spans"
                        : `the rectangle must be at most ${spectrum} on a side`}>
                    fft
                </Control>
                {" "}
                <Toggle {...pressable(flip, true)} aria-pressed={taper}
                    aria-label="taper the region with a hann window"
                    title="bring the region smoothly to zero towards its edges first">
                    hann: {taper ? "on" : "off"}
                </Toggle>
            </Action>
            {picture?.status === "computing" && <Note>computing…</Note>}
            {picture?.status === "failed" &&
                <Note>the server could not compute this spectrum; press fft to try again</Note>
            }
            {picture && picture.status !== "failed" &&
                <Frame hidden={picture.status !== "ready"}>
                    <Picture src={picture.address} alt="the spectrum of the region"
                        onLoad={settle(picture.address, "ready")}
                        onError={settle(picture.address, "failed")} />
                </Frame>
            }
            {picture?.status === "ready" &&
                <Caption>
                    {picture.shape[0]}x{picture.shape[1]}, {picture.tapered ? "hann" : "untapered"}
                    {" "}
                    <Enabled {...pressable(clear, true)} aria-label="clear the spectrum"
                        title="clear the spectrum">
                        ×
                    </Enabled>
                </Caption>
            }
        </Box>
    )
}


// the attributes that make an element a control the mouse and the keyboard can press
const pressable = (action, enabled) => ({
    // it is a button
    role: "button",
    // that the keyboard can reach when it can be pressed
    tabIndex: enabled ? 0 : -1,
    // says whether it can be pressed
    "aria-disabled": !enabled,
    // and does its thing when clicked
    onClick: action,
    // or when the keys that press a button are pressed on it
    onKeyDown: evt => {
        // only those keys
        if (evt.key !== "Enter" && evt.key !== " ") return
        // keep the space from scrolling the panel
        evt.preventDefault()
        // and act
        action()
        // all done
        return
    },
})


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

// a control that is on or off
const Toggle = styled(Enabled)`
    &[aria-pressed="false"] {
        color: ${() => theme.page.dim};
    }
`

// what the picture on display is, under its frame
const Caption = styled.div`
    width: 256px;
    margin: 0.0rem auto;
    text-align: end;
    font-family: inconsolata;
`

// a line about the state of the picture
const Note = styled.div`
    font-family: rubik-light;
    font-style: italic;
    margin-top: 0.5rem;
`

// and when it cannot
const Disabled = styled.span`
    font-family: inconsolata;
    cursor: default;
    color: ${() => theme.page.dim};
`

// the frame of the spectrum, laid out like the window of the peek
const Frame = styled.div`
    width: 256px;
    height: 256px;
    background-color: ${() => theme.page.shaded};
    margin: 0.5rem auto;
    border: 1px solid ${() => theme.page.viewportBorder};
`

// the spectrum, fit into its frame without distortion
const Picture = styled.img`
    display: block;
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
