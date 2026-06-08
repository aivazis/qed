// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the minimap reports the visible window in source pixels and re-renders on every scroll. this
// proves the reported window actually tracks the viewport scroll: scroll to a known place, and the
// minimap's window origin must converge to that scroll scaled by the published zoom -- the exact
// mapping a driver relies on to turn a click into a source pixel. scrolling touches per-page DOM
// state, but it may persist server-side, so this lives in the behavior project (serial, after the
// gate) and restores the scroll it touches.
test.describe.serial("the minimap window tracks the viewport scroll", () => {
    test("scrolling the viewport moves the reported window origin to the scaled scroll", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
        const region = page.locator('[data-qed-region="viewport"]').first()
        await region.waitFor({ timeout: 10_000 })

        // derive the scale the driver would use from the published zoom -- no magic constants
        const [zv, zh] = (await region.getAttribute("data-qed-zoom"))!.split(",").map(Number)
        const [scaleRow, scaleCol] = [2 ** -zv, 2 ** -zh]

        // scroll the viewport to a known place
        const [top, left] = [64, 128]
        await region.evaluate((el, [t, l]) => { el.scrollTop = t; el.scrollLeft = l }, [top, left])

        // the minimap re-renders on scroll, so its window origin converges to the scaled scroll
        const expected = `${Math.round(top * scaleRow)},${Math.round(left * scaleCol)}`
        const box = page.locator('[data-qed-control="minimap"] [data-qed-view-origin]').first()
        await expect.poll(() => box.getAttribute("data-qed-view-origin")).toBe(expected)

        // restore the scroll so the shared store is left as we found it
        await region.evaluate(el => { el.scrollTop = 0; el.scrollLeft = 0 })
    })
})


/* end of file */
