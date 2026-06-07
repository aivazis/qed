// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// anchor selection and the closed-path flag are part of the measure layer's state: selection lives in
// ARIA (an anchor's {aria-pressed}) and is mirrored in the model (`measure.selection`), and the
// closed flag lives in the model (`measure.closed`). this drives both through {window.qed} and reads
// them back through the markup and the model. it mutates the shared store, so it lives in the
// behavior project and restores the blank state on the way out.

const ensureQED = (page: Page) => page.waitForFunction(() => Boolean(window.qed))

const measureToggle = (page: Page) =>
    page.locator('[data-qed-control="viewport"][data-qed-action="measure"]').first()

// a clean three-anchor path with the layer shown
const arrange = async (page: Page) => {
    await page.goto("/controls", { waitUntil: "networkidle" })
    await ensureQED(page)
    await page.evaluate(async () => {
        await window.qed.measure.reset()
        await window.qed.measure.add(100, 100)
        await window.qed.measure.add(200, 150)
        await window.qed.measure.add(300, 120)
    })
    const toggle = measureToggle(page)
    await toggle.waitFor({ timeout: 10_000 })
    if ((await toggle.getAttribute("aria-pressed")) !== "true") await toggle.click()
}

// reset the path and hide the layer
const cleanup = async (page: Page) => {
    await page.goto("/controls", { waitUntil: "networkidle" })
    await ensureQED(page)
    await page.evaluate(() => window.qed.measure.reset())
    const toggle = measureToggle(page)
    await toggle.waitFor({ timeout: 10_000 })
    if ((await toggle.getAttribute("aria-pressed")) === "true") await toggle.click()
}


test.describe.serial("measure selection and the closed path", () => {
    test.afterAll(async ({ browser }) => {
        const page = await browser.newPage()
        await cleanup(page)
        await page.close()
    })

    test("toggling an anchor's selection flips its aria-pressed and the model", async ({ page }) => {
        await arrange(page)
        const anchor = page.locator(`[role="button"][data-qed-marker-index="1"]`)
        await expect(anchor).toHaveAttribute("aria-pressed", "false")

        // select it: the live store updates, so ARIA flips with no reload, and the model agrees
        await page.evaluate(() => window.qed.measure.toggleSelection(1))
        await expect(anchor).toHaveAttribute("aria-pressed", "true")
        expect(await page.evaluate(async () => (await window.qed.state())!.measure!.selection)).toContain(1)

        // toggling again clears it
        await page.evaluate(() => window.qed.measure.toggleSelection(1))
        await expect(anchor).toHaveAttribute("aria-pressed", "false")
        expect(await page.evaluate(async () => (await window.qed.state())!.measure!.selection)).not.toContain(1)
    })

    test("toggling the closed path flips the model's closed flag", async ({ page }) => {
        await arrange(page)
        const closed = () => page.evaluate(async () => (await window.qed.state())!.measure!.closed)
        const before = await closed()
        await page.evaluate(() => window.qed.measure.toggleClosedPath())
        expect(await closed()).toBe(!before)
        // restore the flag
        await page.evaluate(() => window.qed.measure.toggleClosedPath())
        expect(await closed()).toBe(before)
    })
})


/* end of file */
