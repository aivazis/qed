// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Tray } from '~/widgets'

// locals
// styles
import styles from './styles'


// the width the chunk map may take, in pixels
const room = 360


// the chunk map: every cell of the chunk grid, colored by what its chunk holds
export const Chunks = ({ layout, focus, setFocus }) => {
    // unpack the grid
    const { rows, cols, states, codes, sizes, pages } = layout.grid
    // the color of each state, with the fill told apart by whether the library knows its value
    const tint = { ...styles.states, fill: styles.fill(layout.fill.agrees) }
    // the size of a cell, in pixels, so the grid fits the panel
    const cell = Math.max(1, Math.floor(room / Math.max(rows, cols)))
    // the canvas; it is kept as state, since collapsing the tray unmounts it and expanding it
    // mounts a fresh one, which must be drawn on too
    const [node, setNode] = React.useState(null)
    // the cell under the pointer
    const [hover, setHover] = React.useState(null)

    // draw the grid whenever it or the canvas changes
    React.useEffect(() => {
        // if the canvas is not there yet
        if (!node) {
            // there is nothing to draw on
            return
        }
        // get its context
        const context = node.getContext("2d")
        // start afresh
        context.clearRect(0, 0, node.width, node.height)
        // go through the cells
        codes.forEach((code, index) => {
            // paint each one in the color of its state
            context.fillStyle = tint[states[code]]
            // leaving a hairline between cells when they are large enough to show it
            const gap = cell > 3 ? 1 : 0
            // at its place on the grid
            context.fillRect(
                (index % cols) * cell, Math.floor(index / cols) * cell, cell - gap, cell - gap
            )
        })
        // with a page in focus
        if (focus !== null) {
            // outline the chunks that start on it, which a reader fetches together
            context.strokeStyle = styles.focus
            context.lineWidth = cell > 3 ? 2 : 1
            // go through the cells
            pages.forEach((page, index) => {
                // the ones on the page in focus
                if (page === focus) {
                    // get an outline, inside the cell
                    context.strokeRect(
                        (index % cols) * cell + 1, Math.floor(index / cols) * cell + 1,
                        Math.max(1, cell - 3), Math.max(1, cell - 3)
                    )
                }
            })
        }
        // all done
        return
    }, [node, codes, pages, rows, cols, cell, focus])

    // the census of the states
    const census = states.map((name, code) => [name, codes.filter(c => c === code).length])
    // find the cell under the pointer
    const track = event => {
        // the position of the pointer on the canvas
        const box = event.currentTarget.getBoundingClientRect()
        const col = Math.floor((event.clientX - box.left) / cell)
        const row = Math.floor((event.clientY - box.top) / cell)
        // off the grid
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            // there is no cell
            setHover(null)
            // nor a page in focus
            setFocus(null)
            // and nothing more to do
            return
        }
        // the index of the cell
        const index = row * cols + col
        // remember it
        setHover({ row, col, state: states[codes[index]], size: sizes[index], page: pages[index] })
        // and put the page of its chunk in focus, if it has one
        setFocus(pages[index] >= 0 ? pages[index] : null)
        // all done
        return
    }
    // let go of the cell
    const leave = () => {
        // forget it
        setHover(null)
        // and let go of the focus
        setFocus(null)
        // all done
        return
    }

    // render
    return (
        <Tray title="chunks" initially={true} state="enabled" scale={0.5}>
            <Housing>
                <canvas ref={setNode} width={cols * cell} height={rows * cell}
                    onMouseMove={track} onMouseLeave={leave}
                    role="img" aria-label={census.map(([name, count]) => `${name}: ${count}`).join(", ")}
                    data-qed-view="chunk-map" data-qed-chunk={hover ? `${hover.row},${hover.col}` : ""}
                />
                <Legend>
                    {census.map(([name, count]) => (
                        <Key key={name} data-qed-state={name} data-qed-count={count}>
                            <Swatch color={tint[name]} />
                            {name} {count}
                        </Key>
                    ))}
                </Legend>
                <Readout>
                    {hover
                        ? `chunk ${hover.row}, ${hover.col}: ${hover.state}`
                        + (hover.size ? `, ${hover.size} bytes` : "")
                        + (hover.page >= 0 ? `, on page ${hover.page} with the outlined chunks` : "")
                        : "hover over a chunk to see what it holds"}
                </Readout>
            </Housing>
        </Tray>
    )
}


// the housing
const Housing = styled.div`
    margin: 0.25rem 1.0rem 0.5rem 1.0rem;
    font-family: inconsolata;
    font-size: 90%;
    cursor: default;
    color: ${styles.dim};
`

// the legend
const Legend = styled.div`
    display: flex;
    flex-wrap: wrap;
    margin-top: 0.25rem;
`

// an entry in the legend
const Key = styled.span`
    display: inline-flex;
    align-items: center;
    margin-right: 0.75rem;
`

// the swatch of a state
const Swatch = styled.span`
    display: inline-block;
    width: 0.6rem;
    height: 0.6rem;
    margin-right: 0.25rem;
    background-color: ${props => props.color};
`

// what is under the pointer
const Readout = styled.div`
    margin-top: 0.25rem;
    color: ${styles.normal};
`


// end of file
