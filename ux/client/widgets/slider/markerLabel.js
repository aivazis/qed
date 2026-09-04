// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// local
// hooks
import { useConfig } from './useConfig'
import { useEditor } from './useEditor'
// components
import { Hitbox } from './hitbox'


// render the label of a marker; when the slider is {editable}, a double click on the label
// opens an editor over it that lets the user type the pick, with {check} accepting a candidate
// and {commit} sending an accepted one
export const MarkerLabel = ({ value, name = null, check = null, commit = null }) => {
    // unpack the geometry
    const { enabled, markers, markerLabelPosition, markerPrecision, editable } = useConfig()
    // i can be edited when the client asked for it and told me how
    const active = editable && enabled && name !== null && check !== null && commit !== null
    // set up the editor
    const { node, editing, open, editor } = useEditor({
        name: `${name} value`, end: "value", value: value ?? 0, check, commit, fontSize,
    })

    // if the client does not want the value label
    if (!markers) {
        // bail
        return null
    }
    // if there is no value to show, there is nothing to label
    if (value == null) {
        // so render nothing
        return null
    }

    // pick an implementation based on my state
    const Label = enabled ? Enabled : Disabled
    // set up my behaviors
    const behaviors = {}
    // when i can be edited
    if (active) {
        // on double click, open the editor over me
        behaviors["onDoubleClick"] = open
        // tag me so drivers can find the affordance
        behaviors["data-pyre-widget"] = "slider"
        behaviors["data-pyre-widget-part"] = "pick"
        behaviors["data-pyre-pick"] = name
    }

    // what i show
    const text = value.toFixed(markerPrecision)
    // and where
    const position = markerLabelPosition(value)

    // an editable label gets a hit box behind it, so a double click anywhere on it opens the
    // editor; the behaviors go on the group so both the box and the text respond
    if (active) {
        // render; while the editor is up, the label goes invisible so it does not show through
        return (
            <>
                <g {...behaviors}>
                    <Hitbox x={position.x} y={position.y} text={text} fontSize={fontSize} />
                    <Label ref={node} {...position} visibility={editing ? "hidden" : "visible"}>
                        {text}
                    </Label>
                </g>
                {editor}
            </>
        )
    }

    // render
    return (
        <Label ref={node} {...position}>
            {text}
        </Label>
    )
}


// the font size of a marker label, in intrinsic units
const fontSize = 28


// styling
// the base
const Base = styled.text`
    font-family: inconsolata;
    font-size: ${fontSize}px;
    text-anchor: middle;
    cursor: default;
    user-select: none;
`


const Disabled = styled(Base)`
    fill: ${props => theme.page.dim};
`


const Enabled = styled(Base)`
    & {
        fill: ${props => theme.page.normal};
    }

    [data-pyre-widget-part="pick"] > & {
        cursor: text;
    }

    [data-pyre-widget-part="pick"]:hover > & {
        fill: ${props => theme.page.highlight};
    }
`


// end of file
