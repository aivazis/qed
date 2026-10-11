// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// how the playground is looked at is server state: the projection of its diagram, the trays of
// its panel that are open, and where the cameras look. a change made in one window shows in
// every other one, and only the window that made it takes the keys back onto its canvas. this lives in the behavior project
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

// the playground diagram: its id and its factories
const playground = async (page: Page) => {
    // ask
    const response = await page.request.post("graphql", {
        data: { query: "{ qed { playground { id factories { id } } } }" },
    })
    // unpack
    const { data } = await response.json()
    // and hand it back
    return data.qed.playground
}

// where the grip of the first factory sits on the screen
const grip = async (page: Page) => {
    // find it
    const box = await page.locator("[data-qed-kind=factory] [data-qed-grip]").first().boundingBox()
    // and its middle
    return { x: box!.x + box!.width / 2, y: box!.y + box!.height / 2 }
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

    test("a move of the camera in one window shows in another", async ({ browser }) => {
        // two windows of the same size on the playground
        const one = await browser.newPage({ viewport: { width: 1200, height: 800 } })
        const two = await browser.newPage({ viewport: { width: 1200, height: 800 } })
        await one.goto("/about", { waitUntil: "load" })
        // start from a known view, flat, which also forgets where the cameras looked
        await reset(one)
        // put a reader on the playground, so there is something to look at
        const { id: diagram } = await playground(one)
        await one.request.post("graphql", {
            data: {
                query: "mutation ($input: DiagramAddInput!) { diagramAdd(input: $input) { diagram { id } } }",
                variables: { input: { diagram, family: "pyre.viz.readers", x: 0, y: 0, z: 0 } },
            },
        })
        await one.reload({ waitUntil: "load" })
        await two.goto("/about", { waitUntil: "load" })
        // both show it
        for (const page of [one, two]) {
            await page.locator("[data-qed-kind=factory]").first().waitFor({ timeout: 10_000 })
        }

        // the first window zooms in with its keys, after taking them onto its canvas
        await one.locator("[data-qed-diagram]").click({ position: { x: 20, y: 20 } })
        for (let i = 0; i < 3; i++) await one.keyboard.press("z")
        // once the move is over, the second window looks at the same place, at the same zoom
        const there = async () => {
            const [a, b] = [await grip(one), await grip(two)]
            return Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y))
        }
        await expect.poll(there, { timeout: 5_000 }).toBeLessThan(1)

        // the second window pans with its wheel
        const before = await grip(one)
        const box = (await two.locator("[data-qed-diagram]").boundingBox())!
        await two.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
        await two.mouse.wheel(120, 80)
        // and the first one follows
        await expect.poll(async () => (await grip(one)).x, { timeout: 5_000 }).not.toBeCloseTo(before.x, 0)
        await expect.poll(there, { timeout: 5_000 }).toBeLessThan(1)

        // take the reader off the playground
        const { factories } = await playground(one)
        for (const { id } of factories) {
            await one.request.post("graphql", {
                data: {
                    query: "mutation ($input: DiagramRemoveInput!) { diagramRemove(input: $input) { diagram { id } } }",
                    variables: { input: { diagram, node: id } },
                },
            })
        }
        // all done
        await one.close()
        await two.close()
    })
})


// end of file
