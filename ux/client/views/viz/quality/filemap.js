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
import { bytes, plural } from './format'
// styles
import styles from './styles'


// the width the map may take, in pixels, and the height it aims for
const room = 360
const aim = 420


// the file map: every page of the file, in file order, each a stacked bar of the rasters of the
// product on it, of everybody else, and of the metadata and free space
export const FileMap = ({ layout, focus, setFocus }) => {
    // unpack
    const { pageSize, filemap } = layout
    const { pages: count, rasters, selected, others } = filemap
    // the size of a cell: as large as lets the pages fill the area we aim for, within reason
    const cell = Math.min(24, Math.max(4, Math.floor(Math.sqrt(room * aim / Math.max(1, count)))))
    // the cells in a row, and the rows
    const across = Math.floor(room / cell)
    const down = Math.ceil(count / across)
    // the canvas; kept as state, since collapsing the tray unmounts it
    const [node, setNode] = React.useState(null)
    // the page under the pointer
    const [hover, setHover] = React.useState(null)
    // the raster under the pointer in the legend, and the one pinned there by a click
    const [spot, setSpot] = React.useState(null)
    const [pinned, setPinned] = React.useState(null)
    // a different file has different rasters, so let go of the pinned one
    React.useEffect(() => setPinned(null), [filemap])
    // the raster that stands out: the one under the pointer, or else the pinned one
    const picked = spot ?? pinned
    // the color of each raster: the picked one above all, the raster in view as the chunk map
    // draws its data, and the rest of the product a step darker
    const color = index => index === picked
        ? styles.filemap.spot
        : index === selected ? styles.filemap.mine : styles.filemap.neighbor

    // draw the map whenever it, the canvas, or the page in focus changes
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
        for (let page = 0; page < count; page++) {
            // the corner of the cell
            const x = (page % across) * cell
            const y = Math.floor(page / across) * cell
            // the whole page starts out as metadata or free space
            context.fillStyle = styles.filemap.free
            context.fillRect(x, y, tall, tall)
            // the tenants stack up from the bottom of the cell
            let top = y + tall
            // go through the rasters
            rasters.forEach((raster, index) => {
                // the height of its bytes, within the room left in the cell
                const height = Math.min(top - y, Math.round(tall * raster.bytes[page] / pageSize))
                // a raster with nothing on the page
                if (height <= 0) {
                    // leaves no mark
                    return
                }
                // make room for it
                top -= height
                // and draw it
                context.fillStyle = color(index)
                context.fillRect(x, top, tall, height)
            })
            // the height of everybody else, within the room left in the cell
            const height = Math.min(top - y, Math.round(tall * others[page] / pageSize))
            // on top of the rasters
            context.fillStyle = styles.filemap.others
            context.fillRect(x, top - height, tall, height)
        }
        // the page in focus, if it is on the map
        if (focus !== null && focus >= 0 && focus < count) {
            // gets an outline in the color of the focus
            context.strokeStyle = styles.focus
            context.lineWidth = 2
            context.strokeRect(
                (focus % across) * cell + 1, Math.floor(focus / across) * cell + 1,
                cell - 3, cell - 3
            )
        }
        // all done
        return
    }, [node, filemap, pageSize, cell, across, focus, picked])

    // find the page under the pointer
    const track = event => {
        // the position of the pointer on the canvas
        const box = event.currentTarget.getBoundingClientRect()
        const col = Math.floor((event.clientX - box.left) / cell)
        const row = Math.floor((event.clientY - box.top) / cell)
        // the page
        const page = row * across + col
        // off the map
        if (col < 0 || col >= across || row < 0 || page >= count) {
            // there is no page
            setHover(null)
            setFocus(null)
            // and nothing more to do
            return
        }
        // remember it
        setHover(page)
        // and put it in focus
        setFocus(page)
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
    const describe = page => {
        // the rasters on it
        const tenants = rasters.filter(raster => raster.bytes[page] > 0)
        // the bytes of all of them
        const held = tenants.reduce((total, raster) => total + raster.bytes[page], 0)
        // the room left for the metadata and the free space
        const free = Math.max(0, pageSize - held - others[page])
        // the description
        return [
            `page ${page}`,
            ...tenants.map(raster =>
                `${raster.name} ${bytes(raster.bytes[page])} in ${plural(raster.chunks[page], "chunk")}`
            ),
            ...(others[page] > 0 ? [`other datasets ${bytes(others[page])}`] : []),
            `metadata or free ${bytes(free)}`,
        ]
    }

    // render
    return (
        <Tray title="file map" initially={true} state="enabled" scale={0.5}>
            <Housing>
                <Title>{`${count} pages of ${bytes(pageSize)}, in file order`}</Title>
                <canvas ref={setNode} width={across * cell} height={down * cell}
                    onMouseMove={track} onMouseLeave={leave}
                    role="img" aria-label={`the ${count} pages of the file`}
                    data-qed-view="file-map" data-qed-page={focus ?? ""}
                />
                <Legend>
                    {selected !== null &&
                        <Key $selected><Swatch color={styles.filemap.mine} />{rasters[selected].name}</Key>
                    }
                    <Key><Swatch color={styles.filemap.neighbor} />other rasters</Key>
                    <Key><Swatch color={styles.filemap.others} />other datasets</Key>
                    <Key><Swatch color={styles.filemap.free} />metadata or free</Key>
                </Legend>
                <Legend>
                    {rasters.map((raster, index) => (
                        <Pick key={raster.name} $picked={index === picked} $pinned={index === pinned}
                            onMouseEnter={() => setSpot(index)} onMouseLeave={() => setSpot(null)}
                            onClick={() => setPinned(index === pinned ? null : index)}
                            data-qed-raster={raster.name}
                        >
                            {raster.name}
                        </Pick>
                    ))}
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

// an entry in the legend; the raster in view is brighter
const Key = styled.span`
    display: inline-flex;
    align-items: center;
    margin-right: 0.75rem;
    color: ${props => props.$selected ? styles.normal : styles.dim};
`

// the swatch of a color
const Swatch = styled.span`
    display: inline-block;
    width: 0.6rem;
    height: 0.6rem;
    margin-right: 0.25rem;
    background-color: ${props => props.color};
`

// a raster in the list of the rasters of the product: hovering lights up its pages, and a click
// pins it until the next click
const Pick = styled.span`
    margin: 0.1rem 0.5rem 0.1rem 0;
    padding: 0 0.25rem;
    cursor: pointer;
    color: ${props => props.$picked ? styles.filemap.free : styles.dim};
    background-color: ${props => props.$picked ? styles.filemap.spot : "transparent"};
    outline: ${props => props.$pinned ? `1px solid ${styles.filemap.spot}` : "none"};
`

// what is under the pointer
const Readout = styled.div`
    margin-top: 0.25rem;
    min-height: 3.6em;
    color: ${styles.normal};
`


// end of file
