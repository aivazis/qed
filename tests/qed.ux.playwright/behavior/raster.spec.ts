// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// the raster mosaic must size its scrollable extent from the ZOOMED shape, so the visible raster
// grows and shrinks with the zoom level. a regression once forced the *raw* shape onto the box
// (a styled wrapper's class leaked the un-zoomed width/height), freezing the scroll extent at the
// zoom-0 size. this drives the zoom server-side and checks the box actually resizes.
//
// it mutates shared server state (the zoom level), so it runs in the {behavior} project, which is
// gated behind the read-only checks and serialized; it restores the zoom on the way out.

// drive the client's automation surface ({window.qed}) from inside the page; it commits through the
// live Relay store, so the state is set without a raw fetch. the app publishes the facade on mount,
// so wait for it after each navigation
const setZoom = async (page: Page, horizontal: number, vertical: number) => {
    await page.waitForFunction(() => Boolean(window.qed))
    await page.evaluate(level => window.qed.setZoom(level), { horizontal, vertical })
}
const setChannel = async (page: Page, tag: string) => {
    await page.waitForFunction(() => Boolean(window.qed))
    await page.evaluate(channel => window.qed.setChannel(channel), tag)
}

// load the readers view and report the rendered mosaic's pixel extent
const mosaicExtent = async (page: Page) => {
    await page.goto("/", { waitUntil: "load" })
    const box = page.locator('[data-pyre-widget="mosaic"]').first()
    await box.waitFor({ timeout: 10_000 })
    return box.evaluate(m => ({ w: (m as HTMLElement).offsetWidth, h: (m as HTMLElement).offsetHeight }))
}


test.describe.serial("the raster resizes with zoom", () => {
    test.afterAll(async ({ browser }) => {
        // leave the shared server at the default zoom for anything that reuses it
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "load" })
        await setZoom(page, 0, 0)
        await page.close()
    })

    test("the mosaic extent tracks the zoom level", async ({ page }) => {
        // make sure a channel is selected so the mosaic renders; the facade resolves the reader itself
        await page.goto("/", { waitUntil: "load" })
        await setChannel(page, "amplitude")

        // the extent at zoom 0
        await setZoom(page, 0, 0)
        const at0 = await mosaicExtent(page)
        expect(at0.w).toBeGreaterThan(0)

        // zoom out by two octaves: the raster should shrink to about a quarter, NOT stay frozen
        await setZoom(page, -2, -2)
        const out = await mosaicExtent(page)
        expect(out.w).toBeLessThan(at0.w * 0.6)
        expect(out.h).toBeLessThan(at0.h * 0.6)
        // and specifically ~1/4 (allow a few px of rounding)
        expect(Math.abs(out.w - at0.w / 4)).toBeLessThan(5)
        expect(Math.abs(out.h - at0.h / 4)).toBeLessThan(5)
    })
})


/* end of file */
