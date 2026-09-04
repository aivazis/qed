// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import ReactDOM from 'react-dom'

// project
// colors
import { theme } from "~/palette"


// a text field that takes the place of a label while its value is being edited by hand; it is
// rendered through a portal to the document body and pinned over {rect}, the label's rectangle,
// so it sits on top of the label regardless of how the slider is transformed. it owns its
// contents and talks to nobody until the user commits with {Enter} or by leaving the field;
// {Escape} gives up, and the arrow keys step the bound, committing at once since each step is a
// complete number; either way, {close} takes the field down when it is done
export const Editor = ({ name, end, value, step, check, commit, rect, fontSize, close }) => {
    // the text under edit, seeded with the value on record
    const [text, setText] = React.useState(format(value))
    // what the text means, if anything
    const trimmed = text.trim()
    const parsed = trimmed === "" ? NaN : Number(trimmed)
    // whether the contents can be committed
    const valid = Number.isFinite(parsed) && check(parsed)
    // a handle on the field, for the initial focus
    const field = React.useRef(null)

    // send the text to the server, if it is acceptable, and report whether it went
    const apply = () => {
        // refuse anything that cannot be committed
        if (!valid) {
            // and say so
            return false
        }
        // a value that differs from the one on record goes out
        if (parsed !== value) {
            // send it
            commit(parsed)
        }
        // and report success
        return true
    }
    // nudge the bound by {direction} steps, committing at once
    const nudge = direction => {
        // start from the text under edit, when it means something, else from the value on record
        const base = Number.isFinite(parsed) ? parsed : value
        // form the candidate, rounded to the step to keep the digits tidy
        const candidate = Math.round((base + direction * step) / step) * step
        // refuse a candidate that encroaches on the picks
        if (!check(candidate)) {
            // by leaving things alone
            return
        }
        // send it
        commit(candidate)
        // and show it
        setText(format(candidate))
        // all done
        return
    }

    // take the focus and select the contents as soon as the field appears, so typing replaces them
    React.useEffect(() => {
        // get the field
        const input = field.current
        // if it is there
        if (input) {
            // focus and select
            input.focus()
            input.select()
        }
        // all done
        return
    }, [])
    // the field is pinned to a spot on the screen, so a scroll or a resize would leave it
    // floating over the wrong place; give up instead
    React.useEffect(() => {
        // install
        window.addEventListener("scroll", close, true)
        window.addEventListener("resize", close)
        // and clean up
        return () => {
            window.removeEventListener("scroll", close, true)
            window.removeEventListener("resize", close)
        }
    }, [close])

    // leaving the field commits when possible; either way, the editor goes away
    const blur = () => {
        // attempt to commit
        apply()
        // and close
        close()
        // all done
        return
    }
    // track the typing without talking to the server
    const change = evt => {
        // record the text
        setText(evt.target.value)
        // all done
        return
    }
    // the keys that commit, give up, or step
    const keydown = evt => {
        // commit
        if (evt.key === "Enter") {
            // quash the default
            evt.preventDefault()
            // an acceptable value goes out and the editor closes; an unacceptable one stays in
            // the field, painted invalid
            if (apply()) {
                // done here
                close()
            }
            // all done
            return
        }
        // give up
        if (evt.key === "Escape") {
            // quash the default
            evt.preventDefault()
            // and close without committing
            close()
            // all done
            return
        }
        // step
        if (evt.key === "ArrowUp" || evt.key === "ArrowDown") {
            // quash the default
            evt.preventDefault()
            // and nudge in the right direction
            nudge(evt.key === "ArrowUp" ? 1 : -1)
            // all done
            return
        }
        // everything else is typing
        return
    }
    // keep the pointer events of the field away from whatever lies under it
    const swallow = evt => evt.stopPropagation()

    // the field is centered where the label is, with room for a number longer than the label
    const width = Math.max(rect.width, 9 * fontSize * 0.6)
    const height = Math.max(rect.height, 1.4 * fontSize)
    // mix my paint
    const paint = {
        // pin it over the label
        position: "fixed",
        left: rect.left + rect.width / 2 - width / 2,
        top: rect.top + rect.height / 2 - height / 2,
        width, height,
        boxSizing: "border-box",
        zIndex: 10,
        // and dress it like the label
        margin: 0,
        padding: 0,
        fontFamily: "inconsolata",
        fontSize,
        lineHeight: 1,
        textAlign: "center",
        color: valid ? theme.page.highlight : theme.page.danger,
        backgroundColor: theme.page.shaded,
        border: "none",
        borderBottom: `1px solid ${valid ? theme.page.highlight : theme.page.danger}`,
        outline: "none",
    }
    // and render, outside the slider so the field is neither transformed nor hidden with the
    // decorative scale
    return ReactDOM.createPortal(
        <input ref={field} type="text" inputMode="decimal" spellCheck={false} autoComplete="off"
            aria-label={name} aria-invalid={!valid} title={`type a new ${end} and press enter`}
            value={text} style={paint}
            onBlur={blur} onChange={change} onKeyDown={keydown}
            onClick={swallow} onDoubleClick={swallow} onMouseDown={swallow}
        />,
        document.body,
    )
}


// render a bound compactly, with enough digits to round trip the typical controller value
const format = value => String(Number(value.toPrecision(6)))


// end of file
