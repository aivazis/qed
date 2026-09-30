// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


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

    // journal colors, by severity: the x11 colors of the journal's dark terminal palette
    journal: {
        debug: "#6495ed", // cornflower blue
        firewall: "#ff00ff", // fuchsia
        info: "#228b22", // forest green
        warning: "#ffa500", // orange
        error: "#ff0000", // red
        help: "#00ffff", // cyan
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
        link: "hsl(280deg, 80%, 60%)",
        linkActive: "hsl(280deg, 40%, 60%)",
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
        focus: {
            color: "hsl(28deg, 90%, 55%)",
            background: "hsl(0deg, 0%, 15%)",
        },
        selection: {
            color: "hsl(28deg, 90%, 55%)",
            background: "hsl(0deg, 0%, 75%)",
        },
        background: "hsl(0deg, 0%, 10%)",
    },

    // journal colors
    journal: wheel.journal,

    // the quality panel: quiet slates for the data, so the orange of the focus is the one warm
    // color on it, and the hues of the fill the viz pipeline paints where a raster is empty
    quality: {
        // the states of the chunks of a raster
        unwritten: "hsl(0deg, 0%, 12%)",
        data: "hsl(210deg, 22%, 52%)",
        sliver: "hsl(210deg, 30%, 72%)",
        // chunks of fill: brick when the fill the library knows about is what they hold, as
        // {qed::nisar::Absence} paints a declared fill, and teal when the library is told
        // something else, as it paints a fill nobody declared
        fill: "hsl(0deg, 38%, 36%)",
        lie: "hsl(173deg, 47%, 32%)",
        // the map of a file, told apart by lightness rather than hue: the raster in view is drawn
        // as the data, the other rasters of the product a step darker, every other dataset darker
        // still, and the raster picked from the legend in a pale tone above them all
        neighbor: "hsl(35deg, 12%, 38%)",
        others: "hsl(0deg, 0%, 24%)",
        spot: "hsl(210deg, 25%, 86%)",
    },
}


// my default theme
const theme = dark


// publish
export { wheel, dark, theme }


// end of file
