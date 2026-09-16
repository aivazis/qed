// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// the archive tree at the model level: a spec owns a scratch directory on the server's host,
// connects it as a local archive, and drives the tree through {window.qed} -- expanding lists a
// folder, a change on disk shows only after a refresh, collapsing forgets the subtree, and
// disconnecting takes the archive away. nothing here reads the DOM

import { test, expect } from "@playwright/test"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"

// the tree: a root with a file and a folder that holds a file
const root = fs.mkdtempSync(path.join(os.tmpdir(), "qed-archive-"))
fs.writeFileSync(path.join(root, "top.dat"), "")
fs.mkdirSync(path.join(root, "nested"))
fs.writeFileSync(path.join(root, "nested", "inner.dat"), "")
// the archive: its uri is what the mutations address it by
const uri = `file:${root}`
const name = "spec_archive"

// the entries of {folder} in the tree the server reports for our archive, by name
const entries = async (page, folder: string) => page.evaluate(async ([uri, folder]) => {
    const archive = (await window.qed.archives()).find(archive => archive.uri === uri)
    return archive ? archive.items.filter(item => item.parent === folder).map(item => item.name).sort() : null
}, [uri, folder])

test.describe.serial("the automation surface drives the archive tree", () => {
    test.afterAll(() => fs.rmSync(root, { recursive: true, force: true }))

    test("connecting an archive adds it to the catalog, collapsed", async ({ page }) => {
        await page.goto("/explore", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        await page.evaluate(([name, uri]) => window.qed.connectArchive(name, uri), [name, uri])
        const archive = await page.evaluate(
            async uri => (await window.qed.archives()).find(archive => archive.uri === uri), uri)
        expect(archive).toMatchObject({ name, uri, expanded: false, pending: false, error: null, items: [] })
    })

    test("expanding the root lists it, and expanding a folder lists that folder", async ({ page }) => {
        await page.goto("/explore", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // expand the root; the listing may run on a worker, so poll until it lands
        await page.evaluate(uri => window.qed.expandFolder(uri), uri)
        await expect.poll(() => entries(page, uri)).toEqual(["nested", "top.dat"])
        // the folder is reported collapsed, and is a folder
        const nested = await page.evaluate(async uri => (await window.qed.archives())
            .find(archive => archive.uri === uri)!.items.find(item => item.name === "nested"), uri)
        expect(nested).toMatchObject({ isFolder: true, expanded: false, pending: false })
        // expand it
        await page.evaluate(([uri, folder]) => window.qed.expandFolder(uri, folder), [uri, nested!.uri])
        await expect.poll(() => entries(page, nested!.uri)).toEqual(["inner.dat"])
    })

    test("a change on disk shows only after a refresh", async ({ page }) => {
        await page.goto("/explore", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // add a file
        fs.writeFileSync(path.join(root, "nested", "later.dat"), "")
        // the folder, as the tree addresses it: by its resolved location, which may differ from
        // the spelling of the archive's root through a symbolic link
        const folder = await page.evaluate(async uri => (await window.qed.archives())
            .find(archive => archive.uri === uri)!.items.find(item => item.name === "nested")!.uri, uri)
        // the listing is as it was
        expect(await entries(page, folder)).toEqual(["inner.dat"])
        // refresh
        await page.evaluate(uri => window.qed.refreshArchive(uri), uri)
        await expect.poll(() => entries(page, folder)).toEqual(["inner.dat", "later.dat"])
    })

    test("collapsing the root forgets the subtree, and disconnecting removes the archive", async ({ page }) => {
        await page.goto("/explore", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        await page.evaluate(uri => window.qed.collapseFolder(uri), uri)
        const collapsed = await page.evaluate(
            async uri => (await window.qed.archives()).find(archive => archive.uri === uri), uri)
        expect(collapsed).toMatchObject({ expanded: false, items: [] })
        await page.evaluate(uri => window.qed.disconnectArchive(uri), uri)
        const remaining = await page.evaluate(async () => (await window.qed.archives()).map(archive => archive.uri))
        expect(remaining).not.toContain(uri)
    })
})

// end of file
