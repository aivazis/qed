// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the live-sync capability: a state change committed by one client reaches every other connected
// client over the SSE event stream (the /events route + the mutation broadcast), updating the
// receiver's Relay store -- and therefore its rendered DOM -- with no reload or fetch on its side.
// we drive two independent pages on the one shared server: the {driver} mutates through window.qed,
// while the {observer} only watches its own DOM. the assertion is on the DOM, not on {window.qed.
// state()} -- which would re-fetch from the network and pass even if the push never arrived. it
// perturbs viewport 0's zoom and restores it exactly.
test.describe.serial("live client sync over the event stream", () => {
    test("a zoom change on one client re-renders another", async ({ page, context }) => {
        // the client that makes the change
        const driver = page
        // a second, independent client on the same server
        const observer = await context.newPage()

        // bring both up on the viz page and wait for the rendered viewport region
        for (const client of [driver, observer]) {
            await client.goto("/controls", { waitUntil: "load" })
            await client.waitForFunction(() => Boolean(window.qed))
            await client.locator('[data-qed-region="viewport"]').first().waitFor()
        }

        // the observer's region; its {data-qed-zoom} mirrors the store zoom and re-renders on update
        const region = observer.locator('[data-qed-region="viewport"]').first()
        // what the observer renders before anything changes
        const before = (await region.getAttribute("data-qed-zoom")) ?? "0,0"
        const [vertical, horizontal] = before.split(",").map(Number)
        // a symmetric target distinct from the current zoom
        const target = vertical === -2 && horizontal === -2 ? -3 : -2

        // mark the observer so we can later prove it never reloaded
        await observer.evaluate(() => {
            ;(window as typeof window & { synced?: boolean }).synced = true
        })

        // the observer does nothing from here on; the driver mutates on the OTHER client
        await driver.evaluate(level => window.qed.setZoom(level, 0), target)

        // the observer's DOM reflects the new zoom, pushed over the stream and refetched into its store
        await expect(region).toHaveAttribute("data-qed-zoom", `${target},${target}`, { timeout: 10_000 })
        // and it got there in place -- it never navigated or reloaded
        expect(
            await observer.evaluate(() => (window as typeof window & { synced?: boolean }).synced),
        ).toBe(true)

        // restore exactly what was there, and confirm that propagates to the observer too
        await driver.evaluate(
            ([v, h]) => window.qed.setZoom({ vertical: v, horizontal: h }, 0),
            [vertical, horizontal] as const,
        )
        await expect(region).toHaveAttribute("data-qed-zoom", before, { timeout: 10_000 })

        // tidy up the extra client
        await observer.close()
    })
})


/* end of file */
