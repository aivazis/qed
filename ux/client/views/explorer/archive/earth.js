// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useSetActiveView } from '../explorer/useSetActiveView'
// components
import { Busy } from './busy'
import { Panel } from './panel'
import { EnabledConnect, DisabledConnect, Cancel } from './buttons'
import { TypeSelector } from './type'
import { Form, Body, Error } from '../form'

// fields
import { Name } from './name'
import { Geo } from './geo'
import { Filters } from './filters'
// geographic region types
import { BBox } from './bbox'
import { Circle } from './circle'
import { Line } from './line'
import { Point } from './point'
import { Polygon } from './polygon'

// a earth access data archive
export const Earth = ({ view, setType, hide }) => {
    // error placeholder
    const [error, setError] = React.useState(null)
    // set up my state
    const [form, setForm] = React.useState({
        // the nickname
        name: "",
        // the filters
        filters: new Set(),
        // the type of region of interest
        geo: "",
        // bounding box
        bbox: { ne: { longitude: "", latitude: "" }, sw: { longitude: "", latitude: "" } },
        // point
        point: { longitude: "", latitude: "" },
        // circle
        circle: { longitude: "", latitude: "", radius: "" },
        // line
        line: {
            vertices: [],
        },
        // polygon
        polygon: {
            vertices: [],
        },
    })
    // get the view mutator
    const decorate = useSetActiveView()
    // build the mutation request
    const [request, isInFlight] = useMutation(connectMutation)
    // set up the state update
    const update = (field, value) => {
        // clear any errors
        setError(null)
        // replace my state
        setForm(old => {
            // with
            const clone = {
                // a copy of the old state
                ...old,
                // with the value of the given field replaced with the new one
                [field]: old[field] == value ? "" : value,
            }
            // hand it off
            return clone
        })
        // if the field is the archive nickname
        if (field === "name") {
            // update the uri of the archive in the current view
            view.archive.uri = `earth:${value}`
            // and set it
            decorate(view)
        }
        // all done
        return
    }
    // set up the archive connector
    const connect = () => {
        // if there is already a pending operation
        if (isInFlight) {
            // skip this update
            return
        }
        // otherwise, collect the current state
        const name = form.name
        // send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                name: `earth:${name}`,
                uri: `earth:${name}`,
                filters: [...form.filters],
                geo: form.geo,
                bbox: form.bbox,
                point: form.point,
                circle: form.circle,
                line: form.line,
                polygon: form.polygon,
            },
            // updater
            updater: store => {
                // get the root field of the query result
                const payload = store.getRootField("connectEarthAccessArchive")
                // if it's trivial
                if (!payload) {
                    // raise an issue
                    throw new Error("could not connect to the data archive")
                }
                // ask for the new archive
                const archive = payload.getLinkedRecord("archive")
                // get the session manager
                const qed = store.get("QED")
                // get its connected archives
                const archives = qed.getLinkedRecords("archives")
                // add the new one to the pile
                qed.setLinkedRecords([...archives, archive], "archives")
                // all done
                return
            },
            // when done
            onCompleted: data => {
                // clear the error
                setError(null)
                // remove the form from the view
                hide()
                // all done
                return
            },
            // if something went wrong
            onError: error => {
                // record the error
                setError([
                    `got: ${error}`,
                    `while connecting to the data archive '${name}'`,
                ])
                // all done
                return
            }
        })
    }
    // build a handler that removes the form from view
    const cancel = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // remove the view in my viewport from the pile
        hide()
        // all done
        return
    }
    // determine whether i have enough information to make the connection
    const ready = (
        !isInFlight &&
        form.name !== null && form.name.length
    )
    // use this to figure out which button to render
    const Connect = ready ? EnabledConnect : DisabledConnect

    // unpack the selected filters
    const geo = form.filters.has("geo")
    // resolve the geo search type
    const Region = form.geo === "" ? null : regionTypes[form.geo]

    // render
    return (
        <Panel>
            <Form>
                <Body>
                    <TypeSelector value="earth" update={setType} />
                    <Name value={form.name} update={update} />
                    <Filters value={form.filters} update={update} types={filterTypes} />
                    {geo && <Geo value={form.geo} update={update} types={regionTypes} />}
                    {geo && form.geo && <Region region={form[form.geo]} update={update} />}
                </Body>
            </Form>
            <Connect connect={connect} />
            {!isInFlight && <Cancel onClick={cancel}>cancel</Cancel>}
            {error && <Error errors={error} />}
            {isInFlight && <Busy />}
        </Panel >
    )
}


// the mutation that connects an earth access archive
const connectMutation = graphql`
    mutation earthArchiveMutation(
        $name: String!, $uri: String!, $filters: [String!]!,
        $geo: String,
        $bbox: GeoBBoxInput, $point: GeoVertexInput, $circle: GeoCircleInput,
        $line: GeoLineInput, $polygon: GeoPolygonInput
    ) {
        connectEarthAccessArchive(
            name: $name, uri: $uri,
            filters: $filters,
            geo: $geo, bbox: $bbox, point: $point, circle: $circle, line: $line, polygon: $polygon
            ) {
            archive {
                id
                name
                uri
                readers
            }
        }
    }
`

// the dispatch table with the supported filters
const filterTypes = {
    geo: Geo,
}

// the dispatch table with the supported geographic region types
const regionTypes = {
    bbox: BBox,
    point: Point,
    circle: Circle,
    line: Line,
    polygon: Polygon,
}


// end of file
