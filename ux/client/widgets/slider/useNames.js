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
export const useNames = () => {
    // pull what i need from {context}
    const {
        // names
        mainName, crossName, mainCoordinate, crossCoordinate,
        mainCoordinateName, crossCoordinateName, mainNearEdgeName,
        mainPositionName, crossPositionName,
        mainMovementName, crossMovementName, mainOffsetName, crossOffsetName,
    } = React.useContext(Context)

    // and publish it
    return {
        mainName, crossName, mainCoordinate, crossCoordinate,
        mainCoordinateName, crossCoordinateName, mainNearEdgeName,
        mainPositionName, crossPositionName,
        mainMovementName, crossMovementName, mainOffsetName, crossOffsetName,
    }
}


// end of file
