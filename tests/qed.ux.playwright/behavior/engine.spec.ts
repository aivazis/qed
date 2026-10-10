// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// the reader pane picks the engine that draws the tiles of the active view: the pipeline of the
// channel's recipe, or the fused iterators. picking one gives the view a new session, so every
// tile is fetched again and drawn by the engine just picked. the engine is server state, so this
// lives in the behavior project (serial, after the gate) and puts the pipeline back when it is done

// ask the server which engine draws the tiles of the first viewport
const engine = async (page: Page) => {
    // query the views
    const response = await page.request.post("graphql", {
        data: { query: "{ qed { views { engine flowable } } }" },
    })
    // unpack
    const { data } = await response.json()
    // and hand back the first one
    return data.qed.views[0]
}

// pick an engine for the first viewport, the way the control does
const pick = (page: Page, value: string) =>
    page.request.post("graphql", {
        data: {
            query: "mutation ($input: ViewEngineSetInput!) { viewEngineSet(input: $input) { views { id } } }",
            variables: { input: { viewport: 0, engine: value } },
        },
    })


test.describe.serial("the engine control picks what draws the tiles", () => {
    test.afterAll(async ({ browser }) => {
        // leave the store as the rest of the suite expects it: the pipeline draws the tiles
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "load" })
        await pick(page, "flow")
        await page.close()
    })

    test("flipping the engine redraws the tiles with the other one", async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        // the control, in the reader pane
        const group = page.getByRole("radiogroup", { name: "engine" })
        await expect(group).toBeVisible({ timeout: 10_000 })
        const flow = group.getByRole("radio", { name: "flow" })
        const iter = group.getByRole("radio", { name: "iter" })

        // the complex fixture has a pipeline that can draw it, and it is the default
        await expect(flow).toHaveAttribute("aria-checked", "true")
        await expect(flow).toHaveAttribute("aria-disabled", "false")
        expect(await engine(page)).toEqual({ engine: "flow", flowable: true })

        // the address of a tile carries the session it was asked for under
        const tile = page.locator('[data-qed-region="viewport"] img[data-pyre-widget="tile"]').first()
        await tile.waitFor({ timeout: 10_000 })
        const before = await tile.getAttribute("data-src")

        // pick the iterators
        await iter.click()
        // the control follows
        await expect(iter).toHaveAttribute("aria-checked", "true")
        await expect(flow).toHaveAttribute("aria-checked", "false")
        // so does the server
        await expect.poll(async () => (await engine(page)).engine).toBe("iterators")
        // and the tile is asked for again, under the new session
        await expect.poll(() => tile.getAttribute("data-src")).not.toBe(before)

        // and back to the pipeline
        const again = await tile.getAttribute("data-src")
        await flow.click()
        await expect(flow).toHaveAttribute("aria-checked", "true")
        await expect.poll(async () => (await engine(page)).engine).toBe("flow")
        await expect.poll(() => tile.getAttribute("data-src")).not.toBe(again)
    })
})


/* end of file */
