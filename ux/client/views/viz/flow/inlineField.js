// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the input of the forms elsewhere in the app, so these fields look the same
import { EnabledInput } from '~/views/explorer/form'

// local
// paint
import styles from './styles'


// a field over the canvas at {spot} on its panel, styled the way the forms of the app are: an
// optional {prompt}, the text {value} in a plain input that {onChange} hears about, and the
// reason the last try was refused, if any, followed by the {children}, e.g. the values the field
// might take; the canvas owns the input through {field}; a spot that
// was taken from a label carries its font size, so the field reads the same as the label it edits
export const InlineField = ({ spot, prompt, value, placeholder, error, field, onChange, children, ...handles }) => {
    // the size of the text: the one of the label, when known
    const size = spot.size ? { fontSize: `${spot.size}px` } : {}
    // and the least width of the box: the one of what it stands in for, if any
    const width = spot.width ? { minWidth: `${spot.width}px` } : {}
    // the box, which keeps the wheel to itself
    const box = React.useRef(null)
    // once it is up
    React.useEffect(() => {
        // the box
        const element = box.current
        // a wheel turned over the field scrolls what is in it, e.g. a list of values; the canvas
        // listens for the wheel on its container, outside of react, to move the camera, which
        // would carry the diagram away from the field, so the box stops it on its way there
        const keep = evt => evt.stopPropagation()
        // install
        element?.addEventListener("wheel", keep)
        // and remove when done
        return () => element?.removeEventListener("wheel", keep)
    }, [])
    // render
    return (
        <div ref={box} style={{ ...styles.inline.box, ...size, ...width, left: spot.x, top: spot.y }}
            {...handles}>
            <div style={styles.inline.row}>
                {prompt && <span style={styles.inline.prompt}>{prompt}:</span>}
                <EnabledInput ref={field} type="text" value={value} placeholder={placeholder}
                    style={styles.inline.input} spellCheck={false}
                    onChange={evt => onChange(evt.target.value)} />
            </div>
            {error && <div style={styles.inline.error}>{error}</div>}
            {/* whatever goes below the field, e.g. what it might take */}
            {children}
        </div>
    )
}


// the spot for a field that edits the {label}, a text on the canvas, on {panel}: level with it,
// in its font size, so the field scales with the zoom the way the label does, and right after it,
// or right after {after}, when the field belongs past something else, e.g. the ring of a choice,
// or right over {over}, a part of the label the field stands in for, e.g. the value it changes,
// with its text where the text of that part was, and how far the label has to move, {shift}, so
// the two line up to the pixel
export const spotOf = ({ label, panel, after = null, over = null }) => {
    // where they are on the screen
    const box = label.getBoundingClientRect()
    const frame = panel.getBoundingClientRect()
    // the font size of the label on the screen: its size on the canvas, scaled the way the
    // canvas is drawn
    const scale = label.getScreenCTM()
    const size = parseFloat(getComputedStyle(label).fontSize) * Math.hypot(scale.a, scale.b)
    // its text lines up with the label's, once the padding of the box above it is taken out
    const y = box.top - frame.top - 0.1 * size
    // a field that stands in for part of the label
    if (over) {
        // where that part is
        const part = over.getBoundingClientRect()
        // the browser draws the text of the field on a baseline snapped to whole pixels, while the
        // canvas draws the label where it is; so the label moves onto the pixel the field lands
        // on, by {shift}, in its own units, and the field follows it there
        const baseline = new DOMPoint(label.x.baseVal[0].value, label.y.baseVal[0].value)
            .matrixTransform(scale).y
        // how far, on the screen
        const nudge = Math.round(baseline) - baseline
        // starts its text where the text of the part starts, past the padding of its box and of
        // its input, and is at least as wide as the part, so it hides it
        return {
            x: part.left - frame.left - (boxPadding + inputPadding) * size, y: y + nudge, size,
            width: part.width + 2 * (boxPadding + inputPadding) * size,
            shift: nudge / Math.hypot(scale.a, scale.b),
        }
    }
    // otherwise, what the field follows
    const lead = (after ?? label).getBoundingClientRect()
    // and it starts half a character past it
    return { x: lead.right - frame.left + 0.5 * size, y, size }
}


// the padding on either side of the text of the field, in units of its font size: the one of its
// box, and the one of its input; the styles of the field use the same
export const boxPadding = 0.3
export const inputPadding = 0.3


// end of file
