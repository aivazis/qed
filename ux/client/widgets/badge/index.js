// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a button with an SVG image as content
export const Badge = ({ size, state, behaviors, style, children }) => {
    // make local state for the extra styling of the badge and the shape necessary when
    // questioning whether the activity is available
    const [polish, setPolish] = React.useState(false)

    // make a function that resets the highlight
    const reset = () => {
        // by removing any extra styling
        setPolish(false)
        // all done
        return
    }
    // make sure that my extra polish is removed any  time the cursor leaves my area
    let controls = {
        // install
        onMouseLeave: reset,
    }
    // if i'm enabled
    if (state === "enabled") {
        // make a function that can highlight the badge and the shape
        const highlight = () => {
            // and apply them
            setPolish(true)
            // all done
            return
        }
        // install them
        controls = {
            // the basic ones
            ...controls,
            // control the styling
            onMouseEnter: highlight,
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
                    {React.cloneElement(React.Children.only(children), { style: paint })}
                </g>
            </svg>
        </div>
    )
}


// end of file
