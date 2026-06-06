// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// the measure-layer markers carry verifiable identity: each anchor -- on the raster and in the
// control table -- exposes its {row,col} source pixel and its vertex ordinal, so a driver enumerates
// the polygon in order and reads each marker back by coordinate. placing, splitting, and resetting
// anchors mutates the shared server store, so this lives in the behavior project (serial, after the
// read-only gate) and resets the path it touches.

// the same GraphQL endpoint the client uses, driven from inside the page (pyre's minimal server
// understands the browser's {fetch}, not playwright's node-side {request} fixture). the page's Relay
// store does not learn of a raw {fetch} mutation, so callers reload the route afterward to render it.
const gql = (page: Page, query: string) =>
    page.evaluate(async (q) => {
        const response = await fetch("/graphql", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ query: q }),
        })
        return response.json()
    }, query)

// place an anchor at {col,row} on viewport 0; the api is column-major in its arguments ({x},{y}).
// {index: null} appends -- the resolver's {index} parameter has no default, so it must be sent
const place = (page: Page, col: number, row: number) =>
    gql(page, `mutation { viewMeasureAnchorAdd(input: {viewport: 0, x: ${col}, y: ${row}, index: null}) ` +
        `{ measures { dirty } } }`)

// the measure toggle glyph on the viewport actions row
const measureToggle = (page: Page) =>
    page.locator('[data-qed-control="viewport"][data-qed-action="measure"]').first()

// turn the measure layer on so the anchors and the control table both render
const showMeasure = async (page: Page) => {
    const toggle = measureToggle(page)
    await toggle.waitFor({ timeout: 10_000 })
    if ((await toggle.getAttribute("aria-pressed")) !== "true") {
        await toggle.click()
        await expect(toggle).toHaveAttribute("aria-pressed", "true")
    }
}

// reset the path and leave the layer hidden, the blank state the server boots with
const cleanup = async (browser: import("@playwright/test").Browser) => {
    const page = await browser.newPage()
    await page.goto("/controls", { waitUntil: "networkidle" })
    await gql(page, `mutation { viewMeasureReset(input: {viewport: 0}) { measures { dirty } } }`)
    // the raw fetch does not update the page's Relay store, so reload to render the cleared path
    // before operating the toggle; otherwise it acts on stale anchors and the layer does not hide
    await page.goto("/controls", { waitUntil: "networkidle" })
    const toggle = measureToggle(page)
    await toggle.waitFor({ timeout: 10_000 })
    if ((await toggle.getAttribute("aria-pressed")) === "true") {
        await toggle.click()
        await expect(toggle).toHaveAttribute("aria-pressed", "false")
    }
    await page.close()
}


test.describe.serial("measure markers carry verifiable identity", () => {
    // the points we drop, as [col, row] -- well inside the 3929x6049 fixture
    const points: Array<[number, number]> = [[100, 200], [150, 260], [80, 300]]

    test.beforeAll(async ({ browser }) => { await cleanup(browser) })
    test.afterAll(async ({ browser }) => { await cleanup(browser) })

    test("placed markers read back by source coordinate at both ends", async ({ page }) => {
        // drop the points through the client's own endpoint, then reload so the fresh query renders them
        await page.goto("/controls", { waitUntil: "networkidle" })
        for (const [col, row] of points) await place(page, col, row)
        await page.goto("/controls", { waitUntil: "networkidle" })
        // reveal the layer and its table
        await showMeasure(page)

        // each control-table row mirrors the placement order, keyed by its vertex ordinal, and reads
        // back as {row,col} -- the column-major api argument is reported row-major, like the rest of qed
        for (let i = 0; i < points.length; ++i) {
            const [col, row] = points[i]
            const entry = page.locator(`[data-qed-panel="measure"] [data-qed-marker-index="${i}"]`)
            await expect(entry).toHaveAttribute("data-qed-source", `${row},${col}`)
        }

        // the on-raster anchors agree marker for marker; they are the {role=button} carriers, which
        // also disambiguates them from the table rows that share the {data-qed-marker-index} attribute
        for (let i = 0; i < points.length; ++i) {
            const [col, row] = points[i]
            const anchor = page.locator(`[role="button"][data-qed-marker-index="${i}"]`)
            await expect(anchor).toHaveAttribute("data-qed-source", `${row},${col}`)
            // selection state lives in ARIA, never mirrored into a data attribute
            await expect(anchor).toHaveAttribute("aria-pressed", "false")
        }
    })

    test("splitting a segment renumbers the vertices while sources verify the move", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "networkidle" })
        await showMeasure(page)

        // the second point's identity before the edit: ordinal 1, at its placed source
        const [col1, row1] = points[1]
        const second = page.locator(`[data-qed-panel="measure"] [data-qed-marker-index="1"]`)
        await expect(second).toHaveAttribute("data-qed-source", `${row1},${col1}`)

        // insert a vertex between ordinals 0 and 1 -- the midpoint of the two placed points -- then
        // reload so the renumbered path renders
        await gql(page, `mutation { viewMeasureAnchorSplit(input: {viewport: 0, anchor: 0}) { measures { dirty } } }`)
        await page.goto("/controls", { waitUntil: "networkidle" })
        await showMeasure(page)
        const [col0, row0] = points[0]
        const mid = `${Math.round((row0 + row1) / 2)},${Math.round((col0 + col1) / 2)}`

        // the inserted vertex now owns ordinal 1; the point that was ordinal 1 has shifted to ordinal 2,
        // unchanged in source -- proof the ordinal is polygon position, and the source is what verifies a
        // marker across an edit
        const inserted = page.locator(`[data-qed-panel="measure"] [data-qed-marker-index="1"]`)
        await expect(inserted).toHaveAttribute("data-qed-source", mid)
        const shifted = page.locator(`[data-qed-panel="measure"] [data-qed-marker-index="2"]`)
        await expect(shifted).toHaveAttribute("data-qed-source", `${row1},${col1}`)
    })

    test("resetting through the control clears the rendered path live, with no reload", async ({ page }) => {
        // this serial block accumulates anchors across its tests, so start from a known-empty path
        // (backdoor reset is a fine teardown/setup tool) then place exactly two and render them
        await page.goto("/controls", { waitUntil: "networkidle" })
        await gql(page, `mutation { viewMeasureReset(input: {viewport: 0}) { measures { dirty } } }`)
        await page.goto("/controls", { waitUntil: "networkidle" })
        for (const [col, row] of points.slice(0, 2)) await place(page, col, row)
        await page.goto("/controls", { waitUntil: "networkidle" })
        await showMeasure(page)
        const markers = page.locator(`[data-qed-panel="measure"] [data-qed-marker-index]`)
        await expect(markers).toHaveCount(2)

        // reset through the client's OWN control -- a Relay mutation, not a raw fetch. the reset must
        // update the Relay store, so the rendered path clears WITHOUT a reload. if it does not, the
        // client reset is broken and this fails: that is the expectation, recorded
        const reset = page.locator('[data-qed-panel="measure"]')
            .getByRole("button", { name: "reset the values to their defaults" })
        await reset.click()
        await expect(markers).toHaveCount(0)
        await expect(page.locator(`[role="button"][data-qed-marker-index]`)).toHaveCount(0)
    })
})


/* end of file */
