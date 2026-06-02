// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import useDirectionalAttributes from './useDirectionalAttributes'
// styles
import styles from './styles'

// the separator inserted between consecutive items in a flex panel
const separator = ({ beginFlex, name, controls, min = 0, max = Infinity, extent, style }) => {
    // access the flex direction
    const { isRow, mainExtent, crossExtent, transform, cursor } = useDirectionalAttributes()

    // direction dependent settings
    // for the rule
    let dirRuleStyle = {
        cursor,
        [mainExtent]: "1px"
    }
    // for the handle
    let dirHandleStyle = {
        transform,
        [mainExtent]: "9px",
        [crossExtent]: "100%",
    }

    // mix my paint
    const ruleStyle = { ...styles.separator.rule, ...dirRuleStyle, ...style?.rule }
    // the paint of my handle
    const handleStyle = { ...styles.separator.handle, ...dirHandleStyle, ...style?.handle }
    // and the state dependent coloring
    const stateStyle = { ...styles.separator.colors, ...style?.colors }

    // make a ref for the handle
    const ref = React.useRef(null)

    // when the mouse enters my space
    const onMouseEnter = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // get the handle
        const handle = ref.current
        // if the handle has rendered
        if (handle) {
            // paint it
            handle.style.backgroundColor = stateStyle.visible
        }
        // all done
        return
    }

    // when the mouse leaves my space
    const onMouseLeave = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // quash any side effects
        evt.preventDefault()
        // get the handle
        const handle = ref.current
        // if the handle has rendered
        if (handle) {
            // paint it
            handle.style.backgroundColor = stateStyle.hidden
        }
        // all done
        return
    }

    // assemble the handle controls
    const handleControls = {
        onMouseEnter,
        onMouseLeave,
        onMouseDown: beginFlex,
    }

    // describe myself as the divider between the panel i resize and its neighbor; a divider
    // across a row layout reads as vertical, one across a column layout as horizontal
    const orientation = isRow ? "vertical" : "horizontal"
    // my current size is the live extent of the panel i control along the main axis
    const valuenow = extent?.[mainExtent]
    // the semantic markup that doubles as the a11y contract; identity rides in via {name}
    const semantics = {
        role: "separator",
        "aria-orientation": orientation,
        "aria-controls": controls,
        "aria-valuenow": valuenow == null ? undefined : Math.round(valuenow),
        "aria-valuemin": min > 0 ? min : undefined,
        "aria-valuemax": max < Infinity ? max : undefined,
        "data-pyre-widget": "flex",
        "data-pyre-widget-part": "resizer",
        "data-pyre-widget-name": name,
    }

    // paint me
    return (
        <div style={ruleStyle} {...semantics} >
            <div ref={ref} style={handleStyle} {...handleControls} />
        </div>
    )
}


// publish
export default separator


// end of file
