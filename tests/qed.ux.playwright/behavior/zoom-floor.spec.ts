// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// zooming out stops at the level a thumbnail of the dataset comes from: the level at which the
// raster, halved level by level, fits in a single tile. the native fixture is 3929 by 6049 cells in
// tiles of 512 by 512, which takes four halvings, so its zoom scale ends at -4, and a view asked to
// go further out is shown at -4

// the horizontal zoom level the server shows
const horizontal = (page) => page.evaluate(async () => (await window.qed.state())!.zoom!.horizontal)


test.describe.serial("zooming out stops at the thumbnail", () => {
    test("the zoom scale ends at the level of the thumbnail", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // the horizontal zoom track, found by its thumb
        const track = page.locator('[data-pyre-widget="slider"][data-pyre-widget-part="track"]')
            .filter({ has: page.getByRole("slider", { name: "zoom horizontal" }) })
        await track.waitFor()
        // it offers the level of the thumbnail
        await expect(track.locator('[data-pyre-widget-part="tick"][data-pyre-tick="-4"]')).toHaveCount(1)
        // and nothing further out
        await expect(track.locator('[data-pyre-tick="-5"]')).toHaveCount(0)
        await expect(track.locator('[data-pyre-tick="-6"]')).toHaveCount(0)
    })

    test("a view asked to zoom further out is shown at the thumbnail", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // ask for a level past the thumbnail
        await page.evaluate(() => window.qed.setZoom(-6))
        // and see it shown at the thumbnail
        await expect.poll(() => horizontal(page), { timeout: 10_000 }).toBe(-4)
        // restore
        await page.evaluate(() => window.qed.setZoom(0))
        await expect.poll(() => horizontal(page), { timeout: 10_000 }).toBe(0)
    })
})


// end of file
