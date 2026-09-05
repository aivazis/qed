// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a terminal: a frame with a prompt and a cursor
const frame = `
M 120 220
C 120 187 147 160 180 160
L 820 160
C 853 160 880 187 880 220
L 880 780
C 880 813 853 840 820 840
L 180 840
C 147 840 120 813 120 780
Z
M 190 230
L 810 230
L 810 770
L 190 770
Z`

const prompt = `
M 270 360
L 330 300
L 500 470
L 330 640
L 270 580
L 380 470
Z
M 520 620
L 730 620
L 730 690
L 520 690
Z`


// render the shape
export const Console = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }
    const dec = { ...styles.decoration, ...style?.decoration }

    // paint me
    return (
        <>
            <path d={frame} style={ico} fillRule="evenodd" />
            <path d={prompt} style={dec} />
        </>
    )
}


// end of file
