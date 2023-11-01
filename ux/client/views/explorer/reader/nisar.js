// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect, EnabledConnect } from './buttons'
import { Type } from './type'
import { Name } from './name'
import { Form, Body, Field, Values, enumValue } from '../form'


// associate a NISAR reader with a given data product
export const NISAR = ({ view, setType, hide }) => {
    // set up my state
    const [form, setForm] = React.useState({
        // the pyre name of the reader
        name: "",
        // the data product
        product: "",
    })
    // build the mutation request
    const [request, isInFlight] = useMutation(connectMutation)
    // set up the state update
    const update = (field, value) => {
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
                reader: `nisar.${form.product}`,
                name: form.name,
                uri: view.reader.uri,
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
                // show me
                console.log(data)
                // remove the form from view
                hide()
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
                    <Type value="nisar" update={setType} />
                    <Products value={form.product} update={update} />
                    <Name value={form.name} update={update} />
                </Body>
            </Form>
            <Connect connect={connect} />
            <Cancel onClick={cancel}>cancel</Cancel>
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
                <Product name="gunw" rep="gunw" current={value} select={select} />
                <Product name="gcov" rep="gcov" current={value} select={select} />
            </Values>
        </Field>
    )
}


// the product type field
const Product = ({ name, rep, current, select }) => {
    // assemble the behaviors
    const behaviors = {
        onClick: select(rep)
    }
    // deduce my state
    const state = current === rep ? "selected" : "enabled"
    // pick a field selector based on my state
    const Selector = enumValue(state)
    // and render it
    return (
        <Selector {...behaviors}>
            {name}
        </Selector>
    )
}


// the mutation that associates a NISAR reader with a data product
const connectMutation = graphql`
    mutation nisarReaderMutation($reader: String!, $name: String!, $uri: String!) {
        connectReader(reader: $reader, name: $name, uri: $uri) {
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
