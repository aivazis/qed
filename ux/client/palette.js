// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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
        transparent: "hsl(0deg, 0%, 0%, 0%)",
        background: "hsl(0deg, 0%, 5%)",
        shaded: "hsl(0deg, 0%, 7%)",
        relief: "hsl(0deg, 0%, 12%)",
        active: "hsl(0deg, 0%, 17%)",
        selected: "hsl(0deg, 0%, 20%)",
        // contents
        name: "hsl(28deg, 90%, 55%)",
        appversion: "hsl(0deg, 0%, 25%)",
        //
        bright: "hsl(0deg, 0%, 70%)",
        normal: "hsl(0deg, 0%, 50%)",
        dim: "hsl(0deg, 0%, 40%)",
        pale: "hsl(0deg, 0%, 30%)",
        //
        highlight: "hsl(28deg, 90%, 55%)",
        viewportBorder: "hsl(28deg, 90%, 55%, 50%)",
        //
        danger: "hsl(0deg, 100%, 50%)",
    },

    header: {
        color: "hsl(0deg, 0%, 50%)",
        background: "hsl(0deg, 0%, 5%)",
    },

    statusbar: {
        // overall styling
        background: "hsl(0deg, 0%, 17%)",
        separator: "hsl(0deg, 0%, 15%)",
    },

    // app metadata
    colophon: {
        // contents
        copyright: "hsl(0deg, 0%, 23%)",
        author: "hsl(0deg, 0%, 23%)",
    },

    // widgets
    widgets: {
        focus: "hsl(0deg, 0%, 15%)",
        background: "hsl(0deg, 0%, 10%)",
    },

    // journal colors
    journal: wheel.journal,
}


// my default theme
const theme = dark


// publish
export { wheel, dark, theme }


// end of file
