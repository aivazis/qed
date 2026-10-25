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

// the name of the archive, which starts out as the server's {suggestion}
export const Name = ({ value, suggestion = "", update }) => (
    <Nickname value={value} suggestion={suggestion} update={update} pattern={pattern}
        tip="the name of the data archive" />
)


// the names an archive can have
const pattern = /^[\w_]?[\w\d@$()_-]*$/


// end of file
