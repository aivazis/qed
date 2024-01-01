// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { theme } from '~/palette'
// grab the base paint mixer
import paint from '../styles'


// paint mixer
// the toolbar
const bar = (client) => {
    // my toolbar
    const toolbar = {
        // the base layer
        backgroundColor: "hsl(0deg, 0%, 15%, 1)",
        // plus whatever the client specified
        ...paint.toolbar(client)
    }

    // primer
    const primer = paint.activity(client)
    // my badge overrides
    const badge = {
        // the base layer
        ...primer.badge,
        // enhance the base
        base: {
            //  styling
            padding: "0.375rem 0.5rem",
            // make a transparent border of the correct width so the badges don't move around
            // when the corresponding activity is engaged
            borderLeft: `2px solid hsl(0deg, 0%, 0%, 0)`,
            // plus whatever the client asked for
            ...primer.badge.base,
        },
        selected: {
            // styling
            borderLeft: `2px solid ${theme.page.name}`,
            // plus whatever the client asked for
            ...primer.badge.selected,
        },
    }

    const shape = {
        // the base layer
        ...primer.shape,
    }

    // all done
    return { toolbar, badge, shape }
}


// publish
export default {
    bar,
}


// end of file
