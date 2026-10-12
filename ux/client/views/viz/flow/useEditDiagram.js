// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// add factories to the pipeline {diagram} with the given id, pin them in place, and remove them
export const useEditDiagram = diagram => {
    // the mutations
    const [commitAdd] = useMutation(useEditDiagramAddMutation)
    const [commitConfigure] = useMutation(useEditDiagramConfigureMutation)
    const [commitInstantiate] = useMutation(useEditDiagramInstantiateMutation)
    const [commitInvoke] = useMutation(useEditDiagramInvokeMutation)
    const [commitPin] = useMutation(useEditDiagramPinMutation)
    const [commitRemove] = useMutation(useEditDiagramRemoveMutation)
    // report a failure
    const complain = (what, errors) => {
        // show me
        console.log(`viz.flow.useEditDiagram:`)
        console.group()
        console.log(`ERROR while ${what}`)
        console.log(errors)
        console.groupEnd()
        // all done
        return
    }
    // place a factory of {family} at {x, y, z}
    const add = ({ family, x, y, z = 0 }) => {
        // send the request
        commitAdd({
            // the payload
            variables: { input: { diagram, family, x, y, z } },
            // on failure, report
            onError: errors => complain(`adding a ${family} at (${x}, ${y}, ${z})`, errors),
        })
        // all done
        return
    }
    // pin the factory with {id} to the class of {family}, or back to its protocol without one
    const pin = ({ id, family = null }) => {
        // send the request
        commitPin({
            // the payload
            variables: { input: { diagram, node: id, family } },
            // on failure, report
            onError: errors => complain(`pinning ${id} to ${family ?? "its protocol"}`, errors),
        })
        // all done
        return
    }
    // set the setting {trait} of the factory with {id} to {value}, given as text; a factory pinned
    // to a class becomes an instance of it called {name}; {done} hears the reason the server
    // refused, or nothing when the change was made
    const configure = ({ id, trait, value, name = null }, done) => {
        // send the request
        commitConfigure({
            // the payload
            variables: { input: { diagram, node: id, trait, value, name } },
            // when the answer arrives, pass on the verdict
            onCompleted: response => done?.(response?.diagramConfigure?.error ?? null),
            // on failure, report, and say so
            onError: errors => {
                // report
                complain(`setting ${trait} of ${id} to ${value}`, errors)
                // and say so
                done?.("the server could not be reached")
            },
        })
        // all done
        return
    }
    // pin the factory with {id} to a new instance of the class of {family}, or of the class it is
    // pinned to without one, called {name} if it is not empty; {done} hears the reason the server
    // refused, or nothing when the pin was made
    const instantiate = ({ id, family = null, name = null }, done) => {
        // send the request
        commitInstantiate({
            // the payload
            variables: { input: { diagram, node: id, family, name } },
            // when the answer arrives, pass on the verdict
            onCompleted: response => done?.(response?.diagramInstantiate?.error ?? null),
            // on failure, report, and say so
            onError: errors => {
                // report
                complain(`making a new ${family ?? "instance"} for ${id}`, errors)
                // and say so
                done?.("the server could not be reached")
            },
        })
        // all done
        return
    }
    // invoke {method} of the instance the factory with {id} is pinned to; {done} hears what it
    // returned and the reason the server refused, or the call failed
    const invoke = ({ id, method }, done) => {
        // send the request
        commitInvoke({
            // the payload
            variables: { input: { diagram, node: id, method } },
            // when the answer arrives, pass on the outcome
            onCompleted: response => done?.({
                result: response?.diagramInvoke?.result ?? null,
                error: response?.diagramInvoke?.error ?? null,
            }),
            // on failure, report, and say so
            onError: errors => {
                // report
                complain(`invoking ${method} of ${id}`, errors)
                // and say so
                done?.({ result: null, error: "the server could not be reached" })
            },
        })
        // all done
        return
    }
    // remove the factory with {id}
    const remove = id => {
        // send the request
        commitRemove({
            // the payload
            variables: { input: { diagram, node: id } },
            // on failure, report
            onError: errors => complain(`removing ${id}`, errors),
        })
        // all done
        return
    }
    // publish
    return { add, configure, instantiate, invoke, pin, remove }
}


// the mutations; the responses carry the whole diagram, which replaces the one on screen
const useEditDiagramAddMutation = graphql`
    mutation useEditDiagramAddMutation($input: DiagramAddInput!) {
        diagramAdd(input: $input) {
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

const useEditDiagramConfigureMutation = graphql`
    mutation useEditDiagramConfigureMutation($input: DiagramConfigureInput!) {
        diagramConfigure(input: $input) {
            error
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

const useEditDiagramInvokeMutation = graphql`
    mutation useEditDiagramInvokeMutation($input: DiagramInvokeInput!) {
        diagramInvoke(input: $input) {
            result
            error
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

const useEditDiagramInstantiateMutation = graphql`
    mutation useEditDiagramInstantiateMutation($input: DiagramInstantiateInput!) {
        diagramInstantiate(input: $input) {
            error
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

const useEditDiagramPinMutation = graphql`
    mutation useEditDiagramPinMutation($input: DiagramPinInput!) {
        diagramPin(input: $input) {
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

const useEditDiagramRemoveMutation = graphql`
    mutation useEditDiagramRemoveMutation($input: DiagramRemoveInput!) {
        diagramRemove(input: $input) {
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`


// end of file
