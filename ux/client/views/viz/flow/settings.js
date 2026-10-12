// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// the fields over the canvas
import { InlineField } from './inlineField'
// the projection, which places the settings under their factory
import { useProjection } from './projection'
// paint
import styles from './styles'


// the settings of the factories whose hub was clicked, spread out below them; the canvas holds
// which factories have theirs out, and the one being edited, if any
const SettingsContext = React.createContext(null)


// the state of the settings: which factories, among the {factories} of the diagram, have their
// settings spread out, and the setting being edited, if any; a change goes to the server through
// {configure}; a factory that is gone takes its settings along
export const useSettingsState = ({ factories, configure }) => {
    // the ids of the factories whose settings are out
    const [open, setOpen] = React.useState([])
    // the setting being edited: its factory, its trait, where its bead is on the screen, what
    // is asked for, the text so far, the name of the instance to make, and the last refusal
    const [editing, setEditing] = React.useState(null)
    // the ones that are still on the diagram, and pinned far enough down to have settings
    const shown = factories.filter(factory => open.includes(factory.id) && factory.level !== "protocol")
    // spread out the settings of the factory with {id}, or fold them if they are out
    const toggle = id => {
        // flip it
        setOpen(old => old.includes(id) ? old.filter(other => other !== id) : [...old, id])
        // all done
        return
    }
    // start editing the setting {trait} of {factory}, whose bead is at {spot} on the screen
    const edit = ({ factory, trait, spot }) => {
        // with its value as the starting text
        setEditing({
            factory: factory.id, level: factory.level, trait: trait.name, spot,
            stage: "value", value: trait.value ?? "", name: "", error: null,
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
    // take what was typed: a value for a factory pinned to a class asks for the name of the
    // instance to make next; everything else goes to the server
    const commit = () => {
        // with nothing being edited
        if (!editing) {
            // there is nothing to do
            return
        }
        // a new value for a factory pinned to a class
        if (editing.stage === "value" && editing.level === "class") {
            // needs the name of the instance that will carry it
            setEditing({ ...editing, stage: "name", error: null })
            // all done
            return
        }
        // send the change
        configure({
            id: editing.factory, trait: editing.trait, value: editing.value,
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
    // publish
    return { shown, toggle, editing, edit, cancel, type, commit }
}


// hand the state of the {settings} to the nodes and the layer that draws them
export const SettingsProvider = ({ settings, children }) => {
    // render
    return <SettingsContext.Provider value={settings}>{children}</SettingsContext.Provider>
}


// access to the settings, or nothing outside a canvas that has them
export const useSettings = () => React.useContext(SettingsContext)


// the settings that are out, each column under its factory
export const Settings = () => {
    // the state
    const settings = useSettings()
    // with nothing out
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


// the field that edits a setting, over the canvas, next to the bead of the setting; it is plain
// html, placed in screen coordinates, so its text reads at a normal size whatever the zoom
export const SettingEditor = () => {
    // the state
    const settings = useSettings()
    // the field, so it can take the focus and keep its keys to itself
    const field = React.useRef(null)
    // the edit in progress
    const editing = settings?.editing ?? null
    // the state as it is now, for the keys of the field, whose listener outlives a render
    const latest = React.useRef(settings)
    latest.current = settings
    // whenever a field shows up, or the stage changes
    React.useEffect(() => {
        // the field
        const input = field.current
        // if there is none
        if (!input) {
            // there is nothing to do
            return
        }
        // take the focus, with the text selected so typing replaces it
        input.focus()
        input.select()
        // the keys typed here are for the field only: the canvas, the camera among them, listens
        // to them on its container, and react hears them only once they reach the root, so the
        // field handles its own: <enter> takes the text, <escape> leaves it
        const keep = evt => {
            // none of them go any further
            evt.stopPropagation()
            // take it
            if (evt.key === "Enter") {
                // send it
                latest.current.commit()
                // all done
                return
            }
            // leave it
            if (evt.key === "Escape") {
                // as it was
                latest.current.cancel()
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
            onBlur={settings.cancel} data-qed-setting-editor={editing.trait} />
    )
}


// the settings of one {factory}: a stem that hangs from its hub, with a bead for each setting,
// labeled with its name and its value; a setting that was never set reads as "none", dimmer; a
// click on a setting that can be changed from the diagram opens a field to change it
const Column = ({ factory }) => {
    // the state
    const settings = useSettings()
    // the projection, which places things on the screen
    const { project } = useProjection()
    // the settings of the factory: its traits that are not slots
    const traits = factory.traits.filter(trait => trait.kind === "setting")
    // where the factory is on the diagram
    const { x, y, z } = factory.at
    // where each bead goes: down the column, a step apart, starting a little below the hub
    const spots = traits.map((_, k) => project({ x, y: y + first + k * step, z }))
    // where the stem starts, just below the hub, so the hub stays in reach of the pointer, and
    // where it ends
    const top = project({ x, y: y + 0.4, z })
    const bottom = spots.length ? spots[spots.length - 1] : top
    // a click on a setting opens its field, right after its label, if it can be changed
    const open = (trait, evt) => {
        // the canvas clears the selection on a click, so keep this one to myself
        evt.stopPropagation()
        // a setting that cannot be changed from the diagram
        if (!trait.editable) {
            // stays as it is
            return
        }
        // the panel the field goes on, and where the label of the setting is on the screen
        const panel = evt.currentTarget.closest("section").getBoundingClientRect()
        const label = evt.currentTarget.getBoundingClientRect()
        // open the field there
        settings.edit({
            factory, trait, spot: { x: label.right - panel.left + 8, y: label.top - panel.top - 4 },
        })
        // all done
        return
    }
    // render
    return (
        <g data-qed-settings={factory.id}>
            {/* the stem */}
            <line x1={top.x} y1={top.y} x2={bottom.x} y2={bottom.y} style={styles.settings.stem}
                pointerEvents="none" />
            {/* the beads */}
            {traits.map((trait, k) => {
                // where it goes
                const spot = spots[k]
                // a value of {None} means it was never set, which reads as such, dimmer than a value
                const unset = trait.value === null
                // render
                return (
                    <g key={trait.name} data-qed-setting={trait.name} data-qed-editable={trait.editable}
                        style={trait.editable ? styles.settings.editable : undefined}
                        onClick={evt => open(trait, evt)}>
                        <title>{trait.doc ?? trait.name}</title>
                        <circle cx={spot.x} cy={spot.y} r={0.25} style={styles.settings.bead} />
                        <text x={spot.x + 0.5} y={spot.y + 0.15} style={styles.settings.name}>
                            {trait.name}
                            <tspan dx={0.4} style={unset ? styles.settings.unset : styles.settings.value}>
                                {show(trait.value)}
                            </tspan>
                        </text>
                    </g>
                )
            })}
        </g>
    )
}


// how a {value} reads: a setting that was never set says so, and an empty string shows its quotes
const show = value => value === null ? "none" : value === "" ? '""' : value


// how far below the hub the first bead goes, and how far apart they are, in diagram units
const first = 1.25
const step = 1


// end of file
