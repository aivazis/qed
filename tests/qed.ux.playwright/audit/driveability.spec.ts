// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import { test } from "@playwright/test"
import type { Page } from "@playwright/test"


// a LIVE DRIVEABILITY AUDIT, not a gate. it sweeps routes AND states the coverage gate never sees
// (measure on, split viewports, the NISAR reader on its own server) and reports, per scenario, every
// interactive element a driver could not address: no stable handle at all (a findability gap), or a
// handle shared by other controls (an ambiguity that cannot pick one out). it always passes; the
// value is the printed report. run with: QED_PORT/QED_PORT_NISAR matching the servers under test.

const nisarBaseURL = process.env.QED_URL_NISAR ?? `http://localhost:${process.env.QED_PORT_NISAR ?? 8138}`

// drive a GraphQL mutation/query from inside the page, the way the client does
const gql = (page: Page, query: string) =>
    page.evaluate(async (q) => {
        const r = await fetch("/graphql", {
            method: "POST", headers: { "content-type": "application/json" },
            body: JSON.stringify({ query: q }),
        })
        return r.json()
    }, query)

// the audit body runs entirely in the page; it returns a list of human-readable problem lines
const audit = (): { gaps: string[]; ambiguous: string[]; total: number } => {
    // an element is an interactive candidate if it is a native control or shows a pointer cursor
    const NATIVE = ["BUTTON", "INPUT", "SELECT", "TEXTAREA", "SUMMARY", "A"]
    // the aria roles that mark a self-contained control; a driver targets the control, not the SVG
    // leaves or labels nested inside it, so those internals are not separate candidates
    const CONTROL_ROLES = ["button", "link", "slider", "radio", "switch", "tab", "checkbox", "option"]
    const isInternal = (el: Element): boolean => {
        for (let n = el.parentElement, h = 0; n && h < 6; n = n.parentElement, ++h) {
            if (NATIVE.includes(n.tagName)) return true
            const r = n.getAttribute("role")
            if (r && CONTROL_ROLES.includes(r)) return true
            // a leaf-level client identity (a marker, a selector value) is itself the control
            if (n.hasAttribute("data-qed-marker-index") || n.hasAttribute("data-qed-value")) return true
        }
        return false
    }
    const isCandidate = (el: Element): boolean => {
        if (el.closest('[aria-hidden="true"]')) return false
        if (isInternal(el)) return false
        if (NATIVE.includes(el.tagName)) return el.tagName !== "A" || el.hasAttribute("href")
        return window.getComputedStyle(el).cursor === "pointer"
    }

    // climb a few hops accumulating every client identity (data-qed-*) the element sits under -- its
    // own (e.g. data-qed-action) AND its scope (e.g. data-qed-viewport on the panel) -- and note any
    // widget marking, which is itself a usable selector
    const scope = (el: Element): { ids: string[]; widget: boolean } => {
        const ids: string[] = []
        let widget = false
        // climb generously: a per-viewport control (a detail toggle) sits many levels below the panel
        // that carries its data-qed-viewport scope, and that scope is what disambiguates it
        for (let n: Element | null = el, h = 0; n && h < 10; n = n.parentElement, ++h) {
            for (const a of n.getAttributeNames()) {
                if (a.startsWith("data-qed")) ids.push(`${a}=${n.getAttribute(a)}`)
                if (a.startsWith("data-pyre-widget")) widget = true
            }
        }
        return { ids: [...new Set(ids)].sort(), widget }
    }
    // the accessible name a driver would use with getByRole
    const nameOf = (el: Element): string =>
        (el.getAttribute("aria-label")
            ?? (el as HTMLInputElement).placeholder
            ?? el.getAttribute("title")
            ?? el.textContent
            ?? "").trim().slice(0, 40)
    const roleOf = (el: Element): string => el.getAttribute("role")
        ?? (el.tagName === "A" ? "link" : el.tagName === "INPUT" ? "textbox" : el.tagName.toLowerCase())

    // a driver can ADDRESS an element if it carries client identity, a widget marking, or a role (or
    // native interactivity) plus an accessible name; otherwise it is a findability gap. two addressable
    // elements that share a full signature are AMBIGUOUS -- the driver cannot tell them apart
    const candidates = [...document.querySelectorAll("*")].filter(isCandidate)
    const rows = candidates.map(el => {
        const { ids, widget } = scope(el)
        const name = nameOf(el)
        const native = NATIVE.includes(el.tagName)
        const addressable = ids.length > 0 || widget || ((!!el.getAttribute("role") || native) && name.length > 0)
        return { el, addressable, sig: `${ids.join(" ")} | role=${roleOf(el)} | name=${name}` }
    })

    const gaps: string[] = []
    const counts = new Map<string, number>()
    for (const r of rows) {
        if (!r.addressable) gaps.push(`<${r.el.tagName.toLowerCase()}> -- no identity, no role+name`)
        else counts.set(r.sig, (counts.get(r.sig) ?? 0) + 1)
    }
    const seen = new Set<string>()
    const ambiguous: string[] = []
    for (const r of rows) {
        if (r.addressable && (counts.get(r.sig) ?? 0) > 1 && !seen.has(r.sig)) {
            seen.add(r.sig)
            ambiguous.push(`x${counts.get(r.sig)}  ${r.sig}`)
        }
    }
    return { gaps, ambiguous, total: candidates.length }
}

// report one scenario
const report = async (page: Page, label: string) => {
    const { gaps, ambiguous, total } = await page.evaluate(audit)
    const lines = [`\n=== ${label} === (${total} interactive candidates)`]
    lines.push(gaps.length ? `  FINDABILITY GAPS (${gaps.length}):` : `  findability: OK`)
    gaps.forEach(g => lines.push(`    - ${g}`))
    if (ambiguous.length) {
        lines.push(`  AMBIGUOUS HANDLES (${ambiguous.length} signatures shared by >1 control):`)
        ambiguous.forEach(a => lines.push(`    - ${a}`))
    }
    console.log(lines.join("\n"))
}


test("driveability audit across routes and states", async ({ page }) => {
    test.setTimeout(120_000)

    // baseline routes -- the same four the coverage gate sweeps
    for (const route of ["/", "/controls", "/explore", "/doc"]) {
        await page.goto(route, { waitUntil: "networkidle" })
        await report(page, `native ${route}`)
    }

    // STATE: the measure layer on, with a couple of anchors -- exposes the measure panel, the peek
    // pad, and the on-raster markers, none of which the gate's default render shows
    await page.goto("/controls", { waitUntil: "networkidle" })
    await gql(page, `mutation { viewMeasureReset(input: {viewport: 0}) { measures { dirty } } }`)
    await gql(page, `mutation { viewMeasureAnchorAdd(input: {viewport: 0, x: 120, y: 240, index: null}) { measures { dirty } } }`)
    await gql(page, `mutation { viewMeasureAnchorAdd(input: {viewport: 0, x: 180, y: 300, index: null}) { measures { dirty } } }`)
    const measure = page.locator('[data-qed-control="viewport"][data-qed-action="measure"]').first()
    if ((await measure.getAttribute("aria-pressed")) !== "true") await measure.click()
    await page.waitForTimeout(500)
    await report(page, "native /controls + measure layer on, 2 anchors")

    // STATE: the viewport split in two -- a second viewport mounts with its own action row + panels
    const split = page.locator('[data-qed-control="viewport"][data-qed-action="split"]').first()
    await split.click()
    await page.waitForTimeout(500)
    await report(page, "native /controls + split (2 viewports)")
    // restore: collapse the split and clear the measure layer
    await split.click()
    if ((await measure.getAttribute("aria-pressed")) === "true") await measure.click()
    await gql(page, `mutation { viewMeasureReset(input: {viewport: 0}) { measures { dirty } } }`)

    // STATE: the NISAR reader on its own server -- the band/frequency/polarization selectors
    await page.goto(`${nisarBaseURL}/`, { waitUntil: "networkidle" })
    await report(page, "nisar / (reader selectors)")
})


/* end of file */
