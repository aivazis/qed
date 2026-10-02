# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections
import os

# support
import qed


def lists(*, scrape: str) -> list:
    """
    The products a {scrape} has lists for, named after the files that hold them
    """
    # the files whose names end in {.txt}, without the ending, in order
    return sorted(name[:-4] for name in os.listdir(scrape) if name.endswith(".txt"))


def granules(*, scrape: str, product: str):
    """
    Generate the (granule, cycle) pairs of the list of {product} in {scrape}; a granule without a
    repeat cycle, either because the parser does not recognize it or because its product has none,
    e.g. a stream of raw telemetry, comes with a cycle of {None}
    """
    # the parser
    registrar = qed.readers.nisar.daac.registrar()
    # go through the list
    with open(os.path.join(scrape, f"{product}.txt")) as stream:
        # one granule id per line
        for line in stream:
            # clean it up
            granule = line.strip()
            # skip blank lines
            if not granule:
                # by moving on
                continue
            # sift it by its raw fields, which is cheap
            fields = registrar.fields(granule)
            # an id the parser does not recognize
            if fields is None:
                # has no cycle
                yield granule, None
                # and nothing more to say
                continue
            # the cycle, which for a pair is the one of its reference acquisition
            cycle = fields.get("cycle") or fields.get("referenceCycle")
            # hand off the granule and its cycle, if its product has one
            yield granule, None if cycle is None else int(cycle)
    # all done
    return


def cycles(*, scrape: str, products: list) -> dict:
    """
    Count the granules of each of {products} in {scrape} by repeat cycle, with the ids that have no
    cycle, the ones the parser does not recognize and the ones of products without one, counted
    under {None}
    """
    # the counts, by product
    return {
        product: collections.Counter(cycle for _, cycle in granules(scrape=scrape, product=product))
        for product in products
    }


def complete(*, counts: dict) -> list:
    """
    The cycles for which every product in {counts} has granules; a product with no cycles at all,
    e.g. a stream of raw telemetry, has no say
    """
    # the cycles each product has
    cycles = [set(cycle for cycle in tally if cycle is not None) for tally in counts.values()]
    # the products that have any
    known = [held for held in cycles if held]
    # the ones they all have, in order
    return sorted(set.intersection(*known)) if known else []


def spread(*, scrape: str, product: str, cycle: int, count: int) -> list:
    """
    Pick {count} granules of {product} in {cycle} from {scrape}, spread evenly over the ones on
    offer in the order of their ids, which is the order of their tracks and frames
    """
    # the granules of the cycle
    pile = sorted(granule for granule, c in granules(scrape=scrape, product=product) if c == cycle)
    # with no more than asked for
    if len(pile) <= count:
        # take them all
        return pile
    # with one asked for
    if count == 1:
        # take the one in the middle
        return [pile[len(pile) // 2]]
    # otherwise, stride through the pile
    return [pile[round(i * (len(pile) - 1) / (count - 1))] for i in range(count)]


# end of file
