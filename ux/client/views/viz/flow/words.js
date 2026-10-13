// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'


// what a label of the given {category} says, put together from its parts: the names of the
// traits of a connector; the {given} name of an instance, when it is one, and the {family} of
// the component, which is the last word of the family, set apart by the mark of its category;
// or else the {role} of the protocol
export const Words = ({ category, given = null, family = null, role = null, traits = [] }) => {
    // a connector says the names of its traits
    if (traits.length) {
        // all of them
        return <>{traits.join(", ")}</>
    }
    // without a component
    if (family === null) {
        // there is only the role, if it is known
        return <>{role ?? ""}</>
    }
    // the last word of the family names the component
    const name = family.split(".").pop()
    // a component that is not an instance
    if (given === null) {
        // is named by its family alone
        return <>{name}</>
    }
    // an instance is named by its given name, possibly empty, and its family, apart from each
    // other by the mark of the category, with room around it
    return (
        <>
            {/* the given name */}
            {given}
            {/* the mark, with room before it when something precedes it */}
            <tspan dx={given ? separation : 0}>{marks[category] ?? ":"}</tspan>
            {/* and the family */}
            <tspan dx={separation}>{name}</tspan>
        </>
    )
}


// the mark that sets the given name of an instance apart from its family, by category
const marks = { factory: ":", product: "@" }
// and the room on either side of it
const separation = "0.2em"


// end of file
