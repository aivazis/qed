// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// provide access to the {sliding} flag
export const useConfig = () => {
    // pull what i need from {context}
    const {
        arrows, labels,
        min, max, major,
        intervalPosition,
        labelPosition, majorPosition, marker, markerPosition, markerLabelPosition,
    } = React.useContext(Context)

    // and publish
    return {
        arrows, labels,
        min, max, major,
        intervalPosition, labelPosition, majorPosition,
        marker, markerPosition, markerLabelPosition,
    }
}


// end of file
