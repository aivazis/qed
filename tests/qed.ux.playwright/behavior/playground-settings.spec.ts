// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// a click on the hub of a factory of the playground hangs a column below it, with its traits and
// its methods, each string folded behind a bead of its own; a click on a trait opens a field over
// its value, with the values the server suggests in a list below it: a component takes one of a
// closed set, which narrows as something is typed; <escape> leaves the setting as it was, and a
// choice picked on a class asks for the name of the instance that will carry it. this lives in the
// behavior project (serial, after the gate) and takes its reader away when done

// the playground diagram: its id and its factories
const playground = async (page: Page) => {
    // ask
    const response = await page.request.post("graphql", {
        data: { query: "{ qed { playground { id factories { id family level } } } }" },
    })
    // unpack
    const { data } = await response.json()
    // and hand it back
    return data.qed.playground
}

// take every factory off the playground
const clear = async (page: Page) => {
    // the diagram and its factories
    const { id: diagram, factories } = await playground(page)
    // remove each one
    for (const { id } of factories) {
        // through the schema
        await page.request.post("graphql", {
            data: {
                query: "mutation ($input: DiagramRemoveInput!) { diagramRemove(input: $input) { diagram { id } } }",
                variables: { input: { diagram, node: id } },
            },
        })
    }
}

// wait until the first factory stays put on the screen: the camera frames the diagram once it
// arrives, and a click aimed at the hub before then lands wherever the hub used to be
const settled = async (page: Page) => {
    // where it was at the last look
    let last: { x: number, y: number } | null = null
    // look until two looks in a row agree
    await expect.poll(async () => {
        // where it is now
        const box = await page.locator("[data-qed-kind=factory]").first().boundingBox()
        // whether it has stayed put since the last look
        const still = box !== null && last !== null && Math.abs(box.x - last.x) < 0.5 && Math.abs(box.y - last.y) < 0.5
        // remember this look
        last = box
        // and report
        return still
    }, { timeout: 5_000 }).toBe(true)
}

// the column below the factory, and the field that edits a setting
const column = (page: Page) => page.locator("[data-qed-settings]")
const editor = (page: Page) => page.locator("[data-qed-setting-editor]")


test.describe.serial("a factory of the playground hangs its traits and methods below it", () => {
    test.afterAll(async ({ browser }) => {
        // leave the playground empty, as the rest of the suite expects it
        const page = await browser.newPage()
        await page.goto("/about", { waitUntil: "load" })
        await clear(page)
        await page.close()
    })

    test("the hub hangs the column, and a trait offers what it can take", async ({ page }) => {
        // open the playground
        await page.goto("/about", { waitUntil: "load" })
        // start from an empty diagram
        await clear(page)
        // with a flat reader on it
        const { id: diagram } = await playground(page)
        await page.request.post("graphql", {
            data: {
                query: "mutation ($input: DiagramAddInput!) { diagramAdd(input: $input) { diagram { id } } }",
                variables: { input: { diagram, family: "qed.readers.native.flat", x: 0, y: 0, z: 0 } },
            },
        })
        await page.reload({ waitUntil: "load" })
        await page.locator("[data-qed-kind=factory]").first().waitFor({ timeout: 10_000 })
        // and the camera done framing it
        await settled(page)
        // with nothing hanging below it
        await expect(column(page)).toHaveCount(0)

        // a click on its hub hangs the column, with both strings folded
        await page.locator("[data-qed-kind=factory] [data-qed-hub]").first().click({ force: true })
        await expect(column(page)).toHaveCount(1)
        await expect(column(page).locator('[data-qed-expander="traits"]')).toHaveAttribute("data-qed-open", "false")
        await expect(column(page).locator('[data-qed-expander="methods"]')).toHaveAttribute("data-qed-open", "false")
        await expect(column(page).locator("[data-qed-setting]")).toHaveCount(0)

        // its methods spread out, and a class has none to invoke
        await column(page).locator('[data-qed-expander="methods"]').click()
        await expect(column(page).locator('[data-qed-method="open"]')).toHaveAttribute("data-qed-invocable", "false")
        // its traits spread out, each labeled with its name and its value
        await column(page).locator('[data-qed-expander="traits"]').click()
        await expect(column(page).locator('[data-qed-setting="cell"]')).toContainText("cell:")

        // a click on the cell opens a field over its value
        await column(page).locator('[data-qed-setting="cell"]').click()
        await expect(editor(page)).toHaveCount(1)
        // with its choices below it: the datatypes, a closed set
        const suggestions = editor(page).locator("[data-qed-suggestions]")
        await expect(suggestions).toHaveAttribute("data-qed-suggestions", "closed")
        await expect(editor(page).locator("[data-qed-suggestion]")).toHaveCount(13)
        await expect(editor(page).locator("[data-qed-suggestion]").first()).toHaveText("char")
        // which narrow as something is typed
        await page.keyboard.type("complex")
        await expect(editor(page).locator("[data-qed-suggestion]")).toHaveCount(2)
        // <escape> leaves the setting as it was
        await page.keyboard.press("Escape")
        await expect(editor(page)).toHaveCount(0)
        expect((await playground(page)).factories[0].level).toBe("class")

        // picking a choice on a class asks for the name of the instance that will carry it
        await column(page).locator('[data-qed-setting="cell"]').click()
        await editor(page).locator('[data-qed-suggestion="qed.datatypes.complex128"]').click()
        await expect(editor(page)).toContainText("name")
        await expect(editor(page).locator("[data-qed-suggestions]")).toHaveCount(0)
        // <enter> makes it
        await page.keyboard.type(`cells${Date.now()}`)
        await page.keyboard.press("Enter")
        await expect.poll(async () => (await playground(page)).factories[0].level, { timeout: 5_000 })
            .toBe("instance")
        // and the cell is the one picked
        await expect(column(page).locator('[data-qed-setting="cell"]')).toContainText("complex128")
        // whose methods can now be invoked
        await expect(column(page).locator('[data-qed-method="open"]')).toHaveAttribute("data-qed-invocable", "true")

        // another click on the hub takes the column away
        await page.locator("[data-qed-kind=factory] [data-qed-hub]").first().click({ force: true })
        await expect(column(page)).toHaveCount(0)
    })
})


// end of file
