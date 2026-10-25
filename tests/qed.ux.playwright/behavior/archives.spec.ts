// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the archive trays follow the tree the server keeps: expanding through the facade opens the
// archive's tray and shows its folders as trays of their own, and collapsing closes it; the edit
// control of a tray brings up the form that moves its archive, which keeps its name; a new
// archive is offered a name made from where it is

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
        const location = page.getByLabel("path", { exact: true })
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

    test("the edit button replaces the query of an earth access archive", async ({ page }) => {
        // send a graphql document to the server under test
        const gql = (query: string, variables = {}) => page.evaluate(async ([query, variables]) => {
            const response = await fetch("/graphql", {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ query, variables }),
            })
            return (await response.json()).data
        }, [query, variables] as const)
        await page.goto("/explore", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // an archive of the granules of a collection around a point; connecting runs no query
        const uri = "earth:spec_earth"
        await gql(`mutation ($input: ConnectEarthAccessArchiveInput!) {
            connectEarthAccessArchive(input: $input) { archive { name } } }`, {
            input: {
                name: uri, uri, count: "10",
                collection: { shortName: "NISAR_L2_GCOV_BETA_V1", conceptId: "" },
                filters: ["geo"], geo: "point", point: { longitude: "-118.5", latitude: "34.25" },
            },
        })
        // its tray shows up
        await page.reload({ waitUntil: "load" })
        // its edit control brings up the form, filled in with its query
        await tray(page, uri).getByLabel("edit this archive").click()
        await expect(page.getByLabel("collection short name")).toHaveValue("NISAR_L2_GCOV_BETA_V1")
        await expect(page.getByLabel("Count", { exact: true })).toHaveValue("10")
        await expect(page.getByLabel("longitude")).toHaveValue("-118.5")
        await expect(page.getByLabel("latitude")).toHaveValue("34.25")
        // pick another collection and send it
        await page.getByLabel("collection short name").fill("NISAR_L2_GUNW_BETA_V1")
        await page.getByText("update", { exact: true }).click()
        await expect(page.getByText("update", { exact: true })).toHaveCount(0)
        // the archive keeps its name and its point, and searches the new collection
        const data = await gql("query { qed { archives { name earth { collection point } } } }")
        expect(data.qed.archives.filter(archive => archive.name === uri)).toEqual([
            { name: uri, earth: { collection: "NISAR_L2_GUNW_BETA_V1", point: [-118.5, 34.25] } },
        ])
        // clean up the server
        await page.evaluate(uri => window.qed.disconnectArchive(uri), uri)
        await expect(tray(page, uri)).toHaveCount(0)
    })

    test("a new local archive takes the name of its folder, which can be cleared and put back", async ({ page }) => {
        // a folder whose name no archive holds
        const folder = path.join(root, "suggested_folder")
        fs.mkdirSync(folder)
        await page.goto("/explore", { waitUntil: "load" })
        await page.waitForFunction(() => Boolean(window.qed))
        // bring up the form for a new archive, and pick a local one
        await page.getByLabel("connect to this archive").click()
        await page.getByText("local", { exact: true }).click()
        // name the folder; the nickname field takes its name
        await page.getByLabel("path", { exact: true }).fill(folder)
        const nickname = page.getByLabel("nickname", { exact: true })
        await expect(nickname).toHaveValue("suggested_folder")
        // the field can be cleared
        await page.getByLabel("clear the nickname").click()
        await expect(nickname).toHaveValue("")
        // and the suggestion put back
        await page.getByLabel("use the suggested nickname").click()
        await expect(nickname).toHaveValue("suggested_folder")
        // connecting without typing a name takes the suggestion
        await page.getByText("connect", { exact: true }).click()
        await expect(tray(page, "local:suggested_folder")).toHaveCount(1)
        // under that name, at the folder
        const archives = await page.evaluate(() => window.qed.archives())
        expect(archives.filter(archive => archive.name === "local:suggested_folder")
            .map(archive => archive.uri)).toEqual([`file:${folder}`])
        // clean up the server
        await page.evaluate(uri => window.qed.disconnectArchive(uri), `file:${folder}`)
        await expect(tray(page, "local:suggested_folder")).toHaveCount(0)
    })
})


// end of file
