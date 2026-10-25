// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the archive trays follow the tree the server keeps: expanding through the facade opens the
// archive's tray and shows its folders as trays of their own, and collapsing closes it; the edit
// control of a tray brings up the form that moves its archive, which keeps its name

import { test, expect } from "@playwright/test"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"

// a scratch tree with one folder
const root = fs.mkdtempSync(path.join(os.tmpdir(), "qed-tray-"))
fs.mkdirSync(path.join(root, "folder"))
const uri = `file:${root}`
const name = "tray_archive"

// the header of the tray labeled {label}
const tray = (page, label: string) => page.locator(`[data-qed-control="tray"][aria-label="${label}"]`).first()

test.describe.serial("the archive trays follow the server", () => {
    test.afterAll(() => fs.rmSync(root, { recursive: true, force: true }))

    test("expanding and collapsing through the facade moves the trays", async ({ page }) => {
        await page.goto("/explore", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // connect the archive; its tray appears, collapsed
        await page.evaluate(([name, uri]) => window.qed.connectArchive(name, uri), [name, uri])
        await expect(tray(page, name)).toHaveAttribute("aria-expanded", "false")
        // expand the root; the tray opens and the folder shows up as a tray of its own, collapsed
        await page.evaluate(uri => window.qed.expandFolder(uri), uri)
        await expect(tray(page, name)).toHaveAttribute("aria-expanded", "true")
        await expect(tray(page, "folder")).toHaveAttribute("aria-expanded", "false")
        // the archive header carries the refresh control
        await expect(page.locator('[aria-label="refresh this archive"]').first()).toBeVisible()
        // collapse the root; the folder tray goes away
        await page.evaluate(uri => window.qed.collapseFolder(uri), uri)
        await expect(tray(page, name)).toHaveAttribute("aria-expanded", "false")
        await expect(tray(page, "folder")).toHaveCount(0)
        // clean up the server
        await page.evaluate(uri => window.qed.disconnectArchive(uri), uri)
        await expect(tray(page, name)).toHaveCount(0)
    })

    test("the edit button moves an archive to a corrected location, keeping its name", async ({ page }) => {
        // an archive connected at a misspelled location
        const misspelled = `file:${root}/fodler`
        const corrected = `file:${root}/folder`
        const edited = "edited_archive"
        await page.goto("/explore", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        await page.evaluate(([name, uri]) => window.qed.connectArchive(name, uri), [edited, misspelled])
        // its header carries the edit control, which brings up the form, filled in
        await tray(page, edited).getByLabel("edit this archive").click()
        await expect(page.getByText("edit archive", { exact: true })).toBeVisible()
        const location = page.locator("input").last()
        await expect(location).toHaveValue(`${root}/fodler`)
        // the nickname shows, but takes no input
        await expect(page.getByText(edited, { exact: true }).last()).toBeVisible()
        // correct the location and send it
        await location.fill(`${root}/folder`)
        await page.getByText("update", { exact: true }).click()
        // the form goes away, and the archive is at the corrected location, under the same name
        await expect(page.getByText("update", { exact: true })).toHaveCount(0)
        const archives = await page.evaluate(() => window.qed.archives())
        const found = archives.filter(archive => archive.name === edited)
        expect(found.map(archive => archive.uri)).toEqual([corrected])
        // its tray stays
        await expect(tray(page, edited)).toHaveCount(1)
        // clean up the server
        await page.evaluate(uri => window.qed.disconnectArchive(uri), corrected)
        await expect(tray(page, edited)).toHaveCount(0)
    })
})


// end of file
