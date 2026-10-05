// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { Link } from 'react-router-dom'

// project
// hooks
import { useActivityPanel } from '~/views'

// locals
// widgets
import { Badge } from '~/widgets'
// styles
import styles from './styles'


// the base activity rendering mechanics
// an activity is a {Link} that presents a {shape} inside a {Badge}
// {shape} is typically an SVG fragment

// activities can be { "disabled", "enabled", "selected", "available" }
// currently, there is no use case for a disabled activity, so the logic may need to change

export const Activity = ({ size, url, current, disabled = false, children, style, label }) => {
    // grab the activity panel state mutators
    const { showActivityPanel, toggleActivityPanel } = useActivityPanel()
    // which determines its state
    const state = disabled ? "disabled" : current ? "selected" : "enabled"
    // mix my paint
    const paint = styles.activity(style)
    // a disabled activity has nowhere to go
    if (disabled) {
        // so it is a badge that does nothing, marked as unavailable
        return (
            <Badge size={size} state={state} style={paint}
                aria-label={label} aria-disabled={true} data-qed-nav={label} >
                {children}
            </Badge>
        )
    }
    // otherwise, the action on click
    const onClick = current ? toggleActivityPanel : showActivityPanel
    // assemble my behaviors
    const behaviors = { onClick }
    // paint me; the {Link} is the control and carries the accessible name and nav identity, so the
    // badge inside opts out of the button role (no interactive element nested in another)
    return (
        <Link to={url} aria-label={label} data-qed-nav={label} >
            <Badge size={size} state={state} behaviors={behaviors} style={paint} role={undefined} >
                {children}
            </Badge>
        </Link>
    )
}


// end of file
