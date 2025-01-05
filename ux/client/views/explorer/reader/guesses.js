// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// hooks
import { useShapeGuessesLoader, useQueryShapeGuesses } from './useFetchShapeGuesses'
// components
import { Aspect } from './aspect'
import { Cells } from './cells'
import { Field, Value, enumValue } from '../form'


// display the possible shapes of a dataset
export const Guesses = ({ size, aspect, lines, samples, update }) => {
    // preload the query
    const [qref, getGuesses] = useShapeGuessesLoader()
    // schedule the fetch
    React.useEffect(() => {
        // variables
        const variables = {
            size: size || "0",
            aspect: aspect || "0",
        }
        // options
        const options = { fetchPolicy: "store-and-network" }
        // fetch
        getGuesses(variables, options)
        // all done
        return
    }, [size, aspect])
    // if the guesses are not available yet
    if (qref === null) {
        // bail
        return
    }
    // convert the current selection into my tag
    const shape = `${lines} x ${samples}`
    // otherwise, render them
    return (
        <>
            <Cells value={size} />
            <Aspect aspect={aspect} update={update} />
            <Pile qref={qref} shape={shape} update={update} />
        </>
    )
}

// the guesses
const Pile = ({ qref, shape, update }) => {
    // get the guesses
    const guesses = useQueryShapeGuesses(qref)
    // and render them
    return (
        <>
            {guesses.map((guess, idx) => {
                // unpack
                const { lines, samples } = guess
                // form the text
                const text = `${lines} x ${samples}`
                // build the shape mutator
                const pick = () => {
                    // update the form
                    update("lines", lines)
                    // and done
                    return
                }
                // render
                return (
                    <Field key={text}
                        name={idx == 0 ? "possible shapes" : null} value={text}
                        tip={`pick ${text} as the dataset shape`}>
                        <Value>
                            <Guess guess={text} shape={shape} update={pick} />
                        </Value>
                    </Field>
                )
            })}
        </>
    )
}

// guess selection
const Guess = ({ guess, shape, update }) => {
    // deduce my state
    const state = guess === shape ? "selected" : "enabled"
    // assemble my behaviors
    const behaviors = {
        onClick: update
    }
    // pick a field selector based on my state
    const Selector = enumValue(state)
    // and render it
    return (
        <Selector {...behaviors}>
            {guess}
        </Selector>
    )
}

// end of file
