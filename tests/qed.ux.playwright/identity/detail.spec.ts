// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the MORE/LESS detail toggle adjusts how much metadata a panel shows. each direction must be a
// button with a stable, display-independent identity ({data-qed-detail} = the lowercase intent,
// not the uppercased label) so a driver targets it without scraping text; availability lives in
// ARIA ({aria-disabled}), never in a data attribute.
test.describe("the detail toggle", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/", { waitUntil: "networkidle" })
        await page.locator('[data-qed-control="detail"]').first().waitFor({ timeout: 10_000 })
    })

    for (const direction of ["more", "less"]) {
        test(`exposes ${direction} as a labeled button with stable identity`, async ({ page }) => {
            const button = page.locator(`[data-qed-control="detail"][data-qed-detail="${direction}"]`).first()
            await expect(button).toHaveAttribute("role", "button")
            await expect(button).toHaveAttribute("aria-label", new RegExp(`${direction} detail`))
            // availability is exposed (true or false), so assistive tech reads the state
            await expect(button).toHaveAttribute("aria-disabled", /true|false/)
        })
    }
})


/* end of file */
