// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page, Locator } from "@playwright/test"


// scroll-synced viewports must center on the same source pixel even when they sit at different
// zoom levels and carry a relative offset. the pan dispatcher finds the source pixel at the center
// of the panned viewport, applies the relative offset (also source pixels), and centers each peer
// on the result, in its own rendered pixels; centers, unlike corners, mean the same place in
// viewports of any size and zoom. with two viewports at zoom 0 and -2, panning the first must
// center the second on the same source pixel, shifted by the offset. this splits a viewport
// (server state) and collapses it again afterward.

// drive the client's automation surface ({window.qed}) from inside the page; commands commit through
// the live Relay store, with no raw fetch
const ensureQED = (page: Page) => page.waitForFunction(() => Boolean(window.qed))

const setZoom = async (page: Page, viewport: number, horizontal: number, vertical: number) => {
    await ensureQED(page)
    await page.evaluate(([viewport, horizontal, vertical]) =>
        window.qed.setZoom({ horizontal, vertical }, viewport), [viewport, horizontal, vertical])
}

const viewCount = async (page: Page) => {
    await ensureQED(page)
    return (await page.evaluate(() => window.qed.viewports())).length
}

// drive the server back to a single viewport, so the rest of the suite sees the lone fixture view
const collapseToOne = async (page: Page) => {
    for (let n = await viewCount(page); n > 1; n--) {
        await page.evaluate(viewport => window.qed.collapse(viewport), n - 1)
    }
}

// force the scroll-sync flag of a viewport to {want} (the mutation only toggles)
const setScrollSync = async (page: Page, viewport: number, want: boolean) => {
    await ensureQED(page)
    const now = (await page.evaluate(() => window.qed.viewports()))[viewport]?.sync?.scroll
    if (now !== want) {
        await page.evaluate(viewport => window.qed.sync.toggle("scroll", viewport), viewport)
    }
}

// the source pixel at the center of a viewport, derived from its live scroll, its size, and its
// published zoom
const sourceCenter = async (region: Locator) => {
    const { col, row } = await region.evaluate(el => ({
        col: el.scrollLeft + el.clientWidth / 2,
        row: el.scrollTop + el.clientHeight / 2,
    }))
    const [zv, zh] = (await region.getAttribute("data-qed-zoom"))!.split(",").map(Number)
    return { col: col * 2 ** -zh, row: row * 2 ** -zv }
}


test.describe.serial("synced scrolling lines up across mismatched zoom", () => {
    test.afterAll(async ({ browser }) => {
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "load" })
        // leave the store as the rest of the suite expects it: one viewport, unsynced, at zoom 0
        await collapseToOne(page)
        await setScrollSync(page, 0, false)
        await setZoom(page, 0, 0, 0)
        await page.close()
    })

    test("panning one viewport lands its peer on the same source pixel", async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        // start from a single viewport, then split it so there are exactly two
        await collapseToOne(page)
        await page.evaluate(() => window.qed.split(0))

        // put the two viewports at different zoom, scroll-sync both, and give the peer an offset
        const offset = { x: 40, y: 20 }
        await setZoom(page, 0, 0, 0)
        await setZoom(page, 1, -2, -2)
        await setScrollSync(page, 0, true)
        await setScrollSync(page, 1, true)
        // the facade takes row-major {row,col}, so the offset's {x,y} maps to (col=x, row=y)
        await page.evaluate(() => window.qed.sync.updateOffset(0, 0, 0))
        await page.evaluate(([row, col]) => window.qed.sync.updateOffset(row, col, 1), [offset.y, offset.x])

        // load the two-viewport state fresh, so the client picks up the zoom/sync/offsets
        await page.goto("/", { waitUntil: "load" })
        const regions = page.locator('[data-qed-region="viewport"]')
        await expect(regions).toHaveCount(2)
        const [first, second] = [regions.nth(0), regions.nth(1)]

        // pan the first viewport well into the raster, so that the center of the peer lands where
        // the peer can scroll to: near the origin, the peer would have to scroll to a negative
        // offset to line up its center, and would stay clamped at zero
        await first.evaluate(el => { el.scrollLeft = 2000; el.scrollTop = 1500 })
        // the dispatcher scrolls the synced peer; wait for it to move
        await expect.poll(() => second.evaluate(el => el.scrollLeft)).toBeGreaterThan(0)

        // the peer must center on the same source pixel as the panned viewport, shifted by the
        // offset -- not on the panned viewport's raw rendered offset (which an old bug copied
        // verbatim)
        const a = await sourceCenter(first)
        const b = await sourceCenter(second)
        expect(Math.abs((b.col - a.col) - offset.x)).toBeLessThan(8)
        expect(Math.abs((b.row - a.row) - offset.y)).toBeLessThan(8)
    })
})


/* end of file */
