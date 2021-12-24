// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Info } from '~/widgets'
// locals
import { Channel } from './channel'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Channels = ({ dataset, channels }) => {
    // render
    return (
        <>
            <Info name="channels" value="" style={styles.attributes} />
            {channels.map((channel) => (
                <Channel key={channel} dataset={dataset} channel={channel} />
            ))}
        </>
    )
}


// end of file