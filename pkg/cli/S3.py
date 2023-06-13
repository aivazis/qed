# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# support
import boto3
import journal
import qed


# declaration
class S3(qed.shells.command, family="qed.cli.s3"):
    """
    Measure data access performance
    """

    # user configurable state
    profile = qed.properties.str()
    profile.default = "parasim"
    profile.doc = "the access credentials"

    region = qed.properties.str()
    region.default = "eu-central-1"
    region.doc = "the AWS region where the bucket is hosted"

    bucket = qed.properties.str()
    bucket.default = "parasim-ros3eu"
    bucket.doc = "the name of the S3 bucket"

    key = qed.properties.str()
    key.doc = "the lookup key of the bucket entry"

    page = qed.properties.int()
    page.default = 0
    page.doc = "the size of file space management pages"

    # interface
    @qed.export(tip="create an S3 bucket")
    def create(self, plexus, **kwds):
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
    def upload(self, plexus, **kwds):
        """
        Upload a file to an S3 bucket
        """
        # unpack  my state
        profile = self.profile
        bucket = self.bucket
        key = self.key
        # start a session
        s3 = boto3.Session(profile_name=profile).client("s3")
        # get the file
        with open(f"{key}", mode="rb") as stream:
            # upload
            s3.upload_fileobj(stream, bucket, key)
        # all done
        return 0

    @qed.export(tip="download a file from an S3 bucket")
    def download(self, plexus, **kwds):
        """
        Upload a file to an S3 bucket
        """
        # unpack  my state
        profile = self.profile
        bucket = self.bucket
        key = self.key
        # start a session
        s3 = boto3.Session(profile_name=profile).client("s3")
        # download
        s3.download_file(bucket, key, key)
        # all done
        return 0

    @qed.export(tip="delete a file from an S3 bucket")
    def delete(self, plexus, **kwds):
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
    def ls(self, plexus, **kwds):
        """
        Delete a file from an S3 bucket
        """
        # unpack  my state
        profile = self.profile
        bucket = self.bucket
        # start a session
        s3 = boto3.Session(profile_name=profile).client("s3")
        # get the contents
        response = s3.list_objects_v2(Bucket=bucket)
        # make a channel
        channel = journal.info("qed.s3.ls")
        # sign on
        channel.line(f"{bucket}:")
        # push in
        channel.indent()
        # go through the contents
        for key in response["Contents"]:
            # show me
            channel.line(f"{key}")
        # pull out
        channel.outdent()
        # and flush
        channel.log()
        # all done
        return 0

    @qed.export(tip="read the entire structure of a data product")
    def explore(self, **kwds):
        """
        Read the entire structure of a data product
        """
        # unpack  my state
        profile = self.profile
        region = self.region
        bucket = self.bucket
        key = self.key
        # build the uri
        uri = f"s3://{profile}@{region}/{bucket}/{key}"
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

        # make a channel
        channel = journal.info("qed.s3.app.read")
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
        self._newWriter(uri="empty.h5")
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

        # create the file writer
        writer = self._newWriter(uri="rslc.h5")
        # ask it to write an empty rslc
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
            page *= 2 * 1024
            # set the paging characteristics
            fapl.setPageBufferSize(page=page, meta=50, raw=50)
        # make a reader
        reader = qed.h5.reader(uri=uri, fapl=fapl)
        # and return it
        return reader

    def _newWriter(self, uri):
        """
        Build an h5 writer
        """
        # get the h5 bindings
        libh5 = qed.h5.libh5
        # make a creation property list
        fcpl = libh5.FCPL()
        # get my page size
        page = self.page
        # if it's non-trivial
        if page:
            # ask for the paged strategy
            fcpl.setFilespaceStrategy(
                strategy=libh5.FilespaceStrategy.page, persist=False, threshold=1
            )
            # set the page size
            fcpl.setPageSize(size=1024 * self.page)
        # use the fcpl to create the file writer
        writer = qed.h5.writer(uri=uri, fcpl=fcpl)
        # and return it
        return writer


# end of file