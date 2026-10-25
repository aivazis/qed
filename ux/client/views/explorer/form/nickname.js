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
import { Field } from './field'
import { Value } from './value'
import { EnabledInput } from './input'


// the nickname of a component the form makes, e.g. a reader or an archive: the server's
// {suggestion} fills the field, and keeps filling it as it changes until the user edits the name;
// a control clears the field, another puts the suggestion back, and the right arrow fills an empty
// field with it; what the user types must match {pattern}, and {tip} says what the name is for
export const Nickname = ({ value, suggestion = "", update, tip, pattern }) => {
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
    // the suggestion the field took last
    const followed = React.useRef(suggestion)
    // when the suggestion changes
    React.useEffect(() => {
        // a field that still holds the suggestion it took last takes the new one too; one the
        // user edited keeps what the user typed
        if ((value ?? "") === followed.current && suggestion !== followed.current) {
            // fill it
            update("name", suggestion)
        }
        // either way, remember the suggestion, so putting it back resumes the following
        followed.current = suggestion
        // all done
        return
    }, [suggestion])
    // the field is empty when the user has erased the name
    const empty = value === null || value.length == 0
    // whether the server had anything to suggest
    const suggested = suggestion !== null && suggestion.length > 0
    // build the name mutator
    const setName = evt => {
        // get the value
        const candidate = evt.target.value
        // update the form state
        update("name", pattern.test(candidate) ? candidate : value)
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
    // build a handler that empties the field
    const clear = () => {
        // erase the name
        update("name", "")
        // and return the cursor to the field, so the user can type another
        input.current?.focus()
        // all done
        return
    }
    // build a handler that lets the right arrow accept the suggestion of an empty field
    const accept = evt => {
        // a field with text in it keeps its keys, and so does one with nothing to fill in
        if (!empty || !suggested) return
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
        <Field name="nickname" value={value} tip={tip}>
            <Value>
                <NameInput ref={input} type="text" value={value === null ? "" : value}
                    placeholder={suggestion}
                    title={empty && suggested ? "→ fills in the suggestion" : null}
                    {...behaviors} />
                {!empty &&
                    <Action label="clear" description="clear the nickname" act={clear} />
                }
                {suggested && value !== suggestion &&
                    <Action label={`use ${suggestion} instead`}
                        description="use the suggested nickname" act={restore} />
                }
            </Value>
        </Field>
    )
}


// a control next to the field, e.g. the one that clears it, or the one that puts the suggested
// name back in it; {label} is what it shows, {description} what it does
const Action = ({ label, description, act }) => {
    // build a handler that lets the keyboard press the control
    const press = evt => {
        // only the keys that press a button
        if (evt.key !== "Enter" && evt.key !== " ") return
        // keep the space from scrolling the panel
        evt.preventDefault()
        // do what the control does
        act()
        // all done
        return
    }
    // render
    return (
        <Control role="button" tabIndex={0} aria-label={description}
            onClick={act} onKeyDown={press}>
            {label}
        </Control>
    )
}


// the name input, with the suggestion dimmed when the field is empty
const NameInput = styled(EnabledInput)`
    &::placeholder {
        color: hsl(0deg, 0%, 30%);
    }
`

// the look of the controls
const Control = styled.span`
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
