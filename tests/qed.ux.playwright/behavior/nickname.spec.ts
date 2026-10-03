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


// select the scratch file, so the viewport turns into the form that connects it
const selectFile = async (page: Page) => {
    // open the explorer and wait for the facade
    await page.goto("/explore", { waitUntil: "load" })
    await page.waitForFunction(() => Boolean(window.qed))
    // connect the archive and open its root, so the file shows up
    await page.evaluate(([name, uri]) => window.qed.connectArchive(name, uri), [name, uri])
    await page.evaluate(uri => window.qed.expandFolder(uri), uri)
    // select the file
    await page.locator('[title$="/raster.bin"]').click()
}

// open the form that connects the scratch file to a reader, with the type that needs nothing
// from the file
const openForm = async (page: Page) => {
    // select the file
    await selectFile(page)
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

    test("every reader type the archive offers is a family the server knows", async ({ page }) => {
        // select the file
        await selectFile(page)
        // ask the server which reader types the archive offers, the same list the form shows
        const readers: string[] = await page.evaluate(async uri => {
            // through the client's own endpoint
            const response = await fetch("graphql", {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ query: "query { qed { archives { uri readers } } }" }),
            })
            // decode the answer
            const { data } = await response.json()
            // and pick out the scratch archive
            return data.qed.archives.find(archive => archive.uri === uri).readers
        }, uri)
        // the local archive offers several
        expect(readers.length).toBeGreaterThan(1)
        // collect the answers of the server to the requests for a nickname; types that share a
        // family share its answer, so not every choice sends one
        const answers: Promise<any>[] = []
        page.on("response", response => {
            // the requests for a nickname name their query
            if (response.request().postData()?.includes("useFetchNicknameQuery")) {
                // keep the answer
                answers.push(response.json())
            }
        })
        // the form of a type shows up only once the answer for its family is in hand: either
        // the nickname field, or the report that the scratch file is not that kind of product
        const form = page.getByRole("textbox", { name: "nickname" })
            .or(page.getByText(/does not appear to be/))
        // go through the types
        for (const reader of readers) {
            // one step per type, so a failure names it
            await test.step(`the '${reader}' reader`, async () => {
                // pick the type
                await page.getByText(reader, { exact: true }).click()
                // and wait for its form
                await expect(form).toBeVisible()
            })
        }
        // every type asked about a family
        expect(answers.length).toBeGreaterThan(0)
        // and the server knew each one, and suggested a name for it
        for (const body of await Promise.all(answers)) {
            expect(body.errors).toBeUndefined()
            expect(body.data.nickname).not.toBe("")
        }
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
