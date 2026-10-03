// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
import { ErrorBoundary } from '~/boundary'

// locals
// hooks
import { useCollapseViewport } from '../explorer/useCollapseViewport'
import { useNicknameLoader, useQueryNickname } from './useFetchNickname'
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
    // preload the suggestion for the reader name
    const [qref, getNickname] = useNicknameLoader()
    // ask for it once, at mount time; it does not depend on the reader type
    React.useEffect(() => {
        // the dataset whose reader needs a name
        const variables = { archive: view.reader.archive, uri: view.reader.uri }
        // ask the server every time, since the names in use change as readers connect
        const options = { fetchPolicy: "network-only" }
        // fetch
        getNickname(variables, options)
        // all done
        return
    }, [])
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
    // if the suggestion has not been requested yet
    if (qref === null) {
        // bail
        return
    }
    // otherwise, resolve the connector
    const Connector = types[type]
    // a server that cannot suggest a name leaves the user to type one, as before there were
    // suggestions
    const fallback = <Connector view={view} nickname="" setType={update} hide={hide} />
    // render the connector with the suggested name in hand
    return (
        <ErrorBoundary fallback={fallback}>
            <Suggested qref={qref} Connector={Connector} view={view} setType={update} hide={hide} />
        </ErrorBoundary>
    )
}


// the connector of the selected reader type, seeded with the suggested name
const Suggested = ({ qref, Connector, view, setType, hide }) => {
    // get the name the server suggests
    const nickname = useQueryNickname(qref)
    // and render the connector with it
    return (
        <Connector view={view} nickname={nickname} setType={setType} hide={hide} />
    )
}


// the dispatch table with the reader types
const types = {
    gdal: GDAL,
    isce2: ISCE2,
    native: Native,
    nisar: NISAR,
}


// end of file
