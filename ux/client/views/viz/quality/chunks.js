// -*- web -*-
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
export const Chunks = ({ layout }) => {
    // unpack the grid
    const { rows, cols, states, codes, sizes } = layout.grid
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
        // go through the cells
        codes.forEach((code, index) => {
            // paint each one in the color of its state
            context.fillStyle = styles.states[states[code]]
            // leaving a hairline between cells when they are large enough to show it
            const gap = cell > 3 ? 1 : 0
            // at its place on the grid
            context.fillRect(
                (index % cols) * cell, Math.floor(index / cols) * cell, cell - gap, cell - gap
            )
        })
        // all done
        return
    }, [node, codes, rows, cols, cell])

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
            // and nothing more to do
            return
        }
        // the index of the cell
        const index = row * cols + col
        // remember it
        setHover({ row, col, state: states[codes[index]], size: sizes[index] })
        // all done
        return
    }

    // render
    return (
        <Tray title="chunks" initially={true} state="enabled" scale={0.5}>
            <Housing>
                <canvas ref={setNode} width={cols * cell} height={rows * cell}
                    onMouseMove={track} onMouseLeave={() => setHover(null)}
                    role="img" aria-label={census.map(([name, count]) => `${name}: ${count}`).join(", ")}
                    data-qed-view="chunk-map" data-qed-chunk={hover ? `${hover.row},${hover.col}` : ""}
                />
                <Legend>
                    {census.map(([name, count]) => (
                        <Key key={name} data-qed-state={name} data-qed-count={count}>
                            <Swatch color={styles.states[name]} />
                            {name} {count}
                        </Key>
                    ))}
                </Legend>
                <Readout>
                    {hover
                        ? `chunk ${hover.row}, ${hover.col}: ${hover.state}` + (hover.size ? `, ${hover.size} bytes` : "")
                        : "point at a chunk"}
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
