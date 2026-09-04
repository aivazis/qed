// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// local
// hooks
import { useConfig } from './useConfig'
import { useMine } from './useMine'
// components
import { Editor } from './editor'


// render a single label
export const Label = ({ tick, value = null, setValue = null }) => {
    // unpack the geometry
    const { enabled, arrows, labels, labelPosition, tickPrecision, min, max, extent } = useConfig()
    // and the scale, to size the editor's font like mine
    const { ils } = useMine()
    // a handle on my text node, to measure where i am on the screen
    const node = React.useRef(null)
    // the rectangle the editor is pinned over while my value is being edited; {null} otherwise
    const [editing, setEditing] = React.useState(null)

    // check whether my value is the currently chosen one
    const selected = tick === value
    // if so, and the marker is on the same side of the axis as the labels
    if (selected && arrows === labels) {
        // the marker gets drawn in my place; bail
        return null
    }

    // an end label of a slider with a hand-editable extent doubles as its editor
    const end = extent === null ? null : (tick === min ? "min" : (tick === max ? "max" : null))
    // pick an implementation based on my state
    const Label = enabled ? (selected ? Selected : Enabled) : Disabled

    // set up my behaviors
    const behaviors = {}
    // when i have a way to notify the client, am enabled, but not selected
    if (setValue != null && enabled && !selected) {
        // on click, set the value; an editable end label gives up this shortcut, since a double
        // click would trip it on the way to the editor, and the thumb can be dragged to the end
        behaviors["onClick"] = evt => {
            // suppress the placemat listener
            evt.stopPropagation()
            // if i am an editable end
            if (end !== null) {
                // leave the value alone
                return
            }
            // set the value
            setValue(tick)
            // all done
            return
        }
    }
    // when i am an editable end
    if (end !== null && enabled) {
        // on double click, measure myself and open the editor over me
        behaviors["onDoubleClick"] = evt => {
            // suppress the placemat listener
            evt.stopPropagation()
            // and quash any side effects, e.g. text selection
            evt.preventDefault()
            // measure
            const rect = node.current.getBoundingClientRect()
            // and open the editor
            setEditing({
                left: rect.left, top: rect.top, width: rect.width, height: rect.height,
            })
            // all done
            return
        }
        // tag me so drivers can find the affordance
        behaviors["data-pyre-widget"] = "slider"
        behaviors["data-pyre-widget-part"] = "bound"
        behaviors["data-pyre-bound"] = end
    }

    // the editor, if open
    let editor = null
    // when it is
    if (editing !== null) {
        // unpack the extent configuration
        const { names, envelope, resize } = extent
        // and the span of the picks
        const [lowest, highest] = envelope
        // a keyboard step is one unit in the digit below the leading digit of the span, so
        // that stepping produces round numbers at the scale of the slider
        const span = max - min
        const step = span > 0 ? Math.pow(10, Math.floor(Math.log10(span)) - 1) : 1
        // the low end may move anywhere below the lowest pick, as long as the extent stays sane;
        // similarly for the high end
        const check = end === "min"
            ? candidate => candidate < max && candidate <= lowest
            : candidate => candidate > min && candidate >= highest
        // committing one end keeps the other where it is
        const commit = end === "min"
            ? candidate => resize({ min: candidate, max })
            : candidate => resize({ min, max: candidate })
        // the editor closes by clearing the rectangle
        const close = () => setEditing(null)
        // build it, with a font as big as mine on the screen
        editor = (
            <Editor name={names[end === "min" ? 0 : 1]} end={end} value={tick} step={step}
                check={check} commit={commit} rect={editing} fontSize={fontSize * ils} close={close}
            />
        )
    }

    // render; while the editor is up, the label goes invisible so it does not show through
    return (
        <>
            <Label ref={node} {...labelPosition(tick)} {...behaviors}
                visibility={editing === null ? "visible" : "hidden"}
            >
                {tick.toFixed(tickPrecision)}
            </Label>
            {editor}
        </>
    )
}


// the font size of a label, in intrinsic units
const fontSize = 32


// styling
// the base
const Base = styled.text`
    font-family: inconsolata;
    font-size: ${fontSize}px;
    text-anchor: middle;
    cursor: default;
    user-select: none;
`


const Disabled = styled(Base)`
    fill: ${props => theme.page.dim};
`


const Enabled = styled(Base)`
    & {
        fill: ${props => theme.page.normal};
        cursor: pointer;
    }

    &[data-pyre-widget-part="bound"] {
        cursor: text;
    }

    &:hover {
        fill: ${props => theme.page.highlight};
    }

    &:active {
        fill: ${props => theme.page.highlight};
    }
`


const Selected = styled(Base)`
    fill: ${props => theme.page.highlight};
`


// end of file
