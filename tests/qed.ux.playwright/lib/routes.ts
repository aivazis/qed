// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import type { Page } from "@playwright/test"


// the routes that, between them, surface the bulk of the interactive controls
export const routes = ["/", "/controls", "/explore", "/doc"]


// load each {route}, run a read-only DOM {check} inside the page, and tag every problem line it
// returns with its route. {check} is evaluated in the browser, so it must be self-contained: it
// may touch {document}/{window} but must not close over anything from this module.
export const sweep = async (
    page: Page,
    routes: string[],
    check: () => string[],
): Promise<string[]> => {
    // accumulate the problems across routes
    const problems: string[] = []
    // sweep each route
    for (const route of routes) {
        // load it and let the client settle
        await page.goto(route, { waitUntil: "load" })
        // wait for the app shell to mount before inspecting
        await page.locator("[data-pyre-widget]").first().waitFor({ timeout: 10_000 })
        // run the read-only check and tag each problem with its route
        const found = await page.evaluate(check)
        problems.push(...found.map(line => `${route} ${line}`))
    }
    // hand them back; an empty list means the route swept clean
    return problems
}


/* end of file */
