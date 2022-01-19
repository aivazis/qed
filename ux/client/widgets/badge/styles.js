// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { theme } from '~/palette'


// mixer of badge paint
const badge = ({ state, client, polish }) => ({
    // the container
    badge: {
        // the base coat
        ...paint.badge.base, ...client.badge?.base,
        // the state dependent layer
        ...paint.badge[state], ...client.badge?.[state],
        // extra polish from the highlight, if necessary
        ...(polish ? paint.badge.available : null),
        ...(polish ? client.badge?.available : null),
    },
    // the svg container
    shape: {
        // the base coat
        ...paint.shape.base, ...client.shape?.base,
        // the state dependent layer
        ...paint.shape[state], ...client.shape?.[state],
        // extra polish from the highlight, if necessary
        ...(polish ? paint.shape.available : null),
        ...(polish ? client.shape?.available : null),
    },
})


// publish
export default {
    badge,
}


// the default paint
const paint = {
    // the container
    badge: {
        base: {},
        disabled: {},
        enabled: {},
        selected: {},
        available: {},
    },

    // the svg transform that renders the icon
    shape: {
        base: {},
        disabled: {},
        enabled: {},
        selected: {},
        available: {},
    },
}


// end of file
