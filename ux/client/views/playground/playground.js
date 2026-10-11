// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// hooks
import { useActivityPanel } from '~/views/main'
// widgets
import { Flex, Header, Tray } from '~/widgets'
// the canvas, the palette, and the description of the picked factory
import { Canvas, Note, Palette, Picked } from '~/views/viz'
// paint
import styles from '~/views/viz/viz/styles'

// local
// the tab over the canvas
import { Tab } from './tab'
// how every client looks at the playground
import { usePlaygroundView } from './usePlaygroundView'


// a pipeline diagram that belongs to no view, where factories can be placed, moved, and wired
// together freely, next to a panel with the factories on offer
export const Playground = ({ qed }) => {
    // the state of the activity panel
    const { activityPanel } = useActivityPanel()
    // unpack the diagram, the factories on offer, and how every client looks at them
    const { playground, catalog, playgroundView } = useFragment(playgroundGetDiagramFragment, qed)
    // the way the diagram is drawn: flat, or isometric, turned by quarter turns, seen from above
    // or below, and where the cameras look; the server keeps it, so every client draws it the
    // same way
    const { kind, azimuth, below, trays: open, camera } = playgroundView
    // assemble it
    const view = { kind, azimuth, below }
    // the requests that change it
    const { project, point, tray } = usePlaygroundView()
    // every change made here hands the keys back to the canvas, since the click that made it took
    // them away; a change made by another client leaves the focus where it is
    const [focus, setFocus] = React.useState(0)
    // change some of the view
    const adjust = change => {
        // ask the server
        project({ ...view, ...change })
        // and give the canvas the keys back
        setFocus(old => old + 1)
        // all done
        return
    }
    // the trays of my panel are open and closed for every client
    const trays = {
        // whether the tray called {name} is open
        isOpen: name => open.includes(name),
        // the handler that opens or closes it
        toggle: name => expanded => tray(name, expanded),
    }
    // the panel paint, hidden along with the activity panel
    const panelPaint = {
        ...styles.activityPanels,
        panel: { ...styles.activityPanels.panel, display: activityPanel ? "flex" : "none" },
    }
    // render
    return (
        <Flex.Box direction="row" style={styles.flex}>
            {/* the factories on offer, and the description of the picked one */}
            <Flex.Panel min={350} style={panelPaint}>
                <Panel data-qed-panel="playground">
                    {/* the title of the panel */}
                    <Header title="pipeline playground" />
                    {/* the factories on offer, one tray per protocol */}
                    <Palette catalog={catalog} trays={trays} />
                    {/* the products, which will hold the datasets */}
                    <Tray title="products" scale={0.5} data-qed-palette="products"
                        expanded={trays.isOpen("products")} onToggle={trays.toggle("products")}>
                        <Note>the datasets of the readers will appear here</Note>
                    </Tray>
                    {/* the pipelines the user designed */}
                    <Tray title="designs" scale={0.5} data-qed-palette="designs"
                        expanded={trays.isOpen("designs")} onToggle={trays.toggle("designs")}>
                        <Note>the pipelines you design will appear here</Note>
                    </Tray>
                    {/* the description of the factory picked on the diagram */}
                    <Picked diagram={playground} trays={trays} />
                </Panel>
            </Flex.Panel>
            {/* the diagram, under a tab with the choices of how to look at it */}
            <Flex.Panel auto={true} style={styles.flex}>
                <Viewport>
                    <Tab view={view} adjust={adjust} />
                    <Canvas diagram={playground} view={view} focusOn={focus}
                        camera={camera} onCamera={point} />
                </Viewport>
            </Flex.Panel>
        </Flex.Box>
    )
}


// the viewport: the tab over the canvas
const Viewport = styled.div`
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    min-width: 0;
    min-height: 0;
`


// the container of the panel
const Panel = styled.div`
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
`


// my fragment
const playgroundGetDiagramFragment = graphql`
    fragment playgroundGetDiagramFragment on QED {
        # the factories on offer
        catalog {
            family
            name
            entries {
                family
                name
                level
                doc
                inputs
                outputs
            }
        }
        # how every client looks at it
        playgroundView {
            id
            kind
            azimuth
            below
            trays
            camera { x y z }
        }
        # the diagram
        playground {
            id
            # whether its structure can change
            editable
            # what the canvas draws
            ...canvasFlowDiagramFragment
            # and what the inspector shows of its factories
            factories {
                id
                family
                doc
                traits {
                    name
                    kind
                    type
                    value
                    default
                    doc
                }
            }
        }
    }
`


// end of file
