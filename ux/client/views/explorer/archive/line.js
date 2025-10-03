// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { Vertex } from './vertex'
import { Field, Value, SpacerBetween } from '../form'


// collect the coordinates of a line of interest
export const Line = ({ region, update }) => {
    // unpack the region
    const { vertices } = region
    // check the size
    const empty = vertices.length === 0
    // check that the contents are non trivial
    const nontrivial = vertices.some(v => v.longitude !== "" && v.latitude !== "")
    // validate my contents
    const ok = nontrivial ? "ok" : ""
    // make sure there is something the user can modify
    if (empty) {
        // by adding a trivial vertex to the displayed pile
        vertices.splice(0, 0, { longitude: "", latitude: "" })
    }
    // specialize the form update
    const updateLine = (line) => update("line", line)
    // render
    return (
        <Field name="line" value={ok} tip="the coordinates the vertices of a line interest">
            <Value>
                <Title />
                {vertices.map((_, idx) =>
                    <Vertex key={`v${idx}`} idx={idx} region={region} update={updateLine} />
                )}
            </Value>
        </Field>
    )
}


// the table title
const Title = () => {
    return (
        <Box>
            <Header>longitude</Header>
            <SpacerBetween />
            <Header>latitude</Header>
        </Box>
    )
}

// the container
const Box = styled.div`
    display: flex;
    align-items: end;
    font-family: rubik-light;
    height: 1.2em;
    margin: 0em;
    padding: 0.0rem 0.0rem;
`

// headers
const Header = styled.span`
    display: inline-block;
    width: 6.0em;
    text-align: end;
    vertical-align: bottom;
    padding: 0.0rem 0.0 0.0rem 0.0rem;
    margin: 0.0rem 0.0rem 0.0rem 0.0rem;
    cursor: default;
`


// end of file
