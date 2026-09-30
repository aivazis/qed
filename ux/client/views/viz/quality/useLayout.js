// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// the layout of {dataset}: fetched once, since the layout of a product does not change while it
// is connected, and read from the store afterwards
export const useLayout = dataset => {
    // fetch
    const { layout } = useLazyLoadQuery(
        // the query
        layoutQuery,
        // the dataset
        { dataset },
        // the store, if it has it, and the server otherwise
        { fetchPolicy: "store-or-network" }
    )
    // hand it off
    return layout
}


// the query
const layoutQuery = graphql`
    query useLayoutQuery($dataset: String!) {
        layout(dataset: $dataset) {
            dataset
            strategy
            pageSize
            fileBytes
            shape
            tile
            cell
            filters
            summary {
                grid
                written
                stored
                raw
                compression
                empty
                emptyStored
                pages
                emptyPages
                alone
                once
                joint
                fillMean
                totalMean
                locality
                sizes
                fill
            }
            fill {
                status
                hdf5
                cf
                holds
                agrees
                chunks
                bytes
                level
                decodeMs
                makeMs
                encodeMs
                dataDecodeMs
            }
            grid {
                rows
                cols
                states
                codes
                sizes
                pages
            }
            strip {
                pages
                mine
                chunks
                others
                partner
                partnerBytes
            }
            filemap {
                pages
                rasters {
                    name
                    bytes
                    chunks
                }
                selected
                others
            }
            census {
                census
                product
                cycle
                kind
                rasters
                granules
                measures {
                    name
                    label
                    lower
                    value
                    count
                    p10
                    median
                    p90
                    max
                    low
                    high
                    bins
                }
            }
        }
    }
`


// end of file
