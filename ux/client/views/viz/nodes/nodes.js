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
import { Header, Tray } from '~/widgets'

// locals
// hooks
import { useViewports } from '../viz/useViewports'
import { useEditDiagram, useSelection } from '../flow'
// the media type of a factory dragged from the palette
import { factoryMediaType } from '../flow/drops'
// the small picture of a factory
import { Miniature } from './miniature'
// styles
import styles from './styles'


// the panel of the visualization pipeline activity; while it is up, the active view shows its
// pipeline below its data, and the panel describes the factory picked there
export const Nodes = ({ qed }) => {
    // the active viewport
    const { activeViewport } = useViewports()
    // unpack the views
    const { views } = useFragment(nodesGetDiagramFragment, qed)
    // the diagram of the active view
    const diagram = views[activeViewport]?.diagram ?? null

    // render
    return (
        <Panel data-qed-panel="flow">
            {/* the title of the panel */}
            <Header title="visualization pipeline" style={styles.header} />
            {/* the description of the factory picked on the diagram */}
            <Picked diagram={diagram} />
        </Panel>
    )
}


// the factories on offer, one tray per protocol
export const Palette = ({ catalog }) => {
    // render
    return (
        <>
            {catalog.map(group => <Group key={group.family} group={group} />)}
        </>
    )
}


// the description of the factory picked on {diagram}, in a tray of its own
export const Picked = ({ diagram }) => {
    // the nodes picked on the diagram
    const { selection } = useSelection()
    // the factories on the diagram
    const factories = diagram?.factories ?? []
    // the one to describe: the first pick that is a factory of this diagram
    const factory = factories.find(candidate => selection.includes(candidate.id)) ?? null
    // render
    return (
        <Tray title="picked" initially={true} scale={0.5} data-qed-palette="picked">
            {/* without a pick, say how to make one */}
            {factory === null && <Note>pick a factory on the diagram to see what it does</Note>}
            {/* otherwise, describe it */}
            {factory !== null && <Inspector diagram={diagram.id} factory={factory} />}
        </Tray>
    )
}


// a note in place of contents that are not there yet
export const Note = styled.div`
    font-family: inconsolata;
    font-size: 90%;
    cursor: default;
    padding: 0.5rem 1.0rem;
    color: ${styles.dim};
`


// the factories that implement one protocol, in a tray of their own
const Group = ({ group }) => {
    // the filters are where most of the work happens, so their tray starts open
    const initially = group.name === "filters"
    // the count of the factories in the group, next to its title
    const count = <Count>{group.entries.length}</Count>
    // render
    return (
        <Tray title={group.name} initially={initially} scale={0.5} controls={count}
            data-qed-palette={group.family}>
            <Entries>
                {group.entries.map(entry => <Entry key={entry.family} entry={entry} />)}
            </Entries>
        </Tray>
    )
}


// a factory on offer: its picture, its name, and its slots; it can be dragged onto the diagram
const Entry = ({ entry }) => {
    // unpack
    const { family, name, doc, inputs, outputs } = entry
    // the picture, which doubles as the image that follows the pointer during a drag
    const picture = React.useRef(null)
    // a drag carries the family of the factory, and shows its picture
    const onDragStart = evt => {
        // carry the family
        evt.dataTransfer.setData(factoryMediaType, family)
        // as a copy
        evt.dataTransfer.effectAllowed = "copy"
        // and show the picture, held by its hub
        const box = picture.current?.getBoundingClientRect()
        if (box) {
            evt.dataTransfer.setDragImage(picture.current, box.width / 2, box.height / 2)
        }
        // all done
        return
    }
    // what the slots are called, the way a signature reads
    const slots = `${inputs.length ? inputs.join(", ") : "nothing"} \u2192 ${outputs.join(", ")}`
    // render
    return (
        <Row draggable onDragStart={onDragStart} title={doc} data-qed-catalog={family}>
            <Picture><Miniature ref={picture} inputs={inputs} outputs={outputs} scale={7} /></Picture>
            <Words>
                <EntryName>{name}</EntryName>
                <Signature>{slots}</Signature>
            </Words>
        </Row>
    )
}


// the description of a {factory} of {diagram}: what it is, what it consumes, what it makes, and how
// it is set
const Inspector = ({ diagram, factory }) => {
    // the editor
    const { remove } = useEditDiagram(diagram)
    // unpack
    const { id, family, doc, traits } = factory
    // its short name is the last part of its family
    const name = family.split(".").pop()
    // sort its traits by what they are to it
    const pick = kind => traits.filter(trait => trait.kind === kind)
    // render
    return (
        <Section data-qed-inspector={family}>
            {/* who it is */}
            <Name>{name}</Name>
            {/* and a way to remove it */}
            <Remove onClick={() => remove(id)} data-qed-action="remove">remove</Remove>
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

// the factories of a group of the palette
const Entries = styled.div`
    display: flex;
    flex-direction: column;
    padding: 0.25rem 0 0.5rem 0;
`

// a factory of the palette
const Row = styled.div`
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.25rem 1.0rem 0.25rem 1.0rem;
    cursor: grab;
    &:hover {
        background-color: ${styles.hover};
    }
`

// the room for its picture, wide enough that the names line up
const Picture = styled.div`
    flex: 0 0 5.5rem;
    display: flex;
    justify-content: center;
`

// its name and its signature
const Words = styled.div`
    display: flex;
    flex-direction: column;
    min-width: 0;
`

// its name
const EntryName = styled.span`
    font-family: inconsolata;
    font-size: 100%;
    color: ${styles.normal};
    ${Row}:hover & {
        color: ${styles.factory};
    }
`

// the names of its slots
const Signature = styled.span`
    font-family: inconsolata;
    font-size: 80%;
    color: ${styles.dim};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
`

// the count of the factories in a group
const Count = styled.span`
    font-family: inconsolata;
    font-size: 80%;
    color: ${styles.dim};
    padding-right: 0.5rem;
`

// the button that removes the picked factory
const Remove = styled.span`
    font-family: inconsolata;
    font-size: 80%;
    color: ${styles.dim};
    cursor: pointer;
    &:hover {
        color: ${styles.danger};
    }
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
