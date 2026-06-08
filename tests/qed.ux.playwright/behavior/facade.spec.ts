// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the automation surface's catalog read and viewport scrolling: {readers()} lists the readers the
// server offers, and {centerOn} scrolls a viewport so a source pixel sits at the window center. both
// are verified through the same markup the rest of the suite reads, so a broken command fails here.
test.describe.serial("the automation surface reads the catalog and scrolls", () => {
    test("readers() lists the catalog, including the active reader", async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // the catalog the facade reports, and the reader the active view is on
        const { active, names } = await page.evaluate(async () => ({
            active: (await window.qed.state())?.reader,
            names: (await window.qed.readers()).map(reader => reader.name),
        }))
        // the catalog is non-empty and contains the reader the view actually uses
        expect(names.length).toBeGreaterThan(0)
        expect(names).toContain(active)
    })

    test("centerOn scrolls the viewport so the source pixel lands at the window center", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // a channel is selected (the setup project), so the raster renders; at zoom 0 the whole raster
        // is large enough to scroll a mid-raster pixel to the center
        await page.evaluate(() => window.qed.setZoom(0))
        // {centerOn} converts source pixels to a scroll offset against the rendered region, so wait
        // until the mosaic has laid out and the region is actually scrollable before centering --
        // otherwise the offset is computed against an unsized region and clamped to the origin
        const region = page.locator('[data-qed-region="viewport"]').first()
        await region.waitFor()
        await expect
            .poll(() => region.evaluate(el => el.scrollHeight - el.clientHeight))
            .toBeGreaterThan(0)
        const target = { row: 1500, col: 1000 }
        await page.evaluate(t => window.qed.centerOn(t.row, t.col), target)

        // the minimap publishes the visible window's origin and shape in source pixels; its center
        // must be the pixel we asked for, within a few pixels of rounding
        const box = page.locator('[data-qed-control="minimap"] [data-qed-view-origin]').first()
        await expect.poll(async () => {
            const [oRow, oCol] = (await box.getAttribute("data-qed-view-origin"))!.split(",").map(Number)
            const [sRow, sCol] = (await box.getAttribute("data-qed-view-shape"))!.split(",").map(Number)
            return Math.max(Math.abs(oRow + sRow / 2 - target.row), Math.abs(oCol + sCol / 2 - target.col))
        }).toBeLessThan(30)
    })
})


/* end of file */
