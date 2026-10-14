// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// a factory of the playground fans out the next level down around it: a reader, the families of
// its classes, which open onto their members fanned out from the family itself, and a class rises
// to a new instance of it. left and right move the focus among the choices on an arc, up opens the
// family or the class that has the focus, down undoes the last step, and none of the arrows reach
// the camera; a class with the focus previews the factory pinned to it, as the server plans the
// pin; <enter> takes the choice with the focus, a new instance asks for a name it may do without,
// and every pin relabels the factory. this lives in the behavior project (serial, after the gate)
// and takes its reader away when done

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

// where the first factory sits on the screen
const where = async (page: Page) => {
    // find it
    const box = (await page.locator("[data-qed-kind=factory]").first().boundingBox())!
    // and its corner
    return { x: box.x, y: box.y }
}

// the label of the factory on the canvas
const label = (page: Page) => page.locator('[data-qed-label="factory"]').first()

// the choice of the fan that has the focus
const focused = (page: Page) => page.locator('[data-qed-fan] [data-qed-focused="true"]')
// the choices on the arc, from left to right, without the way back
const arc = async (page: Page) => (await page.locator("[data-qed-fan] [data-qed-satellite]")
    .evaluateAll(nodes => nodes.map(node => node.getAttribute("data-qed-satellite"))))
    .filter(name => name !== "back")
// the choice a level starts on: the middle of the arc, where <up> would land
const middle = (choices: (string | null)[]) => choices[Math.floor((choices.length - 1) / 2)]
// move the focus to the choice {target} with the right arrow, from wherever it is
const steer = async (page: Page, target: string) => {
    // the choices, and where the focus and the target are among them
    const choices = await arc(page)
    const from = choices.indexOf(await focused(page).getAttribute("data-qed-satellite"))
    const to = choices.indexOf(target)
    // step to it, wrapping around
    for (let step = 0; step < (to - from + choices.length) % choices.length; step++) {
        await page.keyboard.press("ArrowRight")
    }
    // and make sure it got there
    await expect(focused(page)).toHaveAttribute("data-qed-satellite", target)
}


test.describe.serial("a factory of the playground fans out its choices", () => {
    test.afterAll(async ({ browser }) => {
        // leave the playground empty, as the rest of the suite expects it
        const page = await browser.newPage()
        await page.goto("/about", { waitUntil: "load" })
        await clear(page)
        await page.close()
    })

    test("the keys browse the fan, preview a class, pin it, and undo", async ({ page }) => {
        // open the playground
        await page.goto("/about", { waitUntil: "load" })
        // start from an empty diagram
        await clear(page)
        // with a reader on it
        const { id: diagram } = await playground(page)
        await page.request.post("graphql", {
            data: {
                query: "mutation ($input: DiagramAddInput!) { diagramAdd(input: $input) { diagram { id } } }",
                variables: { input: { diagram, family: "pyre.viz.readers", x: 0, y: 0, z: 0 } },
            },
        })
        await page.reload({ waitUntil: "load" })
        // the reader is on the canvas, labeled by its protocol
        await page.locator("[data-qed-kind=factory]").first().waitFor({ timeout: 10_000 })
        await expect(label(page)).toHaveText("reader")

        // a double click on its hub fans it out
        await page.locator("[data-qed-kind=factory] circle").first().dblclick()
        await expect(page.locator("[data-qed-fan]")).toHaveCount(1)
        // with its families on the arc, the one in the middle in focus, and no way back from a
        // protocol
        await expect(page.locator('[data-qed-fan] [data-qed-satellite="isce2"]')).toHaveCount(1)
        await expect(page.locator('[data-qed-fan] [data-qed-satellite="native"]')).toHaveCount(1)
        const families = await arc(page)
        await expect(focused(page)).toHaveAttribute("data-qed-satellite", middle(families)!)
        await expect(page.locator('[data-qed-satellite="back"]')).toHaveCount(0)

        // where the camera has the diagram
        const before = await where(page)
        // the arrows move the focus along the arc, one step at a time, wrapping around
        const start = families.indexOf(middle(families))
        await page.keyboard.press("ArrowRight")
        await expect(focused(page))
            .toHaveAttribute("data-qed-satellite", families[(start + 1) % families.length]!)
        await page.keyboard.press("ArrowLeft")
        await expect(focused(page)).toHaveAttribute("data-qed-satellite", middle(families)!)
        // all the way to the native family
        await steer(page, "native")
        // a family previews nothing
        await expect(page.locator("[data-qed-preview]")).toHaveCount(0)
        // down has nothing to undo here, and is swallowed anyway
        await page.keyboard.press("ArrowDown")
        await expect(focused(page)).toHaveAttribute("data-qed-satellite", "native")
        // so the camera did not move
        expect(await where(page)).toEqual(before)

        // up opens the family onto its members, which fan out from it, with the way back below
        await page.keyboard.press("ArrowUp")
        await expect(page.locator('[data-qed-fan] [data-qed-satellite="qed.readers.native.flat"]')).toHaveCount(1)
        await expect(page.locator('[data-qed-fan] [data-qed-opened="native"]')).toHaveCount(1)
        await expect(page.locator('[data-qed-satellite="back"]')).toHaveCount(1)
        // and the member in the middle in focus
        await expect(focused(page)).toHaveAttribute("data-qed-satellite", middle(await arc(page))!)
        // down steps back out, onto the family it came from
        await page.keyboard.press("ArrowDown")
        await expect(page.locator('[data-qed-fan] [data-qed-opened]')).toHaveCount(0)
        await expect(focused(page)).toHaveAttribute("data-qed-satellite", "native")
        // and up goes right back in
        await page.keyboard.press("ArrowUp")
        await expect(page.locator('[data-qed-fan] [data-qed-opened="native"]')).toHaveCount(1)

        // the arrows reach the flat reader among the members
        await steer(page, "qed.readers.native.flat")
        // which previews the factory pinned to it, as the server plans the pin: its name; the
        // reader keeps the slot of its raster, so it gains none and lets none go
        const preview = page.locator('[data-qed-preview="qed.readers.native.flat"]')
        await expect(preview).toHaveCount(1)
        await expect(preview.locator("text").first()).toHaveText("flat")
        await expect(preview.locator("[data-qed-preview-slot]")).toHaveCount(0)
        await expect(preview.locator("[data-qed-preview-dropped]")).toHaveCount(0)

        // up rises above the class, to a new instance of it, which takes the focus
        await page.keyboard.press("ArrowUp")
        await expect(page.locator('[data-qed-fan] [data-qed-opened="qed.readers.native.flat"]')).toHaveCount(1)
        await expect(focused(page)).toHaveAttribute("data-qed-satellite", "new")
        // and down steps back down, onto the class
        await page.keyboard.press("ArrowDown")
        await expect(page.locator('[data-qed-fan] [data-qed-opened="qed.readers.native.flat"]')).toHaveCount(0)
        await expect(focused(page)).toHaveAttribute("data-qed-satellite", "qed.readers.native.flat")

        // while the fan is out, the delete keys leave the diagram alone
        await page.keyboard.press("Delete")
        expect((await playground(page)).factories).toHaveLength(1)

        // <enter> pins the reader to it, and the fan folds
        await page.keyboard.press("Enter")
        await expect(page.locator("[data-qed-fan]")).toHaveCount(0)
        await expect.poll(async () => (await playground(page)).factories[0].family, { timeout: 5_000 })
            .toBe("qed.readers.native.flat")
        // and the label on the canvas names the class
        await expect(label(page)).toHaveText("flat")

        // fanned out again, a class offers a new instance of it, and the way back
        await page.locator("[data-qed-kind=factory] circle").first().dblclick()
        await expect(page.locator("[data-qed-fan] [data-qed-satellite]")).toHaveCount(2)
        await expect(page.locator('[data-qed-satellite="new"]')).toHaveCount(1)
        await expect(page.locator('[data-qed-satellite="back"]')).toHaveCount(1)
        // the new instance, alone on the arc, has the focus, and choosing it asks for a name
        await expect(focused(page)).toHaveAttribute("data-qed-satellite", "new")
        await page.keyboard.press("Enter")
        await expect(page.locator("[data-qed-fan-namer]")).toHaveCount(1)
        // the way back undoes that step first: the name goes, and the fan stays where it was
        await page.locator('[data-qed-fan] [data-qed-satellite="back"]').click()
        await expect(page.locator("[data-qed-fan-namer]")).toHaveCount(0)
        await expect(page.locator('[data-qed-fan] [data-qed-satellite="new"]')).toHaveCount(1)
        expect((await playground(page)).factories[0].level).toBe("class")
        // so choosing the new instance again asks for its name again; the click goes to the ring
        // around the plus sign, where a person clicks, since the middle of the whole satellite,
        // label included, is empty canvas that firefox does not hand to it
        await page.locator('[data-qed-fan] [data-qed-satellite="new"] circle').first().click()
        await expect(page.locator("[data-qed-fan-namer]")).toHaveCount(1)
        // which keeps its keys: typing it moves nothing
        const name = `fan${Date.now()}`
        await page.keyboard.type(name)
        expect(await where(page)).toEqual(before)
        // <enter> makes the instance and pins the reader to it, and the fan folds
        await page.keyboard.press("Enter")
        await expect(page.locator("[data-qed-fan]")).toHaveCount(0)
        await expect.poll(async () => (await playground(page)).factories[0].level, { timeout: 5_000 })
            .toBe("instance")
        // the label says what it is, and what it is an instance of
        await expect(label(page)).toHaveText(`${name}:flat`)

        // fanned out again, the way back leads to the class
        await page.locator("[data-qed-kind=factory] circle").first().dblclick()
        await page.keyboard.press("ArrowDown")
        await expect.poll(async () => (await playground(page)).factories[0].level, { timeout: 5_000 })
            .toBe("class")
        await expect(label(page)).toHaveText("flat")
        // and from there, back to the protocol
        await page.keyboard.press("ArrowDown")
        await expect.poll(async () => (await playground(page)).factories[0].level, { timeout: 5_000 })
            .toBe("protocol")
        await expect(label(page)).toHaveText("reader")
        // <escape> folds the fan
        await page.keyboard.press("Escape")
        await expect(page.locator("[data-qed-fan]")).toHaveCount(0)
    })
})


// end of file
