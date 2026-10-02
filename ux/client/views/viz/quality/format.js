// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// render a number with {digits} significant figures, or a dash when there is none
export const number = (value, digits = 3) => value === null || value === undefined
    ? "-" : Math.abs(value) >= 10 ** digits
        // numbers too large for the digits are rounded to whole ones, rather than written in
        // scientific notation
        ? `${Math.round(value)}`
        : trim(Number(value).toPrecision(digits))
// drop the trailing zeros of the fraction of a rendered number, and the point if nothing is left
// after it; the zeros of a whole number stay
const trim = text => text.includes("e") || !text.includes(".")
    ? text : text.replace(/0+$/, "").replace(/\.$/, "")
// render a share as a percentage
export const percent = value => value === null || value === undefined
    ? "-" : `${Math.round(100 * value)}%`
// render a {count} of things called {name}, in the plural unless there is exactly one
export const plural = (count, name) => `${count} ${name}${count === 1 ? "" : "s"}`
// render a byte count in the largest unit that keeps it above one
export const bytes = value => {
    // nothing
    if (value === null || value === undefined) {
        // renders as a dash
        return "-"
    }
    // the units
    const units = ["B", "KiB", "MiB", "GiB", "TiB"]
    // find the one that fits
    let unit = 0
    while (value >= 1024 && unit < units.length - 1) {
        // by moving up
        value /= 1024
        unit += 1
    }
    // and render
    return `${number(value)} ${units[unit]}`
}


// end of file
