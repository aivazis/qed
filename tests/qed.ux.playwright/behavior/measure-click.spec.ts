// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Browser, Page } from "@playwright/test"


// the mouse on the measure layer: a plain click on the raster adds an anchor, while clicking or
// dragging an existing anchor leaves the count alone; with exactly two anchors, the box control in
// the measure panel turns them into the closed corners of the rectangle they span, in every
// viewport whose path is synced. this mutates the shared server store, so it lives in the behavior
// project and restores the path, the viewports, and their sync flags

// the client's automation surface, published on mount
const ensureQED = (page: Page) => page.waitForFunction(() => Boolean(window.qed))

// the measure toggle glyph on the viewport actions row
const measureToggle = (page: Page) =>
    page.locator('[data-qed-control="viewport"][data-qed-action="measure"]').first()

// the anchor at vertex {index} on the raster
const anchor = (page: Page, index: number) =>
    page.locator(`[role="button"][data-qed-marker-index="${index}"]`)

// the measure state of {viewport}, as the model holds it
const measure = async (page: Page, viewport: number = 0) =>
    page.evaluate(async viewport => (await window.qed.state(viewport))!.measure!, viewport)

// the number of viewports
const viewCount = async (page: Page) => (await page.evaluate(() => window.qed.viewports())).length

// drive the server back to a single viewport, so the rest of the suite sees the lone fixture view
const collapseToOne = async (page: Page) => {
    // collapse the viewports from the last one down
    for (let n = await viewCount(page); n > 1; n--) {
        await page.evaluate(viewport => window.qed.collapse(viewport), n - 1)
    }
}

// force the path-sync flag of {viewport} to {want}; the mutation only toggles
const setPathSync = async (page: Page, viewport: number, want: boolean) => {
    // read the flag
    const now = (await page.evaluate(() => window.qed.viewports()))[viewport]?.sync?.path
    // and flip it if it is not what we want
    if (now !== want) {
        await page.evaluate(viewport => window.qed.sync.toggle("path", viewport), viewport)
    }
}

// the center of {locator} on the screen
const center = async (locator: import("@playwright/test").Locator) => {
    // get its bounding box
    const box = (await locator.boundingBox())!
    // and compute its center
    return { x: box.x + box.width / 2, y: box.y + box.height / 2 }
}

// turn the measure layer on so the anchors and the control table both render
const showMeasure = async (page: Page) => {
    // find the toggle
    const toggle = measureToggle(page)
    await toggle.waitFor({ timeout: 10_000 })
    // and press it, unless the layer is already on
    if ((await toggle.getAttribute("aria-pressed")) !== "true") {
        await toggle.click()
        await expect(toggle).toHaveAttribute("aria-pressed", "true")
    }
}

// reset the path and leave the layer hidden in a single unsynced viewport, the blank state the
// server boots with
const cleanup = async (browser: Browser) => {
    // on a page of its own
    const page = await browser.newPage()
    await page.goto("/controls", { waitUntil: "load" })
    await ensureQED(page)
    // back to one viewport, with its path unsynced
    await collapseToOne(page)
    await setPathSync(page, 0, false)
    // clear the path
    await page.evaluate(() => window.qed.measure.reset())
    // and hide the layer
    const toggle = measureToggle(page)
    await toggle.waitFor({ timeout: 10_000 })
    if ((await toggle.getAttribute("aria-pressed")) === "true") {
        await toggle.click()
        await expect(toggle).toHaveAttribute("aria-pressed", "false")
    }
    await page.close()
}


test.describe.serial("the mouse on the measure layer", () => {
    test.beforeAll(async ({ browser }) => { await cleanup(browser) })
    test.afterAll(async ({ browser }) => { await cleanup(browser) })

    test("a plain click adds an anchor; clicking or dragging one does not", async ({ page }) => {
        // seed the path with one anchor through the facade, well inside the fixture
        await page.goto("/controls", { waitUntil: "load" })
        await ensureQED(page)
        await page.evaluate(() => window.qed.measure.add(200, 100))
        await showMeasure(page)
        await expect(anchor(page, 0)).toBeVisible()
        // a plain click on the raster, beside the first anchor
        const first = await center(anchor(page, 0))
        await page.mouse.click(first.x + 60, first.y + 40)
        // adds a second anchor
        await expect.poll(async () => (await measure(page)).path.length).toBe(2)
        await expect(anchor(page, 1)).toBeVisible()

        // clicking the first anchor
        await page.mouse.click(first.x, first.y)
        // toggles its selection
        await expect(anchor(page, 0)).toHaveAttribute("aria-pressed", "true")
        // without adding another
        expect((await measure(page)).path.length).toBe(2)

        // dragging the second anchor
        const second = await center(anchor(page, 1))
        await page.mouse.move(second.x, second.y)
        await page.mouse.down()
        await page.mouse.move(second.x + 30, second.y + 20, { steps: 5 })
        await page.mouse.up()
        // moves it, without adding another
        await expect.poll(async () => (await measure(page)).path.length).toBe(2)
        await page.waitForTimeout(500)
        expect((await measure(page)).path.length).toBe(2)
    })

    test("the box control turns two anchors into the closed corners of a box", async ({ page }) => {
        // start over with two anchors through the facade
        await page.goto("/controls", { waitUntil: "load" })
        await ensureQED(page)
        await page.evaluate(() => window.qed.measure.reset())
        await page.evaluate(() => window.qed.measure.add(200, 100))
        await page.evaluate(() => window.qed.measure.add(260, 150))
        await showMeasure(page)
        // the control shows up with exactly two anchors
        const box = page.getByRole("button", { name: "make a box out of the two anchors" })
        await expect(box).toBeVisible()
        // while the spectrum of the rectangle they span is not offered, since only the datasets
        // of an RSLC have one
        await expect(page.getByRole("button", { name: "compute the spectrum of the region" }))
            .toHaveCount(0)
        // pressing it
        await box.click()
        // leaves the four corners of the rectangle the anchors span, in order around it
        await expect.poll(async () => (await measure(page)).path.length).toBe(4)
        const state = await measure(page)
        expect(state.path).toEqual([
            { row: 200, col: 100 },
            { row: 200, col: 150 },
            { row: 260, col: 150 },
            { row: 260, col: 100 },
        ])
        // closed, with every corner selected
        expect(state.closed).toBe(true)
        expect(state.selection).toEqual([0, 1, 2, 3])
    })

    test("the box reaches every viewport whose path is synced", async ({ page }) => {
        // start from one viewport with an empty path, and split it in two
        await page.goto("/controls", { waitUntil: "load" })
        await ensureQED(page)
        await collapseToOne(page)
        await page.evaluate(() => window.qed.measure.reset())
        await page.evaluate(() => window.qed.split(0))
        await expect.poll(() => viewCount(page)).toBe(2)
        // sync the paths of both
        await setPathSync(page, 0, true)
        await setPathSync(page, 1, true)
        // and clear the path of the new one
        await page.evaluate(() => window.qed.measure.reset(1))
        // two anchors in the first viewport reach the second one too
        await page.evaluate(() => window.qed.measure.add(200, 100, null, 0))
        await page.evaluate(() => window.qed.measure.add(260, 150, null, 0))
        await expect.poll(async () => (await measure(page, 1)).path.length).toBe(2)
        // make the box through the control of the first viewport
        await page.evaluate(() => window.qed.setActive(0))
        await showMeasure(page)
        const box = page.getByRole("button", { name: "make a box out of the two anchors" })
        await box.first().click()
        // both viewports hold the closed box
        for (const viewport of [0, 1]) {
            await expect.poll(async () => (await measure(page, viewport)).path.length).toBe(4)
            expect((await measure(page, viewport)).closed).toBe(true)
        }
    })
})


// end of file
