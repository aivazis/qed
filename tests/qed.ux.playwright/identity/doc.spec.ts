// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the documentation table of contents lists topics that select a guide page when clicked. each
// topic carries a stable identity ({data-qed-topic}); the selectable ones are buttons, and the
// page currently shown is marked with {aria-current} rather than a {data-*} state mirror.
test.describe("the doc table of contents", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/doc", { waitUntil: "load" })
        await page.locator('[data-qed-control="doc-topic"]').first().waitFor({ timeout: 10_000 })
    })

    test("lists topics as identified controls with the current one marked", async ({ page }) => {
        const topics = page.locator('[data-qed-control="doc-topic"]')
        const ids = await topics.evaluateAll(els => els.map(e => e.getAttribute("data-qed-topic")))
        // the guide ships several topics, each with a non-empty identity
        expect(ids.length).toBeGreaterThanOrEqual(5)
        for (const id of ids) expect(id).toBeTruthy()

        // exactly one topic is the current page, marked in ARIA
        await expect(page.locator('[data-qed-control="doc-topic"][aria-current="true"]')).toHaveCount(1)
        // every other topic is a button that selects it
        const buttons = await page.locator('[data-qed-control="doc-topic"][role="button"]').count()
        expect(buttons).toBe(ids.length - 1)
    })
})


/* end of file */
