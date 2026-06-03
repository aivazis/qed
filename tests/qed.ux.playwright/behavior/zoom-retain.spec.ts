// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// changing the zoom level in place must keep you looking at the same place: the source pixel under
// the viewport center should survive the change. the scroll offset lives in rendered pixels (which
// scale as 2**zoom), so a zoom change that does not rescale the offset sends the view careening to
// a corner -- the browser clamps the now-too-large offset against the resized mosaic. this drives
// the zoom IN PLACE through the slider (a Relay mutation, no remount) and reads the visible
// window's source-pixel center off the minimap markup before and after. the coupled cases move
// both axes together; the uncoupled case zooms the columns alone, so a row/col swap in the per-axis
// rescale would drag the row off its pixel. it mutates shared server state, so it lives in the
// behavior project and restores the state it touched.

const gql = (page: Page, query: string) =>
    page.evaluate(async q => (await fetch("/graphql", {
        method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ query: q }),
    })).json(), query)

const waitForZoom = async (page: Page, horizontal: number) =>
    expect.poll(async () =>
        (await gql(page, "{ qed { views { zoom { horizontal } } } }")).data.qed.views[0].zoom.horizontal
    ).toBe(horizontal)

// drive the coupled flag to {want} through its mutation (a no-op when it already matches)
const setCoupled = async (page: Page, want: boolean) => {
    const now = (await gql(page, "{ qed { views { zoom { coupled } } } }")).data.qed.views[0].zoom.coupled
    if (now !== want) await gql(page, "mutation { viewZoomToggleCoupled(viewport: 0) { zoom { coupled } } }")
}

// the visible window's source-pixel center, read off the minimap markup
const readCenter = async (page: Page) => {
    const box = page.locator('[data-qed-control="minimap"] [data-qed-view-origin]').first()
    const [oRow, oCol] = (await box.getAttribute("data-qed-view-origin"))!.split(",").map(Number)
    const [sRow, sCol] = (await box.getAttribute("data-qed-view-shape"))!.split(",").map(Number)
    return { row: oRow + sRow / 2, col: oCol + sCol / 2, sRow, sCol }
}

// click the named tick on the horizontal zoom track and wait for the level to settle
const setHorizontalZoom = async (page: Page, level: number) => {
    const track = page.locator('[data-pyre-widget="slider"][data-pyre-widget-part="track"]')
        .filter({ has: page.locator('[aria-orientation="horizontal"]') })
        .filter({ hasText: "-6" })
    await track.getByText(String(level), { exact: true }).click()
    await waitForZoom(page, level)
    // let the minimap observe the resulting scroll
    await page.waitForTimeout(150)
}

// land at zoom 0 with the requested coupling, scrolled to the middle of the raster, on /controls
const start = async (page: Page, { coupled }: { coupled: boolean }) => {
    await page.goto("/", { waitUntil: "networkidle" })
    await gql(page, "mutation { viewZoomSetLevel(viewport: 0, horizontal: 0, vertical: 0) { zoom { horizontal } } }")
    await setCoupled(page, coupled)
    await page.goto("/controls", { waitUntil: "networkidle" })
    const region = page.locator('[data-qed-region="viewport"]').first()
    await region.waitFor({ timeout: 10_000 })
    // scroll to the middle, so there is room to clamp in either direction
    await region.evaluate(el => {
        el.scrollLeft = (el.scrollWidth - el.clientWidth) / 2
        el.scrollTop = (el.scrollHeight - el.clientHeight) / 2
    })
    await page.waitForTimeout(150)
}

// the centered source pixel must barely move; the bug threw it a half-window away, so a sixteenth
// of the (post-zoom) window is a generous but decisive bound
const expectRetained = (after: Awaited<ReturnType<typeof readCenter>>, before: { row: number, col: number }) => {
    expect(Math.abs(after.col - before.col)).toBeLessThan(after.sCol / 16)
    expect(Math.abs(after.row - before.row)).toBeLessThan(after.sRow / 16)
}


test.describe.serial("an in-place zoom change retains the viewport position", () => {
    test.afterAll(async ({ browser }) => {
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "networkidle" })
        // leave the store as the other specs expect it: coupled, at zoom 0
        await setCoupled(page, true)
        await gql(page, "mutation { viewZoomSetLevel(viewport: 0, horizontal: 0, vertical: 0) { zoom { horizontal } } }")
        await page.close()
    })

    for (const level of [-2, 2]) {
        test(`the centered source pixel survives a coupled in-place zoom to ${level}`, async ({ page }) => {
            await start(page, { coupled: true })
            const before = await readCenter(page)
            await setHorizontalZoom(page, level)
            expectRetained(await readCenter(page), before)
        })
    }

    test("the centered source pixel survives an uncoupled horizontal-only zoom", async ({ page }) => {
        await start(page, { coupled: false })
        const before = await readCenter(page)
        // zoom the columns alone; the rows must not budge, despite the column rescale
        await setHorizontalZoom(page, -2)
        expectRetained(await readCenter(page), before)
    })
})


/* end of file */
