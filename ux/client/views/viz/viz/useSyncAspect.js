// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'
// hooks
import { useSetPixelPath } from './useSetPixelPath'

// build a handler that toggles the specified entry in the sync table
export const useSyncAspect = () => {
    // grab the sync table setter
    const { setSynced, setMeasureLayer } = React.useContext(Context)
    // and the handler that copies pixel paths
    const { copy } = useSetPixelPath()

    // make a handler factory and return it
    const toggle = (viewport, aspect) => () => {
        // check that {toggle} is being applied to the correct aspect
        if (aspect === "offset") {
            // if not, complain, because this is a bug
            console.log(`error: sync aspect toggle applied to ${aspect}`)
            // and bail
            return
        }
        // the new value of the aspect
        let value
        // and a path synced viewport
        let src
        // update the sync table
        setSynced(old => {
            // remember the new value
            value = !old[viewport][aspect]
            // find a viewport that is path synced
            src = old.findIndex(port => port.path)
            // make a copy of the old state
            const clone = old.map(sync => ({ ...sync }))
            // and toggle {aspect} for {viewport}
            clone[viewport][aspect] = value
            // hand off the new entry
            return clone
        })
        // if we are turning on path sync
        if (aspect === "path" && value === true) {
            // turn on the measure layer for this viewport
            setMeasureLayer(old => {
                // make a copy
                const pile = [...old]
                // adjust the entry for this viewport
                pile[viewport] = true
                // and return the bew pile
                return pile
            })
            // if we have a path synced viewport
            if (src >= 0) {
                // copy its pixel path
                copy(src, viewport)
            }
        }
        // all done
        return
    }

    // make a handler factory and return it
    const update = (viewport, aspect) => value => {
        // a path synced viewport
        let src
        // update the sync table
        setSynced(old => {
            // find a viewport that is path synced and save it, in case we are updating {path}
            // into myself
            src = old.findIndex(port => port.path)
            // make a copy of the old state
            const clone = old.map(sync => ({ ...sync }))
            // force {aspect} for {viewport} to {value}
            clone[viewport][aspect] = value
            // and return the new pile
            return clone
        })
        // if we are turning on path sync
        if (aspect === "path" && value === true) {
            // turn on the measure layer for this viewport
            setMeasureLayer(old => {
                // make a copy
                const pile = [...old]
                // adjust the entry for this viewport
                pile[viewport] = true
                // and return the bew pile
                return pile
            })
            // if we have a path synced viewport
            if (src >= 0) {
                // copy its pixel path
                copy(src, viewport)
            }
        }
        // all done
        return
    }

    // make a handler that forces the aspect state of a viewport to all others
    const force = (viewport, aspect) => () => {
        // the new value of the aspect
        let value
        // the set of viewports whose measure layer must be turned on
        let measured = []
        // and a path synced viewport
        let src = -1
        // update the sync table
        setSynced(old => {
            // get the state of the opinionated viewport
            value = old[viewport][aspect]
            // check whether the entire table shares this value
            const consensus = old.every(entry => entry[aspect] == value)
            // if we have consensus
            if (consensus) {
                // toggle
                value = !value
            }
            // if we are path syncing
            if (aspect === "path") {
                // find a viewport that is path synced and save it, in case we are updating {path}
                src = old.findIndex(port => port.path)
                // if there isn't one
                if (src < 0) {
                    // use the active viewport
                    src = viewport
                }
            }
            // if there were no path synced
            // make a copy of the old state and force the new {aspect} value on everybody
            return old.map((entry, port) => {
                // make a copy of the entry
                const clone = {
                    channel: entry.channel,
                    zoom: entry.zoom,
                    scroll: entry.scroll,
                    path: entry.path,
                    offset: { ...entry.offset },
                    // and override the specified aspect
                    [aspect]: value
                }
                // if we are turning on {path} syncing and this entry wasn't synced before
                if (aspect === "path" && value === true && entry.path == false) {
                    // add it to the pile of viewports whose measured layer must be turned on
                    measured.push(port)
                }
                // hand off the new pile
                return clone
            })
        })
        // if we are turning on path sync
        if (aspect === "path" && value === true) {
            // turn on the measure layer for this viewport
            setMeasureLayer(old => {
                // make a copy
                const pile = [...old]
                // adjust the entry for all viewports on the {measure} pile
                measured.forEach(port => {
                    // by turning on their measured layer
                    pile[port] = true
                    // all done
                    return
                })
                // and return the bew pile
                return pile
            })
            // go through all ports that were previously not path synced
            measured.forEach(port => {
                // and adjust their path
                copy(src, port)
                // all done
                return
            })
        }
        // all done
        return
    }

    // all done
    return { toggle, update, force }
}


// end of file
