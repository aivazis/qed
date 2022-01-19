// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a button with an SVG image as content
export const Badge = ({ size, state, behaviors, style, children }) => {
    // make local state for the extra styling of the badge and the shape necessary when
    // questioning whether the activity is available
    const [polish, setPolish] = React.useState(false)

    // support for questioning whether i'm available
    let controls = {}
    // if i'm not disabled
    if (state === "enabled") {
        // make a function that can highlight the badge and the shape
        const highlight = () => {
            // and apply them
            setPolish(true)
            // all done
            return
        }
        // make a function that resets the highlight
        const reset = () => {
            // by removing any extra styling
            setPolish(false)
            // all done
            return
        }
        // install them
        controls = {
            // control the styling
            onMouseEnter: highlight,
            onMouseLeave: reset,
        }
    }
    // inject the client's choices
    controls = { ...controls, ...behaviors }

    // size the shape
    const shrink = `scale(${size / 1000})`
    // mix my paint
    const paint = styles.badge({ state, client: style, polish })
    // and render
    return (
        <div style={paint.badge} {...controls}>
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width={size} height={size} >
                <g transform={shrink} style={paint.shape} >
                    {children}
                </g>
            </svg>
        </div>
    )
}


// end of file
