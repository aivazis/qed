// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay'
import styled from 'styled-components'

// project
// widgets
import { SVG, Slider, Spacer, Tray } from '~/widgets'

// locals
// hooks
import { useReset } from './useReset'
import { useSetLevel } from './useSetLevel'
import { useToggleCoupled } from './useToggleCoupled'
// components
import { Lock } from './lock'
import { Minimap } from './minimap'
import { Reset } from './reset'
import { Save } from './save'


//  display the zoom control
export const Zoom = ({ viewport, view, min = -4, max = 4, ils = 200 }) => {
    // unpack the view
    const { reader, dataset, channel, zoom } = useFragment(zoomControlsGetZoomStateFragment, view)

    // inspect the view components to initialize my state
    const enabled = (reader && dataset && channel) ? true : false
    // make a handler that resets the state to the persisted defaults
    const { reset: restoreDefaults } = useReset(viewport)
    // a handler that sets the zoom level
    const { set: setLevel } = useSetLevel(viewport)
    // and another one that toggle the coupled flag
    const { toggle } = useToggleCoupled(viewport)

    // setup the reset action
    const reset = () => {
        // restore the default
        restoreDefaults()
        // all done
        return
    }

    // make the zoom lock toggle
    const toggleLock = () => {
        // toggle the flag
        toggle()
        // all done
        return
    }

    // adjust the horizontal zoom
    const setHorizontalZoom = value => {
        // build the new value
        const level = { horizontal: value, vertical: zoom.coupled ? value : zoom.vertical }
        // and set it
        setLevel(level)
        // all done
        return
    }
    // adjust the vertical zoom
    const setVerticalZoom = value => {
        // build the new value
        const level = { vertical: value, horizontal: zoom.coupled ? value : zoom.horizontal }
        // and set it
        setLevel(level)
        // all done
        return
    }

    // set up the tick marks
    const major = [...Array((max - min) / 2 + 1).keys()].map((_, idx) => min + 2 * idx)
    const minor = [...Array((max - min) / 2).keys()].map((_, idx) => min + 1 + 2 * idx)
    // slider configuration
    const xSlider = {
        value: zoom.horizontal, setValue: setHorizontalZoom,
        min, max, major, minor, tickPrecision: 0, markerPrecision: 1,
        direction: "row", labels: "top", arrows: "bottom", markers: true,
        height: ils / 2, width: ils,
    }
    const ySlider = {
        value: zoom.vertical, setValue: setVerticalZoom,
        min, max, major, minor, tickPrecision: 0, markerPrecision: 1,
        direction: "column", flipped: true, labels: "right", arrows: "left", markers: true,
        height: ils, width: ils / 2,
    }
    // set up the overall dimensions of the control
    const width = 340
    const height = 290

    // mix my paint
    const state = enabled ? "enabled" : "disabled"
    // and render
    return (
        <Tray title="zoom" initially={true} state={state} scale={0.5}>
            <Header>
                <Spacer />
                <Save save={reset} enabled={false} />
                <Reset reset={reset} enabled={zoom.dirty} />
            </Header>
            {/* the control housing */}
            <Housing height={height} width={width}>
                {/* the vertical slider */}
                <g transform="translate(10 0)">
                    <Controller enabled={enabled} {...ySlider} />
                </g>
                {/* the horizontal slider */}
                <g transform="translate(100 190)">
                    <Controller enabled={enabled} {...xSlider} />
                </g>
                {/* the minimap */}
                <g transform={`translate(100 0) scale(${ils})`}>
                    <Minimap ils={ils} zoom={zoom} shape={dataset.shape} />
                </g>
                {/* the lock */}
                <g transform="translate(60 240)">
                    <Lock lock={zoom.coupled} toggle={toggleLock} />
                </g>
            </Housing>
        </Tray>
    )
}


// the section header
const Header = styled.div`
    height: 1.5rem;
    margin: 0.5rem 0.0rem 0.25rem 1.0rem;
    // for my children
    display: flex;
    flex-direction: row;
    align-items: center;
`

// the slider housing
const Housing = styled(SVG)`
    margin: 1.0rem auto;
`

// the controllers
const Controller = styled(Slider)`
`

// the fragment
const zoomControlsGetZoomStateFragment = graphql`
    fragment zoomControlsGetZoomStateFragment on View {
        reader {
            id
        }
        dataset {
            id
            shape
        }
        channel {
            id
        }
        zoom {
            dirty
            coupled
            horizontal
            vertical
        }
    }
`


// end of file
