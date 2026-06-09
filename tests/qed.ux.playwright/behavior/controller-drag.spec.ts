// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Locator, Page } from "@playwright/test"


// issue #78: a controller drag fires updates far faster than the server round trip. the update hooks
// must not drop the final resting value -- each uses a trailing-edge throttle (one mutation in
// flight, hold only the latest, flush it when the in-flight one settles). we force the in-flight
// overlap with artificial latency on the driver's mutations, perform a real multi-step drag, and
// assert that a SECOND client -- reflecting server state over live-sync -- reaches the final value.
// asserting the observer (the server's view), not the driver's local thumb, is what proves the value
// actually reached the server. the two cases cover the two distinct mechanisms: the Range controller
// (two-thumb, local state, useUpdateRangeController -- the same throttle useUpdateValueController has)
// and the zoom Slider (fragment-driven, useSetLevel).

// slow every mutation on {page} so a quick drag overflows the single in-flight slot
const throttle = (page: Page) =>
    page.route("**/graphql", async route => {
        await new Promise(resolve => setTimeout(resolve, 400))
        return route.continue()
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


test.describe.serial("a controller drag's final value is not dropped", () => {
    test("the range controller's final value reaches the server", async ({ page, context }) => {
        const driver = page
        const observer = await context.newPage()
        for (const client of [driver, observer]) {
            await client.goto("/controls", { waitUntil: "load" })
            await client.waitForFunction(() => Boolean(window.qed))
        }

        const range = (await driver.evaluate(() => window.qed.controllers()))
            .find(controller => controller.kind === "range")
        test.skip(!range, "the active channel exposes no range controller")
        const { slot, min, max } = range!
        const tol = (max - min) * 0.02

        const driverHigh = driver.getByRole("slider", { name: `${slot} high` })
        const observerHigh = observer.getByRole("slider", { name: `${slot} high` })
        await driverHigh.waitFor()
        await observerHigh.waitFor()

        // drag the high thumb left under latency, then read the value the driver settled on locally
        await throttle(driver)
        await dragBy(driver, driverHigh, -60)
        const finalValue = await valueOf(driverHigh)

        // the observer reflects the server; it must catch up to the final value, not a dropped one
        await expect
            .poll(async () => Math.abs((await valueOf(observerHigh)) - finalValue), { timeout: 15_000 })
            .toBeLessThan(tol)

        // restore
        await driver.unroute("**/graphql")
        await driver.evaluate(controller => window.qed.range.reset(controller), slot)
        await observer.close()
    })

    test("the zoom level's final value reaches the server", async ({ page, context }) => {
        const driver = page
        const observer = await context.newPage()
        for (const client of [driver, observer]) {
            await client.goto("/controls", { waitUntil: "load" })
            await client.waitForFunction(() => Boolean(window.qed))
        }

        const driverZoom = driver.getByRole("slider", { name: "zoom horizontal" })
        const observerZoom = observer.getByRole("slider", { name: "zoom horizontal" })
        await driverZoom.waitFor()
        await observerZoom.waitFor()
        // the lowest level the slider allows; dragging far past it clamps here -- a known endpoint
        const min = Number(await driverZoom.getAttribute("aria-valuemin"))

        // drag the horizontal thumb far left under latency, so it lands on the min level
        await throttle(driver)
        await dragBy(driver, driverZoom, -400)

        // the observer must reach the min level; a dropped final value would strand it short of it
        await expect
            .poll(async () => valueOf(observerZoom), { timeout: 15_000 })
            .toBe(min)

        // restore
        await driver.unroute("**/graphql")
        await driver.evaluate(() => window.qed.zoomReset())
        await observer.close()
    })
})


/* end of file */
