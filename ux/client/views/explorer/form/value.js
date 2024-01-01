// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import styled from 'styled-components'


// a container for enum selectors
export const Values = styled.td`
    font-family: "inconsolata";
    text-align: left;
`

// base field value
export const Value = styled.td`
    font-family: "inconsolata";
    text-align: left;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
`

// active
export const EnabledValue = styled(Value)`
    & {
        cursor: pointer;
        color: hsl(0deg, 0%, 60%);
    }

    &:hover {
        color: hsl(28deg, 90%, 55%);
    }
`


// end of file
