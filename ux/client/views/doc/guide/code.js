// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'
// syntax highlighting
import SyntaxHighlighter from 'react-syntax-highlighter'

// project
// paint
import { theme } from '~/palette'

// local
// paint
import hljs from './hljs'


// code fragments
export const Code = ({ className, ...properties }) => {
    // attempt to deduce the language
    const match = /language-(\w+)/.exec(className || "")
    // if we recognize the language
    if (match) {
        // use the syntax highlighter
        return (
            <SyntaxHighlighter style={hljs} language={match[1]} PreTag="div" {...properties} />
        )
    }
    // otherwise, render a code fragment
    return (
        <Inlay className={className} {...properties} />
    )

}


// the simply decorated code fragment
const Inlay = styled.code`
    font-family: "inconsolata";
    font-size: medium;
    color: ${props => theme.page.highlight};
`


// end of file
