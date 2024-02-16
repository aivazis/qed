// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// hooks
import { useConnectReader } from './useConnectReader'
import { useProductMetadataLoader, useQueryProductMetadata } from './useFetchProductMetadata'
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect, EnabledConnect } from './buttons'
import { Guesses } from './guesses'
import { Name } from './name'
import { Preview } from './preview'
import { Product } from './product'
import { Shape } from './shape'
import { Type } from './type'
import { Form, Body, Field, Values, Error } from '../form'


// associate a native reader with a given data product
export const Native = ({ view, setType, hide }) => {
    // preload the metadata query
    const [qref, getMetadata] = useProductMetadataLoader()
    // schedule the fetch; once, at mount time
    React.useEffect(() => {
        // variables
        const variables = {
            archive: view.reader.archive, module: "qed.readers.native", uri: view.reader.uri
        }
        // options
        const options = { fetchPolicy: "store-and-network" }
        // fetch
        getMetadata(variables, options)
        // all done
        return
    }, [])
    // if the data is not available yet
    if (qref === null) {
        // bail
        return
    }

    // render
    return (
        <Spec qref={qref} view={view} setType={setType} hide={hide} />
    )
}


// the panel
const Spec = ({ qref, view, setType, hide }) => {
    // unpack the product metadata
    const {
        uri, product, bytes, cells, shape,
    } = useQueryProductMetadata(qref)
    // the map of product types to their data type size
    const sizeof = {
        char: 1,
        int16: 2,
        int32: 4,
        int64: 8,
        real32: 4,
        real64: 8,
        complex64: 8,
        complex128: 16,
    }
    // set up my state
    const [form, setForm] = React.useState(() => {
        // unpack the shape
        const [lines, samples] = shape ?? ["", ""]
        // the size of the data product, in cells
        let size = cells
        // if it's trivial and we have enough information to compute it
        if (size == null && product) {
            // as the size in bytes divided by the data type size
            size = bytes / sizeof[product]
        }
        // build the form initializer and return it
        return {
            // the pyre name of the reader
            name: "",
            // the data product
            product,
            // its shape
            lines: lines.toString(), samples: samples.toString(),
            // the dataset size
            bytes,
            // the number of cells,
            cells: size?.toString(),
            // the type map
            sizeof,
            // the max aspect ratio for shape guesses
            aspect: "5",
        }
    })
    // get the reader connection support
    const { error, update, makeConnector, cancel } = useConnectReader(setForm, hide)
    // build the payload
    const spec = {
        reader: "native.flat",
        name: form.name,
        uri,
        lines: form.lines.toString(),
        samples: form.samples.toString(),
        cell: form.product,
    }
    // use it to build the connector
    const connect = makeConnector(spec)
    // determine whether i have enough information to make the connection
    const ready = (
        form.name !== null && form.name.length &&
        form.product !== null && form.product.length
    )
    // figure out the state of the connect button
    const Connect = ready ? EnabledConnect : DisabledConnect
    // and render
    return (
        <Panel>
            <Form>
                <Body>
                    <Type value="native" update={setType} readers={view.reader.readers} />
                    <Name value={form.name} update={update} />
                    <Cells value={form.product} update={update} />
                    <Shape lines={form.lines} samples={form.samples} update={update} />
                    {form.cells &&
                        <Guesses
                            size={form.cells} aspect={form.aspect}
                            lines={form.lines} samples={form.samples}
                            update={update} />
                    }
                </Body>
            </Form>
            <Connect connect={connect} />
            <Cancel onClick={cancel}>cancel</Cancel>
            {error && <Error>{error}</Error>}
            {form.lines && form.samples &&
                <Preview
                    reader="native.flat" uri={uri}
                    lines={form.lines} samples={form.samples} cell={form.product} />
            }
        </Panel>
    )
}


// the data type selector
export const Cells = ({ value, update }) => {
    // make a handler that sets the reader type
    const select = type => {
        // build the selector
        return () => {
            // update the form state
            update("product", type)
            // all done
            return
        }
    }
    // render
    return (
        <Field name="data type" value={value} tip="select the reader type">
            <Values>
                <Product name="char" rep="char" current={value} select={select} />
                <Product name="int16" rep="int16" current={value} select={select} />
                <Product name="int32" rep="int32" current={value} select={select} />
                <Product name="int64" rep="int64" current={value} select={select} />
                <Product name="real32" rep="real32" current={value} select={select} />
                <Product name="real64" rep="real64" current={value} select={select} />
                <Product name="complex64" rep="complex64" current={value} select={select} />
                <Product name="complex128" rep="complex128" current={value} select={select} />
            </Values>
        </Field>
    )
}


// end of file
