// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// pull the pages
import Intro from './intro'


// publish the content map
export const topics = [
    //
    {
        link: "intro", title: "Getting started", page: Intro,
        contents: [
            { link: "#dependencies", title: "Dependencies" },
            { link: "#cloning", title: "Cloning the repositories" },
            { link: "#mm", title: "Setting up the build system" },
            { link: "#building", title: "Building" },
            { link: "#launching", title: "Launching" },
        ]
    },
    { link: "archives", title: "Connect to data archives", page: null },
    { link: "readers", title: "Loading datasets", page: null },
    { link: "datasets", title: "Selecting datasets", page: null },
    { link: "views", title: "Adjusting the view", page: null },
    { link: "measure", title: "The measure layer", page: null },
    { link: "panels", title: "Working with multiple data panels", page: null },
]


// end of file
