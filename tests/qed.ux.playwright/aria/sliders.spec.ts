// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// every slider thumb must carry a unique, non-empty accessible name, so a driver -- and assistive
// tech -- can target a specific one (the low vs high of a range, the two zoom axes, one viz
// controller among several) WITHOUT resorting to its value, which is state and which the convention
// (doc/semantic-markup.md) forbids as identity. each name is the server component it reflects (the
// controller slot, the zoom axis) plus the widget's part. the controls view renders the zoom control
// and the active channel's viz controllers (the setup project leaves a channel selected).
test("every slider thumb has a unique accessible name", async ({ page }) => {
    await page.goto("/controls", { waitUntil: "load" })
    await page.waitForFunction(() => Boolean(window.qed))

    // every thumb the controls view renders
    const thumbs = page.locator('[data-pyre-widget="slider"][data-pyre-widget-part="thumb"]')
    await thumbs.first().waitFor()
    const names = await thumbs.evaluateAll(els => els.map(el => el.getAttribute("aria-label")))

    // none is anonymous
    expect(names, `an anonymous slider thumb in ${JSON.stringify(names)}`)
        .not.toContain(null)
    expect(
        names.every(name => (name ?? "").trim().length > 0),
        `an empty slider thumb name in ${JSON.stringify(names)}`,
    ).toBe(true)
    // and each is unique, so exactly one thumb answers to a given name
    expect(
        new Set(names).size,
        `duplicate slider thumb names in ${JSON.stringify(names)}`,
    ).toBe(names.length)
})


/* end of file */
