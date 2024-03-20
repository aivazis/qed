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
import { Type } from './type'
import { Form, Body, Field, Values, Error } from '../form'


// associate a NISAR reader with a given data product
export const NISAR = ({ view, setType, hide }) => {
    // preload the metadata query
    const [qref, getMetadata] = useProductMetadataLoader()
    // schedule the fetch; once, at mount time
    React.useEffect(() => {
        // variables
        const variables = {
            archive: view.reader.archive, module: "qed.readers.nisar", uri: view.reader.uri
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

const Spec = ({ qref, view, setType, hide }) => {
    // there is occasional magical trouble here; let's proceed carefully
    // extract the payload
    const payload = useQueryProductMetadata(qref)
    // unpack the product metadata
    const { uri, product } = payload
    // set up my state
    const [form, setForm] = React.useState({
        // the pyre name of the reader
        name: "",
        // the data product
        product,
    })
    // get the reader connection support
    const { error, update, makeConnector, cancel } = useConnectReader(setForm, hide)
    // build the payload
    const spec = {
        reader: `nisar.${form.product}`,
        name: form.name,
        uri,
        lines: null,
        samples: null,
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
                    <Type value="nisar" update={setType} readers={view.reader.readers} />
                    <Products value={form.product} update={update} />
                    <Name value={form.name} update={update} />
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
                <Product name="rslc" rep="rslc" current={value} select={select} />
                <Product name="rifg" rep="rifg" current={value} select={select} />
                <Product name="roff" rep="roff" current={value} select={select} />
                <Product name="runw" rep="runw" current={value} select={select} />
                <Product name="gslc" rep="gslc" current={value} select={select} />
                <Product name="goff" rep="goff" current={value} select={select} />
                <Product name="gunw" rep="gunw" current={value} select={select} />
                <Product name="gcov" rep="gcov" current={value} select={select} />
            </Values>
        </Field>
    )
}


// end of file
