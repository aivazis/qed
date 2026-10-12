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
// the shapes of the diagram
import { Plex, Slot as SlotShape } from '~/shapes'

// local
// the fields over the canvas
import { InlineField, spotOf } from './inlineField'
// the projection, which places the fan around its node
import { useProjection } from './projection'
// the route of a connector
import { route } from './connector'
// what a pin would do, as the server works it out
import { usePinPreview } from './usePinPreview'
// paint
import styles from './styles'


// the fan that offers the next level down of a factory around it: the classes of its protocol,
// by family; the canvas holds which factory is fanned out, if any
const FanContext = React.createContext(null)


// the state of the fan, which the canvas holds so its keys can drive it: the factory that is
// fanned out, among the {factories} of the {diagram}, the families it has been opened onto, the
// choices it offers, and the one that has the focus; choosing a class asks {pin} to pin the
// factory to it, and choosing "new" above a class asks {instantiate} to pin it to a new instance
// of that class, under a name a person may give it; the {slots} of the diagram show where the
// ones a pin lets go of are; without a {catalog} of what each protocol can be pinned to,
// nothing fans out
export const useFanState = ({ diagram, factories, slots, catalog, pin, instantiate }) => {
    // the id of the factory that is fanned out, if any
    const [id, setId] = React.useState(null)
    // the families the fan has been opened onto, outermost first
    const [browse, setBrowse] = React.useState([])
    // the choice that has the focus: the index of a satellite, "back" for the way back, or nothing
    const [focus, setFocus] = React.useState(null)
    // the new instance being named, if any: the family of its class, the name so far, and the
    // reason the last try was refused
    const [naming, setNaming] = React.useState(null)
    // where the pointer was last seen moving, so a satellite that slides under a pointer at rest
    // does not take the focus
    const pointer = React.useRef(null)
    // watch the pointer, wherever it goes
    React.useEffect(() => {
        // remember where it moved to
        const track = evt => { pointer.current = { x: evt.clientX, y: evt.clientY } }
        // on every move
        window.addEventListener("pointermove", track)
        // and stop when done
        return () => window.removeEventListener("pointermove", track)
    }, [])
    // the factory, as the diagram has it now, so the fan follows its pin; a factory that is gone
    // takes the fan along
    const factory = id === null ? null : factories.find(f => f.id === id) ?? null
    // the classes of its protocol, as the palette offers them
    const group = factory ? catalog?.find(group => group.family === factory.protocol) : null
    // the candidates at the level below the factory's: classes, for a protocol
    const candidates = factory?.level === "protocol"
        ? (group?.entries ?? []).filter(entry => entry.level === "class")
        : []
    // the family or the class being browsed, if any, which remembers where it sits
    const opened = browse.length ? browse[browse.length - 1] : null
    // the satellites: above a class, a new instance of it, whether the class is being browsed or
    // is what the factory is pinned to, directly or through an instance of it; otherwise, the
    // members of the family being browsed, or the families of the candidates
    const satellites = !factory ? []
        : opened && isClass(opened) ? [fresh(opened.family)]
            : opened ? tree(opened.members)
                : factory.level !== "protocol" ? [fresh(factory.family)]
                    : tree(candidates)
    // where they go: around the family being browsed, along the spoke that led to it, or around the
    // factory, straight up
    const spots = satellites.map((_, k) => place({
        k, n: satellites.length, ...(opened ? { origin: opened.spot, ...members } : families),
    }))
    // the way back, in words, if there is one
    const back = !factory ? null : browse.length
        ? (browse.length > 1 ? `back to ${browse[browse.length - 2].name}` : "back to all families")
        : factory.level === "class" ? `back to any ${protocolName(group)}`
            : factory.level === "instance" ? `back to any ${factory.family.split(".").pop()}` : null
    // the choice that has the focus, if it is on the arc
    const pick = typeof focus === "number" ? satellites[focus] ?? null : null
    // the class whose look is previewed on the factory: the one that has the focus, or, for a new
    // instance of a class the factory is not pinned to yet, that class
    const preview = !pick || pick.members ? null
        : pick.create ? (factory.level === "protocol" ? opened : null)
            : pick
    // fan out the factory with {id}
    const open = id => {
        // only when there is something to offer
        if (!catalog) {
            // so there is nothing to do
            return
        }
        // fan it out, from the top, with nothing in focus and nothing being named
        setId(id)
        setBrowse([])
        setFocus(null)
        setNaming(null)
        // all done
        return
    }
    // fold the fan
    const close = () => {
        // by forgetting the factory
        setId(null)
        setBrowse([])
        setFocus(null)
        setNaming(null)
        // all done
        return
    }
    // go back: out of the family being browsed, or down to the class or the protocol
    const goBack = () => {
        // out of a family
        if (browse.length) {
            // the choices one level up: the members of the family that holds this one, or the
            // families of the candidates
            const above = tree(browse.length > 1 ? browse[browse.length - 2].members : candidates)
            // leaves the factory as it is
            setBrowse(browse.slice(0, -1))
            // and hands the focus to the family or class we came out of, so <up> goes right back in
            const k = above.findIndex(satellite => key(satellite) === key(opened))
            setFocus(k < 0 ? null : k)
            // all done
            return
        }
        // an instance goes back to its class, and a class to its protocol
        pin({ id: factory.id, family: factory.level === "instance" ? factory.family : null })
        // which leaves nothing in focus
        setFocus(null)
        // all done
        return
    }
    // choose satellite {k}
    const choose = k => {
        // the satellite
        const satellite = satellites[k]
        // a new instance asks for its name first
        if (satellite.create) {
            // which may be left empty
            setNaming({ family: satellite.create, name: "", error: null })
            // all done
            return
        }
        // a family opens onto its members, which fan out from where it sits
        if (satellite.members) {
            // and leaves the factory as it is
            setBrowse([...browse, { ...satellite, spot: spots[k] }])
            // and the focus starts over
            setFocus(null)
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
    // open the class {k} onto what is above it: a new instance of it
    const rise = k => {
        // the class, which fans out its instances from where it sits
        setBrowse([...browse, { ...satellites[k], spot: spots[k] }])
        // with the new instance in focus, so <enter> names it
        setFocus(0)
        // all done
        return
    }
    // record what was typed as the name of the new instance
    const rename = text => {
        // in the name being made
        setNaming(old => old && { ...old, name: text, error: null })
        // all done
        return
    }
    // stop naming, and go back to the fan
    const unname = () => {
        // forget the name
        setNaming(null)
        // all done
        return
    }
    // make the new instance, under the name typed, if any, and pin the factory to it
    const commitName = () => {
        // with nothing being named
        if (!naming) {
            // there is nothing to do
            return
        }
        // ask the server
        instantiate({ id: factory.id, family: naming.family, name: naming.name.trim() }, error => {
            // a pin that was made folds the fan
            if (error === null) {
                // so fold it
                close()
                // all done
                return
            }
            // a refusal leaves the name open, with the reason
            setNaming(old => old && { ...old, error })
            // all done
            return
        })
        // all done
        return
    }
    // the keys of the fan: left and right move the focus among the choices on the arc, up opens
    // the family or the class that has the focus, down undoes the last step, and <enter> takes the
    // choice that has the focus; reports whether the key was for the fan
    const onKey = evt => {
        // with nothing fanned out, or a name being typed, which keeps its keys
        if (!factory || naming) {
            // no key is for the fan
            return false
        }
        // how many choices there are
        const n = satellites.length
        // along the arc, to the left
        if (evt.key === "ArrowLeft" && n) {
            // one step, wrapping around, starting from the right end
            setFocus(typeof focus === "number" ? (focus + n - 1) % n : n - 1)
            // handled
            return true
        }
        // along the arc, to the right
        if (evt.key === "ArrowRight" && n) {
            // one step, wrapping around, starting from the left end
            setFocus(typeof focus === "number" ? (focus + 1) % n : 0)
            // handled
            return true
        }
        // down undoes the last step: out of the family being browsed, or back to the protocol
        if (evt.key === "ArrowDown" && back) {
            // if there is a way back
            goBack()
            // handled
            return true
        }
        // up goes into the family that has the focus
        if (evt.key === "ArrowUp" && pick?.members) {
            // by opening it
            choose(focus)
            // handled
            return true
        }
        // or rises above the class that has the focus, to its instances
        if (evt.key === "ArrowUp" && pick && isClass(pick)) {
            // by opening it
            rise(focus)
            // handled
            return true
        }
        // and, with nothing on the arc in focus, lands on its middle
        if (evt.key === "ArrowUp" && n && typeof focus !== "number") {
            // so the next <up> can go in
            setFocus(Math.floor((n - 1) / 2))
            // handled
            return true
        }
        // take the choice that has the focus
        if (evt.key === "Enter" && focus !== null) {
            // the way back
            if (focus === "back") {
                // goes back
                goBack()
            }
            // a satellite
            else if (satellites[focus]) {
                // is chosen
                choose(focus)
            }
            // handled
            return true
        }
        // the arrows belong to the fan while it is out, even the ones that have nothing to do at
        // this level, so they never reach the camera
        if (evt.key.startsWith("Arrow")) {
            // swallowed
            return true
        }
        // anything else is not for the fan
        return false
    }
    // a satellite the pointer entered takes the focus, but only when the pointer got there by
    // moving: when the fan changes under a pointer at rest, the browser reports the satellite that
    // slid under it as entered, and that must not steal the focus the keys just placed
    const hover = (k, evt) => {
        // where the pointer was last seen moving
        const last = pointer.current
        // if the pointer is still there, the fan moved, not the pointer
        if (last && last.x === evt.clientX && last.y === evt.clientY) {
            // so leave the focus alone
            return
        }
        // otherwise, the pointer came to it
        setFocus(k)
        // all done
        return
    }
    // publish
    return {
        diagram, slots, factory, browse, satellites, spots, back, focus, preview, naming,
        open, close, goBack, choose, rise, setFocus, hover, onKey, rename, unname, commitName,
    }
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
    // if nothing is fanned out
    if (!fan?.factory) {
        // there is nothing to draw
        return null
    }
    // unpack
    const {
        diagram, slots, factory, browse, satellites, spots, back, focus, preview, goBack, choose, rise,
        hover,
    } = fan
    // where the grip of the factory is on the screen: the middle of its circle, above its hub
    const at = project(factory.at)
    const center = { x: at.x, y: at.y - 1.5 }
    // render
    return (
        <g data-qed-fan={factory.id}>
            {/* the look of the factory pinned to the class that has the focus */}
            {preview && <Preview diagram={diagram} slots={slots} factory={factory} entry={preview} />}
            {/* the families and classes opened so far, where they were, as the trail back */}
            {browse.map(family => (
                <Satellite key={`opened-${key(family)}`} opened
                    satellite={family} spot={family.spot} center={center} />
            ))}
            {/* the satellites, on an arc above the factory, or past what they belong to */}
            {satellites.map((satellite, k) => (
                <Satellite key={key(satellite)}
                    satellite={satellite} spot={spots[k]} center={center}
                    focused={focus === k} onFocus={evt => hover(k, evt)}
                    onChoose={() => choose(k)} onRise={() => rise(k)} />
            ))}
            {/* the way back, right below the factory, out of line with the choices */}
            {back && <Back label={back} center={center} focused={focus === "back"}
                onFocus={evt => hover("back", evt)} onChoose={goBack} />}
        </g>
    )
}


// the field that names a new instance, over the canvas, next to the choice that asked for it; the
// name may be left empty, which makes an instance nobody named
export const FanNamer = () => {
    // the fan
    const fan = useFan()
    // the field, so it can take the focus and keep its keys to itself
    const field = React.useRef(null)
    // where the field goes, on the panel
    const [spot, setSpot] = React.useState(null)
    // the name being made, if any
    const naming = fan?.naming ?? null
    // the state as it is now, for the keys of the field, whose listener outlives a render
    const latest = React.useRef(fan)
    latest.current = fan
    // when a name is asked for, find the choice that asked, and put the field next to it
    React.useLayoutEffect(() => {
        // with nothing being named
        if (!naming) {
            // there is no field
            setSpot(null)
            // all done
            return
        }
        // the choice that asked
        const choice = document.querySelector('[data-qed-fan] [data-qed-satellite="new"]')
        // the panel the field goes on
        const panel = choice?.closest("section")
        // if either is missing
        if (!choice || !panel) {
            // the field goes in the corner
            setSpot({ x: 16, y: 16 })
            // all done
            return
        }
        // the field goes on the right of the ring of the choice, in the size of its label, which
        // is its last text
        setSpot(spotOf({
            label: [...choice.querySelectorAll("text")].pop(), panel,
            after: choice.querySelector(`circle[r="${ring}"]`),
        }))
        // all done
        return
    }, [naming !== null])
    // once the field is up, it takes the focus and handles its own keys
    React.useEffect(() => {
        // the field
        const input = field.current
        // if there is none
        if (!input) {
            // there is nothing to do
            return
        }
        // take the focus
        input.focus()
        // the keys typed here are for the field only; react hears them only once they reach
        // the root, so the field handles its own: <enter> makes the instance, <escape> goes
        // back to the fan
        const keep = evt => {
            // none of them go any further
            evt.stopPropagation()
            // make it
            if (evt.key === "Enter") {
                // under the name typed, if any
                latest.current.commitName()
                // all done
                return
            }
            // go back
            if (evt.key === "Escape") {
                // to the fan
                latest.current.unname()
                // all done
                return
            }
            // all done
            return
        }
        // install
        input.addEventListener("keydown", keep)
        // and remove when done
        return () => input.removeEventListener("keydown", keep)
    }, [spot !== null])
    // with nothing being named, or nowhere to put the field yet
    if (!naming || !spot) {
        // there is nothing to show
        return null
    }
    // render
    return (
        <InlineField spot={spot} prompt="name" value={naming.name} placeholder="unnamed"
            error={naming.error} field={field} onChange={fan.rename} data-qed-fan-namer />
    )
}


// the look of the {factory} of the {diagram} pinned to the class of the catalog {entry}, as the
// server works it out with the plan the pin itself carries out: the name it would have where its
// label goes, the slots it would gain where they would go, with their names, and a mark on the
// ones among the {slots} of the diagram it would let go of; drawn with the shapes and the
// connector routes of the diagram itself, in the paint of a ghost
const Preview = ({ diagram, slots, factory, entry }) => {
    // the projection, which places things on the screen
    const { project } = useProjection()
    // what the pin would do
    const preview = usePinPreview({ diagram, node: factory.id, family: entry.family })
    // until the answer arrives, or if the pin cannot be made
    if (!preview) {
        // there is nothing to show
        return null
    }
    // where the factory is on the diagram
    const { x, y, z } = factory.at
    // the terminals of the factory that would have connectors: a plex where a factory with slots
    // on that side has one
    const plexes = [
        entry.inputs.length ? project({ x: x - 2, y, z }) : null,
        entry.outputs.length ? project({ x: x + 2, y, z }) : null,
    ].filter(Boolean)
    // the slots it would let go of, where they are now
    const dropped = slots.filter(slot => preview.dropped.includes(slot.id)).map(slot => project(slot.at))
    // where the label of the factory goes
    const label = project({ x, y: y - 2.5, z })
    // render
    return (
        <g data-qed-preview={entry.family} pointerEvents="none">
            {/* the name the factory would have */}
            <text x={label.x} y={label.y} style={styles.fan.preview.title}>{preview.label}</text>
            {/* the terminals that would have connectors */}
            {plexes.map((spot, idx) => (
                <g key={`plex-${idx}`} transform={`translate(${spot.x} ${spot.y})`}>
                    <Plex style={{ icon: styles.fan.preview.plex }} />
                </g>
            ))}
            {/* the slots it would let go of */}
            {dropped.map((spot, idx) => (
                <circle key={`dropped-${idx}`} cx={spot.x} cy={spot.y} r={0.75}
                    style={styles.fan.preview.dropped} data-qed-preview-dropped />
            ))}
            {/* the slots it would gain, each with its connectors and its name */}
            {preview.slots.map(({ trait, input, output, at }) => {
                // where the slot is on the screen
                const spot = project(at)
                // the sides it would be connected on: a trait can be both
                const sides = [...(input ? [true] : []), ...(output ? [false] : [])]
                // render
                return (
                    <g key={trait} data-qed-preview-slot={trait}>
                        {sides.map(side => (
                            <path key={side ? "in" : "out"} style={styles.fan.preview.connector}
                                d={route({ factory: factory.at, slot: at, input: side, project })} />
                        ))}
                        <g transform={`translate(${spot.x} ${spot.y})`}>
                            <SlotShape style={{ icon: styles.fan.preview.slot }} />
                        </g>
                        <text x={spot.x} y={spot.y - 0.8} style={styles.fan.preview.name}>{trait}</text>
                    </g>
                )
            })}
        </g>
    )
}


// a satellite of the fan: a class, a family of them, or a new instance of a class; a family or
// a class that is {opened} stays where it was, as a stop on the way from the factory to what is
// past it, and takes no choices; a click chooses it, and a click with <alt> on a class rises
// above it, to its instances
const Satellite = ({
    satellite, spot, center, opened = false, focused = false, onFocus, onChoose, onRise,
}) => {
    // the direction of its spoke
    const a = spot.angle * Math.PI / 180
    // where the spoke starts, just outside whatever it hangs from
    const x0 = center.x + spot.from.x + spot.gap * Math.cos(a)
    const y0 = center.y + spot.from.y + spot.gap * Math.sin(a)
    // where it goes
    const x = center.x + spot.x
    const y = center.y + spot.y
    // where the spoke ends: as far short of it as its own members start past it
    const x1 = x - members.gap * Math.cos(a)
    const y1 = y - members.gap * Math.sin(a)
    // which side of the axis of its arc it is on: clockwise, counterclockwise, or right on it
    const lean = spot.angle - spot.axis
    const side = Math.abs(lean) < 1 ? 0 : Math.sign(lean)
    // what the label says: a family that is still closed says how many it holds
    const text = satellite.members && !opened
        ? `${satellite.name} (${satellite.members.length})` : satellite.name
    // where it goes: the box of its ink is kept the same {clearance} away from what is drawn at
    // the satellite, whichever way it faces, so the gap between the two looks the same all around
    // an opened family or class, and a satellite alone on its arc, have their labels level with
    // them, on the side away from where their arc leans, like the stops of the trail behind them;
    // the one alone may have the focus, so its label clears the ring that shows it; the label of
    // a new instance stays on the left, since its right is where the field that names it goes
    const { lx, ly } = labelAt({
        x, y, a, side, level: opened || spot.lone, ring: !opened && spot.lone,
        family: !!satellite.members, text, left: !!satellite.create,
    })
    // the paint of a class
    const paint = { ...factoryPaint.icon, ...styles.levels.factory.class.icon }
    // a click chooses it, and stays with me
    const onClick = evt => {
        // the canvas clears the selection on a click
        evt.stopPropagation()
        // a click with <alt> on a class
        if (evt.altKey && isClass(satellite)) {
            // rises above it
            onRise()
            // all done
            return
        }
        // otherwise, choose
        onChoose()
        // all done
        return
    }
    // the icon: a family is a cluster of three small pucks, a class is one, and a new instance is
    // a plus sign, as big as the labels
    const icon = satellite.members
        ? [[-0.32, 0.18], [0.32, 0.18], [0, -0.32]].map(([dx, dy], i) => (
            <circle key={i} cx={x + dx} cy={y + dy} r={0.32} style={paint} />
        ))
        : satellite.create
            ? <text x={x} y={y} style={styles.fan.fresh}>+</text>
            : <circle cx={x} cy={y} r={0.6} style={paint} />
    // an opened family or class is part of the trail, not a choice
    if (opened) {
        // so it is drawn quietly, and takes no pointer
        return (
            <g pointerEvents="none" data-qed-opened={key(satellite)}>
                {/* the spoke */}
                <line x1={x0} y1={y0} x2={x1} y2={y1} style={styles.fan.spoke} />
                {/* what it is */}
                {icon}
                {/* the label */}
                <text x={lx} y={ly} style={{ ...styles.fan.label, textAnchor: "start" }}>{text}</text>
            </g>
        )
    }
    // render
    return (
        <g style={styles.fan.satellite} onClick={onClick} onPointerEnter={onFocus}
            data-qed-satellite={key(satellite)}
            data-qed-family-group={satellite.members ? satellite.name : undefined}
            data-qed-focused={focused}>
            {/* the spoke */}
            <line x1={x0} y1={y0} x2={x1} y2={y1} style={styles.fan.spoke} />
            {/* what it is */}
            {icon}
            {/* a ring that makes the whole satellite easy to pick, and shows when it has the focus */}
            <circle cx={x} cy={y} r={ring} style={styles.fan.ring} />
            {/* the focus, drawn the way a picked factory is */}
            {focused && <circle cx={x} cy={y} r={focusRing} style={styles.fan.focus} />}
            {/* the label */}
            <text x={lx} y={ly} style={{ ...styles.fan.label, textAnchor: "start" }}>{text}</text>
        </g>
    )
}


// the way back, below the factory: a quiet "undo", which says where it goes when the pointer
// rests on it
const Back = ({ label, center, focused, onFocus, onChoose }) => {
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
        <g style={styles.fan.satellite} onClick={onClick} onPointerEnter={onFocus}
            data-qed-satellite="back" data-qed-focused={focused}>
            {/* where it goes, for the pointer that rests on it */}
            <title>{label}</title>
            {/* an invisible patch that makes it easy to pick */}
            <rect x={x - 1} y={y - 0.45} width={2} height={0.7} style={styles.fan.ring} />
            {/* the word, brighter when it has the focus */}
            <text x={x} y={y} style={focused ? styles.fan.undo.hover : styles.fan.undo.rest}>undo</text>
        </g>
    )
}


// the choice of a new instance of the class with {family}
const fresh = family => ({ name: "new…", create: family })


// whether a {satellite} is a class: neither a family of them nor a new instance
const isClass = satellite => !satellite.members && !satellite.create


// what tells a {satellite} apart from the others on its arc
const key = satellite => satellite.create ? "new" : satellite.family ?? satellite.name


// the name of the protocol of a catalog {group}, the way its own entry spells it
const protocolName = group => group?.entries.find(entry => entry.level === "protocol")?.name ?? "protocol"


// the ink of the labels, per unit of their font size, as inconsolata draws it: every character
// advances half the size, the tallest letters reach two thirds of it above the baseline, and the
// ones that dip go a sixth of it below
const ink = { advance: 0.5, ascent: 0.67, descent: 0.17 }
// how far the ink of a label stays from what is drawn at its satellite
const clearance = 0.2
// the radius of the ring that shows the focus, the one a picked factory has
const focusRing = 0.75
// the radius of the invisible ring that makes a satellite easy to pick, past which the field that
// names a new instance goes
const ring = 0.95


// where the label {text} of a satellite at {x}, {y}, whose spoke points along {a}, starts and
// sits; the box of its ink is placed at the same {clearance} from the satellite, whichever way the
// spoke points: its center goes out along the spoke past the satellite, then over by half the box,
// on the side of the axis the satellite is on and the way the spoke points vertically, so that the
// corner of the box nearest the satellite is what keeps the distance; labels counterclockwise of
// the axis end at their satellite, the ones clockwise of it start there, and the one on the axis
// is centered on its spoke; a {level} label goes level with its satellite instead, on the side
// away from where its arc leans, which suits an opened family or class, whose members fan out
// along its spoke, and a satellite alone on its arc, unless it is held to the {left}; with
// {ring}, the distance is kept from the ring that shows the focus, rather than from what is drawn
// at the satellite
const labelAt = ({ x, y, a, side, level, ring, family, text, left = false }) => {
    // the size of the font
    const size = styles.fan.label.fontSize
    // the box of the ink of the label
    const w = text.length * ink.advance * size
    const h = (ink.ascent + ink.descent) * size
    // what the label keeps its distance from: the ring that shows the focus, or what is drawn at
    // the satellite, the cluster of a family or the puck of a class
    const r = ring ? focusRing : family ? 0.64 : 0.6
    // the direction the box is pushed out along: down the spoke, or, for a label that is level
    // with its satellite, sideways, away from where its arc leans, unless it is held to the {left}
    const lean = left ? -1 : Math.cos(a) < 0 ? 1 : -1
    const nx = level ? lean : Math.cos(a)
    const ny = level ? 0 : Math.sin(a)
    // which way the box hangs off that point: sideways with the side of the axis, or with the
    // direction it was pushed for a level label; vertically the way the spoke points
    const sx = level ? lean : side
    const sy = level ? 0 : Math.sign(ny)
    // the center of the box
    const cx = x + (r + clearance) * nx + sx * w / 2
    // the box of a label on the axis is centered on its spoke and straddles it, so its edge, not
    // a corner, is what is nearest, and the whole distance goes vertically
    const cy = !level && side === 0
        ? y + sy * (r + clearance + h / 2)
        : y + (r + clearance) * ny + sy * h / 2
    // and where the text starts, on its baseline
    return { lx: cx - w / 2, ly: cy - h / 2 + ink.ascent * size }
}


// the arc of the families, around the factory: straight up, spread over most of a half circle,
// and close in but clear of the label of the factory
const families = { axis: null, span: 176, closest: 3.2, gap: 0.9 }
// the arc of the members of a family, around it: along the spoke that led to it, spread less
// widely so they keep leaning away from the factory, and clear of the cluster of the family
const members = { span: 150, closest: 2.8, gap: 0.95 }


// where satellite {k} of {n} goes: on an arc around {origin}, symmetric about its {axis}, a fixed
// angle apart so that a few choices sit close together, and further out once it gets crowded; the
// arc hangs off the grip of the factory unless it has an {origin}, a spot of an earlier arc, whose
// spoke is the axis; angles are in degrees, distances in diagram units relative to the grip
const place = ({ k, n, origin = null, axis = null, span, closest, gap }) => {
    // the axis: along the spoke of the origin, or straight up
    const center = origin?.angle ?? axis ?? -90
    // the angle between neighbors, smaller as they multiply so the arc stays within its span
    const step = n > 1 ? Math.min(40, span / (n - 1)) : 0
    // the reach that keeps the rings of neighbors just clear of each other
    const ideal = n > 1 ? 2.05 / (2 * Math.sin(step * Math.PI / 360)) : closest
    // close in, but not too far out once it gets crowded
    const reach = Math.min(Math.max(ideal, closest), 6.5)
    // the angle of this one
    const angle = center + (k - (n - 1) / 2) * step
    // where the arc hangs from
    const from = { x: origin?.x ?? 0, y: origin?.y ?? 0 }
    // assemble
    return {
        angle, axis: center, from, gap, lone: n === 1,
        x: from.x + reach * Math.cos(angle * Math.PI / 180),
        y: from.y + reach * Math.sin(angle * Math.PI / 180),
    }
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
