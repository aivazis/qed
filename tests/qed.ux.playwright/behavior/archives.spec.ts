// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// the archive trays follow the tree the server keeps: expanding through the facade opens the
// archive's tray and shows its folders as trays of their own, and collapsing closes it

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
})

// end of file
