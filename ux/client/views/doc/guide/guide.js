// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// routing
import { Routes, Route } from 'react-router-dom'
// syntax highlighting
import SyntaxHighlighter from 'react-syntax-highlighter'


// project
// hooks
import { useActivityPanel } from '~/views'
// widgets
import { Flex } from '~/widgets'

// local
// components
import { TOC } from '../toc'
import { Page } from './page'
import { Title, Section, Subsection, Text } from './theme'
// pages
import Intro from './intro.mdx'
// paint
import hljs from './hljs'
import { flex, toc } from './styles'


// the panel
export const Guide = () => {
    // the activity panel state
    const { activityPanel } = useActivityPanel()

    // mix my paint: copy the toc paint
    const tocPaint = { ...toc }
    // so we can hide it when its not visible
    tocPaint.panel.display = activityPanel ? "flex" : "none"

    // render
    return (
        <Flex.Box direction="row" style={flex}>
            {/* the table of contents */}
            <Flex.Panel min={300} style={tocPaint}>
                <TOC />
            </Flex.Panel>

            {/* the panel with the current page */}
            <Flex.Panel style={flex}>
                <Routes>
                    {topics.map(topic => (
                        <Route key={topic.name} path={topic.name}
                            element={<Page>{topic.page}</Page>} />
                    ))}
                </Routes>
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
    // syntax highlighted code
    code: ({ className, ...properties }) => {
        // attempt to deduce the language
        const match = /language-(\w+)/.exec(className || "")
        console.log(className, properties)
        // pick a renderer
        return match
            ? <SyntaxHighlighter style={hljs} language={match[1]} PreTag="div" {...properties} />
            : <code className={className} {...properties} />
    }
}

// the list of topics
const topics = [
    { name: "intro", page: <Intro components={theme} /> },
]



// end of file
