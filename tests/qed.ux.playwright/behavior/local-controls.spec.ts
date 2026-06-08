// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// controls that carry NO server-state mutation, so the GraphQL surface cannot see them: the MORE/LESS
// detail toggle (local detail level), a {Tray} header (local expand/collapse), and the nav-rail links
// (client routing). these assert the EFFECT -- content revealed, panel collapsed, route changed --
// not just that the control is findable. they touch only client state, so no server cleanup is needed.

test.describe("client-only controls (no server mutation)", () => {
    test("the detail toggle reveals higher-detail metadata rows", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
        // the metadata table carries the detail control in its header
        const table = page.locator('table:has([data-qed-control="detail"])').first()
        await table.waitFor({ timeout: 10_000 })
        // at the initial detail level a threshold-2 row ({shape}) is hidden
        await expect(table.getByText("shape", { exact: true })).toHaveCount(0)

        // MORE raises the local detail level and the row appears -- no server round-trip
        await page.locator('[data-qed-control="detail"][data-qed-detail="more"]').first().click()
        await expect(table.getByText("shape", { exact: true })).toHaveCount(1)

        // LESS restores the original level
        await page.locator('[data-qed-control="detail"][data-qed-detail="less"]').first().click()
        await expect(table.getByText("shape", { exact: true })).toHaveCount(0)
    })

    test("a tray header collapses and reveals its panel", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
        // the sync panel is always present on /controls; its tray renders its children only when open
        const tray = page.locator('[data-qed-panel="sync"] [data-qed-control="tray"]').first()
        await tray.waitFor({ timeout: 10_000 })
        const items = page.locator('[data-qed-panel="sync"] [role="switch"]')

        const start = await tray.getAttribute("aria-expanded")
        expect(["true", "false"]).toContain(start)
        if (start === "false") await tray.click()
        await expect(tray).toHaveAttribute("aria-expanded", "true")
        expect(await items.count()).toBeGreaterThan(0)

        // collapsing hides the panel's contents
        await tray.click()
        await expect(tray).toHaveAttribute("aria-expanded", "false")
        await expect(items).toHaveCount(0)

        // restore the starting state
        if (start === "true") await tray.click()
    })

    test("a nav-rail link routes to its view", async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        // routing is pure client state -- no GraphQL
        await page.locator('[data-qed-nav="explore data archives"]').first().click()
        await expect(page).toHaveURL(/\/explore$/)
        // and back to the datasets view
        await page.locator('[data-qed-nav="datasets"]').first().click()
        await expect(page).toHaveURL(/\/$/)
    })
})


/* end of file */
