// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'


// the provider factory
export const Provider = React.forwardRef(({ viewport, scale, children }, clientRef) => {
    // save the external length scale
    const els = scale
    // build a camera
    const [camera, setCamera] = React.useState({ x: 0, y: 0, z: 1, phi: 0 })
    // the cursor position in ICS
    const [cursor, setCursor] = React.useState(null)

    // the transform from viewport to the internal coordinate system
    const toICS = point => {
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
        const x = Math.round(r * Math.cos(theta))
        const y = Math.round(r * Math.sin(theta))
        // all done
        return { x, y }
    }

    // camera control
    // movement along the x-y plane
    const pan = ({ dx = 0, dy = 0 }) => {
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
    // movement along the z-axis
    const zoom = dz => {
        // adjust the camera
        setCamera(camera => ({
            // the current state
            ...camera,
            // adjust the z-axis
            z: Math.max(camera.z + dz, 0.1),
        }))
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
        // all done
        return
    }
    // reset the cursor position
    const reset = () => {
        // clear the cursor location
        setCursor(null)
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
        // zoom in
        if (key == "z") {
            // zoom
            zoom(0.1)
            // all done
            return
        }
        // zoom out
        if (key == "c") {
            // zoom
            zoom(-0.1)
            // all done
            return
        }
        // reset the camera
        if (key == "s") {
            // reset
            setCamera(camera => ({
                // the current state
                ...camera,
                // reset the location along the x-axis
                x: 0,
                // reset the location along the y-axis
                y: 0,
                // reset the location along the z-axis
                z: 1,
            }))
        }
        // ignore everything else
        return
    }
    // wheel
    const wheel = evt => {
        // unpack the vent
        const { deltaX, deltaY, ctrlKey, shiftKey } = evt
        // scrolling with the <ctrl> or <shift> key pressed
        if (ctrlKey || shiftKey) {
            // is a zoom
            zoom((deltaY > 0 ? -1 : 1) * 0.01)
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
        clientRef.current?.addEventListener("mousemove", track)
        // stop tracking when it leaves my area
        clientRef.current?.addEventListener("mouseleave", reset)
        // install the keypad
        clientRef.current?.addEventListener("keydown", keypad)
        // handle wheel events
        clientRef.current?.addEventListener("wheel", wheel)
        // register a cleanup
        return () => {
            // disconnect the cursor trackers
            clientRef.current?.removeEventListener("mousemove", track)
            clientRef.current?.removeEventListener("mouseleave", reset)
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
        // the transform to diagram coordinates
        toICS: () => { throw new Error(complaint) },
    }
)

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'camera' context: no provider"


// end of file
