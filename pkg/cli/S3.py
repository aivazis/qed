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


# end of file
