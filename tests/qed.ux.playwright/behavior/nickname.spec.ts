// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the form that connects a dataset to a reader starts with the name the server suggests: the
// nickname field holds it; emptied, it shows the suggestion dimmed and disables connect; the right
// arrow or the restore control brings the suggestion back, and any character starts a name of the
// user's own. a server that cannot suggest a name leaves the field to the user and says why

// support
import { test, expect, type Page } from "@playwright/test"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"


// a scratch tree with one file for the form to open
const root = fs.mkdtempSync(path.join(os.tmpdir(), "qed-nickname-"))
// some bytes, since the form only needs a file to point at
fs.writeFileSync(path.join(root, "raster.bin"), Buffer.alloc(64))
// the archive that holds it
const uri = `file:${root}`
// and its name
const name = "nickname_archive"


// open the form that connects the scratch file to a reader, with the type that needs nothing
// from the file
const openForm = async (page: Page) => {
    // open the explorer and wait for the facade
    await page.goto("/explore", { waitUntil: "load" })
    await page.waitForFunction(() => Boolean(window.qed))
    // connect the archive and open its root, so the file shows up
    await page.evaluate(([name, uri]) => window.qed.connectArchive(name, uri), [name, uri])
    await page.evaluate(uri => window.qed.expandFolder(uri), uri)
    // select the file; the viewport turns into the form that connects it
    await page.locator('[title$="/raster.bin"]').click()
    // pick the reader type that needs nothing from the file
    await page.getByText("gdal", { exact: true }).click()
}

// remove the scratch archive from the server
const closeArchive = async (page: Page) => {
    // through the facade
    await page.evaluate(uri => window.qed.disconnectArchive(uri), uri)
}


test.describe.serial("the reader form suggests a nickname", () => {
    // remove the scratch tree once the suite is done with it
    test.afterAll(() => fs.rmSync(root, { recursive: true, force: true }))

    test("the nickname starts with the suggestion and yields to the user", async ({ page }) => {
        // open the form
        await openForm(page)
        // the nickname field
        const nickname = page.getByRole("textbox", { name: "nickname" })
        // the connect control
        const connect = page.getByRole("button", { name: "connect this dataset" })
        // the control that restores the suggestion
        const restore = page.getByRole("button", { name: "use the suggested nickname" })
        // the field starts out with whatever the server suggests, which is also its placeholder
        await expect(nickname).not.toHaveValue("")
        const suggestion = await nickname.inputValue()
        await expect(nickname).toHaveAttribute("placeholder", suggestion)
        // so the form can connect, and there is nothing to restore
        await expect(connect).toHaveAttribute("aria-disabled", "false")
        await expect(restore).toHaveCount(0)
        // emptying the field leaves the suggestion on display, disables connect,
        await nickname.fill("")
        await expect(nickname).toHaveValue("")
        await expect(nickname).toHaveAttribute("placeholder", suggestion)
        await expect(connect).toHaveAttribute("aria-disabled", "true")
        // and offers to put the suggestion back
        await expect(restore).toHaveText(`use ${suggestion} instead`)
        // the right arrow restores the suggestion and moves the cursor by one character
        await nickname.press("ArrowRight")
        await expect(nickname).toHaveValue(suggestion)
        expect(await nickname.evaluate((input: HTMLInputElement) => input.selectionStart)).toBe(1)
        await expect(connect).toHaveAttribute("aria-disabled", "false")
        // a character typed into the empty field starts a name of the user's own
        await nickname.fill("")
        await nickname.press("x")
        await expect(nickname).toHaveValue("x")
        await expect(connect).toHaveAttribute("aria-disabled", "false")
        // the restore control puts the suggestion back and returns the cursor to the field
        await restore.click()
        await expect(nickname).toHaveValue(suggestion)
        await expect(nickname).toBeFocused()
        await expect(restore).toHaveCount(0)
        // clean up the server
        await closeArchive(page)
    })

    test("a server that cannot suggest a name leaves the field to the user", async ({ page }) => {
        // make the suggestion fail, and let every other request through
        await page.route("**/graphql", async route => {
            // the suggestion is the request that names its query
            if (route.request().postData()?.includes("useFetchNicknameQuery")) {
                // answer it with an error
                await route.fulfill({ json: { errors: [{ message: "no suggestion" }] } })
                // and done
                return
            }
            // the rest go to the server
            await route.continue()
        })
        // open the form
        await openForm(page)
        // the nickname field
        const nickname = page.getByRole("textbox", { name: "nickname" })
        // starts out empty, with nothing to suggest
        await expect(nickname).toHaveValue("")
        await expect(nickname).toHaveAttribute("placeholder", "")
        // so connect waits for a name
        await expect(page.getByRole("button", { name: "connect this dataset" }))
            .toHaveAttribute("aria-disabled", "true")
        // and there is nothing to restore
        await expect(page.getByRole("button", { name: "use the suggested nickname" }))
            .toHaveCount(0)
        // the form says why
        await expect(page.getByText("could not suggest a name: no suggestion")).toBeVisible()
        // clean up the server
        await closeArchive(page)
    })
})


// end of file
