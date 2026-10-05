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
// widgets
import { Header } from '~/widgets'

// locals
// hooks
import { useViewports } from '../viz/useViewports'
import { useSelection } from '../flow'
// styles
import styles from './styles'


// the panel with the nodes that a visualization pipeline can be built out of; while it is up,
// the active view shows its pipeline below its data, and the panel describes the node picked there
export const Nodes = ({ qed }) => {
    // the active viewport
    const { activeViewport } = useViewports()
    // the nodes picked on the diagram
    const { selection } = useSelection()
    // unpack the views
    const { views } = useFragment(nodesGetDiagramFragment, qed)
    // the factories on the diagram of the active view
    const factories = views[activeViewport]?.diagram?.factories ?? []
    // the one to describe: the first pick that is a factory of this diagram
    const factory = factories.find(candidate => selection.includes(candidate.id)) ?? null

    // render
    return (
        <Panel data-qed-panel="flow">
            {/* the title of the panel */}
            <Header title="visualization pipeline" style={styles.header} />
            {/* without a pick, say how to make one */}
            {factory === null && <Note>pick a factory on the diagram to see what it does</Note>}
            {/* otherwise, describe it */}
            {factory !== null && <Inspector factory={factory} />}
        </Panel>
    )
}


// the description of a factory: what it is, what it consumes, what it makes, and how it is set
const Inspector = ({ factory }) => {
    // unpack
    const { family, doc, traits } = factory
    // its short name is the last part of its family
    const name = family.split(".").pop()
    // sort its traits by what they are to it
    const pick = kind => traits.filter(trait => trait.kind === kind)
    // render
    return (
        <Section data-qed-inspector={family}>
            {/* who it is */}
            <Name>{name}</Name>
            <Family>{family}</Family>
            {/* what it does */}
            {doc && <Doc>{doc}</Doc>}
            {/* what it reads, what it writes, and how it is set */}
            <Traits title="inputs" traits={pick("input")} />
            <Traits title="outputs" traits={pick("output")} />
            <Traits title="settings" traits={pick("setting")} settings />
        </Section>
    )
}


// a group of traits
const Traits = ({ title, traits, settings = false }) => {
    // render
    return (
        <>
            {/* the title of the group */}
            <Title>{title}</Title>
            {/* an empty group says so */}
            {traits.length === 0 && <Empty>none</Empty>}
            {/* otherwise, one entry per trait */}
            {traits.map(trait => (
                <Trait key={trait.name}>
                    {/* its name and its type */}
                    <TraitName>{trait.name}</TraitName>
                    <TraitType>{trait.type}</TraitType>
                    {/* a setting shows its value, and its default when it differs */}
                    {settings && <TraitValue>{trait.value ?? "-"}</TraitValue>}
                    {settings && trait.default !== null && trait.default !== trait.value &&
                        <TraitDefault>default: {trait.default}</TraitDefault>}
                    {/* what it is for */}
                    {trait.doc && <TraitDoc>{trait.doc}</TraitDoc>}
                </Trait>
            ))}
        </>
    )
}


// the container
const Panel = styled.div`
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
`

// the note shown when there is nothing to describe
const Note = styled.div`
    font-family: inconsolata;
    font-size: 90%;
    cursor: default;
    padding: 0.5rem 1.0rem;
    color: ${styles.dim};
`

// the description
const Section = styled.div`
    padding: 0.5rem 1.0rem;
    cursor: default;
`

// the short name of the factory
const Name = styled.div`
    font-family: noto-italic;
    font-size: 120%;
    color: ${styles.factory};
`

// its family
const Family = styled.div`
    font-family: inconsolata;
    font-size: 80%;
    color: ${styles.dim};
    padding-bottom: 0.5rem;
`

// its documentation
const Doc = styled.div`
    font-family: inconsolata;
    font-size: 90%;
    color: ${styles.normal};
    white-space: pre-wrap;
    padding-bottom: 0.5rem;
`

// the title of a group of traits
const Title = styled.div`
    font-family: rubik-medium;
    font-size: 70%;
    text-transform: uppercase;
    color: ${styles.dim};
    padding: 0.75rem 0 0.25rem 0;
`

// an empty group
const Empty = styled.div`
    font-family: inconsolata;
    font-size: 80%;
    color: ${styles.dim};
`

// a trait
const Trait = styled.div`
    display: grid;
    grid-template-columns: max-content 1fr;
    column-gap: 0.75rem;
    font-family: inconsolata;
    font-size: 85%;
    padding: 0.125rem 0;
`

// its name
const TraitName = styled.span`
    color: ${styles.normal};
`

// its type
const TraitType = styled.span`
    color: ${styles.dim};
`

// the value of a setting
const TraitValue = styled.span`
    grid-column: 1 / span 2;
    padding-left: 1rem;
    color: ${styles.value};
`

// its default, when it differs
const TraitDefault = styled.span`
    grid-column: 1 / span 2;
    padding-left: 1rem;
    color: ${styles.dim};
`

// what the trait is for
const TraitDoc = styled.span`
    grid-column: 1 / span 2;
    padding-left: 1rem;
    color: ${styles.dim};
`


// my fragment
const nodesGetDiagramFragment = graphql`
    fragment nodesGetDiagramFragment on QED {
        views {
            # the diagram of the pipeline of the view
            diagram {
                id
                # its factories, as the inspector describes them
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
    }
`


// end of file
