// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// this suite runs against the SOLO server: a single NISAR source, which the boot path
// auto-selects into the blank viewport BEFORE the reader makes first contact. that is the
// regression surface this spec guards: first contact auto-picks the single-valued selector
// axes on the reader, and the view built at boot must ADOPT those picks -- the client
// deliberately makes single-valued axes inert, so a view that misses them can never
// complete its selection interactively. it operates the polarization control, so it is
// serial and restores what it touches

test.describe.serial("boot-time selection adoption", () => {
    test("the single-valued axis arrives pre-selected, with no interaction", async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        // wait for the reader panel to mount
        await page.locator('[data-qed-reader="gslc"]').waitFor({ timeout: 10_000 })

        // the fixture realizes exactly one band; first contact auto-picked it, and the
        // view adopted the pick -- this radio is checked without a single click
        const band = page.locator('[data-qed-reader="gslc"] [data-qed-axis="band"] [data-qed-value="L"]')
        await expect(band).toHaveAttribute("aria-checked", "true")

        // the frequency and polarization axes are multi-valued, so they wait for the user
        for (const axis of ["frequency", "polarization"]) {
            const group = page.locator(`[data-qed-reader="gslc"] [data-qed-axis="${axis}"]`)
            await expect(group.locator('[aria-checked="true"]')).toHaveCount(0)
        }
    })

    test("clicking the remaining axes completes the selection and surfaces the channels", async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        await page.locator('[data-qed-reader="gslc"]').waitFor({ timeout: 10_000 })

        // the channels row is not on display while the selection is incomplete
        const channels = page.locator('[data-qed-reader="gslc"] [data-qed-control="channel"]')
        await expect(channels).toHaveCount(0)

        // pick the frequency and the polarization through the real radios, the way a user does
        const picks = [["frequency", "A"], ["polarization", "HH"]]
        for (const [axis, value] of picks) {
            const radio = page.locator(
                `[data-qed-reader="gslc"] [data-qed-axis="${axis}"] [data-qed-value="${value}"]`)
            await radio.click()
            await expect(radio).toHaveAttribute("aria-checked", "true")
        }

        // the selection is now fully formed, so the channels radiogroup appears
        await expect(channels).toHaveCount(1)

        // restore the blank selection so a rerun starts clean: toggling each pick clears it
        for (const [axis, value] of picks) {
            const radio = page.locator(
                `[data-qed-reader="gslc"] [data-qed-axis="${axis}"] [data-qed-value="${value}"]`)
            await radio.click()
            await expect(radio).toHaveAttribute("aria-checked", "false")
        }
        await expect(channels).toHaveCount(0)
    })
})


/* end of file */
