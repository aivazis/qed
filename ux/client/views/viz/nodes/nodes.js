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
            {/* the inspector of the factory picked on the diagram */}
            <Inspector diagram={diagram} />
        </Panel>
    )
}


// the factories on offer, one tray per protocol; with {trays}, whoever owns them decides which
// are open, and hears about every toggle
export const Palette = ({ catalog, trays }) => {
    // render
    return (
        <>
            {catalog.map(group => <Group key={group.family} group={group} trays={trays} />)}
        </>
    )
}


// the inspector: the description of the factory picked on {diagram}, or else of what the picked
// slot holds, in a tray of its own, which starts open; with {trays}, whoever owns them decides
// whether it is open, and hears about every toggle
export const Inspector = ({ diagram, trays }) => {
    // the nodes picked on the diagram
    const { selection } = useSelection()
    // the factories on the diagram
    const factories = diagram?.factories ?? []
    // and its slots
    const slots = diagram?.slots ?? []
    // the factory to describe: the first pick that is a factory of this diagram
    const factory = factories.find(candidate => selection.includes(candidate.id)) ?? null
    // without one, the slot to describe: the first pick that is a slot of this diagram
    const slot = factory === null
        ? slots.find(candidate => selection.includes(candidate.id)) ?? null
        : null
    // render
    return (
        <Tray title="inspector" initially={true} scale={0.5} data-qed-palette="inspector"
            expanded={trays?.isOpen("inspector")} onToggle={trays?.toggle("inspector")}>
            {/* without a pick, say how to make one */}
            {factory === null && slot === null &&
                <Note>pick a factory or a slot on the diagram to see what it is</Note>}
            {/* a factory */}
            {factory !== null &&
                <Description diagram={diagram.id} editable={diagram.editable} factory={factory} />}
            {/* a slot */}
            {slot !== null && <Holding product={slot.product} />}
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


// the producers on offer, the protocol of each group of the {catalog}, in a tray of their own,
// which starts open; with {trays}, whoever owns them decides whether it is open
export const Producers = ({ catalog, trays }) => {
    // the protocol of each group, which leads its entries
    const protocols = catalog.flatMap(group => group.entries.filter(entry => entry.level === "protocol"))
    // the count of the producers, next to the title
    const count = <Count>{protocols.length}</Count>
    // render
    return (
        <Tray title="producers" initially={true} scale={0.5} controls={count}
            data-qed-palette="producers"
            expanded={trays?.isOpen("producers")} onToggle={trays?.toggle("producers")}>
            <Entries>
                {protocols.map(entry => <Entry key={entry.family} entry={entry} />)}
            </Entries>
        </Tray>
    )
}


// a protocol and the factories that implement it, in a tray of their own; with {trays}, whoever
// owns them decides whether it is open
const Group = ({ group, trays }) => {
    // the count of the entries in the group, next to its title
    const count = <Count>{group.entries.length}</Count>
    // render
    return (
        <Tray title={group.name} scale={0.5} controls={count} data-qed-palette={group.family}
            expanded={trays?.isOpen(group.family)} onToggle={trays?.toggle(group.family)}>
            <Entries>
                {group.entries.map(entry => <Entry key={entry.family} entry={entry} />)}
            </Entries>
        </Tray>
    )
}


// a factory on offer, either a protocol or a class that implements it: its picture, its name, and
// its slots; it can be dragged onto the diagram
const Entry = ({ entry }) => {
    // unpack
    const { family, name, level, doc, inputs, outputs } = entry
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
        <Row draggable onDragStart={onDragStart} title={doc} data-qed-catalog={family}
            data-qed-level={level}>
            <Picture><Miniature ref={picture} inputs={inputs} outputs={outputs} level={level}
                scale={7} /></Picture>
            <Words>
                <EntryName>{name}</EntryName>
                <Signature>{slots}</Signature>
            </Words>
        </Row>
    )
}


// the description of a {factory} of {diagram}: what it is, what it consumes, what it makes, and how
// it is set; on a diagram that is {editable}, it can also be removed
const Description = ({ diagram, editable, factory }) => {
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
            {/* and, when the diagram can be edited, a way to remove it */}
            {editable && <Remove onClick={() => remove(id)} data-qed-action="remove">remove</Remove>}
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


// the description of what a slot holds, its {product}: the specification it must satisfy, how far
// down it is pinned, the instance behind it, if any, and what that says it holds
const Holding = ({ product }) => {
    // unpack
    const { specification, doc, level, family, given, empty, stale, facts } = product
    // its short name is the last part of the family of its specification
    const name = specification?.split(".").pop() ?? "product"
    // what it is, in words: nothing, a product made or yet to be made, or one that stands for
    // a class or any implementation of its specification
    const status = empty ? "holds nothing"
        : level === "instance" ? (stale ? "stale" : "made")
            : level === "class" ? "any instance of its class"
                : level === "protocol" ? "any implementation of its specification"
                    : "bound to nothing"
    // render
    return (
        <Section data-qed-inspector={specification} data-qed-level={level}>
            {/* what it must be */}
            <Product>{name}</Product>
            <Family>{specification}</Family>
            {/* what that is for */}
            {doc && <Doc>{doc}</Doc>}
            {/* what stands behind it */}
            <Title>product</Title>
            <Trait>
                <TraitName>status</TraitName>
                <TraitValue data-qed-status={status}>{status}</TraitValue>
            </Trait>
            {family !== null &&
                <Trait>
                    <TraitName>class</TraitName>
                    <TraitType>{family}</TraitType>
                </Trait>}
            {given !== null &&
                <Trait>
                    <TraitName>name</TraitName>
                    <TraitValue>{given === "" ? "-" : given}</TraitValue>
                </Trait>}
            {/* and what it says it holds */}
            <Title>contents</Title>
            {facts.length === 0 && <Empty>none</Empty>}
            {facts.map((fact, index) => (
                <Trait key={index}>
                    <TraitName>{fact.name}</TraitName>
                    <TraitValue>{fact.value === "" ? "-" : fact.value}</TraitValue>
                </Trait>
            ))}
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

// the short name of the specification of a product
const Product = styled.div`
    font-family: noto-italic;
    font-size: 120%;
    color: ${styles.product};
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
                # whether its structure can change
                editable
                # and what the inspector shows of what its slots hold
                slots {
                    id
                    product {
                        specification
                        doc
                        level
                        family
                        given
                        empty
                        stale
                        facts {
                            name
                            value
                        }
                    }
                }
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
