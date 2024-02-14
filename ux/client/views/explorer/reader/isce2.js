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
import { Name } from './name'
import { Product } from './product'
import { Shape } from './shape'
import { Type } from './type'
import { Form, Body, Field, Values, Error } from '../form'


// associate an ISCE2 reader with a given data product
export const ISCE2 = ({ view, setType, hide }) => {
    // preload the metadata query
    const [qref, getMetadata] = useProductMetadataLoader()
    // schedule the fetch; once, at mount time
    React.useEffect(() => {
        // variables
        const variables = {
            archive: view.reader.archive, module: "qed.readers.isce2", uri: view.reader.uri
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
        slc: 8,
        int: 8,
        unw: 8,
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
            name: "",
            // the data product
            product,
            // its shape
            lines, samples,
            // the dataset size
            bytes,
            // the number of cells,
            cells: size,
            // the type map
            sizeof,
        }
    })
    // get the reader connection support
    const { error, update, makeConnector, cancel } = useConnectReader(setForm, hide)
    // build the payload
    const spec = {
        reader: `isce2.${form.product}`,
        name: form.name,
        uri,
        lines: form.lines,
        samples: form.samples,
        cell: null,
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
                    <Type value="isce2" update={setType} readers={view.reader.readers} />
                    <Products value={form.product} update={update} />
                    <Name value={form.name} update={update} />
                    <Shape lines={form.lines} samples={form.samples} update={update} />
                </Body>
            </Form>
            <Connect connect={connect} />
            <Cancel onClick={cancel}>cancel</Cancel>
            {error && <Error>{error}</Error>}
        </Panel>
    )
}


// the reader type selector
export const Products = ({ value, update }) => {
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
        <Field name="product" value={value} tip="select the reader type">
            <Values>
                <Product name="slc" rep="slc" current={value} select={select} />
                <Product name="int" rep="int" current={value} select={select} />
                <Product name="unw" rep="unw" current={value} select={select} />
            </Values>
        </Field>
    )
}


// end of file
