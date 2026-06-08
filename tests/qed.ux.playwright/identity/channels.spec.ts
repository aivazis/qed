// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the CHANNELS selector is the client's identity for choosing a visualization channel; it must be
// a radiogroup of radios, one per channel the dataset exposes, with ARIA -- not a {data-*} mirror
// -- carrying which one is selected. the {setup} project selects {amplitude} on the only dataset.
test.describe("the channel selector", () => {
    // it renders on the readers view, beside the active reader
    test.beforeEach(async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        await page.locator('[data-qed-control="channel"]').first().waitFor({ timeout: 10_000 })
    })

    test("is a radiogroup with one radio per channel", async ({ page }) => {
        // the group carries the client identity and the radiogroup role
        const group = page.locator('[data-qed-control="channel"]')
        await expect(group).toHaveAttribute("role", "radiogroup")
        // every option is a radio that names its channel through {data-qed-value}
        const values = await group.locator('[role="radio"]')
            .evaluateAll(els => els.map(e => e.getAttribute("data-qed-value")))
        // the complex fixture exposes exactly these five channels
        expect(new Set(values)).toEqual(new Set(["complex", "amplitude", "phase", "real", "imaginary"]))
    })

    test("marks exactly the selected channel with aria-checked", async ({ page }) => {
        const group = page.locator('[data-qed-control="channel"]')
        // exactly one radio is checked, and ARIA -- not a data attribute -- says so
        const checked = group.locator('[role="radio"][aria-checked="true"]')
        await expect(checked).toHaveCount(1)
        // and it is the channel {setup} selected
        await expect(checked).toHaveAttribute("data-qed-value", "amplitude")
        // the rest are explicitly unchecked, so assistive tech reads the group correctly
        await expect(group.locator('[role="radio"][aria-checked="false"]')).toHaveCount(4)
    })
})


/* end of file */
