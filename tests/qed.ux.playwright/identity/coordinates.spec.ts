// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// to map a click on the rendered raster to a source pixel (and back), a driver needs the geometry
// that relates screen space to source space. the viewport region publishes its full source
// {shape} and the current {zoom} (so the scale is 2**-zoom); the minimap names the same raster and
// reports the visible window's origin and shape in SOURCE PIXELS, row-major like the tile api. the
// minimap re-renders on every scroll, so its window is live -- a driver reads what is on screen
// without doing the pixel arithmetic itself. all of this co-mounts on {/controls}. this spec is
// part of the read-only gate; the behavior project proves the live window tracks a scroll.
test.describe("the viewport coordinate metadata", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/controls", { waitUntil: "networkidle" })
        await page.locator('[data-qed-region="viewport"]').first().waitFor({ timeout: 10_000 })
    })

    test("the viewport region publishes its source shape and zoom", async ({ page }) => {
        const region = page.locator('[data-qed-region="viewport"]').first()
        // the shape is the full source extent, row-major
        await expect(region).toHaveAttribute("data-qed-shape", /^\d+,\d+$/)
        // the zoom is the vertical,horizontal log2 level, so a driver derives the scale as 2**-zoom
        await expect(region).toHaveAttribute("data-qed-zoom", /^-?\d+,-?\d+$/)
    })

    test("the minimap names the same raster and reports the window in source pixels", async ({ page }) => {
        const region = page.locator('[data-qed-region="viewport"]').first()
        const minimap = page.locator('[data-qed-control="minimap"]').first()
        // the minimap describes the same raster the region does
        expect(await minimap.getAttribute("data-qed-shape"))
            .toBe(await region.getAttribute("data-qed-shape"))
        // its viewport box reports the visible window as source-pixel origin + shape, row-major
        const box = minimap.locator('[data-qed-view-origin]')
        await expect(box).toHaveAttribute("data-qed-view-origin", /^\d+,\d+$/)
        await expect(box).toHaveAttribute("data-qed-view-shape", /^\d+,\d+$/)
    })
})


/* end of file */
