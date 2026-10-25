// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'

// local
// components
import { Nickname } from '../form'


// the name of the reader; the server's {suggestion} is its initial value, and shows dimmed when
// the field is empty
export const Name = ({ value, suggestion, update }) => (
    <Nickname value={value} suggestion={suggestion} update={update} pattern={pattern}
        tip="the name of the data reader component" />
)


// the names a reader can have
const pattern = /^[\w_]?[\w\d@$()_.-]*$/


// end of file
