// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Info } from '~/widgets'
// locals
import { Channel } from './channel'
// styles
import styles from './styles'


// display the channels associated with this dataset
export const Channels = ({ reader, dataset, channels }) => {
    // render
    return (
        <>
            <Info name="channels" value="" style={styles.attributes} />
            {channels.map((channel) => (
                <Channel key={channel} reader={reader} dataset={dataset} channel={channel} />
            ))}
        </>
    )
}


// end of file