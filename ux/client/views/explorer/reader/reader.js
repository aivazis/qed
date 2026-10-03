// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useCollapseViewport } from '../explorer/useCollapseViewport'
import { useFetchNickname } from './useFetchNickname'
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect } from './buttons'
import { Type } from './type'
import { Form, Body } from '../form'
// reader types
import { GDAL } from './gdal'
import { ISCE2 } from './isce2'
import { Native } from './native'
import { NISAR } from './nisar'


// the form
export const Reader = ({ view, viewport }) => {
    // get the supported readers
    const supported = view.reader.readers
    // make room for the reader type
    const [type, setType] = React.useState(supported.length == 1 ? supported[0] : null)
    // make a handler that collapses this viewport
    const hide = useCollapseViewport(viewport)
    // ask for a name for the reader whenever the user picks a reader type, since each product
    // family names its products in its own way
    const suggestion = useFetchNickname({
        archive: view.reader.archive, uri: view.reader.uri, module: modules[type] ?? null
    })
    // build a selector with the generic signature
    const update = (field, value) => {
        // set the type
        setType(value)
        // all done
        return
    }
    // build a handler that removes the form from view
    const cancel = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // remove the form from view
        hide()
        // all done
        return
    }
    // if we don't have a type selection yet
    if (type === null) {
        // render
        return (
            <Panel>
                <Form>
                    <Body>
                        <Type value={type} update={update} readers={supported} />
                    </Body>
                </Form>
                <DisabledConnect />
                <Cancel onClick={cancel}>cancel</Cancel>
            </Panel>
        )
    }
    // if the answer for this type has not arrived yet
    if (suggestion === null) {
        // bail
        return
    }
    // otherwise, resolve the connector
    const Connector = types[type]
    // and render it with the suggested name, or with the reason there is none
    return (
        <Connector view={view}
            nickname={suggestion.nickname} nicknameError={suggestion.error}
            setType={update} hide={hide} />
    )
}


// the dispatch table with the reader types
const types = {
    gdal: GDAL,
    isce2: ISCE2,
    native: Native,
    nisar: NISAR,
}

// the packages of the product families, which know how to name their products
const modules = {
    gdal: "qed.readers.native",
    isce2: "qed.readers.isce2",
    native: "qed.readers.native",
    nisar: "qed.readers.nisar",
}


// end of file
