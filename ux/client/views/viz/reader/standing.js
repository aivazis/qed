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


// the reason a source could not be opened, with the part the panel already shows taken out
// a server side error names the product it is about, because a log entry has no other way to
// say which one it means. here the uri is one line above and the verdict is one line up from
// that, so repeating them buys nothing and pushes the part that matters down the tray. when
// the reason quotes the uri of this very reader, drop everything through the quote and keep
// what follows; a reason that never mentions it is already as short as it goes
const explain = (error, uri) => {
    // a failure that arrived without a reason
    if (!error) {
        // still has to say something
        return "first contact failed"
    }
    // a reader without a uri has nothing to match against
    if (!uri) {
        // so the reason stands as it came
        return error
    }
    // look for the uri the way an error that names a product spells it
    const mention = `'${uri}'`
    const at = error.indexOf(mention)
    // one that does not name it is already about nothing else
    if (at < 0) {
        // so leave it alone
        return error
    }
    // otherwise take what follows, less the punctuation that joined the two
    const reason = error.slice(at + mention.length).replace(/^\s*:?\s*/, "")
    // a mention with nothing after it was the whole message, so fall back to what led up to
    // it rather than showing an empty line
    return reason || error.slice(0, at).replace(/\s*$/, "")
}


// report where my reader stands on its way to being viewable
// a source that is ready says nothing: its selectors and channels are the report. one that
// is still being surveyed shows that work is under way, and one whose survey failed shows
// why. either way, the report is an entry in the metadata table of the reader, like the uri
// above it, so it sits on the same grid and reads at the same size
export const Standing = ({ style }) => {
    // get my reader
    const { uri, status, error } = useReader()

    // a source that has completed first contact has nothing to report here
    if (status === "ready") {
        // so render nothing
        return null
    }

    // a source whose survey failed shows the reason
    if (status === "failed") {
        // render the verdict, and the reason underneath, less whatever of it this panel has
        // already said; the control that asks for another attempt lives in the header of my
        // tray
        return (
            <Meta.Entry attribute="status" style={style}>
                <Report data-qed-reader-status="failed">
                    <Verdict>
                        <Failed>could not open</Failed>
                    </Verdict>
                    <Reason>{explain(error, uri)}</Reason>
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

// the reason first contact failed; it may be long, and it may have structure
const Reason = styled.span`
    color: hsl(0deg, 0%, 60%);
    white-space: pre-wrap;
    overflow-wrap: anywhere;
`

// end of file
