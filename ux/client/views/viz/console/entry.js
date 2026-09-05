// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from '~/palette'

// locals
import styles from './styles'


// the notes that are shown in their own slots rather than listed
const shown = new Set(["channel", "severity", "application", "filename", "line", "function"])

// render the time of a record
const clock = time => {
    // the moment
    const moment = new Date(time * 1000)
    // as a time of day with milliseconds
    return moment.toLocaleTimeString([], { hour12: false }) + "." +
        String(moment.getMilliseconds()).padStart(3, "0")
}


// one record
export const Entry = ({ record }) => {
    // whether the details are showing
    const [expanded, setExpanded] = React.useState(false)
    // flip
    const toggle = () => setExpanded(!expanded)
    // unpack
    const { page, notes, pid, time } = record
    // the severity and the channel
    const severity = notes.severity ?? "info"
    const channel = notes.channel ?? ""
    // the color
    const color = styles.color(severity)
    // the first line, and the rest
    const [first = "", ...rest] = page
    // the notes worth listing
    const extra = Object.entries(notes).filter(([key]) => !shown.has(key))

    // render
    return (
        <Housing
            role="button"
            aria-expanded={expanded}
            data-qed-control="entry"
            data-qed-value={severity}
            onClick={toggle}
        >
            <Summary>
                <Severity $color={color}>{severity}</Severity>
                <Channel title={channel}>{channel}</Channel>
                <Line $expanded={expanded}>{first}</Line>
            </Summary>
            {expanded && (
                <Details>
                    {rest.map((line, index) => <Text key={index}>{line}</Text>)}
                    <Meta>
                        <Field>{clock(time)}</Field>
                        <Field>pid {pid}</Field>
                        {notes.filename && (
                            <Field title={notes.filename}>
                                {notes.filename.split("/").pop()}:{notes.line} in {notes.function}
                            </Field>
                        )}
                        {extra.map(([key, value]) => (
                            <Field key={key}>{key}: {value}</Field>
                        ))}
                    </Meta>
                </Details>
            )}
        </Housing>
    )
}


// the container
const Housing = styled.div`
    cursor: pointer;
    padding: 0.15rem 0.5rem;
    border-bottom: 1px solid ${theme.page.relief};
    font-family: inconsolata;
    font-size: 60%;
    &:hover {
        background-color: ${theme.page.relief};
    }
`

// the one line summary
const Summary = styled.div`
    display: flex;
    gap: 0.4rem;
    align-items: baseline;
    min-width: 0;
`

// the severity tag
const Severity = styled.span`
    flex: 0 0 auto;
    width: 4.5em;
    color: ${props => props.$color};
`

// the channel name; it keeps its width and the message yields
const Channel = styled.span`
    flex: 0 0 auto;
    max-width: 40%;
    color: ${theme.page.dim};
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
`

// the first line
const Line = styled.span`
    flex: 1 1 auto;
    min-width: 0;
    color: ${theme.page.bright};
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: ${props => props.$expanded ? "pre-wrap" : "nowrap"};
`

// the rest of the page
const Details = styled.div`
    padding: 0.15rem 0 0.15rem 4.9em;
`

// a line of the page
const Text = styled.div`
    color: ${theme.page.bright};
    white-space: pre-wrap;
    word-break: break-word;
`

// the metadata
const Meta = styled.div`
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-top: 0.15rem;
    color: ${theme.page.dim};
`

// one piece of metadata
const Field = styled.span`
    white-space: nowrap;
`


// end of file
