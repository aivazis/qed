// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// components
import { Row, Prompt, Separator, Required } from './form'


// give every text input rendered directly under this field the field's {name} as its accessible
// label, unless it already carries one -- composite fields (point, circle) name their own latitude
// and longitude, and those distinct names must win over the shared field name
const nameInputs = (node, label) => {
    // pass through anything that is not an element
    if (!React.isValidElement(node)) return node
    // a text input with no name of its own gets the field's
    if (node.props?.type === "text" && !node.props["aria-label"]) {
        return React.cloneElement(node, { "aria-label": label })
    }
    // otherwise descend into the children, if any
    if (node.props?.children) {
        return React.cloneElement(node, {
            children: React.Children.map(node.props.children, child => nameInputs(child, label)),
        })
    }
    // a leaf with nothing to name
    return node
}


// render a field
export const Field = ({ name, value, tip, required = true, children }) => {
    // check validity
    const invalid = value === null || value.toString().length == 0
    // render
    return (
        <Row>
            <Prompt title={tip}>
                {required && invalid && <Required>*</Required>}
                {name}
            </Prompt>
            <Separator>{name && ":"}</Separator>
            {React.Children.map(children, child => nameInputs(child, name))}
        </Row>
    )
}


// end of file
