// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// the tile loader fetches a tile once it comes within a quarter of a tile of the visible part of
// its viewport, and announces each fetch so the pacing of the controllers can wait for the screen
// to fill; these specs pin down the three things that depend on it: tiles far from the screen are
// never fetched, a slow pan never shows a blank tile, and every tile announced arrives

// the scroll container of viewport 0
const region = '[data-qed-region="viewport"][data-qed-viewport="0"]'

// open the raster at full resolution, near its middle, and let its tiles settle
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
    // and let the tiles settle
    await page.waitForLoadState("networkidle")
}

// count the tiles of viewport 0 that are on the screen, and the ones among them that show nothing
const census = (selector: string) => {
    // the scroll container and its extent on the screen
    const box = document.querySelector(selector)!
    const frame = box.getBoundingClientRect()
    // the tiles whose boxes overlap it
    const visible = [...box.querySelectorAll('img[data-pyre-widget="tile"]')].filter(img => {
        const r = img.getBoundingClientRect()
        return r.right > frame.left && r.left < frame.right && r.bottom > frame.top && r.top < frame.bottom
    }) as HTMLImageElement[]
    // and the ones that have no image to show
    const blank = visible.filter(img => !img.complete || img.naturalWidth === 0)
    // hand back the counts
    return { visible: visible.length, blank: blank.length }
}


test.describe.serial("tiles are fetched as they come within reach of the screen", () => {
    test.afterAll(async ({ browser }) => {
        // leave the shared server at the default zoom for anything that reuses it
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        await page.evaluate(() => window.qed.setZoom(0))
        await page.close()
    })

    test("only the tiles within a quarter of a tile of the screen are fetched", async ({ page }) => {
        await open(page)
        // collect the addresses of the tiles fetched from now on
        const fetched: string[] = []
        page.on("request", request => {
            // tiles are the requests for data
            if (request.url().includes("/data/")) {
                // keep their path
                fetched.push(new URL(request.url()).pathname)
            }
        })
        // jump by a screen and a half in both directions
        await page.evaluate(selector => {
            const box = document.querySelector(selector)!
            box.scrollTop += Math.floor(1.5 * box.clientHeight)
            box.scrollLeft += Math.floor(1.5 * box.clientWidth)
        }, region)
        // and let the tiles settle
        await page.waitForLoadState("networkidle")
        // the tiles within reach of the screen: the ones that overlap it, grown by the margin
        const reachable = await page.evaluate(selector => {
            // the scroll container and its extent, grown by a quarter of a tile on each side
            const box = document.querySelector(selector)!
            const frame = box.getBoundingClientRect()
            const margin = 128
            // the tiles that overlap it, by the path of their address
            return [...box.querySelectorAll('img[data-pyre-widget="tile"]')].filter(img => {
                const r = img.getBoundingClientRect()
                return r.right > frame.left - margin && r.left < frame.right + margin
                    && r.bottom > frame.top - margin && r.top < frame.bottom + margin
            }).map(img => new URL(img.getAttribute("data-src")!, location.href).pathname)
        }, region)
        // the jump fetched tiles
        expect(fetched.length).toBeGreaterThan(0)
        // and every one of them is within reach of the screen
        expect(fetched.filter(path => !reachable.includes(path))).toEqual([])
    })

    test("a slow pan never shows a blank tile", async ({ page }) => {
        await open(page)
        // pan slowly, looking at the screen after every step
        let blank = 0
        for (let step = 0; step < 60; ++step) {
            // move by a few pixels
            await page.evaluate(selector => {
                const box = document.querySelector(selector)!
                box.scrollTop += 30
                box.scrollLeft += 20
            }, region)
            // give the tiles a frame or two
            await page.waitForTimeout(40)
            // and count the ones on the screen that show nothing
            blank += (await page.evaluate(census, region)).blank
        }
        // the tiles scrolling into view were fetched before they got there
        expect(blank).toBe(0)
    })

    test("every tile announced as on its way arrives", async ({ page }) => {
        // keep track of the tiles announced and the ones that arrived, from before the client loads
        await page.addInitScript(() => {
            const w = window as any
            w.__pending = new Set()
            w.__announced = 0
            const isTile = (e: Event) => (e.target as Element)?.getAttribute?.("data-pyre-widget") === "tile"
            document.addEventListener("tilefetch", e => { if (isTile(e)) { w.__announced += 1; w.__pending.add(e.target) } }, true)
            const done = (e: Event) => { if (isTile(e)) w.__pending.delete(e.target) }
            document.addEventListener("load", done, true)
            document.addEventListener("error", done, true)
        })
        await open(page)
        // fling across the raster
        for (let step = 0; step < 20; ++step) {
            await page.evaluate(selector => {
                const box = document.querySelector(selector)!
                box.scrollTop += 250
                box.scrollLeft += 150
            }, region)
            await page.waitForTimeout(16)
        }
        // then zoom out, which replaces every tile
        await page.evaluate(() => window.qed.setZoom(-1))
        await page.waitForLoadState("networkidle")
        // tiles were announced, and none of them is still pending, so the controllers pace their
        // updates by the screen rather than waiting out their timeout
        const { announced, pending } = await page.evaluate(() => {
            const w = window as any
            return { announced: w.__announced, pending: w.__pending.size }
        })
        expect(announced).toBeGreaterThan(0)
        expect(pending).toBe(0)
    })
})


/* end of file */
