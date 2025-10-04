// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { Longitude } from './longitude'
import { Latitude } from './latitude'
import { Field, Value, SpacerBetween } from '../form'


// collect the coordinates of a polygon of interest
export const BBox = ({ region, update }) => {
    // unpack the region
    const { ne, sw } = region
    // validate my contents
    const good = (
        // check the north east corner
        ne.longitude !== "" & ne.latitude !== "" &&
        // and the south west corner
        sw.longitude !== "" && sw.latitude !== ""
    )
    // convert into a mark
    const ok = good ? "ok" : ""
    // specialize the form update
    // for the north-east corner
    const updateNE = ne => {
        // adjust my region
        const bbox = { ...region, ne }
        // and update the form
        update("bbox", bbox)
        // all done
        return
    }
    // for the south-west corner
    const updateSW = sw => {
        // adjust my region
        const bbox = { ...region, sw }
        // and update the form
        update("bbox", bbox)
        // all done
        return
    }

    // render
    return (
        <Field name="bbox" value={ok} tip="the bounding box of a region">
            <Value>
                <Title />
                <EntryBox>
                    <Info>SW</Info>
                    <SpacerBetween />
                    <Longitude region={ne} update={updateNE} />
                    <SpacerBetween />
                    <Latitude region={ne} update={updateNE} />
                </EntryBox>
                <EntryBox>
                    <Info>NE</Info>
                    <SpacerBetween />
                    <Longitude region={sw} update={updateSW} />
                    <SpacerBetween />
                    <Latitude region={sw} update={updateSW} />
                </EntryBox>
            </Value>
        </Field>
    )
}


// the table title
const Title = () => {
    return (
        <TitleBox>
            <Info />
            <SpacerBetween />
            <Header>longitude</Header>
            <SpacerBetween />
            <Header>latitude</Header>
        </TitleBox>
    )
}

// the containers
const TitleBox = styled.div`
    display: flex;
    align-items: end;
    font-family: rubik-light;
    height: 1.2em;
    margin: 0rem;
    padding: 0.0rem 0.0rem;
`

const EntryBox = styled.div`
    display: flex;
    align-items: end;
    height: 1.2em;
    margin: 0rem;
    padding: 0.125rem 0.0rem;
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
// entries
const Info = styled.span`
    display: inline-block;
    width: 2.0em;
    text-align: end;
    vertical-align: bottom;
    padding: 0.0rem 0.0 0.0rem 0.0rem;
    margin: 0.0rem 0.0rem 0.0rem 0.0rem;
    cursor: default;
`


// end of file
