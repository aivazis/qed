# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# support
import qed

# my parts
from .LayoutCensus import LayoutCensus
from .LayoutFileMap import LayoutFileMap
from .LayoutFill import LayoutFill
from .LayoutGrid import LayoutGrid
from .LayoutPartner import LayoutPartner
from .LayoutStrip import LayoutStrip
from .LayoutSummary import LayoutSummary


# how a raster sits in its file
class Layout(graphene.ObjectType):
    """
    How a raster sits in its file: the storage settings, how its chunks sit on the pages of the
    file, what it holds where there is no data, the states of the cells of its chunk grid, and
    what every page of the file holds
    """

    # the name of the raster
    dataset = graphene.String(required=True)
    # the file: its file space strategy, its page size, zero when it is not paged, and its size
    strategy = graphene.String()
    pageSize = graphene.Int(required=True)
    fileBytes = graphene.Float()
    # the raster: its shape, the shape of its chunks, its cells, and the filters of its chunks
    shape = graphene.List(graphene.NonNull(graphene.Int), required=True)
    tile = graphene.List(graphene.NonNull(graphene.Int), required=True)
    cell = graphene.String(required=True)
    filters = graphene.List(graphene.NonNull(graphene.String), required=True)
    # how its chunks sit on the pages
    summary = graphene.Field(LayoutSummary, required=True)
    # the datasets that share its pages
    partners = graphene.List(graphene.NonNull(LayoutPartner), required=True)
    # what it holds where there is no data
    fill = graphene.Field(LayoutFill, required=True)
    # the states of the cells of its chunk grid
    grid = graphene.Field(LayoutGrid, required=True)
    # the pages its chunks land on, when the file is paged
    strip = graphene.Field(LayoutStrip)
    # what every page of the file holds, when the file is paged
    filemap = graphene.Field(LayoutFileMap)
    # the census of its kind of product, when there is one to compare against
    census = graphene.Field(LayoutCensus)

    # the resolvers
    @staticmethod
    def resolve_dataset(described, *_):
        """
        The name of the raster
        """
        # easy enough
        return described["name"]

    @staticmethod
    def resolve_strategy(described, *_):
        """
        The file space strategy of the file
        """
        # from its storage settings
        return described["storage"]["strategy"]

    @staticmethod
    def resolve_pageSize(described, *_):
        """
        The page size of the file, zero when it is not paged
        """
        # from the record
        return described["record"]["pageSize"] or 0

    @staticmethod
    def resolve_fileBytes(described, *_):
        """
        The size of the file
        """
        # from its storage settings
        return described["storage"]["bytes"]

    @staticmethod
    def resolve_shape(described, *_):
        """
        The shape of the raster
        """
        # from its storage settings
        return described["storage"]["shape"]

    @staticmethod
    def resolve_tile(described, *_):
        """
        The shape of its chunks
        """
        # from its storage settings
        return described["storage"]["tile"]

    @staticmethod
    def resolve_cell(described, *_):
        """
        The type of its cells
        """
        # from its storage settings
        return described["storage"]["cell"]

    @staticmethod
    def resolve_filters(described, *_):
        """
        The filters its chunks pass through, in the order they are applied
        """
        # from its storage settings
        return described["storage"]["filters"]

    @staticmethod
    def resolve_summary(described, *_):
        """
        How its chunks sit on the pages
        """
        # the record carries the fields by their names
        return described["record"]

    @staticmethod
    def resolve_partners(described, *_):
        """
        The datasets that share its pages, largest share first
        """
        # the partners and their bytes
        partners = described["record"].get("partners", {})
        # in order of their share
        return [
            {"name": name, "bytes": share}
            for name, share in sorted(partners.items(), key=lambda item: -item[1])
        ]

    @staticmethod
    def resolve_fill(described, *_):
        """
        What it holds where there is no data
        """
        # the fill check
        fill = described["nodata"]
        # render a value as the client shows it, or leave it out
        render = lambda value: None if value is None else str(value)
        # convert a time in seconds to one in ms, or leave it out
        ms = lambda seconds: None if seconds is None else 1e3 * seconds
        # what the smallest chunk holds
        holds = render(fill["found"])
        # it agrees with the library when it is a value and the same one
        agrees = None if holds in (None, "data", "unknown") else holds == render(fill["hdf5"])
        # assemble
        return {
            "status": fill["status"],
            "hdf5": render(fill["hdf5"]),
            "cf": render(fill["cf"]),
            "holds": holds,
            "agrees": agrees,
            "chunks": fill.get("fillChunks"),
            "bytes": fill.get("fillBytes"),
            "level": fill.get("level"),
            "decodeMs": ms(fill.get("decode")),
            "makeMs": ms(fill.get("make")),
            "encodeMs": ms(fill.get("encode")),
            "dataDecodeMs": ms(fill.get("data")),
        }

    @staticmethod
    def resolve_strip(described, *_):
        """
        The pages its chunks land on
        """
        # as described
        return described.get("strip")

    @staticmethod
    def resolve_filemap(described, *_):
        """
        What every page of its file holds
        """
        # as described
        return described.get("filemap")

    @staticmethod
    def resolve_census(described, *_):
        """
        The census of its kind of product, and where it falls in it
        """
        # the reference data
        reference = described.get("census")
        # without any
        if reference is None:
            # there is no comparison
            return None
        # the kind of the raster, the last part of its name, e.g. {HHHH} or {mask}
        kind = described["name"].split(".")[-1]
        # the rasters of the same kind, if the census has them, or else all of them
        group = reference.get("groups", {}).get(kind) or reference
        # the measures of this raster
        mine = qed.measurements.census.measures(description=described)
        # assemble
        return {
            **reference,
            "kind": kind if group is not reference else None,
            "rasters": group["rasters"],
            "measures": [
                {"name": name, "value": mine.get(name), **measure}
                for name, measure in group["measures"].items()
            ],
        }

    @staticmethod
    def resolve_grid(described, *_):
        """
        The states of the cells of its chunk grid
        """
        # the grid
        grid = described["states"]
        # with the names of the states
        return {**grid, "states": list(qed.readers.pages.STATES)}


# end of file
