// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the API contract: drive {window.qed} and assert the MODEL it reads back, with no DOM. this exercises
// the resolver + Relay store layer independently of rendering -- so a failure here points at the
// server or the store, not the pixels -- and covers commands whose effect the behavior specs cannot
// assert from the DOM (the colour-stretch controllers). it mutates shared state and restores it.

test.describe.serial("the window.qed contract", () => {
    test.beforeEach(async ({ page }) => {
        await page.goto("/", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
    })

    // the value test selects the phase channel; leave the suite on amplitude, as the rest expect
    test.afterAll(async ({ browser }) => {
        const page = await browser.newPage()
        await page.goto("/", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        await page.evaluate(() => window.qed.setChannel("amplitude"))
        await page.close()
    })

    test("state() returns the documented model shape", async ({ page }) => {
        const s = await page.evaluate(() => window.qed.state())
        expect(s).not.toBeNull()
        expect(typeof s!.viewport).toBe("number")
        expect(s!.reader === null || typeof s!.reader === "string").toBe(true)
        expect(s!.zoom).toMatchObject({
            vertical: expect.any(Number), horizontal: expect.any(Number), coupled: expect.any(Boolean),
        })
        expect(s!.measure).toMatchObject({ active: expect.any(Boolean), closed: expect.any(Boolean) })
        expect(Array.isArray(s!.measure!.path)).toBe(true)
        expect(s!.sync).toMatchObject({ scroll: expect.any(Boolean) })
    })

    test("a zoom mutation is reflected in the model", async ({ page }) => {
        await page.evaluate(() => window.qed.setZoom({ horizontal: -3, vertical: -1 }))
        expect(await page.evaluate(async () => (await window.qed.state())!.zoom)).toMatchObject({
            horizontal: -3, vertical: -1,
        })
        await page.evaluate(() => window.qed.zoomReset())
        expect(await page.evaluate(async () => (await window.qed.state())!.zoom!.horizontal)).toBe(0)
    })

    test("a range controller round-trips its bounds through the server", async ({ page }) => {
        // the amplitude channel (the setup default) carries a range controller
        const range = (await page.evaluate(() => window.qed.controllers())).find(c => c.kind === "range")
        test.skip(!range, "the active channel exposes no range controller")
        const { slot, min, max } = range!
        // a low/high inside the extent
        const bounds = { min, low: min + (max - min) / 4, high: min + (3 * (max - min)) / 4, max }

        // the server echoes the updated controller in the mutation payload
        const result = await page.evaluate(
            ([slot, bounds]) => window.qed.range.update(slot, bounds),
            [slot, bounds] as const,
        ) as { viewRangeUpdate: { controller: { low: number, high: number } } }
        expect(result.viewRangeUpdate.controller.low).toBeCloseTo(bounds.low, 3)
        expect(result.viewRangeUpdate.controller.high).toBeCloseTo(bounds.high, 3)

        // reset restores the defaults (and must not error)
        await page.evaluate(slot => window.qed.range.reset(slot), slot)
    })

    test("a range controller adopts hand-set bounds that enclose its picks and refuses ones that do not", async ({ page }) => {
        // the amplitude channel (the setup default) carries a range controller
        const range = (await page.evaluate(() => window.qed.controllers())).find(c => c.kind === "range")
        test.skip(!range, "the active channel exposes no range controller")
        const { slot, min, max } = range!
        // park the picks well inside the extent
        const quarter = (max - min) / 4
        const picks = { min, low: min + quarter, high: max - quarter, max }
        await page.evaluate(([slot, picks]) => window.qed.range.update(slot, picks), [slot, picks] as const)
        // a wider extent is adopted
        const wider = { min: min - quarter, max: max + quarter }
        const adopted = await page.evaluate(
            ([slot, bounds]) => window.qed.range.resize(slot, bounds),
            [slot, wider] as const,
        ) as { viewRangeResize: { controller: { min: number, max: number } } }
        expect(adopted.viewRangeResize.controller.min).toBeCloseTo(wider.min, 3)
        expect(adopted.viewRangeResize.controller.max).toBeCloseTo(wider.max, 3)
        // an extent that encroaches on the low pick is refused by the server
        const encroaching = { min: picks.low + quarter / 2, max }
        await expect(page.evaluate(
            ([slot, bounds]) => window.qed.range.resize(slot, bounds),
            [slot, encroaching] as const,
        )).rejects.toThrow()
        // and the bounds stay where the adopted edit put them
        const after = (await page.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!
        expect(after.min).toBeCloseTo(wider.min, 3)
        expect(after.max).toBeCloseTo(wider.max, 3)
        // the hand edit pinned the controller
        expect(after.auto).toBe(false)
        // releasing it flips the flag in the payload
        const released = await page.evaluate(
            ([slot]) => window.qed.range.setAuto(slot, true),
            [slot] as const,
        ) as { viewRangeAutoSet: { controller: { auto: boolean, low: number, high: number } } }
        expect(released.viewRangeAutoSet.controller.auto).toBe(true)
        // and in the model, with the picks untouched
        const model = (await page.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!
        expect(model.auto).toBe(true)
        // pinning it again flips it back
        await page.evaluate(([slot]) => window.qed.range.setAuto(slot, false), [slot] as const)
        expect((await page.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!.auto).toBe(false)
        // restore
        await page.evaluate(slot => window.qed.range.reset(slot), slot)
    })

    test("a value controller round-trips its marker through the server", async ({ page }) => {
        // the phase channel carries value controllers (brightness/saturation)
        await page.evaluate(() => window.qed.setChannel("phase"))
        const value = (await page.evaluate(() => window.qed.controllers())).find(c => c.kind === "value")
        test.skip(!value, "the phase channel exposes no value controller")
        const { slot, min, max } = value!
        const bounds = { min, value: min + (max - min) / 2, max }

        const result = await page.evaluate(
            ([slot, bounds]) => window.qed.value.update(slot, bounds),
            [slot, bounds] as const,
        ) as { viewValueUpdate: { controller: { value: number } } }
        expect(result.viewValueUpdate.controller.value).toBeCloseTo(bounds.value, 3)

        await page.evaluate(slot => window.qed.value.reset(slot), slot)
    })
})


/* end of file */
