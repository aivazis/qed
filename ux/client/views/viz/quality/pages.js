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
// formatting
import { bytes, percent, plural } from './format'
// styles
import styles from './styles'


// the width the strip may take, in pixels, and the height it aims for
const room = 360
const aim = 200


// the last two parts of the path of a dataset in the file, which is enough to tell it apart
const short = name => name.startsWith("/") ? name.split("/").slice(-2).join("/") : name


// the strip: every page the chunks of the raster land on, in file order, with how much of it
// holds the raster, how much everybody else, and how much is left over
export const Pages = ({ layout, focus, setFocus }) => {
    // unpack
    const { pageSize, strip } = layout
    // the number of pages
    const count = strip.pages.length
    // the size of a cell: as large as lets the pages fill the area we aim for, within reason
    const cell = Math.min(24, Math.max(4, Math.floor(Math.sqrt(room * aim / Math.max(1, count)))))
    // the cells in a row, and the rows
    const across = Math.floor(room / cell)
    const down = Math.ceil(count / across)
    // the index of each page in the strip
    const index = React.useMemo(
        () => new Map(strip.pages.map((page, position) => [page, position])), [strip]
    )
    // the canvas; kept as state, since collapsing the tray unmounts it
    const [node, setNode] = React.useState(null)
    // the page under the pointer
    const [hover, setHover] = React.useState(null)

    // draw the strip whenever it, the canvas, or the page in focus changes
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
        // leave a hairline between cells
        const gap = 1
        // the height of the bar in a cell
        const tall = cell - gap
        // go through the pages
        strip.pages.forEach((page, position) => {
            // the corner of the cell
            const x = (position % across) * cell
            const y = Math.floor(position / across) * cell
            // the heights of the bytes of the raster and of everybody else, from the bottom
            const mine = Math.round(tall * strip.mine[position] / pageSize)
            const others = Math.min(tall - mine, Math.round(tall * strip.others[position] / pageSize))
            // the room left over
            context.fillStyle = styles.strip.unused
            context.fillRect(x, y, tall, tall)
            // everybody else
            context.fillStyle = styles.strip.others
            context.fillRect(x, y + tall - mine - others, tall, others)
            // and the raster
            context.fillStyle = styles.strip.mine
            context.fillRect(x, y + tall - mine, tall, mine)
        })
        // the page in focus, if it is one of mine
        const position = focus === null ? undefined : index.get(focus)
        // gets an outline
        if (position !== undefined) {
            // in the color of the focus
            context.strokeStyle = styles.focus
            context.lineWidth = 2
            context.strokeRect(
                (position % across) * cell + 1, Math.floor(position / across) * cell + 1,
                cell - 3, cell - 3
            )
        }
        // all done
        return
    }, [node, strip, pageSize, cell, across, focus, index])

    // find the page under the pointer
    const track = event => {
        // the position of the pointer on the canvas
        const box = event.currentTarget.getBoundingClientRect()
        const col = Math.floor((event.clientX - box.left) / cell)
        const row = Math.floor((event.clientY - box.top) / cell)
        // the position in the strip
        const position = row * across + col
        // off the strip
        if (col < 0 || col >= across || row < 0 || position >= count) {
            // there is no page
            setHover(null)
            setFocus(null)
            // and nothing more to do
            return
        }
        // remember it
        setHover(position)
        // and put its page in focus
        setFocus(strip.pages[position])
        // all done
        return
    }
    // let go of it
    const leave = () => {
        // forget the page
        setHover(null)
        // and let go of the focus
        setFocus(null)
        // all done
        return
    }

    // describe the page under the pointer
    const describe = position => {
        // unpack
        const mine = strip.mine[position]
        const others = strip.others[position]
        const partner = strip.partner[position]
        // the room left over
        const unused = Math.max(0, pageSize - mine - others)
        // the description
        return [
            `page ${strip.pages[position]}: this raster ${bytes(mine)} in ${plural(strip.chunks[position], "chunk")} (${percent(mine / pageSize)})`,
            others > 0
                ? `others ${bytes(others)}, mostly ${short(partner)} ${bytes(strip.partnerBytes[position])}`
                : "no other dataset",
            `unused ${bytes(unused)}`,
        ]
    }

    // render
    return (
        <Tray title="pages" initially={true} state="enabled" scale={0.5}>
            <Housing>
                <Title>{`${count} pages of ${bytes(pageSize)}, in file order`}</Title>
                <canvas ref={setNode} width={across * cell} height={down * cell}
                    onMouseMove={track} onMouseLeave={leave}
                    role="img" aria-label={`${count} pages hold this raster`}
                    data-qed-view="page-strip" data-qed-page={focus ?? ""}
                />
                <Legend>
                    <Key><Swatch color={styles.strip.mine} />this raster</Key>
                    <Key><Swatch color={styles.strip.others} />other datasets</Key>
                    <Key><Swatch color={styles.strip.unused} />unused</Key>
                </Legend>
                <Readout>
                    {hover === null
                        ? "hover over a page to see what it holds"
                        : describe(hover).map(line => <div key={line}>{line}</div>)}
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

// the title
const Title = styled.div`
    margin-bottom: 0.25rem;
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

// the swatch of a color
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
    min-height: 3.6em;
    color: ${styles.normal};
`


// end of file
