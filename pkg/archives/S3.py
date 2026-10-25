# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# superclass
from .Archive import Archive


# a S3 data archive
class S3(Archive, family="qed.archives.s3"):
    """
    A data archive that resides in an S3 bucket
    """

    # the location
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="s3")
    uri.doc = "the location of the archive"

    # the authentication profile
    profile = qed.properties.str()
    profile.default = None
    profile.doc = "the name of the authentication profile"

    # the region of the bucket
    region = qed.properties.str()
    region.default = None
    region.doc = "the name of the region where the data bucket resides"

    # constants
    readers = ("nisar",)

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve the archive contents at {uri}, a location expected to belong within the archive
        document space
        """
        # get my root, mounting my filesystem on first contact
        root = self.fs if self.fs is not None else self.mount()
        # normalize the {uri}, until the primitives does this automatically
        uri.address = qed.primitives.path(uri.address)
        # project the request
        projection = uri.address.relativeTo(root.uri.address)
        # ask for the folder at {uri}
        folder = root[projection]
        # look down one level
        folder.discover(levels=1)
        # make a pile of files
        files = [
            (name, node.uri, node.isFolder)
            for name, node in folder.contents.items()
            if not node.isFolder
        ]
        # and a pile of directories
        folders = [
            (name, node.uri, node.isFolder)
            for name, node in folder.contents.items()
            if node.isFolder
        ]
        # and present them in this order
        return folders + files

    def access(self):
        """
        Describe how to get at my contents: the authentication profile and the region, when i
        was told, neither of which is a secret
        """
        # prime by chaining up
        access = super().access()
        # if i know the profile
        if self.profile:
            # say so
            access["profile"] = self.profile
        # if i know the region
        if self.region:
            # say so
            access["region"] = self.region
        # hand them off
        return access

    def credentials(self):
        """
        Generate the credentials necessary to access my contents
        """
        # prime by chaining up
        credentials = super().credentials()
        # get my session
        session = self.session()
        # we need the region
        region = session.region_name
        # and the session credentials
        frozen = session.get_credentials().get_frozen_credentials()
        # pack the S3 credentials
        credentials["region"] = region
        # the access key
        credentials["access_key"] = frozen.access_key
        # the secret key
        credentials["secret_key"] = frozen.secret_key
        # and the session token
        credentials["token"] = frozen.token
        # and hand them off
        return credentials

    def mount(self):
        """
        Mount the filesystem over my bucket, listing its top level
        """
        # build the filesystem over my session, and take a look at the top
        fs = qed.filesystem.s3(root=self.uri, session=self.session()).discover(levels=1)
        # attach it
        self.fs = fs

        # make a channel
        channel = journal.debug("qed.archives.s3")
        # if the channel is active
        if channel:
            # make an explorer
            explorer = qed.filesystem.treeExplorer()
            # show me
            channel.report(report=explorer.explore(node=fs, label=fs.location().address))
            # flush
            channel.log()

        # and hand it back
        return fs

    def session(self):
        """
        Build the AWS session that grants access to my bucket, on first request
        """
        # if i have one already
        if self._session is not None:
            # hand it off
            return self._session
        # get the package, which is only needed once an archive in a bucket is used
        import boto3

        # the session options
        opts = {}
        # if i know the profile
        if self.profile:
            # add it to the pile
            opts["profile_name"] = self.profile
        # if i know the region
        if self.region:
            # add it to the pile
            opts["region_name"] = self.region
        # make a session
        session = boto3.Session(**opts)
        # keep it
        self._session = session
        # and hand it off
        return session

    def reconfigure(self, **kwds):
        """
        Point me at a new location, with new settings
        """
        # chain up
        super().reconfigure(**kwds)
        # the session i built was for the old settings, so the next request builds a new one
        self._session = None
        # all done
        return self

    # naming
    @classmethod
    def nicknames(cls, uri: str, collection: str | None = None) -> list:
        """
        Propose the nicknames of an archive at {uri}: the name of its bucket, then the bucket with
        more and more of the path within it, until all of it is in
        """
        # parse the location
        location = qed.primitives.uri.parse(uri, scheme="s3")
        # the bucket
        bucket = location.authority
        # a location without a bucket has nothing to suggest
        if not bucket:
            # so don't
            return []
        # the folders within the bucket
        levels = [level for level in location.address.split("/") if level]
        # the bucket, then the bucket with its first folder, and so on, each joined into one level
        return ["_".join([bucket] + levels[:count]) for count in range(len(levels) + 1)]

    # hooks
    @classmethod
    def isSupported(cls):
        """
        Check whether there is runtime support for this archive type
        """
        # attempt to
        try:
            # access the external packages we need
            import boto3
        # if anything goes wrong
        except ImportError as error:
            # no dice
            return False
        # otherwise, chances are good the runtime support is present
        return True

    # private data
    # my filesystem, mounted on first contact
    fs = None
    # the session that grants access to my bucket, built on first request
    _session = None

    # constants
    tag = "s3"
    # and the label that names my kind to the user
    label = "s3"


# end of file
