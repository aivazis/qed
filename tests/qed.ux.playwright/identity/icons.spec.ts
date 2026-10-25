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
// accessible name + identity live on the control. every badge also says on hover what a click
// does, with the client's own title or else its label.
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

    test("every badge says on hover what a click does", async ({ page }) => {
        // the badges are the buttons whose only content is a decorative glyph; a tray header
        // starts with a glyph too, but goes on to its title
        const badges = '[role="button"]:has(> svg[aria-hidden="true"]:only-child)'
        // on the datasets panel, and then on the archives panel
        for (const route of ["/", "/explore"]) {
            await page.goto(route, { waitUntil: "load" })
            await page.locator(badges).first().waitFor({ timeout: 10_000 })
            const info = await page.locator(badges).evaluateAll(els => els.map(e => ({
                label: e.getAttribute("aria-label"),
                title: e.getAttribute("title"),
            })))
            // there are some
            expect(info.length).toBeGreaterThan(0)
            // and each one has hover text
            for (const badge of info) expect(badge.title, JSON.stringify(badge)).toBeTruthy()
        }
        // among them the controls of the panel headers
        await expect(page.getByLabel("refresh this archive").first()).toHaveAttribute("title", "refresh this archive")
        await expect(page.getByLabel("connect a new archive")).toHaveAttribute("title", "connect a new archive")
    })
})


/* end of file */
