// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page, Locator } from "@playwright/test"


// the band / frequency / polarization selectors only surface for a multi-dataset NISAR reader, which
// the native fixture does not have. this suite runs against the dedicated NISAR server (its own port
// and data dir, wired in playwright.config) and asserts the selector markup: each axis is a
// radiogroup, each value a radio with its state in ARIA. one spec operates the controls (selects a
// reader and a value through the client's own GraphQL endpoint), so the suite is serial and restores
// what it touches.

// the GSLC reader's axes, as the server reports them (`{ qed { readers { selectors } } }`)
const GSLC = {
    band: ["L", "S"],
    frequency: ["A", "B"],
    polarization: ["HH", "HV", "VH", "VV"],
}

// the same GraphQL endpoint the client uses, driven from inside the page; a raw {fetch} does not
// update the page's Relay store, so callers reload the route afterward to render the change
const gql = (page: Page, query: string) =>
    page.evaluate(async (q) => {
        const response = await fetch("/graphql", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ query: q }),
        })
        return response.json()
    }, query)

// the radiogroup for {axis} within the {reader}'s panel
const group = (page: Page, reader: string, axis: string): Locator =>
    page.locator(`[data-qed-reader="${reader}"] [data-qed-control="selector"][data-qed-axis="${axis}"]`)


test.describe.serial("the NISAR axis selectors are tagged radiogroups", () => {
    test("each gslc axis is a radiogroup whose values are radios named by their text", async ({ page }) => {
        await page.goto("/", { waitUntil: "networkidle" })
        // the readers panel renders both fixtures; wait for the gslc reader to mount
        await page.locator('[data-qed-reader="gslc"]').waitFor({ timeout: 10_000 })

        // every axis the gslc reader offers is a radiogroup named for the axis it binds
        for (const [axis, values] of Object.entries(GSLC)) {
            const radiogroup = group(page, "gslc", axis)
            await expect(radiogroup).toHaveAttribute("role", "radiogroup")
            await expect(radiogroup).toHaveAttribute("aria-label", axis)

            // each value is a radio, its accessible name carried by its visible text
            for (const value of values) {
                const option = radiogroup.locator(`[data-qed-value="${value}"]`)
                await expect(option).toHaveAttribute("role", "radio")
                await expect(option).toHaveText(value)
            }
        }
    })

    test("selecting a value checks exactly that radio, with the state living in ARIA", async ({ page }) => {
        // select the gslc reader, then pick frequency A, through the same endpoint the client uses
        await page.goto("/", { waitUntil: "networkidle" })
        await gql(page, `mutation { viewSelectReader(viewport: 0, reader: "gslc") { view { id } } }`)
        await gql(page, `mutation { viewToggleCoordinate(selection: ` +
            `{viewport: 0, reader: "gslc", selector: "frequency", value: "A"}) { view { id } } }`)
        await page.goto("/", { waitUntil: "networkidle" })

        // exactly one radio in the frequency group is checked, and it is A -- state in ARIA, never
        // mirrored into a data attribute
        const frequency = group(page, "gslc", "frequency")
        await expect(frequency.locator('[data-qed-value="A"]')).toHaveAttribute("aria-checked", "true")
        await expect(frequency.locator('[data-qed-value="B"]')).toHaveAttribute("aria-checked", "false")
        await expect(frequency.locator('[aria-checked="true"]')).toHaveCount(1)

        // restore the blank selection so a rerun starts clean: toggling A again clears it
        await gql(page, `mutation { viewToggleCoordinate(selection: ` +
            `{viewport: 0, reader: "gslc", selector: "frequency", value: "A"}) { view { id } } }`)
    })
})


/* end of file */
