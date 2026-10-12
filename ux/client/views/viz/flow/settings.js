// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the paint of the choices of the forms, so the suggestions of a closed set read the same way
import { enumValue } from '~/views/explorer/form'

// local
// the drag in progress, which the column follows
import { useDrag } from './drag'
// the fields over the canvas
import { InlineField, spotOf } from './inlineField'
// the values the server suggests for a setting
import { useSuggestions } from './useSuggestions'
// the projection, which places the settings under their factory
import { useProjection } from './projection'
// paint
import styles from './styles'


// what hangs below the factories whose hub was clicked: a string of their traits and one of their
// methods, each folded behind a bead of its own; the canvas holds which columns and strings are out, the setting being edited, if
// any, and what the methods that were invoked handed back
const SettingsContext = React.createContext(null)


// the state of what hangs below the {factories} of the {diagram}: which strings are out, the setting
// being edited, if any, and the outcome of the last call of each method; a change of a setting goes
// to the server through {configure}, a call of a method through {invoke}
export const useSettingsState = ({ diagram, factories, configure, invoke }) => {
    // the ids of the factories whose hub was clicked, which have their column out
    const [hung, setHung] = React.useState([])
    // the strings that are out, by factory and then by group, "traits" or "methods"
    const [open, setOpen] = React.useState({})
    // the setting being edited: its factory, its trait, where its bead is on the screen, what
    // is asked for, the text it started with, the text so far, the name of the instance to make,
    // and the last refusal
    const [editing, setEditing] = React.useState(null)
    // the outcome of the last call of each method, by factory and method: whether it is under
    // way, what it handed back, and why it failed, if it did
    const [calls, setCalls] = React.useState({})
    // the factories that are still on the diagram and have their column out
    const shown = factories.filter(factory => hung.includes(factory.id))
    // hang the column of the factory with {id}, or take it down if it is out
    const toggle = id => {
        // flip it
        setHung(old => old.includes(id) ? old.filter(other => other !== id) : [...old, id])
        // all done
        return
    }
    // whether the {group} of the factory with {id} is out
    const isOpen = (id, group) => open[id]?.[group] ?? false
    // fold the {group} of the factory with {id}, or spread it out
    const fold = (id, group) => {
        // flip it
        setOpen(old => ({ ...old, [id]: { ...old[id], [group]: !(old[id]?.[group] ?? false) } }))
        // all done
        return
    }
    // start editing the setting {trait} of {factory}, whose bead is at {spot} on the screen
    const edit = ({ factory, trait, spot }) => {
        // with its value as the starting text
        setEditing({
            factory: factory.id, level: factory.level, trait: trait.name, spot,
            stage: "value", start: trait.value ?? "", value: trait.value ?? "", name: "", error: null,
        })
        // all done
        return
    }
    // stop editing, leaving the setting as it was
    const cancel = () => {
        // forget the edit
        setEditing(null)
        // all done
        return
    }
    // record what was typed into the field that is asked for
    const type = text => {
        // in the field of the stage
        setEditing(old => old && { ...old, [old.stage]: text, error: null })
        // all done
        return
    }
    // take what was typed, or the {chosen} value, when one was picked from the suggestions: a
    // value for a factory pinned to a class asks for the name of the instance to make next;
    // everything else goes to the server
    const commit = (chosen = null) => {
        // with nothing being edited
        if (!editing) {
            // there is nothing to do
            return
        }
        // the value: the one picked, if any, or the one typed
        const value = chosen !== null && editing.stage === "value" ? chosen : editing.value
        // a new value for a factory pinned to a class
        if (editing.stage === "value" && editing.level === "class") {
            // needs the name of the instance that will carry it
            setEditing({ ...editing, value, stage: "name", error: null })
            // all done
            return
        }
        // send the change
        configure({
            id: editing.factory, trait: editing.trait, value,
            name: editing.stage === "name" ? editing.name.trim() : null,
        }, error => {
            // a change that was made
            if (error === null) {
                // ends the edit
                setEditing(null)
                // all done
                return
            }
            // one that was refused stays open, with the reason
            setEditing(old => old && { ...old, error })
            // all done
            return
        })
        // all done
        return
    }
    // invoke {method} of the instance {factory} is pinned to
    const call = ({ factory, method }) => {
        // the key of the call
        const key = `${factory.id}/${method.name}`
        // note that it is under way
        setCalls(old => ({ ...old, [key]: { busy: true, result: null, error: null } }))
        // send it, and record what comes back
        invoke({ id: factory.id, method: method.name }, ({ result, error }) => {
            // as the outcome of the call
            setCalls(old => ({ ...old, [key]: { busy: false, result, error } }))
            // all done
            return
        })
        // all done
        return
    }
    // the outcome of the last call of {method} of {factory}, if there was one
    const outcome = (factory, method) => calls[`${factory.id}/${method.name}`] ?? null
    // publish
    return { diagram, shown, toggle, isOpen, fold, editing, edit, cancel, type, commit, call, outcome }
}


// hand the state of the {settings} to the nodes and the layer that draws them
export const SettingsProvider = ({ settings, children }) => {
    // render
    return <SettingsContext.Provider value={settings}>{children}</SettingsContext.Provider>
}


// access to the settings, or nothing outside a canvas that has them
export const useSettings = () => React.useContext(SettingsContext)


// what hangs below each factory whose hub was clicked
export const Settings = () => {
    // the state
    const settings = useSettings()
    // with no columns out
    if (!settings?.shown.length) {
        // there is nothing to draw
        return null
    }
    // render
    return (
        <g>
            {settings.shown.map(factory => <Column key={factory.id} factory={factory} />)}
        </g>
    )
}


// the field that edits a setting, over the canvas, in place of the value of the setting; it is
// plain html, placed in screen coordinates, in the size of the label it stands in for; below it,
// the values the server suggests, in a list that scrolls, since there may be lots of them: a
// setting that takes one of a closed set marks the one it has, the way the forms mark their
// choices; once something is typed, the list keeps only the suggestions that contain it
export const SettingEditor = () => {
    // the state
    const settings = useSettings()
    // the field, so it can take the focus and keep its keys to itself
    const field = React.useRef(null)
    // the edit in progress
    const editing = settings?.editing ?? null
    // the suggestions for the value being edited
    const suggestions = useSuggestions({
        diagram: settings?.diagram ?? null,
        node: editing?.factory ?? null,
        trait: editing?.stage === "value" ? editing.trait : null,
    })
    // the suggestions on show: all of them, until something is typed that tells them apart
    const shown = narrow({ suggestions, editing })
    // the one the arrow keys picked, if any
    const [pick, setPick] = React.useState(-1)
    // a new list starts with nothing picked
    React.useEffect(() => setPick(-1), [shown.length, editing?.factory, editing?.trait])
    // the state as it is now, for the keys of the field, whose listener outlives a render
    const latest = React.useRef(null)
    latest.current = { settings, shown, pick }
    // whenever a field shows up, or the stage changes
    React.useEffect(() => {
        // the field
        const input = field.current
        // if there is none
        if (!input) {
            // there is nothing to do
            return
        }
        // take the focus, with the caret after the text
        input.focus()
        input.setSelectionRange(input.value.length, input.value.length)
        // the keys typed here are for the field only: the canvas, the camera among them, listens
        // to them on its container, and react hears them only once they reach the root, so the
        // field handles its own: the arrows walk the suggestions, <enter> takes the one picked or
        // the text, <escape> leaves it
        const keep = evt => {
            // none of them go any further
            evt.stopPropagation()
            // the state as it is now
            const { settings, shown, pick } = latest.current
            // down the list
            if (evt.key === "ArrowDown" && shown.length) {
                // keep the caret where it is
                evt.preventDefault()
                // pick the next one, stopping at the last
                setPick(Math.min(pick + 1, shown.length - 1))
                // all done
                return
            }
            // up the list
            if (evt.key === "ArrowUp" && shown.length) {
                // keep the caret where it is
                evt.preventDefault()
                // pick the previous one, or none above the first
                setPick(Math.max(pick - 1, -1))
                // all done
                return
            }
            // take it
            if (evt.key === "Enter") {
                // the suggestion picked, if any, or the text
                settings.commit(pick >= 0 ? shown[pick].value : null)
                // all done
                return
            }
            // leave it
            if (evt.key === "Escape") {
                // as it was
                settings.cancel()
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
    }, [editing?.factory, editing?.trait, editing?.stage])
    // with nothing being edited
    if (!editing) {
        // there is nothing to show
        return null
    }
    // what has been typed for what is being asked for
    const text = editing[editing.stage]
    // render
    return (
        <InlineField spot={editing.spot} prompt={editing.stage === "name" ? "name" : null}
            value={text} placeholder={editing.stage === "name" ? "unnamed" : ""}
            error={editing.error} field={field} onChange={settings.type}
            onBlur={settings.cancel} data-qed-setting-editor={editing.trait}>
            {editing.stage === "value" && suggestions?.choices.length > 0 &&
                <Suggestions suggestions={suggestions} shown={shown} pick={pick} setPick={setPick}
                    current={editing.start} take={settings.commit} />
            }
        </InlineField>
    )
}


// the list of the {suggestions} {shown} below a field, with the one the arrows {pick}ed brought
// into view; in a closed set, the {current} value is marked; a click {take}s a suggestion
const Suggestions = ({ suggestions, shown, pick, setPick, current, take }) => {
    // the row that is picked, so it can be brought into view
    const picked = React.useRef(null)
    // and the one of the current value of a closed set, which is brought into view to start with
    const marked = React.useRef(null)
    // when the list shows up
    React.useEffect(() => {
        // bring the current value into view, if it is among them, moving the list as little as
        // possible
        marked.current?.scrollIntoView({ block: "nearest" })
        // all done
        return
    }, [])
    // whenever the pick changes
    React.useEffect(() => {
        // bring it into view, if there is one, moving the list as little as possible
        picked.current?.scrollIntoView({ block: "nearest" })
        // all done
        return
    }, [pick])
    // how many there are, and how many are on show
    const total = suggestions.choices.length
    const count = shown.length === total ? `${total}` : `${shown.length} of ${total}`
    // render
    return (
        <div style={styles.inline.suggestions.box} data-qed-suggestions={suggestions.closed ? "closed" : "open"}>
            {/* how many */}
            <div style={styles.inline.suggestions.count}>
                {count} {suggestions.closed ? "choices" : "suggestions"}
            </div>
            {/* the list, which scrolls */}
            <div style={styles.inline.suggestions.list}>
                {shown.map((choice, k) => {
                    // whether it is the current one of a closed set, which is marked
                    const isCurrent = suggestions.closed && choice.value === current
                    // the paint of the choice
                    const Choice = enumValue(isCurrent ? "selected" : "enabled")
                    // render
                    return (
                        <div key={choice.value} ref={k === pick ? picked : isCurrent ? marked : null}
                            style={k === pick ? styles.inline.suggestions.picked : styles.inline.suggestions.row}
                            data-qed-suggestion={choice.value}
                            // a press must not take the focus from the field, which would end the edit
                            onMouseDown={evt => evt.preventDefault()}
                            onMouseEnter={() => setPick(k)}
                            onClick={() => take(choice.value)}>
                            <Choice>{choice.label}</Choice>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}


// the suggestions on show while {editing}: all of them, until the text differs from the one the
// edit started with, and then the ones whose value or label contain it, whatever the case
const narrow = ({ suggestions, editing }) => {
    // with no suggestions
    if (!suggestions || !editing) {
        // there is nothing to show
        return []
    }
    // the text so far
    const text = editing.value.trim().toLowerCase()
    // until something is typed that differs from where the edit started
    if (!text || editing.value === editing.start) {
        // all of them are on show
        return suggestions.choices
    }
    // otherwise, only the ones that contain the text
    return suggestions.choices.filter(
        choice => choice.value.toLowerCase().includes(text) || choice.label.toLowerCase().includes(text)
    )
}


// what hangs below one {factory}: a stem from its hub, with a blue bead that spreads out its
// traits, which are data, and a green one that spreads out its methods; the bead of a trait is
// filled once the factory is an instance, since only then do its traits hold values, and so is
// the bead of a method, since only then can it be invoked; a click on a trait that can be changed
// from the diagram opens a field to change it, and a click on a method invokes it
const Column = ({ factory }) => {
    // the state
    const settings = useSettings()
    // the projection, which places things on the screen
    const { project } = useProjection()
    // the column follows its factory while it is dragged
    const { dx, dy, dz } = useDrag().shiftOf(factory.id)
    // the traits of the factory that are data rather than slots
    const traits = factory.traits.filter(trait => trait.kind === "setting")
    // and its methods
    const methods = factory.methods
    // whether it is an instance, which fills the beads
    const instance = factory.level === "instance"
    // the rows of the column, from the top: each string behind its bead, when it is out
    const rows = [
        ...strand({ group: "traits", items: traits, open: settings.isOpen(factory.id, "traits") }),
        ...strand({ group: "methods", items: methods, open: settings.isOpen(factory.id, "methods") }),
    ]
    // where the factory is on the diagram, and where it is headed during a drag
    const [x, y, z] = [factory.at.x + dx, factory.at.y + dy, (factory.at.z ?? 0) + dz]
    // where each bead goes: down the column, a step apart, starting a little below the hub
    const spots = rows.map((_, k) => project({ x, y: y + first + k * step, z }))
    // where the stem starts, just below the hub, and where it ends
    const top = project({ x, y: y + 0.4, z })
    const bottom = spots.length ? spots[spots.length - 1] : top
    // a click on a trait opens its field, right after its label, if it can be changed
    const edit = (trait, evt) => {
        // the canvas clears the selection on a click, so keep this one to myself
        evt.stopPropagation()
        // a trait that cannot be changed from the diagram
        if (!trait.editable) {
            // stays as it is
            return
        }
        // the label of the trait, its value, and the panel the field goes on
        const label = evt.currentTarget.querySelector("text")
        const value = label.querySelector("tspan")
        const panel = evt.currentTarget.closest("section")
        // open the field over the value, in the size of the label
        settings.edit({ factory, trait, spot: spotOf({ label, panel, over: value }) })
        // all done
        return
    }
    // how far the label of {trait} moves while its field is up, so the two line up to the pixel
    const shiftOf = trait => {
        // the edit in progress
        const editing = settings.editing
        // the label of the trait being edited
        if (editing?.factory === factory.id && editing.trait === trait.name) {
            // moves as far as its field asked for
            return editing.spot.shift ?? 0
        }
        // the rest stay where they are
        return 0
    }
    // a click on a method invokes it, if it can be
    const call = (method, evt) => {
        // keep the click to myself
        evt.stopPropagation()
        // a method of a factory that is not an instance yet
        if (!method.invocable) {
            // has nothing to be invoked on
            return
        }
        // invoke it
        settings.call({ factory, method })
        // all done
        return
    }
    // a click on the bead of a string folds it or spreads it out
    const toggle = (group, evt) => {
        // keep the click to myself
        evt.stopPropagation()
        // flip it
        settings.fold(factory.id, group)
        // all done
        return
    }
    // render
    return (
        <g data-qed-settings={factory.id}>
            {/* the stem */}
            <line x1={top.x} y1={top.y} x2={bottom.x} y2={bottom.y} style={styles.settings.stem}
                pointerEvents="none" />
            {/* the rows */}
            {rows.map((row, k) => {
                // where it goes
                const spot = spots[k]
                // the bead of a string
                if (row.kind === "expander") {
                    // render
                    return (
                        <Expander key={row.group} group={row.group} spot={spot} open={row.open}
                            onClick={evt => toggle(row.group, evt)} />
                    )
                }
                // a trait
                if (row.kind === "traits") {
                    // render
                    return (
                        <Trait key={`trait:${row.item.name}`} trait={row.item} spot={spot}
                            instance={instance} shift={shiftOf(row.item)}
                            onClick={evt => edit(row.item, evt)} />
                    )
                }
                // a method
                return (
                    <Method key={`method:${row.item.name}`} method={row.item} spot={spot}
                        outcome={settings.outcome(factory, row.item)}
                        onClick={evt => call(row.item, evt)} />
                )
            })}
        </g>
    )
}


// the rows of a string of {items} of a {group}: the bead that folds it, followed by the items, when
// it is {open}; a factory with no items in the group has no string
const strand = ({ group, items, open }) => {
    // with nothing in it
    if (!items.length) {
        // there is no string
        return []
    }
    // the bead, and the items when it is out
    return [
        { kind: "expander", group, open },
        ...(open ? items.map(item => ({ kind: group, item })) : []),
    ]
}


// the bead that folds the string of a {group} at {spot}, with a "+" when it is folded and a "-"
// when it is out, and the name of the group next to it
const Expander = ({ group, spot, open, onClick }) => {
    // the paint of the group
    const paint = styles.settings.expander[group]
    // half the length of the arms of the glyph
    const arm = 0.14
    // render
    return (
        <g data-qed-expander={group} data-qed-open={open} style={styles.settings.clickable}
            onClick={onClick}>
            <title>{open ? `fold the ${group}` : `show the ${group}`}</title>
            {/* what the pointer hits */}
            <Row spot={spot} chars={group.length} />
            {/* no ring, just a patch of the page that hides the stem behind the glyph, so a "-"
                does not read as a "+" */}
            <circle cx={spot.x} cy={spot.y} r={0.25} style={styles.settings.expander.patch} />
            <line x1={spot.x - arm} y1={spot.y} x2={spot.x + arm} y2={spot.y} style={paint.glyph} />
            {!open && (
                <line x1={spot.x} y1={spot.y - arm} x2={spot.x} y2={spot.y + arm} style={paint.glyph} />
            )}
            <text x={spot.x + 0.5} y={spot.y + 0.15} style={paint.label} pointerEvents="none">
                {group}
            </text>
        </g>
    )
}


// the bead of a {trait} at {spot}, filled when the factory is an {instance}, labeled with its
// name and its value: a value that was never set reads as "none", dimmer; the label moves by
// {shift} while it is edited, onto the pixel the text of its field lands on
const Trait = ({ trait, spot, instance, shift, onClick }) => {
    // a value of {None} means it was never set
    const unset = trait.value === null
    // render
    return (
        <g data-qed-setting={trait.name} data-qed-editable={trait.editable}
            style={trait.editable ? styles.settings.clickable : undefined} onClick={onClick}>
            <title>{trait.doc ?? trait.name}</title>
            {/* what the pointer hits: the name, its colon, the room after it, and the value */}
            <Row spot={spot} chars={trait.name.length + 2 + show(trait.value).length} />
            <circle cx={spot.x} cy={spot.y} r={0.25}
                style={instance ? styles.settings.trait.instance : styles.settings.trait.blank} />
            <text x={spot.x + 0.5} y={spot.y + 0.15 + shift} style={styles.settings.name}
                pointerEvents="none">
                {trait.name}:
                <tspan dx={separation} style={unset ? styles.settings.unset : styles.settings.value}>
                    {show(trait.value)}
                </tspan>
            </text>
        </g>
    )
}


// the bead of a {method} at {spot}, filled when it can be invoked, labeled with its name and the
// {outcome} of its last call, if any
const Method = ({ method, spot, outcome, onClick }) => {
    // render
    return (
        <g data-qed-method={method.name} data-qed-invocable={method.invocable}
            style={method.invocable ? styles.settings.clickable : undefined} onClick={onClick}>
            <title>{method.doc ?? method.name}</title>
            {/* what the pointer hits: the name of the method, and what its last call handed back */}
            <Row spot={spot} chars={method.name.length + told(outcome)} />
            <circle cx={spot.x} cy={spot.y} r={0.25}
                style={method.invocable ? styles.settings.method.instance : styles.settings.method.blank} />
            <text x={spot.x + 0.5} y={spot.y + 0.15} style={styles.settings.method.name}
                pointerEvents="none">
                {method.name}
                {outcome && <Outcome outcome={outcome} />}
            </text>
        </g>
    )
}


// what the last call of a method handed back: that it is under way, why it failed, or its result
const Outcome = ({ outcome }) => {
    // a call that is under way
    if (outcome.busy) {
        // says so
        return <tspan dx={separation} style={styles.settings.unset}>…</tspan>
    }
    // a call that failed
    if (outcome.error !== null) {
        // says why
        return <tspan dx={separation} style={styles.settings.failure}>{outcome.error}</tspan>
    }
    // otherwise, show what it handed back
    return (
        <tspan dx={separation} style={outcome.result === null ? styles.settings.unset : styles.settings.value}>
            → {show(outcome.result)}
        </tspan>
    )
}


// what the pointer hits in a row of the column at {spot}: its bead, and a label of {chars}
// characters after it, one row tall, so neighboring rows never overlap; the text of the labels
// stays out of the pointer's way, since webkit hit-tests text drawn this small, scaled up by the
// camera, well beyond what it covers, and would hand a click on one row to the label of the next
const Row = ({ spot, chars }) => {
    // render
    return (
        <rect x={spot.x - 0.35} y={spot.y - step / 2} width={0.85 + chars * advance} height={step}
            style={styles.settings.row} />
    )
}


// how many characters the {outcome} of the last call of a method takes after its name, counting
// the room in front of it: none without a call, the ellipsis of one under way, the reason it
// failed, or the arrow and what it handed back
const told = outcome => {
    // without a call
    if (!outcome) {
        // there is nothing after the name
        return 0
    }
    // what follows the name, the way {Outcome} shows it
    const text = outcome.busy ? "…" : outcome.error !== null ? outcome.error : `→ ${show(outcome.result)}`
    // and the room in front of it
    return 1 + text.length
}


// how a {value} reads: a setting that was never set says so, and an empty string shows its quotes
const show = value => value === null ? "none" : value === "" ? '""' : value


// how far below the hub the first bead goes, and how far apart they are, in diagram units: whole
// steps, so every bead sits on a point of the grid, where the nodes of the diagram sit, and the
// beads can be bound to some day the way slots are
const first = 1
const step = 1
// how far a character of the label font advances, in diagram units: inconsolata gives every
// character half of its size, and the labels are 0.45 units tall
const advance = 0.225
// the room between the colon after a name and its value: one character of the label font
const separation = advance


// end of file
