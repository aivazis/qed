// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// hooks
import { useConnectReader } from './useConnectReader'
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect, EnabledConnect } from './buttons'
import { Type } from './type'
import { Name } from './name'
import { Form, Body, Error } from '../form'


// associate a GDAL reader with a given data product
export const GDAL = ({ view, setType, hide }) => {
    // set up my state
    const [form, setForm] = React.useState({
        // the pyre name of the reader
        name: "",
    })
    // get the reader connection support
    const { error, update, makeConnector, cancel } = useConnectReader(setForm, hide)
    // build the payload
    const spec = {
        reader: "native.gdal",
        name: form.name,
        uri: view.reader.uri,
        lines: null,
        samples: null,
        cell: null,
    }
    // use it to build the connector
    const connect = makeConnector(spec)
    // determine whether i have enough information to make the connection
    const ready = (
        form.name !== null && form.name.length
    )
    // figure out the state of the connect button
    const Connect = ready ? EnabledConnect : DisabledConnect
    // and render
    return (
        <Panel>
            <Form>
                <Body>
                    <Type value="gdal" update={setType} readers={view.reader.readers} />
                    <Name value={form.name} update={update} />
                </Body>
            </Form>
            <Connect connect={connect} />
            <Cancel onClick={cancel}>cancel</Cancel>
            {error && <Error>{error}</Error>}
        </Panel>
    )
}


// end of file
