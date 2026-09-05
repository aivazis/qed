// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test, expect } from "@playwright/test"


// the journal console: the server's journal reaches the client over a stream of its own (the
// /journal route), a newcomer is opened with the history, and entries flushed after that arrive
// live. the panel owns the subscription, so the stream is open only while it is mounted. a bad
// graphql query is the deterministic way to make the server say something: the handler logs a
// warning on {qed.ux.graphql} for every error it reports back
test.describe.serial("the journal console", () => {
    test("the console opens with the history and hears what the server says next", async ({ page }) => {
        // bring the client up on the viz page
        await page.goto("/controls", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // with the console closed, there is no stream
        expect(await page.evaluate(() => window.qed.journal.live())).toBe(false)

        // open the console
        await page.locator('[data-qed-nav="journal"]').click()
        const panel = page.locator('[data-qed-panel="journal"]')
        await panel.waitFor()
        // the stream is open
        await expect.poll(() => page.evaluate(() => window.qed.journal.live())).toBe(true)
        // and the history arrived: the server announced its address when it came up
        const entries = panel.locator('[data-qed-control="entry"]')
        await expect(entries.filter({ hasText: "web server on" }).first()).toBeVisible({ timeout: 10_000 })

        // provoke a warning: a query that names a field the schema does not have
        const response = await page.request.post("graphql", { data: { query: "{ noSuchField }" } })
        expect(response.ok()).toBe(true)
        // the warning reaches the console live, as a warning row from the graphql channel
        const warning = entries.filter({ hasText: "qed.ux.graphql" }).last()
        await expect(warning).toBeVisible({ timeout: 10_000 })
        await expect(warning).toHaveAttribute("data-qed-value", "warning")
        // and the facade reads the same buffer the panel renders
        const buffer = await page.evaluate(() => window.qed.journal.entries())
        expect(buffer.some(record => record.notes.channel === "qed.ux.graphql")).toBe(true)

        // a row expands on click to show its details
        await expect(warning).toHaveAttribute("aria-expanded", "false")
        await warning.click()
        await expect(warning).toHaveAttribute("aria-expanded", "true")
        await expect(warning).toContainText("noSuchField")

        // the severity toggles are pressed buttons; releasing {warning} hides the row
        const toggle = panel.locator('[data-qed-control="severity"][data-qed-value="warning"]')
        await expect(toggle).toHaveAttribute("aria-pressed", "true")
        await toggle.click()
        await expect(toggle).toHaveAttribute("aria-pressed", "false")
        await expect(entries.filter({ hasText: "qed.ux.graphql" })).toHaveCount(0)
        await toggle.click()
        await expect(entries.filter({ hasText: "qed.ux.graphql" }).last()).toBeVisible()

        // the channel prefix narrows the list to a subtree
        const prefix = panel.locator('[data-qed-control="channel"]')
        await prefix.fill("qed.ux.graphql")
        await expect(entries.filter({ hasText: "web server on" })).toHaveCount(0)
        await expect(entries.filter({ hasText: "qed.ux.graphql" }).last()).toBeVisible()
        await prefix.fill("")

        // the channels tray lists the graphql channel, since it has spoken, with its switch on
        await panel.locator('[data-qed-panel="journal-channels"] [data-qed-control="tray"]').click()
        const graphqlSwitch = panel.locator('[data-qed-control="channel-active"][data-qed-value="warning:qed.ux.graphql"]')
        await expect(graphqlSwitch).toHaveAttribute("aria-pressed", "true", { timeout: 10_000 })
        // the facade reads the same listing
        const channels = await page.evaluate(() => window.qed.journal.channels())
        expect(channels.some(channel => channel.severity === "warning" && channel.name === "qed.ux.graphql" && channel.active)).toBe(true)
        // a channel nobody has heard of can be turned on through the facade
        await page.evaluate(() => window.qed.journal.setActive("debug", "qed.test.console", true))
        expect(
            (await page.evaluate(() => window.qed.journal.channels()))
                .find(channel => channel.id === "debug:qed.test.console")?.active,
        ).toBe(true)
        // and off again
        await page.evaluate(() => window.qed.journal.setActive("debug", "qed.test.console", false))
        expect(
            (await page.evaluate(() => window.qed.journal.channels()))
                .find(channel => channel.id === "debug:qed.test.console")?.active,
        ).toBe(false)

        // clearing empties the buffer, and nothing else
        await panel.locator('[data-qed-control="clear"]').click()
        await expect(entries).toHaveCount(0)
        expect(await page.evaluate(() => window.qed.journal.entries())).toEqual([])

        // leaving the console closes the stream
        await page.locator('[data-qed-nav="view controls"]').click()
        await expect.poll(() => page.evaluate(() => window.qed.journal.live())).toBe(false)
    })

    test("a warning provoked by one client reaches the console of another", async ({ page, context }) => {
        // the client that provokes the warning
        const driver = page
        // a second, independent client on the same server, watching the console
        const observer = await context.newPage()
        await observer.goto("/console", { waitUntil: "load" })
        await observer.waitForFunction(() => Boolean(window.qed))
        const entries = observer.locator('[data-qed-panel="journal"] [data-qed-control="entry"]')
        await entries.first().waitFor({ timeout: 10_000 })
        // how many the observer has heard so far
        const before = await entries.count()

        // the driver provokes a warning without ever opening the console
        await driver.goto("/controls", { waitUntil: "load" })
        await driver.request.post("graphql", { data: { query: "{ noSuchField }" } })

        // the observer hears it
        await expect.poll(() => entries.count(), { timeout: 10_000 }).toBeGreaterThan(before)
        await expect(entries.filter({ hasText: "qed.ux.graphql" }).last()).toBeVisible()

        // tidy up the extra client
        await observer.close()
    })
})


/* end of file */
