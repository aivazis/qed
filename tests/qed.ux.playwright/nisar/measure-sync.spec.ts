// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Browser, Page } from "@playwright/test"


// two products side by side, with their paths synced, is how acquisitions are compared; toggling
// the measure layer in one viewport must turn it on or off in both, and leave each one showing its
// own product. this runs against the NISAR server, whose two fixtures make two different readers,
// with the controls panel open, since its sync table draws a row for every viewport. it operates
// the controls, so it restores the viewports, the selections, and the flags it touches

// the client's automation surface, published on mount
const ensureQED = (page: Page) => page.waitForFunction(() => Boolean(window.qed))

// the models of the viewports
const viewports = (page: Page) => page.evaluate(() => window.qed.viewports())

// ask the server something through the endpoint the client uses
const ask = (page: Page, query: string) =>
    page.evaluate(async query => {
        // post the query
        const response = await fetch("/graphql", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        })
        // and hand back what it carries
        return (await response.json()).data
    }, query)

// the selections the view in {viewport} holds, as a table
const selections = async (page: Page, viewport: number) => {
    // ask for the selections of every view
    const { qed } = await ask(page, "query { qed { views { selections { name value } } } }")
    // and tabulate the ones of {viewport}
    return Object.fromEntries(
        (qed.views[viewport].selections ?? []).map(({ name, value }) => [name, value])
    ) as Record<string, string>
}

// change the selections of {viewport} to {wanted}, one axis at a time; selecting a value that is
// already selected clears it, so axes that already agree are left alone
const select = async (page: Page, viewport: number, wanted: Record<string, string | undefined>) => {
    // what the view holds now
    const held = await selections(page, viewport)
    // go through the axes of either table
    for (const axis of new Set([...Object.keys(held), ...Object.keys(wanted)])) {
        // the axes that agree
        if (held[axis] === wanted[axis]) {
            // need nothing
            continue
        }
        // an axis that should be clear is cleared by selecting its value again; any other one
        // gets the value it should have
        const value = wanted[axis] ?? held[axis]
        // make the change
        await page.evaluate(([axis, value, viewport]) =>
            window.qed.selectValue(axis as string, value as string, viewport as number),
            [axis, value, viewport])
    }
}

// show {reader} in {viewport}, with the selections of its first dataset and a channel, so that
// the viewport has something to draw; hand back the name of the dataset
const show = async (page: Page, viewport: number, reader: string) => {
    // select the reader
    await page.evaluate(([reader, viewport]) =>
        window.qed.selectReader(reader as string, viewport as number), [reader, viewport])
    // the datasets of the reader
    const datasets = async () => {
        // ask the server for them
        const { qed } = await ask(page, "query { qed { readers { name datasets { name selector { name value } channels { tag } } } } }")
        // and pick out the ones of {reader}
        return qed.readers.find(entry => entry.name === reader).datasets
    }
    // a reader learns its datasets once its product has been opened, which happens after the
    // server boots, so wait for them
    await expect.poll(async () => (await datasets()).length, { timeout: 30_000 }).toBeGreaterThan(0)
    // then take the first one
    const [dataset] = await datasets()
    // select it
    await select(page, viewport, Object.fromEntries(dataset.selector.map(({ name, value }) => [name, value])))
    // and pick its first channel, unless the view has one already
    if ((await page.evaluate(viewport => window.qed.state(viewport), viewport))!.channel === null) {
        // pick it
        await page.evaluate(([tag, viewport]) =>
            window.qed.setChannel(tag as string, viewport as number), [dataset.channels[0].tag, viewport])
    }
    // hand back the name of the dataset
    return dataset.name as string
}

// force the path sync flag of {viewport} to {want}; the mutation only toggles
const setPathSync = async (page: Page, viewport: number, want: boolean) => {
    // read the flag
    const now = (await viewports(page))[viewport]?.sync?.path
    // and flip it if it is not what we want
    if (now !== want) {
        await page.evaluate(viewport => window.qed.sync.toggle("path", viewport), viewport)
    }
}

// what the first viewport shows when the spec starts, so it can be put back
let initial: { reader: string | null, selections: Record<string, string> } | null = null

// put the server back the way the spec found it: one viewport, its path unsynced, its measure
// layer off, showing what it showed with the selections it held
const restore = async (browser: Browser) => {
    // on a page of its own
    const page = await browser.newPage()
    await page.goto("/", { waitUntil: "load" })
    await ensureQED(page)
    // collapse the viewports from the last one down
    for (let n = (await viewports(page)).length; n > 1; n--) {
        await page.evaluate(viewport => window.qed.collapse(viewport), n - 1)
    }
    // leave the path sync group
    await setPathSync(page, 0, false)
    // hide the measure layer
    if ((await viewports(page))[0]?.measure?.active) {
        await page.evaluate(() => window.qed.measure.toggle(0))
    }
    // if the spec got as far as recording what the first viewport showed, and it showed a reader
    if (initial?.reader) {
        // show it again
        await page.evaluate(reader => window.qed.selectReader(reader as string, 0), initial.reader)
    }
    // and give the view of the first viewport its original selections back
    await select(page, 0, initial?.selections ?? {})
    // all done
    await page.close()
}


test.describe.serial("the measure layer of path synced viewports", () => {
    test.afterAll(async ({ browser }) => { await restore(browser) })

    test("toggling it in one viewport turns it on or off in both, and neither changes products", async ({ page }) => {
        // collect what the page throws, which is how a crash of the client shows up
        const errors: string[] = []
        page.on("pageerror", error => errors.push(error.message))
        // start from the controls panel, whose sync table draws a row for every viewport
        await page.goto("/controls", { waitUntil: "load" })
        await ensureQED(page)
        // record what the first viewport shows, so it can be put back
        initial = { reader: (await viewports(page))[0].reader, selections: await selections(page, 0) }

        // show the slc in the first viewport
        const early = await show(page, 0, "gslc")
        // split it, which makes a second viewport that shows the same thing
        await page.evaluate(() => window.qed.split(0))
        await expect.poll(async () => (await viewports(page)).length).toBe(2)
        // and show the covariance in the second one
        const late = await show(page, 1, "gcov")
        // sync the paths of both, which also turns on their measure layers
        await setPathSync(page, 0, true)
        await setPathSync(page, 1, true)
        // make the first viewport the active one, so the controls panel draws its trays
        await page.evaluate(() => window.qed.setActive(0))
        // the sync table names both datasets
        await expect(page.getByText(early, { exact: true })).toBeVisible()
        await expect(page.getByText(late, { exact: true })).toBeVisible()

        // check that each viewport still shows its own product, with its layer in the given state
        const check = async (active: boolean) => {
            // get the models
            const [first, second] = await viewports(page)
            // the first viewport still shows the slc
            expect(first.reader).toBe("gslc")
            expect(first.dataset).not.toBeNull()
            // the second still shows the covariance
            expect(second.reader).toBe("gcov")
            expect(second.dataset).not.toBeNull()
            // and their layers agree
            expect(first.measure!.active).toBe(active)
            expect(second.measure!.active).toBe(active)
        }
        // both layers start out on
        await check(true)
        // turn the layer off in the second viewport
        await page.evaluate(() => window.qed.measure.toggle(1))
        // it goes off in both, and neither viewport changes products
        await expect.poll(async () => (await viewports(page))[0].measure!.active).toBe(false)
        await check(false)
        // turn it back on in the first one
        await page.evaluate(() => window.qed.measure.toggle(0))
        // and it comes back on in both
        await expect.poll(async () => (await viewports(page))[0].measure!.active).toBe(true)
        await check(true)

        // the sync table still names both datasets
        await expect(page.getByText(early, { exact: true })).toBeVisible()
        await expect(page.getByText(late, { exact: true })).toBeVisible()
        // and the client never crashed
        expect(errors).toEqual([])
    })
})


// end of file
