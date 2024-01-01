// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// make an error boundary
export class ErrorBoundary extends React.Component {

    // metamethods
    constructor(props) {
        // chain up
        super(props);
        // initialize
        this.state = { clean: true };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI.
        return { clean: false };
    }

    componentDidCatch(error, info) {
        // if something went wrong, log
        console.log(error, info.componentStack);
    }

    render() {
        // if an error has been caught
        if (!this.state.clean) {
            // do something special
            return this.props.fallback
        }
        // otherwise, just render my children
        return this.props.children;
    }
}
// end of file
