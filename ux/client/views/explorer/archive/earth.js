// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useSetActiveView } from '../explorer/useSetActiveView'
import { connectArchiveUpdater, reconfigureArchiveUpdater } from '../archives/archiveListUpdaters'
// components
import { Busy } from './busy'
import { Panel } from './panel'
import { EnabledConnect, DisabledConnect, Cancel } from './buttons'
import { TypeSelector } from './type'
import { Form, Body, Error } from '../form'

// fields
import { Name } from './name'
import { useFetchArchiveNickname } from './useFetchArchiveNickname'
import { Count } from './count'
import { Collection } from './collection'
import { Granule } from './granule'
import { Geo } from './geo'
import { Filters } from './filters'
// time interval
import { When } from './when'
// geographic region types
import { BBox } from './bbox'
import { Circle } from './circle'
import { Line } from './line'
import { Point } from './point'
import { Polygon } from './polygon'

// a earth access data archive; the form connects a new one, or reconfigures {edit}
export const Earth = ({ view, edit = null, setType, hide }) => {
    // error placeholder
    const [error, setError] = React.useState(null)
    // set up my state, from what the archive being reconfigured says about itself, if any
    const [form, setForm] = React.useState(() => describe(edit))
    // get the view mutator
    const decorate = useSetActiveView()
    // build the mutation request: a new archive gets connected, an existing one reconfigured
    const [request, isInFlight] = useMutation(edit === null ? connectMutation : reconfigureMutation)
    // ask the server for a nickname, once the form names a collection; the location of the
    // archive is made from its name, so the collection is all there is to go on
    const suggestion = useFetchArchiveNickname({
        // of my kind
        type: "earth",
        // with no location yet, and nothing to go on until there is a collection
        uri: form.collection.shortName ? "earth:" : "",
        // for the granules of the collection
        collection: form.collection.shortName || null,
        // and the name of the archive being reconfigured, which is its own to keep
        current: edit?.name ?? null,
    })
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
                input: {
                    // the payload: an archive is named after its nickname, and its location is made
                    // from its name; an existing one is found by the location it has now, keeps
                    // its name if the user left the nickname alone, and is replaced by a new one
                    // if the user renamed it
                    ...(edit === null
                        ? { name: `earth:${name}`, uri: `earth:${name}` }
                        : name === describe(edit).name
                            ? { name: edit.name, uri: edit.uri, location: edit.uri }
                            : { name: `earth:${name}`, uri: edit.uri, location: `earth:${name}` }),
                    count: form.count,
                    collection: form.collection,
                    granule: form.granule,
                    filters: [...form.filters],
                    when: form.when,
                    geo: form.geo,
                    bbox: form.bbox,
                    point: form.point,
                    circle: form.circle,
                    line: form.line,
                    polygon: form.polygon,
                }
            },
            // updater: a new archive joins the pile, an existing one takes its own old place
            updater: (edit === null)
                ? connectArchiveUpdater("connectEarthAccessArchive")
                : reconfigureArchiveUpdater(edit.uri, "reconfigureEarthAccessArchive"),
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
                    `while ${edit === null ? "connecting" : "reconfiguring"} the data archive '${name}'`,
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
        form.name.length > 0
    )
    // use this to figure out which button to render
    const Connect = ready ? EnabledConnect : DisabledConnect

    // unpack the selected filters
    const geo = form.filters.has("geo")
    const when = form.filters.has("when")
    // resolve the geo search type
    const Region = form.geo === "" ? null : regionTypes[form.geo]

    // render
    return (
        <Panel>
            <Form>
                <Body>
                    <TypeSelector value="earth" update={setType} />
                    <Count form={form} update={update} />
                    <Collection form={form} update={update} />
                    <Granule form={form} update={update} />
                    <Filters value={form.filters} update={update} types={filterTypes} />
                    {when && <When interval={form.when} update={update} />}
                    {geo && <Geo value={form.geo} update={update} types={regionTypes} />}
                    {geo && form.geo && <Region region={form[form.geo]} update={update} />}
                    <Name value={form.name} suggestion={suggestion} update={update} />
                </Body>
            </Form>
            <Connect connect={connect} label={edit === null ? "connect" : "update"} />
            {!isInFlight && <Cancel onClick={cancel}>cancel</Cancel>}
            {error && <Error errors={error} />}
            {isInFlight && <Busy />}
        </Panel >
    )
}


// the mutation that connects an earth access archive
// the state of a blank form
const blank = () => ({
    // the nickname
    name: "",
    // limit on the number of results
    count: "",
    // data collection
    collection: { conceptId: "", shortName: "" },
    // granule
    granule: { pattern: "" },
    // the filters
    filters: new Set(),
    // a time interval
    when: { begin: "", end: "" },
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

// the state of the form that describes {archive}, or of a blank one when there is no archive
const describe = archive => {
    // start from a blank form
    const form = blank()
    // with no archive
    if (archive === null) {
        // that is all
        return form
    }
    // the query of the archive
    const query = archive.earth
    // the form holds text, and an unset trait shows as an empty field
    const text = value => (value === null || value === undefined) ? "" : `${value}`
    // the vertices of a line or a polygon, as the form holds them
    const vertices = pairs => pairs.map(([longitude, latitude]) => ({
        // each one a longitude
        longitude: text(longitude),
        // and a latitude
        latitude: text(latitude),
    }))
    // the kind of region of interest, if any
    const geo = ["bbox", "point", "circle", "line", "polygon"].find(kind => query[kind]) ?? ""
    // the filters in force: a time window, when either end is set
    const filters = new Set(query.begin || query.end ? ["when"] : [])
    // and a region, when there is one
    if (geo) filters.add("geo")
    // fill the form
    return {
        // starting from the blank one
        ...form,
        // the nickname, which is the name of the archive without its kind
        name: archive.name.replace(/^earth:/, ""),
        // the cap on the number of granules
        count: text(query.count),
        // the collection
        collection: { conceptId: text(query.conceptId), shortName: text(query.collection) },
        // the pattern for the granule names
        granule: { pattern: text(query.pattern) },
        // the filters in force
        filters,
        // the time window
        when: { begin: text(query.begin), end: text(query.end) },
        // the kind of region
        geo,
        // the bounding box, as (west, south, east, north)
        bbox: query.bbox ? {
            ne: { longitude: text(query.bbox[2]), latitude: text(query.bbox[3]) },
            sw: { longitude: text(query.bbox[0]), latitude: text(query.bbox[1]) },
        } : form.bbox,
        // the point
        point: query.point
            ? { longitude: text(query.point[0]), latitude: text(query.point[1]) }
            : form.point,
        // the circle
        circle: query.circle ? {
            longitude: text(query.circle[0]),
            latitude: text(query.circle[1]),
            radius: text(query.circle[2]),
        } : form.circle,
        // the line
        line: query.line ? { vertices: vertices(query.line) } : form.line,
        // and the polygon
        polygon: query.polygon ? { vertices: vertices(query.polygon) } : form.polygon,
    }
}


const connectMutation = graphql`
    mutation earthArchiveMutation($input: ConnectEarthAccessArchiveInput!) {
        connectEarthAccessArchive(input: $input) {
            archive {
                id
                name
                type
                uri
                credentials {
                    name
                    value
                }
                earth {
                    collection conceptId pattern count begin end
                    bbox point circle line polygon
                }
                readers
                expanded
                pending
                error
                hits
                dirty
                items {
                    id
                    name
                    uri
                    isFolder
                    parent
                    expanded
                    pending
                    error
                }
            }
        }
    }
`

// the dispatch table with the supported filters
const filterTypes = {
    when: When,
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


// the mutation that replaces the query of an earth access archive
const reconfigureMutation = graphql`
    mutation earthArchiveReconfigureMutation($input: ReconfigureEarthAccessArchiveInput!) {
        reconfigureEarthAccessArchive(input: $input) {
            archive {
                id
                name
                type
                uri
                credentials {
                    name
                    value
                }
                earth {
                    collection conceptId pattern count begin end
                    bbox point circle line polygon
                }
                readers
                expanded
                pending
                error
                hits
                dirty
                items {
                    id
                    name
                    uri
                    isFolder
                    parent
                    expanded
                    pending
                    error
                }
            }
        }
    }
`


// end of file
