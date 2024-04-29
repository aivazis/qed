// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// pull the pages
import Intro from './intro'
import Readers from './readers'
import Datasets from './datasets'
import Controls from './controls'
import Measure from './measure'
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
            { link: "#readers.nisar", title: "Connecting a NISAR reader" },
            { link: "#readers.flat", title: "Reading flat binary files" },
            { link: "#readers.isce2", title: "Support for isce2" },
            { link: "#readers.gdal", title: "Using gdal" },
        ]
    },
    {
        link: "datasets", title: "Selecting datasets", page: Datasets,
        contents: [
            { link: "#datasets.selectors", title: "Working with the data selectors" },
            { link: "#datasets.channels", title: "Picking a visualization channel" },
            { link: "#datasets.availability", title: "Data products and channels" },
        ]
    },
    {
        link: "views", title: "Adjusting the view", page: Controls,
        contents: [
            { link: "#controls.zoom", title: "The zoom level" },
            { link: "#controls.viz", title: "The visualization parameters" },
        ]
    },
    {
        link: "measure", title: "The measure layer", page: Measure,
        contents: [
            { link: "#measure.peek", title: "Peeking at pixel values" },
            { link: "#measure.path", title: "Selecting a path" },
        ]
    },
    {
        link: "panels", title: "Working with multiple data panes", page: null,
        contents: [
        ]
    },
    {
        link: "archives", title: "Connecting to data archives", page: Archives,
        contents: [
            { link: "#archives.local", title: "Local" },
            { link: "#archives.s3", title: "S3" },
        ]
    },
]


// end of file
