// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme, wheel } from '~/palette'
// widgets
import { Spacer } from '~/widgets'
// the paint of the viewer tabs, which this one matches
import viewerPaint from '~/views/viz/viewer/styles'


// the tab across the top of the playground: its name, and the choices of how to look at the
// diagram: flat or isometric and, when isometric, a quarter turn either way, and from above or
// below
export const Tab = ({ view, adjust }) => {
    // whether the view is isometric, which is when the other choices matter
    const iso = view.kind === "iso"
    // render
    return (
        <div style={viewerPaint.tab("selected")} data-qed-tab="playground">
            {/* my name */}
            <Name>pipeline playground</Name>
            <Spacer />
            {/* flat or isometric */}
            {["flat", "iso"].map(kind => (
                <Choice key={kind} $current={view.kind === kind}
                    onClick={() => adjust({ kind })} data-qed-projection={kind}>
                    {kind}
                </Choice>
            ))}
            {/* in an isometric view, the rest */}
            {iso && <Separator>|</Separator>}
            {/* a quarter turn either way */}
            {iso && <Choice onClick={() => adjust({ azimuth: view.azimuth - 1 })}
                title="turn the view a quarter turn to the left" data-qed-turn="left">
                {"\u21ba"}
            </Choice>}
            {iso && <Choice onClick={() => adjust({ azimuth: view.azimuth + 1 })}
                title="turn the view a quarter turn to the right" data-qed-turn="right">
                {"\u21bb"}
            </Choice>}
            {/* from above or below */}
            {iso && <Choice $current={true} onClick={() => adjust({ below: !view.below })}
                title="look from the other side of the floor" data-qed-below={view.below}>
                {view.below ? "below" : "above"}
            </Choice>}
        </div>
    )
}


// the name of the tab
const Name = styled.span`
    font-family: rubik-light;
    font-size: 80%;
    color: ${theme.page.highlight};
    padding: 0 0.5rem;
    cursor: default;
`

// a choice
const Choice = styled.span`
    font-family: inconsolata;
    font-size: 80%;
    padding: 0 0.3rem;
    cursor: pointer;
    color: ${props => props.$current ? theme.page.highlight : theme.page.dim};
    &:hover {
        color: ${theme.page.bright};
    }
`

// between groups of choices
const Separator = styled.span`
    font-family: inconsolata;
    font-size: 80%;
    padding: 0 0.25rem;
    color: ${wheel.gray.concrete};
    cursor: default;
`


// end of file
