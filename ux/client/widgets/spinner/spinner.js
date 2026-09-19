// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// theme
import { theme } from '~/palette'


// the indicator that work is under way
// there is one of these in the app, so that every place that waits looks like every other:
// {size} is the diameter of the ring and {weight} the thickness of its stroke, both css
// lengths; everything else lands on the ring itself, e.g. client identity for drivers
export const Spinner = ({ size = "1.0em", weight = "3px", style, ...rest }) => {
    // mix my paint
    const paint = {
        // the geometry travels as custom properties, so the ring has one definition
        "--spinner-size": size,
        "--spinner-weight": weight,
        // plus whatever my client said
        ...style,
    }
    // paint me; the role tells assistive technology that this is a report, not a control
    return (
        <Ring style={paint} role="status" aria-label="working" {...rest} />
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
`


// end of file
