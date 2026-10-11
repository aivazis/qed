// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'


// how long the camera must sit still before a move is over and is told to the server
const SETTLE = 150
// how long to wait for the server to say back what it was told before believing it again
const PATIENCE = 2000
// how close two places must be to be the same one, in diagram units and in zoom
const NEAR = 1e-6


// the provider factory; with {onSettle}, the camera is shared: every move of the user is told to
// {onSettle}, once it is over, as the diagram point at the middle of my area and the zoom, and
// the place in {shared}, where every client's camera looks, is adopted whenever the user is not
// moving the camera
export const Provider = React.forwardRef((
    { viewport, scale, focus, focusKey, shared, onSettle, children }, clientRef
) => {
    // save the external length scale
    const els = scale
    // build a camera
    const [camera, setCamera] = React.useState({ x: 0, y: 0, z: 1, phi: 0 })
    // the camera as of the latest drawing, for the timers that outlive it
    const latest = React.useRef(camera)
    // keep it current
    latest.current = camera
    // whether the user is moving the camera
    const moving = React.useRef(false)
    // the timer that ends a move once the camera sits still
    const settler = React.useRef(null)
    // the place i last told the server about, until it says it back
    const told = React.useRef(null)
    // the timer that stops waiting for it
    const waiting = React.useRef(null)
    // the middle of my area, in units of the external length scale
    const middle = () => {
        // get the extent of my area
        const { width = 0, height = 0 } = clientRef.current?.getBoundingClientRect() ?? {}
        // and halve it
        return { mx: width / (2 * els), my: height / (2 * els) }
    }
    // the diagram point at the middle of my area under {camera}, and its zoom
    const placeOf = camera => {
        // the middle of my area
        const { mx, my } = middle()
        // undo the pan and the zoom
        return { x: (mx - camera.x) * camera.z, y: (my - camera.y) * camera.z, z: camera.z }
    }
    // the pan and zoom that put the diagram point {x, y} at the middle of my area, at zoom {z}
    const aim = ({ x, y, z }) => {
        // the middle of my area
        const { mx, my } = middle()
        // solve for the pan
        return { x: mx - x / z, y: my - y / z, z }
    }
    // whether two places are the same one
    const same = (a, b) =>
        Math.abs(a.x - b.x) < NEAR && Math.abs(a.y - b.y) < NEAR && Math.abs(a.z - b.z) < NEAR
    // the user moved the camera: once it sits still, tell my owner where it looks
    const moved = () => {
        // unless the camera is not shared
        if (!onSettle) {
            // in which case there is nobody to tell
            return
        }
        // a move is under way
        moving.current = true
        // and it is not over until the camera sits still
        clearTimeout(settler.current)
        // so wait for that
        settler.current = setTimeout(() => {
            // the move is over
            moving.current = false
            // where the camera looks now
            const place = placeOf(latest.current)
            // is what the server will be told, and what it should say back
            told.current = place
            // unless it never does, in which case i stop waiting for it
            clearTimeout(waiting.current)
            // after a while
            waiting.current = setTimeout(() => { told.current = null }, PATIENCE)
            // tell my owner
            onSettle(place)
            // all done
            return
        }, SETTLE)
        // all done
        return
    }
    // adopt where every client's camera looks, unless the user is moving mine
    React.useEffect(() => {
        // if the camera is not shared, or nobody has moved a camera yet
        if (!shared) {
            // there is nothing to adopt
            return
        }
        // if the user is moving mine
        if (moving.current) {
            // what the user does wins
            return
        }
        // if i am waiting for the server to say back where i told it my camera looks
        if (told.current) {
            // and this is it
            if (same(shared, told.current)) {
                // the wait is over
                told.current = null
                // and the timer that would have ended it is not needed
                clearTimeout(waiting.current)
            }
            // either way, this is either what i have, or older news, e.g. a refetch that left
            // before the server heard from me
            return
        }
        // if i am already looking there
        if (same(shared, placeOf(latest.current))) {
            // there is nothing to do
            return
        }
        // otherwise, look there, keeping the orientation
        setCamera(camera => ({ ...camera, ...aim(shared) }))
        // all done
        return
    }, [shared?.x, shared?.y, shared?.z])
    // let go of the timers when i go away
    React.useEffect(() => () => {
        // the end of a move
        clearTimeout(settler.current)
        // and the wait for the server
        clearTimeout(waiting.current)
    }, [])
    // the camera that puts the {focus} at the center of my area, at the given zoom; without a
    // focus, or before my area has a size, the origin goes to the top left corner
    const home = (z = 1) => {
        // get the extent of my area
        const { width, height } = clientRef.current?.getBoundingClientRect() ?? {}
        // if there is nothing to center or nowhere to center it
        if (!focus || !width || !height) {
            // fall back to the corner
            return { x: 0, y: 0, z }
        }
        // otherwise, solve for the pan that maps the focus onto the middle of my area
        return { x: width / (2 * els) - focus.x / z, y: height / (2 * els) - focus.y / z, z }
    }
    // center on my focus when i first show up, and whenever what i look at changes, as told by
    // {focusKey}; not when the focus merely shifts because something in view moved, which would
    // pull the picture out from under the user. this waits until the commit is over, since my
    // area belongs to my client, whose ref is attached after my own layout effects run
    React.useEffect(() => {
        // without a focus there is nothing to aim at
        if (!focus) {
            // so leave the camera alone
            return
        }
        // aim the camera, keeping its zoom and orientation
        setCamera(camera => ({ ...camera, ...home(camera.z) }))
        // all done
        return
    }, [focusKey, focus === null])
    // the cursor position in ICS
    const [cursor, setCursor] = React.useState(null)
    // and the same position before it is rounded onto the grid, for clients that map it further
    const [pointer, setPointer] = React.useState(null)

    // the transform from viewport to the internal coordinate system
    // the diagram coordinates of a point on the screen, rounded onto the grid unless asked not
    // to; a drag subtracts two of these, and rounding each one before the subtraction would make
    // the difference flicker whenever the pointer sits half way between two grid points
    const toICS = (point, round = true) => {
        // get the origin of my viewport
        const { left, top } = clientRef.current?.getBoundingClientRect() ?? { left: 0, top: 0 }
        // project the mouse coordinates to ICS
        const rx = (point.x - left - els * camera.x) / (els / camera.z)
        const ry = (point.y - top - els * camera.y) / (els / camera.z)
        // compute the length of this vector
        const r = (rx ** 2 + ry ** 2) ** 0.5
        // and its angle with the x-axis
        const phi = Math.atan2(ry, rx)
        // from this, compute its angle with the rotated diagram x-axis
        const theta = phi - Math.PI / 180 * camera.phi
        // use the camera angle to project to the actual diagram coordinates
        const [x, y] = [r * Math.cos(theta), r * Math.sin(theta)]
        // if the caller wants grid points
        if (round) {
            // round
            return { x: Math.round(x), y: Math.round(y) }
        }
        // all done
        return { x, y }
    }

    // camera control
    // movement along the x-y plane
    const pan = ({ dx = 0, dy = 0 }) => {
        // it is a move of the user
        moved()
        // adjust the camera
        setCamera(camera => ({
            // the current state
            ...camera,
            // adjust the x-axis
            x: camera.x - dx / els,
            // adjust the x-axis
            y: camera.y - dy / els,
        }))
        // all done
        return
    }
    // movement along the z-axis that keeps the point under {anchor} where it is on the screen;
    // {z} is the distance of the camera from the diagram, so a positive {dz} moves away and makes
    // the picture smaller; {anchor} is in screen coordinates, and the center of my area stands in
    // when there is none
    const zoom = (dz, anchor = null) => {
        // it is a move of the user
        moved()
        // get the extent of my area
        const { left = 0, top = 0, width = 0, height = 0 } = clientRef.current?.getBoundingClientRect() ?? {}
        // the anchor relative to my area, in units of the external length scale
        const ax = ((anchor?.x ?? left + width / 2) - left) / els
        const ay = ((anchor?.y ?? top + height / 2) - top) / els
        // adjust the camera
        setCamera(camera => {
            // the new zoom
            const z = Math.max(camera.z + dz, 0.1)
            // how much the scale of the picture changes
            const ratio = camera.z / z
            // pan so the diagram point under the anchor stays under it
            return {
                // the current state
                ...camera,
                // the pan along the x-axis that pins the anchor
                x: ax - (ax - camera.x) * ratio,
                // and along the y-axis
                y: ay - (ay - camera.y) * ratio,
                // and the zoom
                z,
            }
        })
        // all done
        return
    }

    // event handlers
    // keep track of the cursor position
    const track = evt => {
        // unpack the cursor position
        const { clientX: x, clientY: y } = evt
        // record the location
        setCursor(toICS({ x, y }))
        // and the location before rounding
        setPointer(toICS({ x, y }, false))
        // all done
        return
    }
    // reset the cursor position
    const reset = () => {
        // clear the cursor location
        setCursor(null)
        // in both forms
        setPointer(null)
        // all done
        return
    }
    // keypad
    const keypad = evt => {
        // unpack the key
        const { key } = evt
        // the base displacement
        let displacement = 5.0
        // left
        if (key == "a" || key == "h" || key == "ArrowLeft") {
            // pan left
            pan({ dx: displacement })
            // all done
            return
        }
        // right
        if (key == "d" || key == "l" || key == "ArrowRight") {
            // pan left
            pan({ dx: -displacement })
            // all done
            return
        }
        // up
        if (key == "w" || key == "k" || key == "ArrowUp") {
            // pan left
            pan({ dy: displacement })
            // all done
            return
        }
        // down
        if (key == "x" || key == "j" || key == "ArrowDown") {
            // pan left
            pan({ dy: -displacement })
            // all done
            return
        }
        // zoom in, making the picture bigger
        if (key == "z") {
            // by moving closer, about the center of my area
            zoom(-0.1)
            // all done
            return
        }
        // zoom out, making the picture smaller
        if (key == "c") {
            // by moving away, about the center of my area
            zoom(0.1)
            // all done
            return
        }
        // reset the camera
        if (key == "s") {
            // it is a move of the user
            moved()
            // go back to the focus at the original zoom, keeping the orientation
            setCamera(camera => ({ ...camera, ...home() }))
        }
        // ignore everything else
        return
    }
    // wheel
    const wheel = evt => {
        // prevent the default behavior
        evt.preventDefault()
        // unpack the event
        const { deltaX, deltaY, ctrlKey, shiftKey, clientX, clientY } = evt
        // scrolling with the <ctrl> or <shift> key pressed
        if (ctrlKey || shiftKey) {
            // is a zoom about the pointer: spreading the fingers or scrolling up zooms in, pinching
            // or scrolling down zooms out
            zoom((deltaY > 0 ? 1 : -1) * 0.01, { x: clientX, y: clientY })
            // all done
            return
        }
        // scrolling without modifiers is a pan
        pan({ dx: deltaX, dy: deltaY })
        // all done
        return
    }

    // install the event listeners
    React.useEffect(() => {
        // track the cursor when it moves in my area
        clientRef.current?.addEventListener("pointermove", track)
        // stop tracking when it leaves my area
        clientRef.current?.addEventListener("pointerleave", reset)
        // install the keypad
        clientRef.current?.addEventListener("keydown", keypad)
        // handle wheel events
        clientRef.current?.addEventListener("wheel", wheel)
        // register a cleanup
        return () => {
            // disconnect the cursor trackers
            clientRef.current?.removeEventListener("pointermove", track)
            clientRef.current?.removeEventListener("pointerleave", reset)
            // disconnect the keypad
            clientRef.current?.removeEventListener("keydown", keypad)
            // disconnect the wheel listener
            clientRef.current?.removeEventListener("wheel", wheel)
            // all done
            return
        }
    }, [camera, setCamera])

    // build the context
    const context = {
        // the external length scale
        els,
        // the camera
        camera, setCamera,
        // the current cursor position in ICS
        cursor, setCursor,
        // and before rounding
        pointer,
        // the transform to diagram coordinates
        toICS,
    }

    // provide for my children
    return (
        <Context.Provider value={context}>
            {children}
        </Context.Provider>

    )
})


// set up the camera context
export const Context = React.createContext(
    // the default value that users see when outside the provides
    {
        // the external length scale
        els: 1,
        // the camera
        camera: null,
        setCamera: () => { throw new Error(complaint) },
        // the cursor position
        cursor: null,
        setCursor: () => { throw new Error(complaint) },
        // before rounding
        pointer: null,
        // the transform to diagram coordinates
        toICS: () => { throw new Error(complaint) },
    }
)

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'camera' context: no provider"


// end of file
