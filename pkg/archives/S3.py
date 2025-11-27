# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal
import boto3

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

    profile = qed.properties.str()
    profile.default = None
    profile.doc = "the name of the authentication profile"

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
        # get my root
        root = self.fs
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

    def credentials(self):
        """
        Generate the credentials necessary to access my contents
        """
        # prime by chaining up
        credentials = super().credentials()
        # unpack my state
        session = self.fs.session
        # we need the region
        region = session.region_name
        # and the session credentials
        frozen = session.get_credentials().get_frozen_credentials()
        # pack the S3 credentials
        credentials["region"] = region
        credentials["access_key"] = frozen.access_key
        credentials["secret_key"] = frozen.secret_key
        credentials["token"] = frozen.token
        # and hand them off
        return credentials

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # unpack my state
        uri = self.uri
        profile = self.profile
        region = self.region
        # build the AWS credentials
        opts = {}
        # if i know the profile
        if profile:
            # add it to the pile
            opts["profile_name"] = profile
        # if i know the region
        if region:
            # add it to the pile
            opts["region_name"] = region
        # make a session
        session = boto3.Session(**opts)
        # mount my s3 filesystem
        self.fs = qed.filesystem.s3(root=uri, session=session).discover(levels=1)

        # make a channel
        channel = journal.debug("qed.archives.s3")
        # if the channel is active
        if channel:
            # make an explorer
            explorer = qed.filesystem.treeExplorer()
            # show me
            channel.report(
                report=explorer.explore(node=self.fs, label=self.fs.location().address)
            )
            # flush
            channel.log()

        # all done
        return

    # visitor support
    def identify(self, visitor, **kwds):
        """
        Let {visitor} know i'm an S3 archive
        """
        # attempt to
        try:
            # ask {visitor} for it's base handler
            handler = visitor.onS3
        # if it doesn't understand
        except AttributeError:
            # chain up
            return super().identify(visitor=visitor, **kwds)
        # if all went well, invoke the hook
        return handler(archive=self, **kwds)

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

    # constants
    tag = "s3"
    label = "s3"


# end of file
