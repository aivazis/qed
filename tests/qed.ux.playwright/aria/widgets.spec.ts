// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import { routes, sweep } from "../lib/routes"


// the widgets we tag must carry the aria state their role implies; a slider with no
// {aria-valuenow} or a mosaic with no accessible name reads as broken to assistive tech even
// though it is "marked up". this narrows a bug to the specific widget part that is incomplete.
const findIncomplete = (): string[] => {
    // the aria each widget kind/part owes, keyed by "<kind>/<part>"
    const required: Record<string, string[]> = {
        "slider/thumb": ["role", "aria-valuenow", "aria-valuemin", "aria-valuemax", "aria-orientation"],
        "flex/resizer": ["role", "aria-orientation"],
        "mosaic/": ["role", "aria-label"],
    }

    // collect the gaps
    const problems: string[] = []
    // for every element we marked as a widget
    for (const node of document.querySelectorAll("[data-pyre-widget]")) {
        // form its kind/part key
        const kind = node.getAttribute("data-pyre-widget")
        const part = node.getAttribute("data-pyre-widget-part") ?? ""
        const owed = required[`${kind}/${part}`]
        // nothing required for this kind/part
        if (!owed) continue
        // check each obligation
        for (const attr of owed) {
            // a missing attribute is a gap
            if (node.getAttribute(attr) == null) {
                problems.push(`INCOMPLETE ${kind}/${part} missing ${attr}`)
            }
        }
    }
    // hand them back
    return problems
}


// every tagged widget must carry the aria its role implies, on every route
test("tagged widgets carry the aria their role implies", async ({ page }) => {
    // sweep the routes
    const problems = await sweep(page, routes, findIncomplete)
    // silence is pass; report every gap on failure
    expect(problems, problems.join("\n")).toEqual([])
})


/* end of file */
