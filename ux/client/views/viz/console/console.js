// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Header } from '~/widgets'
// colors
import { theme } from '~/palette'

// locals
// the store
import { journal } from './store'
// hooks
import { useJournal } from './useJournal'
// components
import { Entry } from './entry'
import { Filters } from './filters'
// styles
import styles from './styles'


// render a record the way the terminal would, for the clipboard
const plain = record => {
    // the identity
    const head = `${record.notes.severity} ${record.notes.channel}:`
    // the page, one line each
    return [head, ...record.page.map(line => `  ${line}`)].join("\n")
}


// the journal console
export const Console = () => {
    // the records; subscribing keeps the stream open while i am mounted
    const entries = useJournal()
    // the severities that are showing
    const [severities, setSeverities] = React.useState(() => new Set(styles.severities))
    // and the channel prefix
    const [prefix, setPrefix] = React.useState("")
    // the list, so the newest entry can be kept in view
    const list = React.useRef(null)

    // flip a severity
    const toggle = severity => {
        // make a copy
        const next = new Set(severities)
        // flip
        if (next.has(severity)) {
            next.delete(severity)
        } else {
            next.add(severity)
        }
        // and set
        setSeverities(next)
        // all done
        return
    }

    // the records that pass the filters
    const visible = entries.filter(record =>
        severities.has(record.notes.severity ?? "info")
        && (record.notes.channel ?? "").startsWith(prefix)
    )

    // keep the newest entry in view as records arrive
    React.useEffect(() => {
        // the list
        const node = list.current
        // if it is there
        if (node) {
            // scroll to the bottom
            node.scrollTop = node.scrollHeight
        }
        // all done
        return
    }, [visible.length])

    // copy the visible records to the clipboard
    const copy = () => {
        // render them
        const text = visible.map(plain).join("\n")
        // and hand them to the clipboard, if there is one
        navigator.clipboard?.writeText(text)
        // all done
        return
    }

    // render
    return (
        <Panel data-qed-panel="journal">
            {/* the title of the panel */}
            <Header title="journal" style={styles.header}>
                <Action type="button" aria-label="copy" data-qed-control="copy" onClick={copy}>
                    copy
                </Action>
                <Action type="button" aria-label="clear" data-qed-control="clear" onClick={journal.clear}>
                    clear
                </Action>
            </Header>
            {/* the filters */}
            <Filters severities={severities} toggle={toggle} prefix={prefix} setPrefix={setPrefix} />
            {/* the records */}
            <List ref={list} data-qed-region="journal-entries">
                {visible.map(record => <Entry key={record.key} record={record} />)}
            </List>
        </Panel>
    )
}


// the container
const Panel = styled.div`
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    min-height: 0;
`

// a header action
const Action = styled.button`
    font-family: rubik-medium;
    font-size: 100%;
    text-transform: uppercase;
    cursor: pointer;
    margin-left: 0.5rem;
    padding: 0 0.25rem;
    border: none;
    color: ${theme.header.color};
    background-color: transparent;
    &:hover {
        color: ${theme.page.bright};
    }
`

// the list of records
const List = styled.div`
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
`


// end of file
