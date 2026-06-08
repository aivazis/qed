// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the viewport action glyphs split into two kinds. {split} and {print} are momentary actions, so
// they carry identity and a label but no toggle state. {measure} and {sync} are toggle buttons:
// their on/off truth lives in ARIA ({aria-pressed}), never in a data attribute. this spec is part
// of the read-only gate, so it asserts only the static markup contract; the behavior project
// proves that operating a toggle flips its state and governs its panel. the sync panel always
// renders on the controls view and carries its own client identity ({data-qed-panel}).
test.describe("the viewport actions", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
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

    test("toggle actions carry their on/off state in aria-pressed", async ({ page }) => {
        for (const action of ["measure", "sync"]) {
            const button = page.locator(`[data-qed-control="viewport"][data-qed-action="${action}"]`).first()
            await expect(button).toHaveAttribute("role", "button")
            // state is a definite boolean in ARIA, so assistive tech and drivers read it directly
            await expect(button).toHaveAttribute("aria-pressed", /true|false/)
        }
    })

    test("the sync panel is identifiable by its client identity", async ({ page }) => {
        // the sync panel renders whenever the controls view does, found without scraping its title
        await expect(page.locator('[data-qed-panel="sync"]')).toBeVisible()
    })
})


/* end of file */
