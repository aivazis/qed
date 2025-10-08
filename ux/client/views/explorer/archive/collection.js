// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { Field, Values, EnabledInput } from '../form'


// information about a data collection
export const Collection = ({ form, update }) => {
    // unpack the collection
    const { conceptId, shortName } = form.collection
    // validate my contents
    const ok = (conceptId !== "" || shortName !== "") ? "ok" : ""
    // render
    return (
        <Field
            name="collection" value={ok}
            tip="the collection of data product; required when filtering by region"
        >
            <Values>
                <Box>
                    <Spacer title="the data collection name">name:</Spacer>
                    <Name form={form} update={update} />
                </Box>
                <Box>
                    <Spacer title="the data collection concept id">concept id:</Spacer>
                    <Concept form={form} update={update} />
                </Box>
            </Values >
        </Field>
    )
}


// container
const Box = styled.div`
`

// header
const Spacer = styled.span`
    display: inline-block;
    width: 5.0rem;
    text-align: end;
    padding: 0.0rem 0.25rem 0.25rem 0.0rem;
`


// data entry
const Entry = styled(EnabledInput)`
    width: 12.0rem;
`

// the collection name
const Name = ({ form, update }) => {
    // specialize the update
    const setName = evt => {
        // get the value
        const shortName = evt.target.value.toUpperCase()
        // build the new collection
        const collection = { ...form.collection, shortName }
        // and update the form
        update("collection", collection)
        // all done
        return
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setName
    }
    // render
    return (
        <Entry type="text" value={form.collection.shortName} {...behaviors} />
    )
}

// the data collection concept id
const Concept = ({ form, update }) => {
    // specialize the update
    const setConcept = evt => {
        // get the value
        const conceptId = evt.target.value.toUpperCase()
        // build the new collection
        const collection = { ...form.collection, conceptId }
        // and update the form
        update("collection", collection)
        // all done
        return
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setConcept
    }
    // render
    return (
        <Entry type="text" value={form.collection.conceptId} {...behaviors} />
    )
}


// end of file
