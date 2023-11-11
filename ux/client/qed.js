// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// the component framework
import React, { Suspense } from 'react'
import { createRoot } from 'react-dom/client'
// relay
import { RelayEnvironmentProvider } from 'react-relay/hooks'
// routing
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
// generator support
import 'regenerator-runtime'

// support for image lazy loading
import 'lazysizes'
// detect attribute changes in transformed elements
import 'lazysizes/plugins/attrchange/ls.attrchange'
// use native lazy loading whenever possible
import 'lazysizes/plugins/native-loading/ls.native-loading'


// locals
// context
import { environment } from './environment'
// components
import { ErrorBoundary } from './boundary'
// views
import {
    // data archives
    Explorer, Archives,
    // datasets
    Viz, Controls, Datasets,
    // the main page
    Main,
    // boilerplate
    Loading, NYI, Stop, Dead,
} from '~/views'


// the app layout
const QEDApp = () => {
    // page layout and top-level, disrupting, navigation
    // the app renders a client area over a status bar
    // most urls render the normal ui, but
    // - /stop: the user clicked on the "kill the server" action; show a "close this window" page
    // - /loading: shown while the app is fetching itself from the server

    // see the discussion in <Root> about how hosting complexities affect the app routes

    // render
    return (
        <Routes >
            {/* the app */}
            <Route path="/" element={<Main />} >
                {/* specific activities */}
                <Route path="about" element={<NYI />} />
                <Route path="help" element={<NYI />} />

                {/* data archives */}
                <Route element={<Explorer />}>
                    <Route path="explore" element={<Archives />} />
                </Route>

                {/* datasets */}
                <Route element={<Viz />} >
                    <Route path="controls" element={<Controls />} />
                    <Route index element={<Datasets />} />
                </Route>
            </Route>

            {/* meta navigation */}
            {/* the closing page */}
            <Route path="/stop" element={<Stop />} />
            {/* the page to render while waiting for data to arrive */}
            <Route path="/loading" element={<Loading />} />
        </Routes>
    )
}


// the outer component that sets up access to the {relay}, {suspense}, and {router} environments
const Root = () => {
    // a bit of complexity arises from the fact that we have to support
    // the following hosting use cases

    // - hosting on the local machine at some port:
    //   users run the server, it grabs a port on its host and browsers connect directly
    //   using host:port

    // - hosting as a embedded app in an existing document structure
    //   an example of which is the NISAR on-demand system, where the url seen by the user,
    //   e.g. https://<host>/ondemand/user/<username>/qed, is forwarded to the qed server port

    // in order to support these use cases, we require that the embedding url ends in "qed/"
    const regex = /^(?<base>.*\/qed).*/
    // run the current location through it
    const match = location.pathname.match(regex)
    // deduce the base url
    const basename = match === null ? "/" : match.groups.base
    // render
    return (
        <RelayEnvironmentProvider environment={environment}>
            <ErrorBoundary fallback={<Dead />}>
                <Suspense fallback={< Loading />}>
                    <Router basename={basename}>
                        <QEDApp />
                    </Router>
                </Suspense>
            </ErrorBoundary>
        </RelayEnvironmentProvider>
    )
}


// instantiate
const root = createRoot(document.getElementById('qed'))
// and render
root.render(<Root />)


// end of file
