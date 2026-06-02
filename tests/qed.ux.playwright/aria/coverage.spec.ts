// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import { routes, sweep } from "../lib/routes"


// every control a user can interact with must carry semantic identity: an aria {role}, a
// {data-pyre-widget} from the widget library, or a {data-qed-*} identity from the client. a
// failure here means a control is invisible to assistive tech and to automated drivers.
//
// THIS IS THE ROLLOUT BACKLOG. It is expected to fail today (icon controls and the /doc
// accordions are not yet tagged); it lives in the {backlog} project and is excluded from the
// gate. Run it explicitly with {npx playwright test --project=backlog} to see what remains.
const findUntagged = (): string[] => {
    // a node counts as tagged if it or a nearby ancestor carries identity or a role; widgets put
    // the marking on a wrapper, not on every leaf, so we walk up a few levels
    const tagged = (node: Element): boolean => {
        // climb at most a few hops
        for (let el: Element | null = node, hops = 0; el && hops < 4; el = el.parentElement, ++hops) {
            // an aria role counts
            if (el.getAttribute("role")) return true
            // so does any identity attribute in either namespace
            for (const name of el.getAttributeNames()) {
                if (name.startsWith("data-pyre-widget") || name.startsWith("data-qed")) return true
            }
        }
        // nothing found
        return false
    }

    // native html controls carry an implicit role and are accessible without our help, so they
    // are not ARIA offenders; only non-semantic elements that are made clickable need a role
    const nativelyAccessible = (node: Element): boolean => {
        // a link only has the {link} role when it actually points somewhere
        if (node.tagName === "A") return node.hasAttribute("href")
        // the rest are interactive by construction
        return ["BUTTON", "INPUT", "SELECT", "TEXTAREA", "SUMMARY"].includes(node.tagName)
    }

    // collect a compact description of each offender
    const problems: string[] = []
    // sweep every element on the page
    for (const node of document.querySelectorAll("*")) {
        // a pointer cursor is our proxy for "this reacts to a click"
        if (window.getComputedStyle(node).cursor !== "pointer") continue
        // native controls are already accessible
        if (nativelyAccessible(node)) continue
        // so is anything nested inside a native control (e.g. an svg icon in a link or button)
        if (node.closest("a[href], button, summary")) continue
        // already-tagged elements are fine
        if (tagged(node)) continue
        // describe the offender so a human can find it
        const text = (node.textContent ?? "").trim().slice(0, 40)
        const title = node.getAttribute("title") ?? ""
        problems.push(`UNTAGGED <${node.tagName.toLowerCase()}> "${text || title}"`)
    }
    // hand them back
    return problems
}


// every interactive control must carry semantic identity, on every route
test("every interactive control carries semantic identity", async ({ page }) => {
    // sweep the routes
    const problems = await sweep(page, routes, findUntagged)
    // silence is pass; report every offender on failure
    expect(problems, problems.join("\n")).toEqual([])
})


/* end of file */
