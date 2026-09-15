# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# superclass
from .Archive import Archive


# an earth access data archive
class EarthAccess(Archive, family="qed.archives.earth"):
    """
    A data archive that consists of the granules that match a query of the NASA common metadata
    repository, answered through {earthaccess}

    The archive is the query: its traits are the query parameters, one per parameter of the
    {earthaccess} query builder, so a configuration section reads as a search
    """

    # user configurable state
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="earth", address=())
    uri.doc = "the archive identifier"

    collection = qed.properties.str()
    collection.default = None
    collection.doc = "the short name of the data collection"

    conceptId = qed.properties.str()
    conceptId.default = None
    conceptId.doc = "the concept id of the data collection"

    pattern = qed.properties.str()
    pattern.default = None
    pattern.doc = "a pattern, with wildcards, that the granule names must match"

    count = qed.properties.int()
    count.default = None
    count.doc = "the cap on the number of granules fetched; unset fetches every match"

    begin = qed.properties.str()
    begin.default = None
    begin.doc = "the start of the acquisition window, as an ISO 8601 date"

    end = qed.properties.str()
    end.default = None
    end.doc = "the end of the acquisition window, as an ISO 8601 date"

    bbox = qed.properties.tuple(schema=qed.properties.float())
    bbox.default = None
    bbox.doc = "a bounding box as (west, south, east, north), in degrees"

    point = qed.properties.tuple(schema=qed.properties.float())
    point.default = None
    point.doc = "a point of interest as (longitude, latitude), in degrees"

    circle = qed.properties.tuple(schema=qed.properties.float())
    circle.default = None
    circle.doc = "a circle as (longitude, latitude, radius), in degrees and meters"

    line = qed.properties.list(schema=qed.properties.tuple(schema=qed.properties.float()))
    line.default = None
    line.doc = "the (longitude, latitude) vertices of a line, in degrees"

    polygon = qed.properties.list(schema=qed.properties.tuple(schema=qed.properties.float()))
    polygon.default = None
    polygon.doc = "the (longitude, latitude) vertices of a polygon, in degrees"

    # constants
    readers = ("nisar",)

    # public data
    @property
    def constrained(self):
        """
        Check whether my query narrows the collection down, spatially, temporally, or by name
        """
        # a collection alone matches six figures of granules, so it does not count
        return any(
            trait is not None
            for trait in (
                self.pattern,
                self.begin,
                self.end,
                self.bbox,
                self.point,
                self.circle,
                self.line,
                self.polygon,
            )
        )

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve the archive contents at {uri}, a location expected to belong within the archive
        document space
        """
        # an unconstrained query is not a listing
        if not self.constrained:
            # make a channel
            channel = journal.warning("qed.archives.earth.contents")
            # explain
            channel.line(f"'{self.pyre_name}' lists nothing")
            channel.line("an earth archive needs a spatial or temporal constraint")
            channel.line("or a pattern for the granule names")
            # flush
            channel.log()
            # and report an empty archive
            return []
        # get my filesystem, mounting it on first contact
        fs = self.fs if self.fs is not None else self.mount()
        # project the request onto the tree
        rel = self.project(uri=uri)
        # and break it into its crumbs
        crumbs = tuple(rel.names)
        # the root is the filesystem itself
        if not crumbs:
            # so there is nothing to look up
            folder = fs
        # a folder below it
        else:
            # cannot be on a page that has never been fetched
            if fs.info(node=fs).sync is None:
                # so fetch it
                fs.discover()
            # attempt to
            try:
                # find the folder on the page
                folder = fs[rel]
            # if the page does not have it
            except fs.NotFoundError:
                # make a channel
                channel = journal.warning("qed.archives.earth.contents")
                # explain
                channel.line(f"'{self.pyre_name}': no folder at '{uri}'")
                channel.line("the page may have changed since the folder was listed")
                # flush
                channel.log()
                # and report an empty folder
                return []
        # bring the folder current: at the root, this runs the query; below it, the page in
        # hand answers
        folder.discover(levels=1)
        # make a channel
        channel = journal.debug("qed.archives.earth.contents")
        # show me
        channel.line(f"{self}")
        channel.indent()
        channel.line(f"query: {fs.query}")
        channel.line(f"hits: {fs.hits}")
        channel.line(f"folder: {folder.uri}")
        # make a pile for the folders
        folders = []
        # and one for the granules
        granules = []
        # go through the folder contents, in order
        for name, node in sorted(folder.contents.items()):
            # the location of the entry
            location = self.location(node=node)
            # a granule without a payload cannot be read
            if location is None:
                # so skip it
                continue
            # show me
            channel.line(f"entry:")
            channel.indent()
            channel.line(f"name: {name}")
            channel.line(f"location: {location}")
            channel.outdent()
            # form the item
            item = (name, location, node.isFolder)
            # and add it to the right pile
            (folders if node.isFolder else granules).append(item)
        # outdent
        channel.outdent()
        # flush
        channel.log()
        # folders first
        return folders + granules

    def mount(self, engine=None):
        """
        Mount the filesystem over my query, using {engine} to run it
        """
        # build the filesystem
        fs = qed.filesystem.earthaccess(
            query=self.query(), count=self.count, layout=self.layout, engine=engine
        )
        # attach it
        self.fs = fs
        # and hand it back
        return fs

    def query(self):
        """
        Assemble my traits into the parameters of an {earthaccess} query
        """
        # make a pile
        query = {}
        # the collection, by short name
        if self.collection is not None:
            # goes in
            query["short_name"] = self.collection
        # and by concept id
        if self.conceptId is not None:
            # goes in
            query["concept_id"] = self.conceptId
        # the pattern for the granule names
        if self.pattern is not None:
            # goes in
            query["granule_name"] = self.pattern
        # the acquisition window, open on whichever end is unset
        if self.begin is not None or self.end is not None:
            # goes in
            query["temporal"] = (self.begin, self.end)
        # the bounding box
        if self.bbox is not None:
            # goes in
            query["bounding_box"] = tuple(self.bbox)
        # the point
        if self.point is not None:
            # goes in
            query["point"] = tuple(self.point)
        # the circle
        if self.circle is not None:
            # goes in
            query["circle"] = tuple(self.circle)
        # the line
        if self.line is not None:
            # goes in
            query["line"] = [tuple(vertex) for vertex in self.line]
        # the polygon
        if self.polygon is not None:
            # get its vertices
            vertices = [tuple(vertex) for vertex in self.polygon]
            # the repository wants a closed ring
            if vertices[0] != vertices[-1]:
                # so close it
                vertices.append(vertices[0])
            # and the ring goes in
            query["polygon"] = vertices
        # all done
        return query

    def location(self, node):
        """
        Build the uri of {node}: a folder is a location within my document space, and a granule
        is the location of its payload
        """
        # a folder is addressed within me
        if node.isFolder:
            # by its path on the tree, relative to the root of the filesystem
            rel = node.uri.relativeTo(qed.primitives.path("/"))
            # appended to my own address
            return str(self.uri.clone(address=str(self.base() / rel)))
        # a granule is addressed by its payload; go through the direct access links
        for link in node.info.links:
            # looking for the product
            if link.startswith("s3://") and link.endswith(".h5"):
                # convert it into a uri the readers understand; the address keeps the slash
                # that separates it from the authority
                uri = qed.primitives.uri(
                    scheme="s3", authority="daac@us-west-2", address=link[len("s3:/") :]
                )
                # and hand it off
                return str(uri)
        # a granule without a product is unreadable
        return None

    def project(self, uri):
        """
        Project {uri}, a location within my document space, onto the tree
        """
        # the location is the address of the uri, relative to my own
        return qed.primitives.path(uri.address).relativeTo(self.base())

    def base(self):
        """
        The path that anchors my document space
        """
        # get my address
        address = self.uri.address
        # an archive without one anchors at the root
        return qed.primitives.path(address) if address else qed.primitives.path("/")

    # the layout of the tree
    @staticmethod
    def layout(granule):
        """
        Place {granule} on the tree: under its stack, then its acquisition date
        """
        # the catalog name of the granule is its id
        gid = granule["meta"]["native-id"]
        # parse it
        descriptor = qed.readers.nisar.daac.descriptor(granule=gid)
        # a granule the grammar cannot place hangs off the root
        if not descriptor:
            # under its own name
            return (gid,)
        # the stack is the track, the pass direction, and the frame
        track = descriptor.track
        direction = descriptor.direction
        # which products at level 0 do not have
        frame = getattr(descriptor, "frame", None)
        # form the stack name the way the catalog spells it
        stack = f"{track:03}_{direction}" if frame is None else f"{track:03}_{direction}_{frame:03}"
        # the date is that of the acquisition, the reference one for pairs
        date = f"{descriptor.mark:%Y-%m-%d}"
        # place the granule
        return stack, date, gid

    # hooks
    @classmethod
    def isSupported(cls):
        """
        Check whether there is runtime support for this archive type
        """
        # attempt to
        try:
            # access the external packages we need
            import earthaccess
        # if anything goes wrong
        except ImportError as error:
            # no dice
            return False
        # otherwise, chances are good there is runtime support
        return True

    # constants
    tag = "earth"
    label = "earth-access"

    # private data
    # the filesystem over my query, mounted on first contact
    fs = None


# end of file
