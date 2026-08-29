// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
// hooks
import { useReader } from './useReader'
import { useStageReader } from './useStageReader'


// report where my reader stands on its way to being viewable
// a source that is ready says nothing: its selectors and channels are the report. one that
// is still being surveyed shows that work is under way, and one whose survey failed shows
// why, along with the control that asks for another attempt
export const Standing = () => {
    // get my reader
    const { name, status, error } = useReader()
    // and the handler that asks for another attempt
    const { stage, isInFlight } = useStageReader(name)

    // a source that has completed first contact has nothing to report here
    if (status === "ready") {
        // so render nothing
        return null
    }

    // a source whose survey failed shows the reason and offers a retry
    if (status === "failed") {
        // make a handler that asks for another attempt
        const retry = evt => {
            // this control is not a reader selection, so keep the click to myself
            evt.stopPropagation()
            // and quash any default behavior
            evt.preventDefault()
            // ask the server to survey the product again
            stage()
            // all done
            return
        }
        // render the reason and the control
        return (
            <Failure data-qed-reader-status="failed">
                <Reason>{error ?? "first contact failed"}</Reason>
                <Retry onClick={retry} disabled={isInFlight}
                    aria-label={`retry first contact with '${name}'`}>
                    retry
                </Retry>
            </Failure>
        )
    }

    // everything else is work in progress: the source is either waiting for its survey to
    // be assigned or being surveyed right now
    return (
        <Progress data-qed-reader-status={status}>
            <Ring />
            <Note>opening...</Note>
        </Progress>
    )
}


// the row that reports work in progress
const Progress = styled.div`
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.0rem;
`

// the spinner, sized to sit on a line of text
const Ring = styled.div`
    width: 0.9rem;
    height: 0.9rem;
    border: 2px solid hsl(28deg, 90%, 55%);
    border-radius: 50%;
    border-top: 2px solid hsl(28deg, 90%, 55%, 0.5);
    animation: busy 1s linear infinite;
`

// the label that names the work
const Note = styled.span`
    font-size: 60%;
    color: hsl(0deg, 0%, 60%);
`

// the block that reports a failure
const Failure = styled.div`
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.0rem;
`

// the reason first contact failed
const Reason = styled.span`
    font-size: 60%;
    color: hsl(0deg, 60%, 60%);
    overflow-wrap: anywhere;
`

// the control that asks for another attempt
const Retry = styled.button`
    font-family: inherit;
    font-size: 60%;
    color: hsl(28deg, 90%, 55%);
    background: none;
    border: 1px solid hsl(28deg, 90%, 55%);
    border-radius: 0.25rem;
    padding: 0.1rem 0.4rem;
    cursor: pointer;

    &:disabled {
        color: hsl(0deg, 0%, 50%);
        border-color: hsl(0deg, 0%, 50%);
        cursor: default;
    }
`


// end of file
