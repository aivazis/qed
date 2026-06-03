// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Locator } from "@playwright/test"


// the measure and sync viewport glyphs are toggle buttons backed by server-side state
// (viewMeasureToggleLayer / the scroll sync flag), so operating them mutates the shared store.
// this lives in the behavior project -- serial, after the read-only gate -- and restores the state
// it touches. the payoff: a driver confirms the button-governs-panel relationship through ARIA and
// {data-qed-panel}, with no pixel arithmetic and no title scraping.

// click {button} and wait for its {aria-pressed} to settle on {value}
const clickUntilPressed = async (button: Locator, value: string) => {
    await button.click()
    await expect(button).toHaveAttribute("aria-pressed", value)
}

test.describe.serial("the viewport toggle actions govern their panels", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/controls", { waitUntil: "networkidle" })
        await page.locator('[data-qed-control="viewport"][data-qed-action="measure"]')
            .first().waitFor({ timeout: 10_000 })
    })

    test("toggling measure flips aria-pressed and reveals the measure panel", async ({ page }) => {
        const button = page.locator('[data-qed-control="viewport"][data-qed-action="measure"]').first()
        const panel = page.locator('[data-qed-panel="measure"]')

        // the starting state is a definite boolean, and the panel presence agrees with it
        const start = await button.getAttribute("aria-pressed")
        expect(["true", "false"]).toContain(start)
        if (start === "true") await expect(panel).toBeVisible()
        else await expect(panel).toHaveCount(0)

        // toggling flips the ARIA state and the panel follows -- no pixels, no title scraping
        const flipped = start === "true" ? "false" : "true"
        await clickUntilPressed(button, flipped)
        if (flipped === "true") await expect(panel).toBeVisible()
        else await expect(panel).toHaveCount(0)

        // restore the starting state so the shared store is left as we found it
        await clickUntilPressed(button, start!)
    })

    test("toggling sync flips aria-pressed beside an identifiable sync panel", async ({ page }) => {
        const button = page.locator('[data-qed-control="viewport"][data-qed-action="sync"]').first()
        // the sync panel renders whenever the controls view does, found by its stable identity
        await expect(page.locator('[data-qed-panel="sync"]')).toBeVisible()

        // its on/off truth is a definite boolean in ARIA, and a click flips it
        const start = await button.getAttribute("aria-pressed")
        expect(["true", "false"]).toContain(start)
        await clickUntilPressed(button, start === "true" ? "false" : "true")

        // restore the starting state so the shared store is left as we found it
        await clickUntilPressed(button, start!)
    })
})


/* end of file */
