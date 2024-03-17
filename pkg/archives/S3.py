# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal


# a S3 data archive
class S3(qed.component, family="qed.archives.s3", implements=qed.protocols.archive):
    """
    A data archive that resides in an S3 bucket
    """

    # the location
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="file", address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"

    # constants
    readers = ("nisar",)

    # interface
    def contents(self, uri):
        """
        Retrieve my contents at {path}
        """
        # get my uri
        uri = self.uri
        # unpack the server info
        region, _, profile, _ = uri.server
        # if the {profile} is trivial
        if not profile:
            # set it to {default}
            profile = "default"
        # get the profile configuration
        config = self.pyre_user.aws.profile(name=profile)
        # if the {region} is trivial
        if not region:
            # ask the profile
            region = config.get("region", "")
        # reassemble the authority
        authority = f"{profile}@{region}"
        # get the address
        address = uri.address
        # ensure the address ends with a slash
        if not address.endswith("/"):
            # by adding the missing slash
            address = f"{address}/"
        # assemble the canonical prefix of my contents
        prefix = qed.primitives.uri(scheme="s3", authority=authority, address=address)
        # get my contents
        contents = self._contents
        # if i haven't retrieved them before
        if contents is None:
            # connect and retrieve
            contents = self._retrieve()
            # and populate the cache
            self._contents = contents
            # make a channel
            channel = journal.info("qed.archives.s3")
            # sign on
            channel.line(f"retrieving the contents of '{self.uri}'")
            channel.line(f"prefix: {prefix}")
            channel.line(f"contents:")
            # show me the contents
            channel.indent()
            channel.report(report=contents)
            channel.outdent()
            # and flush
            channel.log()
        # don't do more, for now
        return list((key, f"{prefix}{key}", False) for key in contents)

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # set up the content cache
        self._contents = None
        # establish the session
        self._session = self._connect()
        # all done
        return

    # implementation details
    def _retrieve(self):
        """
        Retrieve the contents of the data archive
        """
        # get the session
        s3 = self._session
        # if i couldn't establish one
        if not s3:
            # i'm empty
            return []
        # if we have support, unpack my state
        uri = self.uri
        # get the address and turn it into a path
        address = qed.primitives.path(uri.address)
        # the bucket is the root
        bucket = address[1]
        # get the contents
        response = s3.list_objects_v2(
            Bucket=bucket, MaxKeys=10000, Prefix="/".join(address[2:])
        )
        # retrieve the contents
        contents = response.get("Contents", [])
        # make a list of the keys and return them
        return list(entry["Key"] for entry in contents)

    def _connect(self):
        """
        Establish a connection to the archive
        """
        # attempt to
        try:
            # get the AWS support
            import boto3
        # if this fails
        except ImportError:
            # we have a problem
            channel = journal.error("qed.archives.s3")
            # complain
            channel.line(f"while attempting to connect to {self.uri}")
            channel.line(f"could not import 'boto3'")
            channel.line(f"this installation of 'qed' doesn't support S3 data archives")
            # flush
            channel.log()
            # and bail
            return None
        # if we have support, unpack my state
        uri = self.uri
        # unpack the profile and region from the authority field
        region, _, profile, _ = uri.server
        # attempt to
        try:
            # start a session
            s3 = boto3.Session(profile_name=profile, region_name=region).client("s3")
        # if there is something wrong with the boto3 installation
        except ImportError as error:
            # we have a problem
            channel = journal.error("qed.archives.s3")
            # complain
            channel.line(f"while attempting to connect to {self.uri}")
            channel.line(f"something is wrong with the 'boto3' installation")
            channel.line(f"this installation of 'qed' doesn't support S3 data archives")
            # flush
            channel.log()
            # just in case errors aren't fatal
            s3 = None
        # and return it
        return s3


# end of file
