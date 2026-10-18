// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Browser, Page } from "@playwright/test"


// a click in a viewport the user is not working in makes it the active one, and nothing else: it
// must not also drop an anchor on its measure layer. once the viewport is active, a click adds an
// anchor as usual. this mutates the shared server store, so it lives in the behavior project and
// restores the viewports and their measure layers

// the client's automation surface, published on mount
const ensureQED = (page: Page) => page.waitForFunction(() => Boolean(window.qed))

// the models of the viewports
const viewports = (page: Page) => page.evaluate(() => window.qed.viewports())

// the index of the active viewport, which is the one the facade addresses by default
const active = async (page: Page) => (await page.evaluate(() => window.qed.state()))!.viewport

// the number of anchors on the path of {viewport}
const anchors = async (page: Page, viewport: number) =>
    (await viewports(page))[viewport].measure!.path.length

// the anchor at vertex {index} on the measure layer of {viewport}
const anchor = (page: Page, viewport: number, index: number) =>
    page.locator(`[data-qed-viewport="${viewport}"] [role="button"][data-qed-marker-index="${index}"]`)

// back to a single viewport, with an empty path and its measure layer off, the way the server boots
const cleanup = async (browser: Browser) => {
    // on a page of its own
    const page = await browser.newPage()
    await page.goto("/", { waitUntil: "load" })
    await ensureQED(page)
    // collapse the viewports from the last one down
    for (let n = (await viewports(page)).length; n > 1; n--) {
        await page.evaluate(viewport => window.qed.collapse(viewport), n - 1)
    }
    // clear the path
    await page.evaluate(() => window.qed.measure.reset(0))
    // and hide the layer
    if ((await viewports(page))[0].measure!.active) {
        await page.evaluate(() => window.qed.measure.toggle(0))
    }
    // all done
    await page.close()
}


test.describe.serial("a click that activates a viewport", () => {
    test.beforeAll(async ({ browser }) => { await cleanup(browser) })
    test.afterAll(async ({ browser }) => { await cleanup(browser) })

    test("does not drop an anchor; the next click does", async ({ page }) => {
        // start from the viewer
        await page.goto("/", { waitUntil: "load" })
        await ensureQED(page)
        // split the viewport, which makes a second one that shows the same raster
        await page.evaluate(() => window.qed.split(0))
        await expect.poll(async () => (await viewports(page)).length).toBe(2)
        // clear the path of both
        await page.evaluate(() => window.qed.measure.reset(0))
        await page.evaluate(() => window.qed.measure.reset(1))
        // show the measure layer of the second one
        if (!(await viewports(page))[1].measure!.active) {
            await page.evaluate(() => window.qed.measure.toggle(1))
        }
        // and seed its path with an anchor, so there is a spot on its raster to click beside
        await page.evaluate(() => window.qed.measure.add(200, 100, null, 1))
        await expect(anchor(page, 1, 0)).toBeVisible()
        // make the first viewport the active one
        await page.evaluate(() => window.qed.setActive(0))
        await expect.poll(() => active(page)).toBe(0)

        // find a spot on the raster of the second viewport, beside its anchor
        const box = (await anchor(page, 1, 0).boundingBox())!
        const spot = { x: box.x + box.width / 2 + 60, y: box.y + box.height / 2 + 40 }
        // click it
        await page.mouse.click(spot.x, spot.y)
        // the second viewport becomes the active one
        await expect.poll(() => active(page)).toBe(1)
        // and its path is left alone
        expect(await anchors(page, 1)).toBe(1)

        // click the same spot again, now that the viewport is active
        await page.mouse.click(spot.x, spot.y)
        // and the click adds an anchor
        await expect.poll(() => anchors(page, 1)).toBe(2)
    })
})


// end of file
