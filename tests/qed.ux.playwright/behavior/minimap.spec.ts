// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// the minimap translates a click on its overview into a scroll of the active viewport, scaled by
// the current zoom. a regression let the click/drag handlers capture a STALE zoom factor: after
// zooming and returning to a previous level *in place* (without remounting), a click scrolled by
// the wrong amount, because the effect that binds the handler only re-ran when {scale} changed --
// and {scale} is invariant under zoom for a large raster.
//
// the bug only appears across an *in-place* zoom transition, so this drives the zoom through the
// client's own slider (a Relay mutation, no remount), then checks the invariant: a click on a
// fixed minimap spot must scroll to the same place no matter the zoom history.

const gql = (page: Page, query: string) =>
    page.evaluate(async q => (await fetch("/graphql", {
        method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ query: q }),
    })).json(), query)

// the active viewport is the mosaic's scrollable parent
const readScrollLeft = (page: Page) =>
    page.evaluate(() => {
        const m = document.querySelector('[data-pyre-widget="mosaic"]')
        return (m?.parentElement as HTMLElement)?.scrollLeft ?? null
    })
const resetScroll = (page: Page) =>
    page.evaluate(() => {
        const vp = document.querySelector('[data-pyre-widget="mosaic"]')?.parentElement as HTMLElement
        if (vp) { vp.scrollLeft = 0; vp.scrollTop = 0 }
    })
const waitForZoom = async (page: Page, horizontal: number) =>
    expect.poll(async () =>
        (await gql(page, "{ qed { views { zoom { horizontal } } } }")).data.qed.views[0].zoom.horizontal
    ).toBe(horizontal)


test.describe.serial("the minimap tracks the current zoom", () => {
    test.afterAll(async ({ browser }) => {
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "networkidle" })
        await gql(page, "mutation { viewZoomSetLevel(input: {viewport: 0, horizontal: 0, vertical: 0}) { zooms { horizontal } } }")
        await page.close()
    })

    test("a minimap click maps to the same scroll regardless of zoom history", async ({ page }) => {
        // a channel must be selected and the zoom at 0 to start
        await page.goto("/", { waitUntil: "networkidle" })
        const reader = (await gql(page, "{ qed { views { reader { name } } } }")).data.qed.views[0].reader.name
        await gql(page, `mutation { viewChannelSet(input: {viewport: 0, reader: "${reader}", value: "amplitude"}) { views { channel { tag } } } }`)
        await gql(page, "mutation { viewZoomSetLevel(input: {viewport: 0, horizontal: 0, vertical: 0}) { zooms { horizontal } } }")
        await page.goto("/controls", { waitUntil: "networkidle" })

        // the minimap's data rect (Placemat, Data, Viewport -> the second one) and the horizontal
        // zoom slider (the slider with a horizontal thumb whose ticks include -6)
        const dataRect = page.locator('[data-qed-control="minimap"] rect').nth(1)
        await dataRect.waitFor({ timeout: 10_000 })
        const zoomTrack = page.locator('[data-pyre-widget="slider"][data-pyre-widget-part="track"]')
            .filter({ has: page.locator('[aria-orientation="horizontal"]') })
            .filter({ hasText: "-6" })

        const clickAt = { position: { x: 60, y: 30 } }

        // baseline at zoom 0: a click yields a definite, unclamped scroll
        await resetScroll(page)
        await dataRect.click(clickAt)
        await page.waitForTimeout(150)
        const baseline = await readScrollLeft(page)
        // the click must land somewhere meaningful (and far from the buggy 1/4 value)
        expect(baseline).toBeGreaterThan(800)

        // zoom out two octaves and back to 0, IN PLACE, through the coupled zoom slider
        await zoomTrack.getByText("-2", { exact: true }).click()
        await waitForZoom(page, -2)
        await zoomTrack.getByText("0", { exact: true }).click()
        await waitForZoom(page, 0)

        // the same click must scroll to the same place; a stale zoom factor would divide it by ~4
        await resetScroll(page)
        await dataRect.click(clickAt)
        await page.waitForTimeout(150)
        const afterHistory = await readScrollLeft(page)
        expect(Math.abs(afterHistory! - baseline!)).toBeLessThan(30)
    })
})


/* end of file */
