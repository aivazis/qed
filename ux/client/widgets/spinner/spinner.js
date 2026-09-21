// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// hooks
import { useReachability } from '~/hooks'
// theme
import { theme } from '~/palette'


// the indicator that work is under way
// there is one of these in the app, so that every place that waits looks like every other:
// {size} is the diameter of the ring and {weight} the thickness of its stroke, both css
// lengths; everything else lands on the ring itself, e.g. client identity for drivers
//
// a turning ring claims that work is under way and that this client is watching it. the
// second half is false while the client is out of touch with its server: the work may be
// going on, may have finished, or may have died with the server, and nothing on this page can
// tell which. so the ring stops and changes color for as long as that lasts, and picks up
// where it left off when contact is back, if whatever it was waiting for is still pending
export const Spinner = ({ size = "1.0em", weight = "3px", style, ...rest }) => {
    // find out whether we are in touch with the server
    const { state, since } = useReachability()
    // we are stalled when we know that we are not
    const stalled = state === "error"
    // mix my paint
    const paint = {
        // the geometry travels as custom properties, so the ring has one definition
        "--spinner-size": size,
        "--spinner-weight": weight,
        // plus whatever my client said
        ...style,
    }
    // what i report: either that work is under way, or that there is no way to tell
    const label = stalled ? "no contact with the server" : "working"
    // when stalled, say since when on hover, since how long is the useful part
    const title = stalled && since ? `no contact with the server since ${since.toString()}` : null
    // paint me; the role tells assistive technology that this is a report, not a control
    return (
        <Ring style={paint} role="status" aria-label={label} title={title}
            data-qed-spinner={stalled ? "stalled" : "working"} {...rest} />
    )
}


// the ring, in the color of the app. one quadrant is faded, since a uniform ring looks the
// same at every angle and its rotation would go unnoticed. the {busy} animation owns my
// transform while it runs, so i must never be positioned with one: clients that want me
// centered arrange for that in my container
const Ring = styled.div`
    /* for my container: i neither stretch nor shrink */
    flex: 0 0 auto;
    /* geometry */
    width: var(--spinner-size);
    height: var(--spinner-size);
    border-radius: 50%;
    /* paint */
    border: var(--spinner-weight) solid ${() => theme.page.name};
    border-top: var(--spinner-weight) solid ${() => theme.page.viewportBorder};
    /* motion */
    animation: busy 1s linear infinite;

    /* out of touch with the server: hold still, in the color of trouble */
    &[data-qed-spinner="stalled"] {
        animation-play-state: paused;
        border-color: ${() => theme.journal.error};
        border-top-color: ${() => theme.page.viewportBorder};
        opacity: 0.6;
    }
`


// end of file
