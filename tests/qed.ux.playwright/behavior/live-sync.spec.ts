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

    test("a range-controller change on one client re-renders another", async ({ page, context }) => {
        // the client that makes the change
        const driver = page
        // a second, independent client on the same server
        const observer = await context.newPage()

        // bring both up on the controls page and wait for the controller sliders to render
        for (const client of [driver, observer]) {
            await client.goto("/controls", { waitUntil: "load" })
            await client.waitForFunction(() => Boolean(window.qed))
            await client.locator('[data-pyre-widget="slider"][data-pyre-widget-part="thumb"]').first().waitFor()
        }

        // the range controller the active channel exposes (the setup leaves amplitude selected)
        const range = (await driver.evaluate(() => window.qed.controllers())).find(c => c.kind === "range")
        test.skip(!range, "the active channel exposes no range controller")
        const { slot, min, max } = range!

        // read this controller's two thumbs -- identified by their shared extent, which the zoom
        // slider (-6..4) does not share -- as [low, high]. this reads the rendered DOM, not
        // window.qed.controllers(), which would re-fetch and pass even if the push never arrived
        const readBounds = (client: typeof page) => client.evaluate(({ min, max }) => {
            const thumbs = [...document.querySelectorAll(
                '[data-pyre-widget="slider"][data-pyre-widget-part="thumb"]',
            )]
            return thumbs
                .filter(t => Math.abs(Number(t.getAttribute("aria-valuemin")) - min) < 1e-6
                    && Math.abs(Number(t.getAttribute("aria-valuemax")) - max) < 1e-6)
                .map(t => Number(t.getAttribute("aria-valuenow")))
                .sort((a, b) => a - b)
        }, { min, max })

        // a target band well inside the extent, and a tolerance that absorbs server rounding
        const span = max - min
        const target = { min, low: min + span * 0.3, high: min + span * 0.6, max }
        const tol = span * 0.02

        // mark the observer so we can prove it never reloaded
        await observer.evaluate(() => {
            ;(window as typeof window & { synced?: boolean }).synced = true
        })

        // drive the change on the OTHER client
        await driver.evaluate(([s, b]) => window.qed.range.update(s, b), [slot, target] as const)

        // the observer's thumbs move to the new band, pushed over the stream into its store
        await expect.poll(async () => {
            const [low, high] = await readBounds(observer)
            return Math.max(Math.abs(low - target.low), Math.abs(high - target.high))
        }, { timeout: 10_000 }).toBeLessThan(tol)
        // and it updated in place -- it never navigated or reloaded
        expect(
            await observer.evaluate(() => (window as typeof window & { synced?: boolean }).synced),
        ).toBe(true)

        // restore: reset returns the controller to its defaults, and the observer follows -- its
        // high thumb leaves the target band, proving the reset propagated too
        await driver.evaluate(s => window.qed.range.reset(s), slot)
        await expect.poll(async () => {
            const [, high] = await readBounds(observer)
            return Math.abs(high - target.high)
        }, { timeout: 10_000 }).toBeGreaterThan(tol)

        // tidy up the extra client
        await observer.close()
    })
})


/* end of file */
