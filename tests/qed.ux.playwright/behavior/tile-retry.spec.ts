// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// a tile the server could not produce for now comes back as a 503; the tile loader asks for it
// again a while later and the tile shows up, while a tile the server keeps refusing, e.g. one
// whose render took a crew member down, is asked about once more and then left blank. the
// server's answers are replaced here, so the specs do not depend on making a real renderer run
// out of time or crash

// the scroll container of viewport 0
const region = '[data-qed-region="viewport"][data-qed-viewport="0"]'

// a tile request ends with the origin and shape of the tile
const isTile = (url: URL) => /\/\d+x\d+\+\d+x\d+$/.test(url.pathname)

// answer the first request for each tile with {status}, and every later one too if {always};
// otherwise let the later ones through. hand back the kinds of the requests that came for
// tiles, in order
const interpose = async (page: Page, status: number, always: boolean = false) => {
    // the tiles that have been answered already
    const seen = new Set<string>()
    // the kinds of the requests for tiles
    const kinds: string[] = []
    // intercept the tile requests
    await page.route(isTile, async route => {
        // record what kind of request this is
        kinds.push(route.request().resourceType())
        // the address of the tile
        const url = route.request().url()
        // the first request for it, or every one when the answer never changes
        if (always || !seen.has(url)) {
            // is remembered
            seen.add(url)
            // and answered with {status}
            return route.fulfill({ status, body: "" })
        }
        // the rest go to the server
        return route.continue()
    })
    // hand back the record
    return kinds
}

// open the raster at full resolution, near its middle
const open = async (page: Page) => {
    // load the client
    await page.goto("/", { waitUntil: "load" })
    // wait for the automation surface
    await page.waitForFunction(() => Boolean(window.qed))
    // go to full resolution
    await page.evaluate(() => window.qed.setZoom(0))
    // and wait for the viewport to get there
    await page.waitForFunction(
        selector => document.querySelector(selector)?.getAttribute("data-qed-zoom") === "0,0",
        region,
    )
    // look at the middle of the raster
    const { dataset } = (await page.evaluate(() => window.qed.state()))!
    await page.evaluate(([row, col]) => window.qed.centerOn(row, col), [
        Math.floor(dataset!.shape[0] / 2),
        Math.floor(dataset!.shape[1] / 2),
    ])
}

// count the tiles of viewport 0 that are on the screen, and the ones among them that show nothing
const census = (selector: string) => {
    // the scroll container and its extent on the screen
    const box = document.querySelector(selector)!
    const frame = box.getBoundingClientRect()
    // the tiles whose boxes overlap it
    const visible = [...box.querySelectorAll('img[data-pyre-widget="tile"]')].filter(img => {
        const r = img.getBoundingClientRect()
        return r.right > frame.left && r.left < frame.right
            && r.bottom > frame.top && r.top < frame.bottom
    }) as HTMLImageElement[]
    // and the ones that have no image to show
    const blank = visible.filter(img => !img.complete || img.naturalWidth === 0)
    // hand back the counts
    return { visible: visible.length, blank: blank.length }
}


test.describe.serial("tiles the server could not produce for now are asked for again", () => {
    test.afterAll(async ({ browser }) => {
        // leave the shared server at the default zoom for anything that reuses it
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        await page.evaluate(() => window.qed.setZoom(0))
        await page.close()
    })

    test("a tile answered with a 503 shows up once the server has it", async ({ page }) => {
        // make the first answer to every tile a 503
        const kinds = await interpose(page, 503)
        // open the raster
        await open(page)
        // the tiles on the screen fill in once the loader asks again
        await expect.poll(async () => (await page.evaluate(census, region)).blank, {
            timeout: 20_000,
        }).toBe(0)
        // there were tiles to look at
        expect((await page.evaluate(census, region)).visible).toBeGreaterThan(0)
        // and the loader asked again in a way that sees the status of the answer
        expect(kinds).toContain("fetch")
    })

    test("a tile the server keeps refusing is asked about once", async ({ page }) => {
        // refuse every request for every tile
        const kinds = await interpose(page, 404, true)
        // open the raster
        await open(page)
        // give the loader time for its first look, and more than enough for a second one
        await page.waitForTimeout(9_000)
        // the tiles on the screen are blank
        const { visible, blank } = await page.evaluate(census, region)
        expect(visible).toBeGreaterThan(0)
        expect(blank).toBe(visible)
        // the loader looked once for every tile that failed to load, and never again
        const loads = kinds.filter(kind => kind === "image").length
        const looks = kinds.filter(kind => kind === "fetch").length
        expect(looks).toBe(loads)
    })
})


// end of file
