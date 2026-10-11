// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// how the playground is looked at is server state: the projection of its diagram and the trays
// of its panel that are open. a change made in one window shows in every other one, and only the
// window that made it takes the keys back onto its canvas. this lives in the behavior project
// (serial, after the gate) and puts the view back when it is done

// set the view the way a fresh store has it: flat, unturned, from above, only the picked tray open
const reset = async (page: Page) => {
    // the projection
    await page.request.post("graphql", {
        data: {
            query: "mutation ($input: PlaygroundProjectionSetInput!) { playgroundProjectionSet(input: $input) { view { id } } }",
            variables: { input: { kind: "flat", azimuth: 0, below: false } },
        },
    })
    // ask which trays are open
    const response = await page.request.post("graphql", {
        data: { query: "{ qed { playgroundView { trays } } }" },
    })
    // unpack
    const { data } = await response.json()
    // close every one of them but the picked one
    for (const tray of data.qed.playgroundView.trays.filter((name: string) => name !== "picked")) {
        // one at a time
        await page.request.post("graphql", {
            data: {
                query: "mutation ($input: PlaygroundTraySetInput!) { playgroundTraySet(input: $input) { view { id } } }",
                variables: { input: { tray, expanded: false } },
            },
        })
    }
}

// the header of the tray of a palette group, by the family of its protocol
const header = (page: Page, family: string) =>
    page.locator(`[data-qed-palette="${family}"] [data-qed-control="tray"]`)


test.describe.serial("every window looks at the playground the same way", () => {
    test.afterAll(async ({ browser }) => {
        // leave the store as the rest of the suite expects it
        const page = await browser.newPage()
        await page.goto("/about", { waitUntil: "load" })
        await reset(page)
        await page.close()
    })

    test("a projection and a tray picked in one window show in another", async ({ browser }) => {
        // two windows on the playground
        const one = await browser.newPage()
        const two = await browser.newPage()
        await one.goto("/about", { waitUntil: "load" })
        await two.goto("/about", { waitUntil: "load" })
        // start from a known view
        await reset(one)

        // both draw it flat
        for (const page of [one, two]) {
            await expect(page.locator('[data-qed-projection="flat"]')).toBeVisible({ timeout: 10_000 })
            await expect(page.locator("[data-qed-turn]")).toHaveCount(0)
        }

        // the first one picks the isometric view
        await one.locator('[data-qed-projection="iso"]').click()
        // both show the controls of an isometric view
        for (const page of [one, two]) {
            await expect(page.locator('[data-qed-turn="left"]')).toBeVisible({ timeout: 10_000 })
        }
        // the window that clicked has the keys on its canvas; the other one does not
        await expect.poll(() => one.evaluate(() => document.activeElement?.tagName)).toBe("SECTION")
        expect(await two.evaluate(() => document.activeElement?.tagName)).not.toBe("SECTION")

        // the second one looks from below
        await two.locator("[data-qed-below]").click()
        // and the first one follows
        await expect(one.locator("[data-qed-below]")).toHaveAttribute("data-qed-below", "true")

        // the readers tray starts closed in both
        for (const page of [one, two]) {
            await expect(header(page, "pyre.viz.readers")).toHaveAttribute("aria-expanded", "false")
        }
        // the first one opens it
        await header(one, "pyre.viz.readers").click()
        // and it is open in both, with the reader protocol on offer
        for (const page of [one, two]) {
            await expect(header(page, "pyre.viz.readers")).toHaveAttribute("aria-expanded", "true")
            await expect(page.locator('[data-qed-catalog="pyre.viz.readers"]')).toBeVisible()
        }
        // the second one closes it, and the first one follows
        await header(two, "pyre.viz.readers").click()
        await expect(header(one, "pyre.viz.readers")).toHaveAttribute("aria-expanded", "false")

        // all done
        await one.close()
        await two.close()
    })
})


// end of file
