// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the sync controls on the controls view are two interactive layers: a per-viewport switch for
// each aspect (channel/zoom/scroll/path), and a column header that toggles that aspect across all
// viewports. each carries the {sync} identity and its aspect; switch state lives in ARIA.
test.describe("the sync controls", () => {
    const aspects = ["channel", "zoom", "scroll", "path"]

    test.beforeEach(async ({ page }) => {
        await page.goto("/controls", { waitUntil: "networkidle" })
        await page.locator('[data-qed-control="sync"]').first().waitFor({ timeout: 10_000 })
    })

    test("each aspect has a toggle-all-viewports button in the header", async ({ page }) => {
        for (const aspect of aspects) {
            const header = page.locator(
                `[data-qed-control="sync"][data-qed-scope="all"][data-qed-aspect="${aspect}"]`
            )
            await expect(header).toHaveAttribute("role", "button")
            await expect(header).toHaveAttribute("aria-label", new RegExp(`sync ${aspect}`))
        }
    })

    test("each per-viewport cell is a switch with its state in ARIA", async ({ page }) => {
        const switches = page.locator('[data-qed-control="sync"][data-qed-viewport]')
        await expect(switches.first()).toBeVisible()
        // collect each switch's role, checked state, and aspect
        const cells = await switches.evaluateAll(els => els.map(e => ({
            role: e.getAttribute("role"),
            checked: e.getAttribute("aria-checked"),
            aspect: e.getAttribute("data-qed-aspect"),
        })))
        // the single fixture viewport contributes one switch per aspect
        expect(cells.length).toBeGreaterThanOrEqual(aspects.length)
        for (const cell of cells) {
            expect(cell.role).toBe("switch")
            expect(["true", "false"]).toContain(cell.checked)
            expect(aspects).toContain(cell.aspect)
        }
    })
})


/* end of file */
