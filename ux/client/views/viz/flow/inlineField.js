// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the input of the forms elsewhere in the app, so these fields look the same
import { EnabledInput } from '~/views/explorer/form'

// local
// paint
import styles from './styles'


// a field over the canvas at {spot} on its panel, styled the way the forms of the app are: an
// optional {prompt}, the text {value} in a plain input that {onChange} hears about, and the
// reason the last try was refused, if any; the canvas owns the input through {field}
export const InlineField = ({ spot, prompt, value, placeholder, error, field, onChange, ...handles }) => {
    // render
    return (
        <div style={{ ...styles.inline.box, left: spot.x, top: spot.y }} {...handles}>
            <div style={styles.inline.row}>
                {prompt && <span style={styles.inline.prompt}>{prompt}:</span>}
                <EnabledInput ref={field} type="text" value={value} placeholder={placeholder}
                    style={styles.inline.input} spellCheck={false}
                    onChange={evt => onChange(evt.target.value)} />
            </div>
            {error && <div style={styles.inline.error}>{error}</div>}
        </div>
    )
}


// end of file
