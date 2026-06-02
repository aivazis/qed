// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import { routes, sweep } from "../lib/routes"


// the marker grammar must hold regardless of what data is loaded: every {data-pyre-widget} names
// a known widget kind, and every {-part}/{-name} sub-marker lives inside a {-widget}. a failure
// here points at a typo or a stray marker rather than a missing control, so it is data-independent.
const findGrammarErrors = (): string[] => {
    // the vocabulary of widget kinds we ship
    const kinds = new Set(["flex", "slider", "toolbar", "tile", "mosaic"])

    // collect the violations
    const problems: string[] = []

    // every widget marker must name a known kind
    for (const node of document.querySelectorAll("[data-pyre-widget]")) {
        // read the kind
        const kind = node.getAttribute("data-pyre-widget")
        // flag anything outside the vocabulary
        if (!kind || !kinds.has(kind)) {
            problems.push(`UNKNOWN-KIND data-pyre-widget="${kind}"`)
        }
    }

    // every sub-marker must descend from a widget marker
    for (const node of document.querySelectorAll("[data-pyre-widget-part], [data-pyre-widget-name]")) {
        // a sub-marker on the same element as its {data-pyre-widget} is fine
        if (node.hasAttribute("data-pyre-widget")) continue
        // otherwise it must have a widget ancestor
        if (!node.closest("[data-pyre-widget]")) {
            const part = node.getAttribute("data-pyre-widget-part") ?? node.getAttribute("data-pyre-widget-name")
            problems.push(`ORPHAN-MARKER "${part}" has no data-pyre-widget ancestor`)
        }
    }

    // hand them back
    return problems
}


// the grammar must hold on every route
test("widget markers form a valid grammar", async ({ page }) => {
    // sweep the routes
    const problems = await sweep(page, routes, findGrammarErrors)
    // silence is pass; report every problem on failure
    expect(problems, problems.join("\n")).toEqual([])
})


/* end of file */
