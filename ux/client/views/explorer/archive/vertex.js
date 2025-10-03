// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Badge } from '~/widgets'
// shapes
import { Plus, X } from '~/shapes'

// local
// components
import { Latitude } from './latitude'
import { Longitude } from './longitude'
import { SpacerBetween } from '../form'
// styles
import { add as paintAdd, del as paintDelete } from './styles'


// a point in a line or polygon geographic search
export const Vertex = ({ idx, region, update }) => {
    // unpack the region
    let { vertices } = region
    // set up my flags
    const only = vertices.length == 1
    const last = idx == vertices.length - 1
    // extract my vertex
    const vertex = vertices[idx]

    // build the form mutators
    // edit a vertex in-place
    const edit = (value) => {
        // adjust the pile
        vertices[idx] = value
        // and update the form
        update({ ...region, vertices })
        // all done
        return
    }
    // add a vertex between two others
    const insert = () => {
        // get the next entry; it is guaranteed to exist
        const next = vertices[idx + 1]
        // build the new entry; convert to number, interpolate, and back to string
        const newbie = {
            latitude: ((Number(vertex.latitude) + Number(next.latitude)) / 2).toString(),
            longitude: ((Number(vertex.longitude) + Number(next.longitude)) / 2).toString(),
        }
        // add it to the pile
        vertices.splice(idx + 1, 0, newbie)
        // and update the form
        update({ ...region, vertices })
        // all done
        return
    }
    // add an empty vertex
    const push = () => {
        // add an entry at the end
        vertices.push({ longitude: "", latitude: "" })
        // and update the form
        update({ ...region, vertices })
        // all done
        return
    }
    // delete a vertex
    const remove = () => {
        // adjust the pile
        vertices.splice(idx, 1)
        // and update the form
        update({ ...region, vertices })
        // all done
        return
    }

    // render
    return (
        <Box>
            <Longitude region={vertex} update={edit} />
            <SpacerBetween />
            <Latitude region={vertex} update={edit} />
            {!last && <Add update={insert} />}
            {last && vertex.longitude != "" && vertex.latitude != "" && <Add update={push} />}
            {!only && <Delete update={remove} />}
        </Box>
    )
}

// add a vertex
const Add = ({ update }) => {
    // build the button behaviors
    const behaviors = {
        onClick: update,
    }
    // render
    return (
        <Badge size={12} state="enabled" behaviors={behaviors} style={paintAdd}>
            <Plus />
        </Badge>
    )
}
// the delete action
const Delete = ({ update }) => {
    // build the button behaviors
    const behaviors = {
        onClick: update,
    }
    // render
    return (
        <Badge size={12} state="enabled" behaviors={behaviors} style={paintDelete}>
            <X />
        </Badge>
    )
}


// the container
const Box = styled.div`
    display: flex;
    align-items: end;
    font-family: inconsolata;
    height: 1.2em;
    margin: 0em;
    padding: 0.125rem 0.0rem;
`

// end of file
