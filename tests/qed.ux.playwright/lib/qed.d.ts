// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// ambient typing for the {window.qed} automation facade (doc/automation-surface.md), so specs and
// agents that drive the app through it get completion. coordinates are row-major source pixels

type QEDViewModel = {
    viewport: number
    reader: string | null
    dataset: { shape: number[], origin: number[], channels: string[] } | null
    channel: string | null
    selectors: Record<string, string[]>
    zoom: { vertical: number, horizontal: number, coupled: boolean } | null
    measure: { active: boolean, closed: boolean, path: { row: number, col: number }[], selection: number[] } | null
    sync: { scroll: boolean, channel: boolean, zoom: boolean, path: boolean } | null
}

interface QED {
    // queries
    state(viewport?: number): Promise<QEDViewModel | null>
    viewports(): Promise<QEDViewModel[]>
    readers(): Promise<{ name: string, selectors: Record<string, string[]> }[]>
    controllers(viewport?: number): Promise<{ kind: string, slot: string, min: number, max: number }[]>
    // commands
    setActive(viewport: number): void
    centerOn(row: number, col: number, viewport?: number): Promise<void>
    split(viewport?: number): Promise<unknown>
    collapse(viewport?: number): Promise<unknown>
    selectReader(reader: string, viewport?: number): Promise<unknown>
    selectValue(selector: string, value: string, viewport?: number): Promise<unknown>
    setChannel(tag: string, viewport?: number): Promise<unknown>
    setZoom(level: number | { vertical: number, horizontal: number }, viewport?: number): Promise<unknown>
    toggleCoupled(viewport?: number): Promise<unknown>
    zoomReset(viewport?: number): Promise<unknown>
    measure: {
        toggle(viewport?: number): Promise<unknown>
        reset(viewport?: number): Promise<unknown>
        add(row: number, col: number, index?: number | null, viewport?: number): Promise<unknown>
        move(handle: number, row: number, col: number, viewport?: number): Promise<unknown>
        split(handle: number, viewport?: number): Promise<unknown>
        remove(handle: number, viewport?: number): Promise<unknown>
        toggleClosedPath(viewport?: number): Promise<unknown>
        toggleSelection(handle: number, viewport?: number): Promise<unknown>
        toggleSelectionMulti(handle: number, viewport?: number): Promise<unknown>
        extendSelection(handle: number, viewport?: number): Promise<unknown>
    }
    sync: {
        toggle(aspect: string, viewport?: number): Promise<unknown>
        toggleAll(aspect: string, viewport?: number): Promise<unknown>
        updateOffset(row: number, col: number, viewport?: number): Promise<unknown>
        reset(viewport?: number): Promise<unknown>
    }
    range: {
        update(controller: string, bounds: { min: number, low: number, high: number, max: number }, channel?: string, viewport?: number): Promise<unknown>
        reset(controller: string, channel?: string, viewport?: number): Promise<unknown>
    }
    value: {
        update(controller: string, bounds: { min: number, value: number, max: number }, channel?: string, viewport?: number): Promise<unknown>
        reset(controller: string, channel?: string, viewport?: number): Promise<unknown>
    }
}

interface Window {
    qed: QED
}

/* end of file */
