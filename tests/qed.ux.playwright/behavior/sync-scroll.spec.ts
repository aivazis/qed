// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page, Locator } from "@playwright/test"


// scroll-synced viewports must show the same source pixel even when they sit at different zoom
// levels and carry a relative offset. the scroll offset lives in rendered pixels (scale 2**zoom),
// so the pan dispatcher converts the panned viewport's offset to source pixels, applies the
// relative offset (also source pixels), and converts into each peer's own rendered pixels. with
// two viewports at zoom 0 and -2, panning the first must land the second on the same source pixel,
// shifted by the offset. this splits a viewport (server state) and collapses it again afterward.

const gql = (page: Page, query: string) =>
    page.evaluate(async q => (await fetch("/graphql", {
        method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ query: q }),
    })).json(), query)

const viewCount = async (page: Page) =>
    (await gql(page, "{ qed { views { id } } }")).data.qed.views.length

// drive the server back to a single viewport, so the rest of the suite sees the lone fixture view
const collapseToOne = async (page: Page) => {
    for (let n = await viewCount(page); n > 1; n--) {
        await gql(page, `mutation { viewCollapse(input: {viewport: ${n - 1}}) { view { id } } }`)
    }
}

// force the scroll-sync flag of a viewport to {want} (the mutation only toggles)
const setScrollSync = async (page: Page, viewport: number, want: boolean) => {
    const now = (await gql(page, "{ qed { views { sync { scroll } } } }")).data.qed.views[viewport].sync.scroll
    if (now !== want) {
        await gql(page, `mutation { viewSyncToggleViewport(input: {viewport: ${viewport}, aspect: "scroll"}) { view { sync { scroll } } } }`)
    }
}

// the source-pixel origin of a viewport, derived from its live scroll and its published zoom
const sourceOrigin = async (region: Locator) => {
    const { left, top } = await region.evaluate(el => ({ left: el.scrollLeft, top: el.scrollTop }))
    const [zv, zh] = (await region.getAttribute("data-qed-zoom"))!.split(",").map(Number)
    return { col: left * 2 ** -zh, row: top * 2 ** -zv }
}


test.describe.serial("synced scrolling lines up across mismatched zoom", () => {
    test.afterAll(async ({ browser }) => {
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "networkidle" })
        // leave the store as the rest of the suite expects it: one viewport, unsynced, at zoom 0
        await collapseToOne(page)
        await setScrollSync(page, 0, false)
        await gql(page, "mutation { viewZoomSetLevel(input: {viewport: 0, horizontal: 0, vertical: 0}) { zooms { horizontal } } }")
        await page.close()
    })

    test("panning one viewport lands its peer on the same source pixel", async ({ page }) => {
        await page.goto("/", { waitUntil: "networkidle" })
        // start from a single viewport, then split it so there are exactly two
        await collapseToOne(page)
        await gql(page, "mutation { viewSplit(input: {viewport: 0}) { view { id } } }")

        // put the two viewports at different zoom, scroll-sync both, and give the peer an offset
        const offset = { x: 40, y: 20 }
        await gql(page, "mutation { viewZoomSetLevel(input: {viewport: 0, horizontal: 0, vertical: 0}) { zooms { horizontal } } }")
        await gql(page, "mutation { viewZoomSetLevel(input: {viewport: 1, horizontal: -2, vertical: -2}) { zooms { horizontal } } }")
        await setScrollSync(page, 0, true)
        await setScrollSync(page, 1, true)
        await gql(page, "mutation { viewSyncUpdateOffset(input: {viewport: 0, x: 0, y: 0}) { sync { offsets { x } } } }")
        await gql(page, `mutation { viewSyncUpdateOffset(input: {viewport: 1, x: ${offset.x}, y: ${offset.y}}) { sync { offsets { x } } } }`)

        // load the two-viewport state fresh, so the client picks up the zoom/sync/offsets
        await page.goto("/", { waitUntil: "networkidle" })
        const regions = page.locator('[data-qed-region="viewport"]')
        await expect(regions).toHaveCount(2)
        const [first, second] = [regions.nth(0), regions.nth(1)]

        // pan the first viewport to a modest spot (kept small so the peer does not clamp)
        await first.evaluate(el => { el.scrollLeft = 400; el.scrollTop = 300 })
        // the dispatcher scrolls the synced peer; wait for it to move
        await expect.poll(() => second.evaluate(el => el.scrollLeft)).toBeGreaterThan(0)

        // the peer must show the same source pixel as the panned viewport, shifted by the offset --
        // not the panned viewport's raw rendered offset (which the bug copied verbatim)
        const a = await sourceOrigin(first)
        const b = await sourceOrigin(second)
        expect(Math.abs((b.col - a.col) - offset.x)).toBeLessThan(8)
        expect(Math.abs((b.row - a.row) - offset.y)).toBeLessThan(8)
    })
})


/* end of file */
