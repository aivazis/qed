// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the paint of factories
import factoryPaint from '~/shapes/factory/styles'

// local
// the diagram on the canvas
import { useDiagram } from './diagram'
// the projection, which places the fan around its node
import { useProjection } from './projection'
// the editor
import { useEditDiagram } from './useEditDiagram'
// paint
import styles from './styles'


// the fan that offers the next level down of a factory around it: the classes of its protocol,
// by family; the canvas holds which factory is fanned out, if any
const FanContext = React.createContext(null)


// the state of the fan, which the canvas holds so its keys can open and fold it: the factory
// that is fanned out, among the {factories} of the diagram, and the families it has been opened
// onto; without a {catalog} of what each protocol can be pinned to, nothing fans out
export const useFanState = ({ factories, catalog }) => {
    // the id of the factory that is fanned out, if any
    const [id, setId] = React.useState(null)
    // the families the fan has been opened onto, outermost first
    const [browse, setBrowse] = React.useState([])
    // the factory, as the diagram has it now, so the fan follows its pin; a factory that is gone
    // takes the fan along
    const factory = id === null ? null : factories.find(f => f.id === id) ?? null
    // fan out the factory with {id}
    const open = id => {
        // only when there is something to offer
        if (!catalog) {
            // so there is nothing to do
            return
        }
        // fan it out, from the top
        setId(id)
        setBrowse([])
        // all done
        return
    }
    // fold the fan
    const close = () => {
        // by forgetting the factory
        setId(null)
        setBrowse([])
        // all done
        return
    }
    // publish
    return { factory, catalog, browse, setBrowse, open, close }
}


// hand the state of the {fan} to the nodes and the fan itself
export const FanProvider = ({ fan, children }) => {
    // render
    return <FanContext.Provider value={fan}>{children}</FanContext.Provider>
}


// access to the fan, or nothing outside a canvas that has one
export const useFan = () => React.useContext(FanContext)


// the fan around the factory that is fanned out, if any
export const Fan = () => {
    // the fan
    const fan = useFan()
    // the projection, which places the factory on the screen
    const { project } = useProjection()
    // the editor of the diagram on the canvas
    const { pin } = useEditDiagram(useDiagram().id)
    // if nothing is fanned out
    if (!fan?.factory) {
        // there is nothing to draw
        return null
    }
    // unpack
    const { factory, catalog, browse, setBrowse, close } = fan
    // the classes of its protocol, as the palette offers them
    const group = catalog.find(group => group.family === factory.protocol)
    // the candidates at the level below the factory's: classes, for a protocol
    const candidates = factory.level === "protocol"
        ? (group?.entries ?? []).filter(entry => entry.level === "class")
        : []
    // the satellites: the members of the family being browsed, or the families of the candidates
    const satellites = tree(browse.length ? browse[browse.length - 1].members : candidates)
    // the way back, in words, if there is one
    const back = browse.length
        ? (browse.length > 1 ? `back to ${browse[browse.length - 2].name}` : "back to all families")
        : factory.level === "class" ? `back to any ${protocolName(group)}` : null
    // where the grip of the factory is on the screen: the middle of its circle, above its hub
    const at = project(factory.at)
    const center = { x: at.x, y: at.y - 1.5 }
    // go back: out of the family being browsed, or up to the protocol
    const goBack = () => {
        // out of a family
        if (browse.length) {
            // leaves the factory as it is
            setBrowse(browse.slice(0, -1))
            // all done
            return
        }
        // up to the protocol
        pin({ id: factory.id, family: null })
        // all done
        return
    }
    // choose a satellite
    const choose = satellite => {
        // a family opens onto its members
        if (satellite.members) {
            // and leaves the factory as it is
            setBrowse([...browse, satellite])
            // all done
            return
        }
        // a class pins the factory to it
        pin({ id: factory.id, family: satellite.family })
        // and, with nothing below a class to offer yet, the fan folds
        close()
        // all done
        return
    }
    // render
    return (
        <g data-qed-fan={factory.id}>
            {/* the satellites, on an arc above the factory */}
            {satellites.map((satellite, k) => (
                <Satellite key={satellite.family ?? satellite.name}
                    satellite={satellite} spot={place(k, satellites.length)} center={center}
                    onChoose={() => choose(satellite)} />
            ))}
            {/* the way back, right below the factory, out of line with the choices */}
            {back && <Back label={back} center={center} onChoose={goBack} />}
        </g>
    )
}


// a satellite of the fan: a class, or a family of them
const Satellite = ({ satellite, spot, center, onChoose }) => {
    // where it goes
    const a = spot.angle * Math.PI / 180
    const x = center.x + spot.reach * Math.cos(a)
    const y = center.y + spot.reach * Math.sin(a)
    // its label goes further out along the spoke, on the side it leans to
    const lx = center.x + (spot.reach + 1.2) * Math.cos(a)
    const ly = center.y + (spot.reach + 1.2) * Math.sin(a) + 0.2
    const anchor = Math.cos(a) > 0.35 ? "start" : Math.cos(a) < -0.35 ? "end" : "middle"
    // the paint of a class
    const paint = { ...factoryPaint.icon, ...styles.levels.factory.class.icon }
    // a click chooses it, and stays with me
    const onClick = evt => {
        // the canvas clears the selection on a click
        evt.stopPropagation()
        // choose
        onChoose()
        // all done
        return
    }
    // render
    return (
        <g style={styles.fan.satellite} onClick={onClick}
            data-qed-satellite={satellite.family ?? satellite.name}
            data-qed-family-group={satellite.members ? satellite.name : undefined}>
            {/* the spoke */}
            <line x1={center.x + 0.9 * Math.cos(a)} y1={center.y + 0.9 * Math.sin(a)} x2={x} y2={y}
                style={styles.fan.spoke} />
            {/* a family is a cluster of three small pucks; a class is one */}
            {satellite.members
                ? [[-0.32, 0.18], [0.32, 0.18], [0, -0.32]].map(([dx, dy], i) => (
                    <circle key={i} cx={x + dx} cy={y + dy} r={0.32} style={paint} />
                ))
                : <circle cx={x} cy={y} r={0.6} style={paint} />}
            {/* a ring that makes the whole satellite easy to pick */}
            <circle cx={x} cy={y} r={0.95} style={styles.fan.ring} />
            {/* the label */}
            <text x={lx} y={ly} style={{ ...styles.fan.label, textAnchor: anchor }}>
                {satellite.members ? `${satellite.name} (${satellite.members.length})` : satellite.name}
            </text>
        </g>
    )
}


// the way back, below the factory
const Back = ({ label, center, onChoose }) => {
    // where it goes
    const x = center.x
    const y = center.y + 2.9
    // a click goes back, and stays with me
    const onClick = evt => {
        // the canvas clears the selection on a click
        evt.stopPropagation()
        // go back
        onChoose()
        // all done
        return
    }
    // render
    return (
        <g style={styles.fan.satellite} onClick={onClick} data-qed-satellite="back">
            {/* a small hollow puck with a curved arrow */}
            <circle cx={x} cy={y} r={0.5} style={styles.fan.back} />
            <path d={`M ${x + 0.2} ${y + 0.15} A 0.2 0.2 0 1 0 ${x - 0.2} ${y - 0.05} M ${x - 0.3} ${y - 0.2} L ${x - 0.2} ${y - 0.05} L ${x - 0.05} ${y - 0.15}`}
                style={styles.fan.arrow} />
            {/* a ring that makes it easy to pick */}
            <circle cx={x} cy={y} r={0.8} style={styles.fan.ring} />
            {/* where it goes back to */}
            <text x={x + 0.9} y={y + 0.2} style={{ ...styles.fan.label, ...styles.fan.backLabel }}>{label}</text>
        </g>
    )
}


// the name of the protocol of a catalog {group}, the way its own entry spells it
const protocolName = group => group?.entries.find(entry => entry.level === "protocol")?.name ?? "protocol"


// where satellite {k} of {n} goes: on an arc above the factory, symmetric about the vertical, a
// fixed angle apart so that a few choices sit close together, and further out once it gets crowded;
// the angle is in degrees, the reach in diagram units
const place = (k, n) => {
    // the angle between neighbors, smaller as they multiply so the arc never wraps past the sides
    const step = n > 1 ? Math.min(32, 176 / (n - 1)) : 0
    // the reach that keeps neighbors about three units apart
    const reach = n > 1 ? 2.8 / (2 * Math.sin(step * Math.PI / 360)) : 4.8
    // assemble
    return { angle: -90 + (k - (n - 1) / 2) * step, reach: Math.min(Math.max(reach, 4.8), 9.5) }
}


// split catalog {entries} into what the fan shows: the entries themselves when they share one
// package, otherwise one satellite per family, cut at the first segment where their families part
const tree = entries => {
    // the packages of the entries
    const pkgs = entries.map(entry => entry.family.split(".").slice(0, -1))
    // how many leading segments they all share
    let depth = 0
    while (pkgs.length && pkgs.every(p => p.length > depth && p[depth] === pkgs[0][depth])) depth++
    // all in one package: show them as they are
    if (pkgs.every(p => p.length === depth)) {
        // in the order they came
        return entries
    }
    // otherwise, sort them by the segment where they part
    const by = new Map()
    entries.forEach((entry, i) => {
        // the segment
        const key = pkgs[i][depth] ?? ""
        // file the entry under it
        by.set(key, [...(by.get(key) ?? []), i])
    })
    // a family of one shows its member; a bigger one is named by what its members share past the cut
    const out = []
    for (const [key, members] of by) {
        // the ones with no segment there, or alone in theirs
        if (key === "" || members.length === 1) {
            // stand for themselves
            members.forEach(i => out.push(entries[i]))
            // on to the next
            continue
        }
        // otherwise, find how far the members agree
        let end = depth
        while (members.every(i => pkgs[i].length > end && pkgs[i][end] === pkgs[members[0]][end])) end++
        // and make a family of them
        out.push({
            name: pkgs[members[0]].slice(depth, end).join("."),
            members: members.map(i => entries[i]),
        })
    }
    // hand them off
    return out
}


// end of file
