// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the server starts with a blank viewport that has auto-selected the single fixture dataset but
// no channel, so nothing renders. select a channel through the same GraphQL endpoint the client
// uses, so exactly one Mosaic -- and the zoom slider on {/controls} -- renders for the read-only
// specs. the selection is server-side state, so it persists for the {gate} and {backlog} pages.
//
// the GraphQL call is made from inside the page (browser {fetch}), exactly as the client does it;
// node's HTTP client (playwright's {request} fixture) is not understood by pyre's minimal server.
test("a viz view renders on load", async ({ page }) => {
    // load the app, which itself drives the same GraphQL endpoint, so {fetch} is known to work
    await page.goto("/", { waitUntil: "networkidle" })

    // discover the auto-selected reader and a channel, then select it on viewport 0
    const channel = await page.evaluate(async () => {
        // a small GraphQL helper, same-origin
        const gql = async (query: string) => {
            const response = await fetch("/graphql", {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ query }),
            })
            return response.json()
        }

        // the reader and the channels its dataset offers
        const state = await gql("{ qed { views { reader { name } dataset { channels { tag } } } } }")
        const view = state.data.qed.views[0]
        const reader = view.reader.name
        const tags = view.dataset.channels.map((c: { tag: string }) => c.tag)
        // prefer amplitude, the most legible channel, but fall back to whatever the dataset offers
        const choice = tags.includes("amplitude") ? "amplitude" : tags[0]

        // select it
        const result = await gql(
            `mutation { viewChannelSet(selection: ` +
            `{viewport: 0, reader: "${reader}", selector: "channel", value: "${choice}"}) ` +
            `{ views { channel { tag } } } }`
        )
        // hand back what the server confirms
        return result.data.viewChannelSet.views[0].channel.tag
    })
    // the server made a selection
    expect(channel).toBeTruthy()

    // sanity: the viz widgets now render, so the gate inspects real controls, not an empty shell
    await page.goto("/controls", { waitUntil: "networkidle" })
    await expect(page.locator('[data-pyre-widget="mosaic"]')).toHaveCount(1)
    await expect(
        page.locator('[data-pyre-widget="slider"][data-pyre-widget-part="thumb"]').first()
    ).toBeVisible()
})


/* end of file */
