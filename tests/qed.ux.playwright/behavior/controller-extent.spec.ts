// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"
import type { Page } from "@playwright/test"


// the display bounds of a colour-stretch controller are editable by hand: a double click on an
// end label of the slider opens a text field over it that owns its contents and talks to the
// server only on commit, so typing a number digit by digit never sends a partial value. a
// committed extent pins the controller, and the lock button on the header releases it. the server
// refuses an extent that encroaches on the picks; the field shows the refusal and closes on escape

// the marker label of {slot} that edits the pick named {name}
const pickLabel = (page: Page, slot: string, name: string) =>
    page.locator(`[data-qed-control="${slot}"] [data-pyre-widget-part="pick"][data-pyre-pick="${name}"]`)

// the end label of {slot} that edits the {end} of its extent
const endLabel = (page: Page, slot: string, end: "min" | "max") =>
    page.locator(`[data-qed-control="${slot}"] [data-pyre-widget-part="bound"][data-pyre-bound="${end}"]`)

test.describe.serial("a controller's display bounds are editable by hand", () => {
    test("typing a new min commits on enter, pins the controller, and the lock releases it", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))

        // the range controller of the active channel
        const range = (await page.evaluate(() => window.qed.controllers()))
            .find(controller => controller.kind === "range")
        test.skip(!range, "the active channel exposes no range controller")
        const { slot, min, max } = range!
        const quarter = (max - min) / 4

        // a double click on the low end label opens the editor over it
        await endLabel(page, slot, "min").dblclick()
        const field = page.getByRole("textbox", { name: `${slot} min` })
        await field.waitFor()
        // seeded with the server value
        expect(Number(await field.inputValue())).toBeCloseTo(min, 3)

        // type a lower bound, one keystroke at a time, and commit with enter
        const lower = min - quarter
        await field.fill("")
        await field.pressSequentially(String(lower))
        // nothing has been sent yet
        expect((await page.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!.min).toBeCloseTo(min, 3)
        await field.press("Enter")
        // the model catches up with the committed value
        await expect
            .poll(async () => (await page.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!.min)
            .toBeCloseTo(lower, 3)
        // the edit pinned the controller
        expect((await page.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!.auto).toBe(false)
        // the editor closed on commit, and the label now shows the new bound
        await expect(field).toHaveCount(0)
        await expect(endLabel(page, slot, "min")).toHaveText(lower.toFixed(1))

        // the lock on the header reports the pin and releases it on click
        const lock = page.getByRole("button", { name: `${slot} auto` })
        await expect(lock).toHaveAttribute("aria-pressed", "false")
        await lock.click()
        await expect
            .poll(async () => (await page.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!.auto)
            .toBe(true)
        await expect(lock).toHaveAttribute("aria-pressed", "true")

        // restore
        await page.evaluate(slot => window.qed.range.reset(slot), slot)
    })

    test("an extent that encroaches on the picks is refused and escape reverts the field", async ({ page }) => {
        await page.goto("/controls", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))

        // the range controller of the active channel
        const range = (await page.evaluate(() => window.qed.controllers()))
            .find(controller => controller.kind === "range")
        test.skip(!range, "the active channel exposes no range controller")
        const { slot, min, max } = range!
        // park the picks well inside the extent
        const quarter = (max - min) / 4
        await page.evaluate(
            ([slot, picks]) => window.qed.range.update(slot, picks),
            [slot, { min, low: min + quarter, high: max - quarter, max }] as const,
        )

        // a double click on the high end label opens the editor over it
        await endLabel(page, slot, "max").dblclick()
        const field = page.getByRole("textbox", { name: `${slot} max` })
        await field.waitFor()
        // an upper bound below the high pick
        await field.fill(String(max - 2 * quarter))
        // is flagged before it is ever sent
        await expect(field).toHaveAttribute("aria-invalid", "true")
        // and enter does not commit it
        await field.press("Enter")
        expect((await page.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!.max).toBeCloseTo(max, 3)
        // escape gives up: the editor closes and the label still shows the server value
        await field.press("Escape")
        await expect(field).toHaveCount(0)
        await expect(endLabel(page, slot, "max")).toHaveText(max.toFixed(1))

        // restore
        await page.evaluate(slot => window.qed.range.reset(slot), slot)
    })

    test("typing a pick into a marker label reaches the server without pinning the controller", async ({ page, context }) => {
        const driver = page
        const observer = await context.newPage()
        for (const client of [driver, observer]) {
            await client.goto("/controls", { waitUntil: "load" })
            await client.waitForFunction(() => Boolean(window.qed))
        }

        // the range controller of the active channel
        const range = (await driver.evaluate(() => window.qed.controllers()))
            .find(controller => controller.kind === "range")
        test.skip(!range, "the active channel exposes no range controller")
        const { slot, min, max, auto } = range!
        const quarter = (max - min) / 4
        // park the picks at known places
        await driver.evaluate(
            ([slot, picks]) => window.qed.range.update(slot, picks),
            [slot, { min, low: min + quarter, high: max - quarter, max }] as const,
        )

        // a double click on the low marker label opens the editor over it
        await pickLabel(driver, slot, `${slot} low`).dblclick()
        const field = driver.getByRole("textbox", { name: `${slot} low value` })
        await field.waitFor()
        // seeded with the pick
        expect(Number(await field.inputValue())).toBeCloseTo(min + quarter, 3)
        // a pick below the lower limit is flagged before it is sent
        await field.fill(String(min - quarter))
        await expect(field).toHaveAttribute("aria-invalid", "true")
        // a pick inside the limits is not
        const low = min + quarter / 2
        await field.fill(String(low))
        await expect(field).toHaveAttribute("aria-invalid", "false")
        // commit
        await field.press("Enter")
        await expect(field).toHaveCount(0)
        // the driver's thumb moves
        await expect.poll(async () =>
            Number(await driver.getByRole("slider", { name: `${slot} low` }).getAttribute("aria-valuenow"))
        ).toBeCloseTo(low, 3)
        // and so does the observer's, which proves the pick reached the server
        await expect.poll(async () =>
            Number(await observer.getByRole("slider", { name: `${slot} low` }).getAttribute("aria-valuenow")),
            { timeout: 15_000 },
        ).toBeCloseTo(low, 3)
        // a typed pick is not a hand edit of the bounds, so the flag is untouched
        expect((await driver.evaluate(() => window.qed.controllers())).find(c => c.slot === slot)!.auto).toBe(auto)

        // restore
        await driver.evaluate(slot => window.qed.range.reset(slot), slot)
        await observer.close()
    })
})


/* end of file */
