// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the app's icon controls are SVG glyphs with no text, so they are invisible to a driver and to
// assistive tech unless named. the nav-rail items are links that carry the name; the viewport
// action glyphs are {Badge} buttons; in both cases the svg is decorative (aria-hidden) and the
// accessible name + identity live on the control.
test.describe("icon controls", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        await page.locator('[data-qed-nav]').first().waitFor({ timeout: 10_000 })
    })

    test("the nav-rail items are named links with a nav identity", async ({ page }) => {
        const items = page.locator("[data-qed-nav]")
        // explore, datasets, controls, help (at least) are always present
        const labels = await items.evaluateAll(els => els.map(e => e.getAttribute("aria-label")))
        expect(labels.length).toBeGreaterThanOrEqual(4)
        // every one has a non-empty accessible name
        for (const label of labels) expect(label).toBeTruthy()
    })

    test("each viewport action is a named control with a stable identity", async ({ page }) => {
        const actions = page.locator('[data-qed-control="viewport"][data-qed-action]')
        const info = await actions.evaluateAll(els => els.map(e => ({
            action: e.getAttribute("data-qed-action"),
            label: e.getAttribute("aria-label"),
        })))
        // the single viewport offers several actions (split, measure, sync, print, ...)
        expect(info.length).toBeGreaterThanOrEqual(3)
        for (const a of info) {
            expect(a.action).toBeTruthy()
            expect(a.label).toBeTruthy()
        }
        // and the glyph each one wraps is decorative, so its name comes from the control
        await expect(actions.first().locator("svg").first()).toHaveAttribute("aria-hidden", "true")
    })
})


/* end of file */
