// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page, Locator } from "@playwright/test"


// the viewport scroll position is now server state: a viewport carries a look-at center -- the source
// pixel under the middle of its window, row-major -- and any move pushes it through the {viewLookAt}
// mutation, so it reflects on every connected client over the SSE event stream (like zoom, channel,
// or the controllers). each client converts that resolution-independent center to its own scroll via
// its own geometry, so two clients of the same size land on the same source pixel. we drive two
// independent pages on the one shared server: the {driver} moves viewport 0, the {observer} only
// watches its own DOM scroll -- never {window.qed.state()}, which would re-fetch and pass even if the
// push never arrived. one test exercises the deterministic facade path ({window.qed.lookAt}); the
// other exercises the real path -- a raw DOM scroll the viewport handler turns into the mutation.


// drive the client's automation surface from inside the page
const ensureQED = (page: Page) => page.waitForFunction(() => Boolean(window.qed))

// the source pixel under the center of {region}, from its live scroll, size, and published zoom;
// the same mapping the viewport handler and {window.qed.centerOn} use
const sourceCenter = async (region: Locator) => {
    const { left, top, w, h } = await region.evaluate(el => ({
        left: el.scrollLeft, top: el.scrollTop, w: el.clientWidth, h: el.clientHeight,
    }))
    const [zv, zh] = (await region.getAttribute("data-qed-zoom"))!.split(",").map(Number)
    return { col: (left + w / 2) * 2 ** -zh, row: (top + h / 2) * 2 ** -zv }
}

// bring a client up on the viz page and wait for its rendered viewport region
const open = async (client: Page) => {
    await client.goto("/controls", { waitUntil: "load" })
    await ensureQED(client)
    await client.locator('[data-qed-region="viewport"]').first().waitFor()
}


test.describe.serial("viewport scroll syncs across clients", () => {
    test.afterAll(async ({ browser }) => {
        // leave viewport 0 looking at the origin, as the rest of the suite expects
        const page = await browser.newPage()
        await page.goto("/controls", { waitUntil: "load" })
        await ensureQED(page)
        await page.evaluate(() => window.qed.lookAt(0, 0, 0))
        await page.close()
    })

    test("a look-at set on one client recenters another", async ({ page, context }) => {
        // the client that makes the change
        const driver = page
        // a second, independent client on the same server
        const observer = await context.newPage()
        // bring both up
        await open(driver)
        await open(observer)

        // the observer's region; its scroll mirrors the store's look-at and moves when it updates
        const region = observer.locator('[data-qed-region="viewport"]').first()
        // the raster center is always a reachable look-at, and (for a zoomable raster) well away from
        // the initial top-left view, so the move is real rather than a no-op against a clamped edge
        const [rows, cols] = (await region.getAttribute("data-qed-shape"))!.split(",").map(Number)
        const target = { row: Math.round(rows / 2), col: Math.round(cols / 2) }

        // mark the observer so we can later prove it never reloaded
        await observer.evaluate(() => {
            ;(window as typeof window & { synced?: boolean }).synced = true
        })

        // the driver aims viewport 0 through the server; nothing happens on the observer's side
        await driver.evaluate(t => window.qed.lookAt(t.row, t.col, 0), target)

        // the observer's own scroll converges on that source pixel, pushed over the stream
        await expect.poll(async () => {
            const { row, col } = await sourceCenter(region)
            return Math.max(Math.abs(row - target.row), Math.abs(col - target.col))
        }, { timeout: 10_000 }).toBeLessThan(2)
        // and it got there in place -- it never navigated or reloaded
        expect(
            await observer.evaluate(() => (window as typeof window & { synced?: boolean }).synced),
        ).toBe(true)

        // tidy up the extra client
        await observer.close()
    })

    test("a raw scroll on one client recenters another", async ({ page, context }) => {
        // the client that makes the change
        const driver = page
        // a second, independent client on the same server
        const observer = await context.newPage()
        // bring both up
        await open(driver)
        await open(observer)

        // both regions; the driver scrolls its own, the observer must follow
        const driverRegion = driver.locator('[data-qed-region="viewport"]').first()
        const observerRegion = observer.locator('[data-qed-region="viewport"]').first()

        // where the observer is looking before anything moves
        const before = await sourceCenter(observerRegion)

        // a plain user-style scroll on the driver: the viewport handler converts it to a look-at and
        // pushes it. kept modest so neither client clamps at an edge
        await driverRegion.evaluate(el => { el.scrollLeft = 500; el.scrollTop = 400 })
        // the source pixel the driver now looks at, after its own scroll
        let aim = { row: 0, col: 0 }
        await expect.poll(async () => {
            aim = await sourceCenter(driverRegion)
            return Math.max(Math.abs(aim.row - before.row), Math.abs(aim.col - before.col))
        }).toBeGreaterThan(2)

        // two clients of the same size resolve the same look-at center to the same scroll, so the
        // observer must converge on exactly the source pixel the driver scrolled to
        await expect.poll(async () => {
            const here = await sourceCenter(observerRegion)
            return Math.max(Math.abs(here.row - aim.row), Math.abs(here.col - aim.col))
        }, { timeout: 10_000 }).toBeLessThan(2)
        // and the observer genuinely moved from where it started
        const after = await sourceCenter(observerRegion)
        expect(Math.max(Math.abs(after.row - before.row), Math.abs(after.col - before.col)))
            .toBeGreaterThan(2)

        // tidy up the extra client
        await observer.close()
    })
})


/* end of file */
