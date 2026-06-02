// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { defineConfig, devices } from "@playwright/test"


// the port the server under test listens on; a dedicated test port, overridable so parallel
// suites do not collide, and passed through to {qed} on the command line below
const port = Number(process.env.QED_PORT ?? 8137)
// the base url; the {webServer} below brings the server up, but an existing one can be reused
// (or pointed at) via {QED_URL}
const baseURL = process.env.QED_URL ?? `http://localhost:${port}`
// the shared, generated test-data directory holding {qed.yaml} and the fixture raster; mm injects
// it (the qed.data step produces it). the fallback lets the suite run by hand from its source tree
const dataDir = process.env.QED_DATA_NATIVE ?? "../data/native"


// the qed.ux suite drives the built client in a headless browser to enforce the semantic-markup
// convention (doc/semantic-markup.md). playwright owns discovery, parallelism, and -- via the
// {webServer} block -- the isolated qed server the specs run against.
export default defineConfig({
    // the specs live alongside this config
    testDir: ".",
    // fail the run if a spec is accidentally left focused
    forbidOnly: !!process.env.CI,
    // the suite is read-only against a server it owns, so it is safe to parallelize
    fullyParallel: true,
    // one line per spec; silence-on-pass in spirit
    reporter: [["list"]],

    use: {
        // every {page.goto} and {request} call is relative to the server under test
        baseURL,
        // collect a trace on first retry to debug flakes
        trace: "on-first-retry",
    },

    projects: [
        // a one-shot setup that selects a channel so a Mosaic (and the zoom slider) renders for
        // the read-only specs; without it the viewport is an empty shell and the gate is vacuous
        { name: "setup", testMatch: /.*\.setup\.ts/, use: { ...devices["Desktop Chrome"] } },
        // the gate: the grammar and widget-aria checks must pass
        {
            name: "gate",
            testMatch: [/identity\/.*\.spec\.ts/, /aria\/widgets\.spec\.ts/],
            dependencies: ["setup"],
            use: { ...devices["Desktop Chrome"] },
        },
        // the backlog: the coverage check tracks the rollout TODO and is expected to fail; it is
        // excluded from the gate (run it explicitly with {--project=backlog})
        {
            name: "backlog",
            testMatch: /aria\/coverage\.spec\.ts/,
            dependencies: ["setup"],
            use: { ...devices["Desktop Chrome"] },
        },
    ],

    // bring up an isolated qed server on the shared generated dataset; the installed {qed} command
    // reads {qed.yaml} from {dataDir} and we override its port on the command line
    webServer: {
        command: `qed --qed.app.nexus.services.web.address=ip4:0.0.0.0:${port}`,
        cwd: dataDir,
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
        stdout: "ignore",
        stderr: "pipe",
    },
})


/* end of file */
