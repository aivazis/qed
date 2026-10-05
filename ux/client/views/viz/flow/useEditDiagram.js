// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// project
// the active viewport, whose pipeline the diagram shows
import { useViewports } from '../viz/useViewports'


// add factories to the pipeline diagram of the active view, and remove them
export const useEditDiagram = () => {
    // the active viewport
    const { activeViewport } = useViewports()
    // the two mutations
    const [commitAdd] = useMutation(useEditDiagramAddMutation)
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
            variables: { input: { viewport: activeViewport, family, x, y, z } },
            // on failure, report
            onError: errors => complain(`adding a ${family} at (${x}, ${y}, ${z})`, errors),
        })
        // all done
        return
    }
    // remove the factory with {id}
    const remove = id => {
        // send the request
        commitRemove({
            // the payload
            variables: { input: { viewport: activeViewport, node: id } },
            // on failure, report
            onError: errors => complain(`removing ${id}`, errors),
        })
        // all done
        return
    }
    // publish
    return { add, remove }
}


// the mutations; the responses carry the whole diagram, which replaces the one on screen
const useEditDiagramAddMutation = graphql`
    mutation useEditDiagramAddMutation($input: ViewDiagramAddInput!) {
        viewDiagramAdd(input: $input) {
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

const useEditDiagramRemoveMutation = graphql`
    mutation useEditDiagramRemoveMutation($input: ViewDiagramRemoveInput!) {
        viewDiagramRemove(input: $input) {
            diagram {
                id
                ...contentsFlowDiagramFragment
            }
        }
    }
`

// end of file
