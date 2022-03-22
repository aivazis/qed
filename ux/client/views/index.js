// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// publish
// app layout
export Status from './status'

// the main page
export { Main, useActivityPanel } from './main'

// sandboxes
export { GiQL } from './graphiql'
export { Viz, Controls, Datasets } from './viz'

// a blank panel with size information
export Blank from './blank'
// not yet implemented
export { NYI } from './nyi'
// while {suspense} is waiting
export Loading from './loading'
// the page rendered when the user kills the server
export Stop from './stop'


// end of file
