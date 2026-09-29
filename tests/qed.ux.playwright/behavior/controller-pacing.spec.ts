// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Locator, Page } from "@playwright/test"


// a change to a controller invalidates every tile on the screen, so the controllers pace their
// updates by the screen: while one update is in flight they hold only the latest, and send it once
// the viewport shows the tiles of the one before, or a second has passed. with the tiles slowed
// down, a quick drag therefore sends a few updates rather than one per step, and still delivers
// its final value

// slow every tile on {page} down by {delay} milliseconds
const slowTiles = (page: Page, delay: number) =>
    page.route("**/data/**", async route => {
        await new Promise(resolve => setTimeout(resolve, delay))
        // a tile the client gave up on arrives here already handled, which is not a failure
        try {
            // hand the request on to the server
            await route.continue()
        } catch {
            // the request is gone, so there is nothing left to forward
        }
    })

// drag {thumb} by {dx} pixels along the horizontal axis, in many small steps
const dragBy = async (page: Page, thumb: Locator, dx: number) => {
    const box = await thumb.boundingBox()
    const y = box!.y + box!.height / 2
    const x0 = box!.x + box!.width / 2
    await page.mouse.move(x0, y)
    await page.mouse.down()
    for (let i = 1; i <= 12; ++i) await page.mouse.move(x0 + dx * (i / 12), y)
    await page.mouse.up()
}

// the current value a thumb reports
const valueOf = (thumb: Locator) => thumb.getAttribute("aria-valuenow").then(Number)


test("a quick drag of a range controller sends a few updates, and its final value", async ({ page, context }) => {
    // a second client reflects the state of the server over live sync, which is what proves the
    // final value reached it
    const observer = await context.newPage()
    for (const client of [page, observer]) {
        await client.goto("/controls", { waitUntil: "load" })
        await client.waitForFunction(() => Boolean(window.qed))
    }

    const range = (await page.evaluate(() => window.qed.controllers()))
        .find(controller => controller.kind === "range")
    test.skip(!range, "the active channel exposes no range controller")
    const { slot, min, max } = range!
    const tol = (max - min) * 0.02

    const high = page.getByRole("slider", { name: `${slot} high` })
    const observerHigh = observer.getByRole("slider", { name: `${slot} high` })
    await high.waitFor()
    await observerHigh.waitFor()

    // count the updates of range controllers the page sends
    let updates = 0
    page.on("request", request => {
        // the updates are graphql mutations
        if (request.url().endsWith("/graphql") && (request.postData() ?? "").includes("viewRangeUpdate")) {
            // count them
            updates += 1
        }
    })

    // slow the tiles down, so each screen takes a while to arrive
    await slowTiles(page, 300)
    // drag the high thumb quickly, in twelve steps
    await dragBy(page, high, -60)
    const finalValue = await valueOf(high)

    // the final value reaches the server
    await expect
        .poll(async () => Math.abs((await valueOf(observerHigh)) - finalValue), { timeout: 15_000 })
        .toBeLessThan(tol)
    // in a few updates, not one per step
    expect(updates).toBeGreaterThan(0)
    expect(updates).toBeLessThanOrEqual(3)

    // restore
    await page.unroute("**/data/**")
    await page.evaluate(controller => window.qed.range.reset(controller), slot)
    await observer.close()
})


// end of file
