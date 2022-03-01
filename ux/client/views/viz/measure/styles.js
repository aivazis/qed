// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { theme, wheel } from '~/palette'
// and the base styles
import styles from '../styles'


// measuring layer
const measure = ({ width, height }) => ({
    position: "absolute",
    top: "0px",
    left: "0px",
    width: `${width}px`,
    height: `${height}px`,
})


// publish
export default {
    measure,
}


// end of file
