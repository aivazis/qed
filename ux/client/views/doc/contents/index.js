// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// pull the pages
import Intro from './intro'
import Readers from './readers'
import Archives from './archives'


// publish the content map
export const topics = [
    //
    {
        link: "intro", title: "Getting started", page: Intro,
        contents: [
            { link: "#intro.dependencies", title: "Dependencies" },
            { link: "#intro.cloning", title: "Cloning the repositories" },
            { link: "#intro.mm", title: "Setting up the build system" },
            { link: "#intro.building", title: "Building" },
            { link: "#intro.launching", title: "Launching" },
        ]
    },
    {
        link: "readers", title: "Loading datasets", page: Readers,
        contents: [
            { link: "#readers.nisar", title: "Connecting a NISAR reader" }
        ]
    },
    {
        link: "archives", title: "Connecting to data archives", page: Archives,
        contents: [
            { link: "#archives.local", title: "Local" },
            { link: "#archives.s3", title: "S3" },
        ]
    },
    { link: "datasets", title: "Selecting datasets", page: null },
    { link: "views", title: "Adjusting the view", page: null },
    { link: "measure", title: "The measure layer", page: null },
    { link: "panels", title: "Working with multiple data panels", page: null },
]


// end of file
