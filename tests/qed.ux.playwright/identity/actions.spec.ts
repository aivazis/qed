// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the viewport action glyphs split into two kinds. {split} and {print} are momentary actions, so
// they carry identity and a label but no toggle state. {measure} and {sync} are toggle buttons:
// their on/off truth lives in ARIA ({aria-pressed}), never in a data attribute, and each governs a
// panel on the controls view. those panels carry a stable, display-independent identity
// ({data-qed-panel}) so a driver confirms the button-governs-panel relationship without scraping
// the panel title or doing pixel arithmetic. all of this co-mounts on {/controls}, where the
// viewport tab and the controls panels render together.
test.describe("the viewport actions", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/controls", { waitUntil: "networkidle" })
        await page.locator('[data-qed-control="viewport"][data-qed-action="measure"]')
            .first().waitFor({ timeout: 10_000 })
    })

    test("momentary actions are labeled buttons with no toggle state", async ({ page }) => {
        for (const action of ["split", "print"]) {
            const button = page.locator(`[data-qed-control="viewport"][data-qed-action="${action}"]`).first()
            await expect(button).toHaveAttribute("aria-label", /.+/)
            // a momentary action is not a toggle, so it must not claim a pressed state
            await expect(button).not.toHaveAttribute("aria-pressed", /.*/)
        }
    })

    test("the measure action is a toggle button that governs the measure panel", async ({ page }) => {
        const button = page.locator('[data-qed-control="viewport"][data-qed-action="measure"]').first()
        await expect(button).toHaveAttribute("role", "button")
        const panel = page.locator('[data-qed-panel="measure"]')

        // the starting state is a definite boolean in ARIA, and the panel presence agrees with it
        const start = await button.getAttribute("aria-pressed")
        expect(["true", "false"]).toContain(start)
        if (start === "true") await expect(panel).toBeVisible()
        else await expect(panel).toHaveCount(0)

        // toggling flips the ARIA state and the panel follows -- no pixels, no title scraping
        await button.click()
        const flipped = start === "true" ? "false" : "true"
        await expect(button).toHaveAttribute("aria-pressed", flipped)
        if (flipped === "true") await expect(panel).toBeVisible()
        else await expect(panel).toHaveCount(0)

        // restore the starting state so later specs see a clean slate
        await button.click()
        await expect(button).toHaveAttribute("aria-pressed", start)
    })

    test("the sync action is a toggle button beside an identifiable sync panel", async ({ page }) => {
        const button = page.locator('[data-qed-control="viewport"][data-qed-action="sync"]').first()
        await expect(button).toHaveAttribute("role", "button")
        // the sync panel renders whenever the controls view does, found by its stable identity
        await expect(page.locator('[data-qed-panel="sync"]')).toBeVisible()

        // its on/off truth is a definite boolean in ARIA, and a click flips it
        const start = await button.getAttribute("aria-pressed")
        expect(["true", "false"]).toContain(start)
        await button.click()
        await expect(button).toHaveAttribute("aria-pressed", start === "true" ? "false" : "true")

        // restore the starting state so later specs see a clean slate
        await button.click()
        await expect(button).toHaveAttribute("aria-pressed", start)
    })
})


/* end of file */
