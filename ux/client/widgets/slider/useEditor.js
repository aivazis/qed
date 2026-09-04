// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useConfig } from './useConfig'
import { useMine } from './useMine'
// components
import { Editor } from './editor'


// the machinery shared by the labels that double as editors of the number they show: {name} is
// the accessible name of the field, {end} says what it edits for the tooltip, {value} seeds it,
// {check} accepts a candidate, {commit} sends an accepted one, and {fontSize} is the size of the
// label in intrinsic units, so the field can match it on the screen
export const useEditor = ({ name, end, value, check, commit, fontSize }) => {
    // the limits set the scale of a keyboard step
    const { min, max } = useConfig()
    // and the slider scale sets the size of the font on the screen
    const { ils } = useMine()
    // a handle on the label's text node, to measure where it is on the screen
    const node = React.useRef(null)
    // the rectangle the editor is pinned over while it is up; {null} otherwise
    const [rect, setRect] = React.useState(null)

    // measure the label and open the editor over it
    const open = evt => {
        // suppress the placemat listener
        evt.stopPropagation()
        // and quash any side effects, e.g. text selection
        evt.preventDefault()
        // measure
        const box = node.current.getBoundingClientRect()
        // and open
        setRect({ left: box.left, top: box.top, width: box.width, height: box.height })
        // all done
        return
    }
    // close the editor by dropping the rectangle; stable, since the editor listens with it
    const close = React.useCallback(() => setRect(null), [])

    // a keyboard step is one unit in the digit below the leading digit of the span, so that
    // stepping produces round numbers at the scale of the slider
    const span = max - min
    const step = span > 0 ? Math.pow(10, Math.floor(Math.log10(span)) - 1) : 1

    // the editor, when it is up, with a font as big as the label on the screen
    const editor = rect === null ? null : (
        <Editor name={name} end={end} value={value} step={step}
            check={check} commit={commit} rect={rect} fontSize={fontSize * ils} close={close}
        />
    )

    // hand back the handle, the state, the opener, and the element
    return { node, editing: rect !== null, open, editor }
}


// end of file
