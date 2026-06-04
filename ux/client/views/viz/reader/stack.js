// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Meta } from '~/widgets'

// local
// context
import { Context } from './context'
// components
import { Member } from './member'
// hooks
import { useSetMembers } from './useSetMembers'
// styles
import styles from './styles'


// display the stack member participation control
export const Stack = () => {
    // get my stack details from the reader context
    const { stackExtent, members } = React.useContext(Context)
    // the mutation that updates the membership mask
    const setMembers = useSetMembers()

    // if i am not a stack, or the stack has too few members to be worth toggling
    if (!stackExtent || stackExtent < 2) {
        // there is nothing to show
        return null
    }

    // the effective mask; when i'm not the active reader i have no view, so assume the default
    // all-on state until the user activates me by interacting with a member
    const mask = members ?? Array(stackExtent).fill(true)
    // how many members are active; the last active member is locked on so the stack is never empty
    const live = mask.filter(Boolean).length

    // toggle member {index}, committing the full new mask
    const toggle = index => {
        // refuse to turn off the last active member
        if (mask[index] && live === 1) {
            // nothing to do
            return
        }
        // flip member {index} and send the whole mask to the server
        setMembers(mask.map((on, i) => (i === index ? !on : on)))
        // all done
        return
    }

    // mix my paint
    const paint = styles.axis()
    // and render; the members form a group of independent toggles, one per stack member, and the
    // client identifies the control as the stack so a driver can find every member under it
    return (
        <Meta.Entry attribute="members" style={paint}>
            <div role="group" aria-label="stack members" data-qed-control="stack">
                {mask.map((on, index) => (
                    <Member key={index} index={index}
                        active={on} locked={on && live === 1} toggle={toggle} />
                ))}
            </div>
        </Meta.Entry>
    )
}


/* end of file */
