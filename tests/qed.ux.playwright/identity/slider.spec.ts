// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// a slider's value is conveyed to assistive tech by its thumb (role=slider, aria-valuenow). the
// axis, ticks, and numeric tick labels are a visual scale that duplicates the thumb -- they stay
// clickable for mouse users but are decorative for assistive tech, so they live in an aria-hidden
// group and the thumb stays in the accessible tree. the zoom slider renders on the controls view.
test.describe("the slider scale", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/controls", { waitUntil: "networkidle" })
        await page.locator('[data-pyre-widget="slider"][data-pyre-widget-part="thumb"]')
            .first().waitFor({ timeout: 10_000 })
    })

    test("keeps the thumb accessible and hides the decorative scale", async ({ page }) => {
        // the thumb is the accessible control: it is not buried in a decorative subtree
        const thumb = page.locator('[data-pyre-widget="slider"][data-pyre-widget-part="thumb"]').first()
        const thumbExposed = await thumb.evaluate(el => el.closest('[aria-hidden="true"]') === null)
        expect(thumbExposed).toBe(true)

        // the numeric tick labels are present but live inside an aria-hidden (decorative) group
        const hiddenTicks = page.locator('[data-pyre-widget="slider"] [aria-hidden="true"] text')
        expect(await hiddenTicks.count()).toBeGreaterThan(0)
    })

    test("names the zoom minimap and gives it an identity", async ({ page }) => {
        const minimap = page.locator('[data-qed-control="minimap"]')
        await expect(minimap.first()).toHaveAttribute("aria-label", /minimap/)
    })
})


/* end of file */
