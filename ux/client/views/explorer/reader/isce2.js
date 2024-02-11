// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect, EnabledConnect } from './buttons'
import { Name } from './name'
import { Product } from './product'
import { Shape } from './shape'
import { Type } from './type'
import { Form, Body, Field, Values, Error } from '../form'


// associate a ISCE2 reader with a given data product
export const ISCE2 = ({ view, setType, hide }) => {
    // error placeholder
    const [error, setError] = React.useState(null)
    // set up my state
    const [form, setForm] = React.useState({
        // the pyre name of the reader
        name: "",
        // the data product
        product: "",
        // its shape
        lines: "",
        samples: "",
    })
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
                [field]: value,
            }
            // hand it off
            return clone
        })
        // all done
        return
    }
    // set up the reader connector
    const connect = () => {
        // if there is already a pending operation
        if (isInFlight) {
            // skip this update
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                spec: {
                    reader: `isce2.${form.product}`,
                    name: form.name,
                    uri: view.reader.uri,
                    lines: form.lines,
                    samples: form.samples,
                    cell: null,
                }
            },
            updater: store => {
                // get the root field of the query result
                const payload = store.getRootField("connectReader")
                // ask for the new reader
                const reader = payload.getLinkedRecord("reader")
                // get the session manager
                const qed = store.get("QED")
                // get its connected archives
                const readers = qed.getLinkedRecords("readers")
                // add the new one to the pile
                qed.setLinkedRecords([...readers, reader], "readers")
                // all done
                return
            },
            // when done
            onCompleted: data => {
                // clear the error
                setError(null)
                // remove the form from view
                hide()
                // all done
                return
            },
            // if something went wrong
            onError: error => {
                // clear the form
                update("product", "")
                update("lines", "")
                update("samples", "")
                // and now record the error
                setError(error)
                // all done
                return
            }
        })
    }
    // build the handler that removes the form from view
    const cancel = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effect
        evt.preventDefault()
        // remove the view in my viewport from the pile
        hide()
        // all done
        return
    }
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
                    <Type value="isce2" update={setType} />
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
                <Product name="slc" rep="rslc" current={value} select={select} />
                <Product name="int" rep="int" current={value} select={select} />
                <Product name="unw" rep="unw" current={value} select={select} />
            </Values>
        </Field>
    )
}


// the mutation that associates a ISCE2 reader with a data product
const connectMutation = graphql`
    mutation isce2ReaderMutation($spec: ReaderInput!) {
        connectReader(spec: $spec) {
            reader {
                id
                name
                uri
                api
                selectors {
                    name
                    values
                }
                datasets {
                    name
                    datatype
                    selector {
                        name
                        value
                    }
                    channels
                    shape
                    origin
                    tile
                }
            }
        }
    }
`


// end of file
