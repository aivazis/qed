// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// theme
import { theme } from '~/palette'
// widgets
import { Meta, Spinner } from '~/widgets'

// locals
// hooks
import { useReader } from './useReader'


// report where my reader stands on its way to being viewable
// a source that is ready says nothing: its selectors and channels are the report. one that
// is still being surveyed shows that work is under way, and one whose survey failed shows
// why. either way, the report is an entry in the metadata table of the reader, like the uri
// above it, so it sits on the same grid and reads at the same size
export const Standing = ({ style }) => {
    // get my reader
    const { status, error } = useReader()

    // a source that has completed first contact has nothing to report here
    if (status === "ready") {
        // so render nothing
        return null
    }

    // a source whose survey failed shows the reason
    if (status === "failed") {
        // render the verdict, and the reason underneath, as the server reported it; the
        // control that asks for another attempt lives in the header of my tray
        return (
            <Meta.Entry attribute="status" style={style}>
                <Report data-qed-reader-status="failed">
                    <Verdict>
                        <Failed>could not open</Failed>
                    </Verdict>
                    <Reason>{error ?? "first contact failed"}</Reason>
                </Report>
            </Meta.Entry>
        )
    }

    // everything else is work in progress: the source is either waiting for its survey to
    // be assigned or being surveyed right now
    return (
        <Meta.Entry attribute="status" style={style}>
            <Report data-qed-reader-status={status}>
                <Verdict>
                    <Spinner size="0.8em" weight="2px" />
                    <Note>opening</Note>
                </Verdict>
            </Report>
        </Meta.Entry>
    )
}


// the report, a stack of lines in the value column
const Report = styled.div`
    display: flex;
    flex-direction: column;
    gap: 0.25em;
`

// the first line of the report: what happened
const Verdict = styled.div`
    display: flex;
    align-items: center;
    gap: 0.75em;
`

// the label that names the work
const Note = styled.span`
    color: hsl(0deg, 0%, 60%);
`

// the statement that first contact failed
const Failed = styled.span`
    color: ${() => theme.page.danger};
`

// the reason first contact failed, verbatim; it may be long, and it may have structure
const Reason = styled.span`
    color: hsl(0deg, 0%, 60%);
    white-space: pre-wrap;
    overflow-wrap: anywhere;
`

// end of file
