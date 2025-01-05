# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import boto3
import journal
import os
import qed


# declaration
class S3(qed.shells.command, family="qed.cli.s3"):
    """
    Utilities for exploring S3 buckets
    """

    # user configurable state
    profile = qed.properties.str()
    profile.default = None
    profile.doc = "the access credentials"

    region = qed.properties.str()
    region.default = None
    region.doc = "the AWS region where the bucket is hosted"

    bucket = qed.properties.str()
    bucket.default = ""
    bucket.doc = "the name of the S3 bucket"

    key = qed.properties.str()
    key.default = ""
    key.doc = "the lookup key of the bucket entry"

    arn = qed.properties.str()
    arn.default = ""
    arn.doc = "the ARN"

    token = qed.properties.str()
    token.default = ""
    token.doc = "the web identity token"

    page = qed.properties.int()
    page.default = 0
    page.doc = "the size of file space management pages, in K"

    cache = qed.properties.int()
    cache.default = 64
    cache.doc = "the size of the read cache, in pages"

    tile = qed.properties.tuple(schema=qed.properties.int())
    tile.default = (8 * 1024, 8 * 1024)
    tile.doc = "the shape of autogenerated datasets"

    # interface
    @qed.export(tip="assume a role and print out its credentials")
    def webid(self, **kwds):
        """
        Assume a role and print out its credentials
        """
        # make a channel
        channel = journal.info("qed.s3.webid")
        # get the role ARN
        arn = self.arn
        # if the user didn't pick one
        if not arn:
            # read the corresponding environment variable
            arn = os.getenv("AWS_ROLE_ARN")
            # if that's not available either
            if not arn:
                # make a channel
                channel = journal.error("qed.s3.webid")
                # complain
                channel.log("no role ARN specified")
                # and bail
                return 0
        # get the web id token
        token = self.token
        # if the user didn't supply one
        if not token:
            # get the path to the file with the token from the environment
            path = os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE")
            # if that's not available either
            if not path:
                # make a channel
                channel = journal.error("qed.s3.webid")
                # complain
                channel.log("no web id token")
                # and bail
                return 0
            # open the file and extract the toke
            token = open(path, mode="r").read()
        # access the security token service
        sts = boto3.Session(profile_name=self.profile).client(service_name="sts")
        # assume the role
        role = sts.assume_role_with_web_identity(
            RoleArn=arn, RoleSessionName="assume-role", WebIdentityToken=token
        )
        # extract the credentials
        credentials = role["Credentials"]
        # and from there the signing parameters
        aws_access_key = credentials["AccessKeyId"]
        aws_secret_access_key_id = credentials["SecretAccessKey"]
        aws_session_token = credentials["SessionToken"]
        # show me
        channel.line(f"role arn: '{arn}'")
        channel.indent()
        channel.line(f"access key: '{aws_access_key}'")
        channel.line(f"secret key: '{aws_secret_access_key_id}'")
        channel.line(f"session token: '{aws_session_token}'")
        channel.outdent()
        # flush
        channel.log()
        # all done
        return 0

    @qed.export(tip="create an S3 bucket")
    def create(self, **kwds):
        """
        Create an S3 bucket
        """
        # unpack  my state
        profile = self.profile
        region = self.region
        bucket = self.bucket
        # start a session
        s3 = boto3.Session(profile_name=profile).client("s3")
        # create a bucket
        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
        # all done
        return 0

    @qed.export(tip="upload a file to an S3 bucket")
    def upload(self, argv, **kwds):
        """
        Upload a file to an S3 bucket
        """
        # if the user didn't supply a file to upload
        if not argv:
            # make a channel
            channel = journal.error("qed.s3.upload")
            # complain
            channel.line("please specify a file to upload")
            channel.line("usage:")
            channel.indent()
            channel.line(
                "qed s3 --profile=<name> --bucket=<bucket> --key=<key> <filename>"
            )
            channel.outdent()
            # flush
            channel.log()
            # and bail, in case errors aren't fatal
            return 1
        # otherwise, grab the filename
        filename = argv.pop(0)
        # unpack  my state
        profile = self.profile
        bucket = self.bucket
        key = self.key
        # start a session
        s3 = boto3.Session(profile_name=profile).client("s3")
        # get the file
        with open(filename, mode="rb") as stream:
            # upload
            s3.upload_fileobj(stream, bucket, key)
        # all done
        return 0

    @qed.export(tip="download a file from an S3 bucket")
    def download(self, argv, **kwds):
        """
        Upload a file to an S3 bucket
        """
        # unpack  my state
        profile = self.profile
        bucket = self.bucket
        key = self.key
        # if the user supplied a destination filename
        if argv:
            # extract it
            dst = argv.pop(0)
        # otherwise
        else:
            # convert the key into a path
            path = qed.primitives.path(key)
            # and use the final segment as the local filename
            dst = path.name
        # start a session
        s3 = boto3.Session(profile_name=profile).client("s3")
        # download
        s3.download_file(bucket, key, dst)
        # all done
        return 0

    @qed.export(tip="delete a file from an S3 bucket")
    def delete(self, **kwds):
        """
        Delete a file from an S3 bucket
        """
        # unpack  my state
        profile = self.profile
        bucket = self.bucket
        key = self.key
        # start a session
        s3 = boto3.Session(profile_name=profile).client("s3")
        # delete
        s3.delete_object(Bucket=bucket, Key=key)
        # all done
        return 0

    @qed.export(tip="list the contents of an S3 bucket")
    def ls(self, **kwds):
        """
        List the contents of an S3 bucket
        """
        # unpack my state
        profile = self.profile
        region = self.region
        bucket = self.bucket
        # start a session
        s3 = boto3.Session(profile_name=profile).client("s3")
        # get the contents
        response = s3.list_objects_v2(Bucket=bucket)
        # make a channel
        channel = journal.info("qed.s3.ls")
        # sign on
        channel.line(f"profile: {profile}")
        channel.line(f"region: {region}")
        channel.line(f"bucket: {bucket}")
        channel.line(f"contents:")
        # push in
        channel.indent()
        # go through the contents
        for record in response.get("Contents", []):
            # get the file name
            name = record["Key"]
            # show me
            channel.line(f"{name}")
        # pull out
        channel.outdent()
        # and flush
        channel.log()
        # all done
        return 0

    @qed.export(tip="read the entire structure of a data product")
    def explore(self, argv, **kwds):
        """
        Read the entire structure of a data product
        """
        # make a channel
        channel = journal.info("qed.s3.explore")

        # if there is a uri on the command line
        if argv:
            # grab it
            uri = qed.primitives.uri.parse(argv.pop(0))
        # otherwise build it from my state
        else:
            # unpack  my state
            profile = self.profile
            region = self.region
            bucket = self.bucket
            key = self.key
            # assemble the authority
            authority = "@".join(filter(None, (profile, region)))
            # and the address
            address = "/".join(filter(None, (bucket, key)))
            # build the uri
            uri = qed.primitives.uri(
                scheme="s3", authority=authority, address=f"/{address}"
            )
        # show me
        channel.log(f"opening {uri}")
        # make a reader
        reader = self._newReader(uri=uri)

        # make a timer
        timer = qed.timers.wall("qed.app.s3.read")
        # start it
        timer.start()
        # get the data
        reader.read()
        # stop the time
        timer.stop()

        # report
        channel.line(f"in {timer.sec()} sec")
        # and flush
        channel.log()

        # all done
        return

    # specific datasets
    @qed.export(
        tip="create an empty file with the given file space management page size"
    )
    def empty(self, **kwds):
        """
        Create an empty file with the given file space management page size
        """
        # make a writer; this creates an empty file as a side-effect
        self._newWriter(seed="empty")
        # all done
        return 0

    @qed.export(
        tip="create an empty RSLC file with the given file space management page size"
    )
    def rslc(self, **kwds):
        """
        Create an empty NISAR RSLC file with the given file space management page size
        """
        # get the product specs
        import nisar.products.spec as spec

        # sign on
        channel = journal.info("qed.s3.rslc")
        # show me what we are doing
        channel.line(f"profile: {self.profile}")
        channel.line(f"region: {self.region}")
        channel.line(f"bucket: {self.bucket}")
        channel.line(f"key: rsls.h5")
        channel.line(f"page: {self.page}")
        channel.line(f"tile: {self.tile}")
        # flush
        channel.log()

        # build the rslc description
        spec = spec.rslc()
        # assemble it into an actual product
        data = qed.h5.product(spec=spec)
        # set the list of frequencies
        data.science.LSAR.identification.listOfFrequencies = ["A"]
        # get the swaths
        swaths = data.science.LSAR.RSLC.swaths
        # trim the B frequency
        del swaths.frequencyB
        # get the A frequency
        a = swaths.frequencyA
        # set the list of polarizations
        a.listOfPolarizations = ["HH"]
        # go through the other polarizations
        for pol in "HV", "VH", "VV", "RH", "RV":
            # and remove them
            delattr(a, pol)
        # get the HH dataset
        hh = a.HH
        # set the shape
        hh.shape = self.tile
        # make a grid
        grid = hh.memtype.grid(shape=hh.shape)
        # populate it
        for i in range(hh.shape[0]):
            # every so often
            if i % 100 == 0:
                # show me some progress
                print(i)
            # build the imaginary part
            for j in range(hh.shape[1]):
                # place value in the grid
                grid[i, j] = complex(i, j) / hh.shape[0]
        # dress it up as a tile
        tile = hh.tile(
            data=grid, type=hh.memtype, shape=hh.shape, origin=[0] * len(hh.shape)
        )
        # stage it
        hh._staged.append(tile)

        # create the file writer
        writer = self._newWriter(seed="rslc")
        # and write the data product
        writer.write(data=data)

        # all done
        return 0

    # implementation details
    def _newReader(self, uri):
        """
        Build an h5 reader
        """
        # get the h5 bindings
        libh5 = qed.h5.libh5
        # make an access property list
        fapl = libh5.FAPL()
        # get my page size
        page = self.page
        # if it's non-trivial
        if page:
            # convert it into K, and make it a little bigger
            cache = self.cache * 1024 * page
            # set the paging characteristics
            fapl.setPageBufferSize(page=cache, meta=50, raw=50)
        # make a reader
        reader = qed.h5.reader(uri=uri, fapl=fapl)

        # make a channel
        channel = journal.info("qed.s3.reader")
        # show me
        channel.line(f"opened '{uri}'")
        channel.indent()
        channel.line(
            f"page size: {reader._file._pyre_id.fapl.getPageBufferSize()} bytes"
        )
        channel.outdent()
        # flush
        channel.log()

        # and return the reader
        return reader

    def _newWriter(self, seed):
        """
        Build an h5 writer
        """
        # get the h5 bindings
        libh5 = qed.h5.libh5
        # make a creation property list
        fcpl = libh5.FCPL()
        # get the page size
        page = self.page
        # if it's non-trivial
        if page:
            # ask for the paged strategy
            fcpl.setFilespaceStrategy(
                strategy=libh5.FilespaceStrategy.page, persist=False, threshold=1
            )
            # set the page size
            fcpl.setPageSize(size=1024 * page)
        # make a tag
        tag = "default" if page == 0 else f"{page}k"
        # assemble the filename
        uri = f"{seed}-{tag}.h5"
        # use the fcpl to create the file writer
        writer = qed.h5.writer(uri=uri, fcpl=fcpl)
        # and return it
        return writer


# end of file
