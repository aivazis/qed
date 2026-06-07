// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// the reset and toggle-all commands, read back through the model: {zoomReset} returns a viewport to
// the default zoom, {sync.toggleAll} flips an aspect across every viewport at once, and {sync.reset}
// clears one viewport's flags. these mutate the shared store, so they run in the behavior project and
// restore the lone unsynced zoom-0 view on the way out.

const ensureQED = (page: Page) => page.waitForFunction(() => Boolean(window.qed))

// drive the server back to a single, unsynced, zoom-0 viewport
const restore = async (page: Page) => {
    await page.goto("/", { waitUntil: "networkidle" })
    await ensureQED(page)
    await page.evaluate(async () => {
        for (let n = (await window.qed.viewports()).length; n > 1; n--) await window.qed.collapse(n - 1)
        await window.qed.sync.reset(0)
        await window.qed.setZoom(0, 0)
    })
}


test.describe.serial("the reset and toggle-all commands", () => {
    test.afterAll(async ({ browser }) => {
        const page = await browser.newPage()
        await restore(page)
        await page.close()
    })

    test("zoomReset returns the viewport to the default zoom", async ({ page }) => {
        await page.goto("/", { waitUntil: "networkidle" })
        await ensureQED(page)
        const horizontal = () => page.evaluate(async () => (await window.qed.state())!.zoom!.horizontal)

        await page.evaluate(() => window.qed.setZoom(-2))
        expect(await horizontal()).toBe(-2)
        await page.evaluate(() => window.qed.zoomReset())
        expect(await horizontal()).toBe(0)
    })

    test("sync toggleAll flips the aspect on every viewport; reset clears one", async ({ page }) => {
        await page.goto("/", { waitUntil: "networkidle" })
        await ensureQED(page)
        const scroll = () => page.evaluate(async () => (await window.qed.viewports()).map(v => v.sync!.scroll))

        // two viewports, both scroll-sync off
        await page.evaluate(async () => {
            for (let n = (await window.qed.viewports()).length; n > 1; n--) await window.qed.collapse(n - 1)
            await window.qed.split(0)
            for (const vp of [0, 1]) {
                if ((await window.qed.viewports())[vp].sync!.scroll) await window.qed.sync.toggle("scroll", vp)
            }
        })
        expect(await scroll()).toEqual([false, false])

        // toggle the whole column on at once
        await page.evaluate(() => window.qed.sync.toggleAll("scroll", 0))
        expect(await scroll()).toEqual([true, true])

        // reset one viewport's flags; the other is untouched
        await page.evaluate(() => window.qed.sync.reset(1))
        const after = await scroll()
        expect(after[1]).toBe(false)
        expect(after[0]).toBe(true)
    })
})


/* end of file */
