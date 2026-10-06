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


// a pipeline diagram that belongs to no view, where factories can be placed, moved, and wired
// together freely, next to a panel with the factories on offer
export const Playground = ({ qed }) => {
    // the state of the activity panel
    const { activityPanel } = useActivityPanel()
    // unpack the diagram and the factories on offer
    const { playground, catalog } = useFragment(playgroundGetDiagramFragment, qed)
    // the way the diagram is drawn: flat, or isometric, turned by quarter turns, seen from above
    // or below
    const [view, setView] = React.useState({ kind: "flat", azimuth: 0, below: false })
    // change some of it
    const adjust = change => setView(old => ({ ...old, ...change }))
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
                    <Palette catalog={catalog} />
                    {/* the products, which will hold the datasets */}
                    <Tray title="products" scale={0.5} data-qed-palette="products">
                        <Note>the datasets of the readers will appear here</Note>
                    </Tray>
                    {/* the pipelines the user designed */}
                    <Tray title="designs" scale={0.5} data-qed-palette="designs">
                        <Note>the pipelines you design will appear here</Note>
                    </Tray>
                    {/* the description of the factory picked on the diagram */}
                    <Picked diagram={playground} />
                </Panel>
            </Flex.Panel>
            {/* the diagram, under a tab with the choices of how to look at it */}
            <Flex.Panel auto={true} style={styles.flex}>
                <Viewport>
                    <Tab view={view} adjust={adjust} />
                    <Canvas diagram={playground} view={view} />
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
                doc
                inputs
                outputs
            }
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
