// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'


// project
// hooks
import { useTopic, useActivityPanel } from '~/views'
// widgets
import { Flex } from '~/widgets'

// local
// contents
import { topics } from '../contents'
// components
import { TOC } from '../toc'
import { Code } from './code'
import { Page } from './page'
import { Title, Section, Subsection, Text, Bold, Link } from './theme'
// paint
import { flex, toc } from './styles'


// the panel
export const Guide = () => {
    // the current topic
    const { topic } = useTopic()
    // the activity panel state
    const { activityPanel } = useActivityPanel()

    // mix my paint: copy the toc paint
    const tocPaint = { ...toc }
    // so we can hide it when its not visible
    tocPaint.panel.display = activityPanel ? "flex" : "none"

    // find the topic entry
    const entry = topics.find(entry => entry.link === topic)
    // and get its page
    const Topic = entry?.page

    // render
    return (
        <Flex.Box direction="row" style={flex}>
            {/* the table of contents */}
            <Flex.Panel min={300} style={tocPaint}>
                <TOC />
            </Flex.Panel>

            {/* the panel with the current page */}
            <Flex.Panel style={flex}>
                <Page>
                    <Topic components={theme} />
                </Page>
            </Flex.Panel>

        </Flex.Box>
    )

}


// the theme
const theme = {
    // #
    h1: Title,
    // ##
    h2: Section,
    // ###
    h3: Subsection,
    // text
    p: Text,
    strong: Bold,
    // syntax highlighted code
    code: Code,
    // links
    a: Link,
}


// end of file
