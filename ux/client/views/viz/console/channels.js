// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Tray } from '~/widgets'
// colors
import { theme } from '~/palette'

// locals
// hooks
import { useChannels } from './useChannels'
import { useSetChannel } from './useSetChannel'
// styles
import styles from './styles'


// the tray with the channels the server knows about, and a switch for each
export const Channels = () => {
    // render; the listing suspends the first time, while the store fills
    return (
        <Tray title="channels" initially={false} state="enabled" scale={0.5}
            data-qed-panel="journal-channels">
            <React.Suspense fallback={<Loading>loading</Loading>}>
                <Listing />
            </React.Suspense>
        </Tray>
    )
}


// the listing
const Listing = () => {
    // the channels
    const channels = useChannels()
    // and the mutator
    const { setActive } = useSetChannel()

    // render
    return (
        <Housing>
            {channels.map(channel => (
                <Row key={channel.id}>
                    <Severity $color={styles.color(channel.severity)}>{channel.severity}</Severity>
                    <Name title={channel.name}>{channel.name}</Name>
                    <Switch
                        type="button"
                        aria-pressed={channel.active}
                        aria-label={`${channel.severity} ${channel.name} active`}
                        title={channel.active ? "turn the channel off" : "turn the channel on"}
                        data-qed-control="channel-active"
                        data-qed-value={channel.id}
                        $on={channel.active}
                        onClick={() => setActive({
                            severity: channel.severity, name: channel.name, active: !channel.active,
                        })}
                    >
                        {channel.active ? "on" : "off"}
                    </Switch>
                </Row>
            ))}
        </Housing>
    )
}


// the container; the tray has already set the font size, so it is inherited as is
const Housing = styled.div`
    display: flex;
    flex-direction: column;
    padding: 0.25rem 0.5rem;
    font-family: inconsolata;
`

// while the listing loads
const Loading = styled.div`
    padding: 0.25rem 0.5rem;
    font-family: inconsolata;
    color: ${theme.page.dim};
`

// one channel
const Row = styled.div`
    display: flex;
    gap: 0.4rem;
    align-items: baseline;
    min-width: 0;
    padding: 0.1rem 0;
`

// the severity tag
const Severity = styled.span`
    flex: 0 0 auto;
    width: 4.5em;
    color: ${props => props.$color};
`

// the channel name
const Name = styled.span`
    flex: 1 1 auto;
    min-width: 0;
    color: ${theme.page.bright};
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
`

// the switch: plain text, dim when off, lit with the app color when on, like a selector value
const Switch = styled.button`
    flex: 0 0 auto;
    width: 2.5em;
    font-family: inconsolata;
    font-size: 100%;
    cursor: pointer;
    padding: 0;
    border: none;
    text-align: right;
    color: ${props => props.$on ? theme.page.name : theme.page.dim};
    background-color: transparent;
`


// end of file
