// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the server boots passive and stages its catalog when the viz activity declares it relevant, so
// the blank viewport auto-selects the single fixture dataset only after the staging round trip
// lands. arrange the state through {window.qed}, the scriptable automation surface
// (doc/automation-surface.md): it reads the model and commits the channel through the live Relay
// store, so exactly one Mosaic -- and the zoom slider on {/controls} -- renders for the read-only
// specs, with no raw-fetch reload dance. the selection is server-side state, so it persists for
// the {gate} pages.
test("a viz view renders on load", async ({ page }) => {
    // load the app and wait for the facade to publish itself
    await page.goto("/", { waitUntil: "load" })
    await page.waitForFunction(() => Boolean((window as { qed?: unknown }).qed))
    // mounting the viz activity asks the server to stage the catalog, and the survey runs
    // on a crew, so the auto-selected dataset arrives a round trip later; poll the facade
    // until the discovered state has reached this client
    await expect.poll(
        async () => await page.evaluate(async () => {
            // grab the facade
            const qed = (window as unknown as {
                qed: { state: () => Promise<{ dataset: { channels: string[] } | null }> }
            }).qed
            // and report how many channels the bound dataset offers, if there is one
            return (await qed.state()).dataset?.channels.length ?? 0
        }),
        { timeout: 20_000 }
    ).toBeGreaterThan(0)

    // discover a channel the dataset offers, set it, and read back what the server confirms
    const channel = await page.evaluate(async () => {
        const qed = (window as { qed: { state: () => Promise<{ channel: string | null,
            dataset: { channels: string[] } }>, setChannel: (tag: string) => Promise<unknown> } }).qed
        const { dataset } = await qed.state()
        // prefer amplitude, the most legible channel, but fall back to whatever the dataset offers
        const choice = dataset.channels.includes("amplitude") ? "amplitude" : dataset.channels[0]
        await qed.setChannel(choice)
        return (await qed.state()).channel
    })
    // the server made a selection
    expect(channel).toBeTruthy()

    // sanity: the viz widgets now render, so the gate inspects real controls, not an empty shell
    await page.goto("/controls", { waitUntil: "load" })
    await expect(page.locator('[data-pyre-widget="mosaic"]')).toHaveCount(1)
    await expect(
        page.locator('[data-pyre-widget="slider"][data-pyre-widget-part="thumb"]').first()
    ).toBeVisible()
})


/* end of file */
