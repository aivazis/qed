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

    # interface
    def getContents(self, uri):
        """
        Retrieve my contents at {path}
        """
        # get my uri
        uri = str(self.uri)
        # if it doesn't end in a slash
        if not uri.endswith("/"):
            # make sure it does
            uri = f"{uri}/"

        # get my contents
        contents = self._contents
        # if i haven't retrieved them before
        if contents is None:
            # connect and retrieve
            contents = self._retrieve()
            # and populate the cache
            self._contents = contents
            # make a channel
            channel = journal.debug("qed.archives.s3")
            # sign on
            channel.line(f"{self.uri}:")
            # show me the contents
            channel.indent()
            channel.report(report=contents)
            channel.outdent()
            # and flush
            channel.log()
        # don't do more, for now
        return list((key, f"{uri}{key}", False) for key in contents)

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
        response = s3.list_objects_v2(Bucket=bucket)
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
