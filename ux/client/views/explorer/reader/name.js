// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { EnabledInput, Field, Value } from '../form'


// the name of the reader; the server's {suggestion} is its initial value, and shows dimmed when
// the field is empty
export const Name = ({ value, suggestion, update }) => {
    // keep track of the input, so the cursor can go back to it
    const input = React.useRef(null)
    // the cursor position to apply once a restored suggestion is in the field
    const caret = React.useRef(null)
    // once the field shows the new value
    React.useLayoutEffect(() => {
        // if a cursor position is pending
        if (caret.current !== null) {
            // place the cursor
            input.current?.setSelectionRange(caret.current, caret.current)
            // and clear the request
            caret.current = null
        }
        // all done
        return
    }, [value])
    // the field is empty when the user has erased the name
    const empty = value === null || value.length == 0
    // build the name mutator
    const setName = evt => {
        // set up the validation regex
        const regex = /^[\w_]?[\w\d@$()_.-]*$/g
        // get the value
        const candidate = evt.target.value
        // update the form state
        update("name", regex.test(candidate) ? candidate : value)
    }
    // build a handler that puts the suggestion back in the field
    const restore = () => {
        // replace the name with the suggestion
        update("name", suggestion)
        // and return the cursor to the field, so the user can keep editing
        input.current?.focus()
        // all done
        return
    }
    // build a handler that lets the right arrow accept the suggestion of an empty field
    const accept = evt => {
        // a field with text in it keeps its keys
        if (!empty) return
        // so do keys other than the right arrow
        if (evt.key !== "ArrowRight") return
        // otherwise, take over the key
        evt.preventDefault()
        // the arrow still moves the cursor by one character, into the restored name
        caret.current = Math.min(1, suggestion.length)
        // fill the field with the suggestion
        update("name", suggestion)
        // all done
        return
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setName,
        onKeyDown: accept,
    }
    // all done
    return (
        <Field name="nickname" value={value} tip="the name of the data reader component">
            <Value>
                <NameInput ref={input} type="text" value={value === null ? "" : value}
                    placeholder={suggestion} title={empty ? "→ fills in the suggestion" : null}
                    {...behaviors} />
                {value !== suggestion &&
                    <Restore suggestion={suggestion} restore={restore} />
                }
            </Value>
        </Field>
    )
}


// the control that puts the suggested name back in the field
const Restore = ({ suggestion, restore }) => {
    // build a handler that lets the keyboard press the control
    const press = evt => {
        // only the keys that press a button
        if (evt.key !== "Enter" && evt.key !== " ") return
        // keep the space from scrolling the panel
        evt.preventDefault()
        // put the suggestion back
        restore()
        // all done
        return
    }
    // render
    return (
        <Suggestion role="button" tabIndex={0} aria-label="use the suggested nickname"
            onClick={restore} onKeyDown={press}>
            use {suggestion} instead
        </Suggestion>
    )
}


// the name input, with the suggestion dimmed when the field is empty
const NameInput = styled(EnabledInput)`
    &::placeholder {
        color: hsl(0deg, 0%, 30%);
    }
`

// the look of the control
const Suggestion = styled.span`
    & {
        cursor: pointer;
        margin-left: 0.5rem;
        color: hsl(0deg, 0%, 40%);
    }

    &:hover, &:focus {
        outline: none;
        color: hsl(28deg, 90%, 55%);
    }
`


// end of file
