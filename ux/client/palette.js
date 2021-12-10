// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// a color wheel
const wheel = {
    // greys; the names are borrowed from {omni graffle}
    gray: {
        obsidian: "#000",
        basalt: "#333333",
        gabro: "#424242",
        steel: "#666",
        shale: "#686868",
        flint: "#8a8a8a",
        granite: "#9a9a9a",
        aluminum: "#a5a5a5",
        concrete: "#b8b8b8",
        soapstone: "#d6d6d6",
        cement: "#eee",
        marble: "#f1f1f1",
        flour: "#fafafa",
        chalk: "#ffffff",
    },

    // pyre colors
    pyre: {
        blue: "hsl(203deg, 77%, 60%)",
        green: "hsl(63deg, 40%, 50%)",
        orange: "hsl(31deg, 80%, 58%)",
    },

    // journal colors
    journal: {
        error: "hsl(0deg, 90%, 50%)",
    }
}


// my dark theme
const dark = {
    // the page
    page: {
        background: "hsl(0deg, 0%, 5%)",
        // contents
        name: "hsl(28deg, 90%, 55%)",
        appversion: "hsl(0deg, 0%, 25%)",
    },

    header: {
        color: "hsl(0deg, 0%, 50%)",
        background: "hsl(0deg, 0%, 5%)",
    },

    statusbar: {
        // overall styling
        background: "hsl(0deg, 0%, 31%)",
        separator: "hsl(0deg, 0%, 15%)",
    },

    // app metadata
    colophon: {
        // contents
        copyright: "hsl(0deg, 0%, 40%)",
        author: "hsl(0deg, 0%, 40%)",
    },

    // widgets
    widgets: {
        background: "hsl(0deg, 0%, 7%)",
    },

    // journal colors
    journal: wheel.journal,
}


// my default theme
const theme = dark


// publish
export { wheel, dark, theme }


// end of file
