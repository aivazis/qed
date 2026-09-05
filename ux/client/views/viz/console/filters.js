// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme, wheel } from '~/palette'

// locals
import styles from './styles'


// the filters: one toggle per severity, and a channel prefix
export const Filters = ({ severities, toggle, prefix, setPrefix }) => {
    // render
    return (
        <Housing data-qed-region="journal-filters">
            <Severities>
                {styles.severities.map(severity => (
                    <Severity
                        key={severity}
                        type="button"
                        aria-pressed={severities.has(severity)}
                        aria-label={`show ${severity}`}
                        data-qed-control="severity"
                        data-qed-value={severity}
                        $color={styles.color(severity)}
                        $on={severities.has(severity)}
                        onClick={() => toggle(severity)}
                    >
                        {severity}
                    </Severity>
                ))}
            </Severities>
            <Channel
                type="text"
                value={prefix}
                placeholder="channel prefix"
                aria-label="channel prefix"
                spellCheck={false}
                autoComplete="off"
                data-qed-control="channel"
                onChange={e => setPrefix(e.target.value)}
            />
        </Housing>
    )
}


// the container
const Housing = styled.div`
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    font-family: inconsolata;
    font-size: 60%;
`

// the row of severity toggles
const Severities = styled.div`
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
`

// a severity toggle: plain text, grayed out when off, lit with its color when on
const Severity = styled.button`
    font-family: inconsolata;
    font-size: 100%;
    cursor: pointer;
    padding: 0.05rem 0.4rem 0.05rem 0;
    border: none;
    color: ${props => props.$on ? props.$color : wheel.gray.gabro};
    background-color: transparent;
`

// the channel prefix
const Channel = styled.input`
    font-family: inconsolata;
    font-size: 100%;
    padding: 0.1rem 0.4rem;
    border: 1px solid ${theme.page.relief};
    border-radius: 0.2rem;
    color: ${theme.page.bright};
    background-color: ${theme.page.background};
    outline: none;
    &:focus {
        border-color: ${theme.page.highlight};
    }
`


// end of file
