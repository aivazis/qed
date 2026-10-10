// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// local
// the views
import { FlatFactory } from './flat/factory'
import { FlatSlot } from './flat/slot'
import { IsoFactory } from './iso/factory'
import { IsoSlot } from './iso/slot'


// the components that draw a factory and a slot, by the name of the projection in use; each
// takes the plain state of its node, so the data layer stays the same for every view
export const glyphs = {
    flat: { Factory: FlatFactory, Slot: FlatSlot },
    iso: { Factory: IsoFactory, Slot: IsoSlot },
}


// end of file
