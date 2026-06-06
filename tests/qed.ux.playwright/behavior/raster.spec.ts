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

// a GraphQL helper, same-origin; selecting {zoom} forces the lazy server-side mutator to run
const gql = (page: Page, query: string) =>
    page.evaluate(async q => (await fetch("/graphql", {
        method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ query: q }),
    })).json(), query)

const setZoom = (page: Page, h: number, v: number) =>
    gql(page, `mutation { viewZoomSetLevel(input: {viewport: 0, horizontal: ${h}, vertical: ${v}}) { zooms { horizontal vertical } } }`)

// load the readers view and report the rendered mosaic's pixel extent
const mosaicExtent = async (page: Page) => {
    await page.goto("/", { waitUntil: "networkidle" })
    const box = page.locator('[data-pyre-widget="mosaic"]').first()
    await box.waitFor({ timeout: 10_000 })
    return box.evaluate(m => ({ w: (m as HTMLElement).offsetWidth, h: (m as HTMLElement).offsetHeight }))
}


test.describe.serial("the raster resizes with zoom", () => {
    test.afterAll(async ({ browser }) => {
        // leave the shared server at the default zoom for anything that reuses it
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "networkidle" })
        await setZoom(page, 0, 0)
        await page.close()
    })

    test("the mosaic extent tracks the zoom level", async ({ page }) => {
        // make sure a channel is selected so the mosaic renders
        await page.goto("/", { waitUntil: "networkidle" })
        const reader = (await gql(page, "{ qed { views { reader { name } } } }")).data.qed.views[0].reader.name
        await gql(page, `mutation { viewChannelSet(input: {viewport: 0, reader: "${reader}", value: "amplitude"}) { views { channel { tag } } } }`)

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
