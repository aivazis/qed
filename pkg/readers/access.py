# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# the fields the infrastructure expects when it is handed credentials for an s3 bucket
s3 = ("region", "access_key", "secret_key", "token")
# the region of last resort: the one the NISAR archives live in
fallback = "us-west-2"


def resolve(uri, grant):
    """
    Turn {grant}, what is known about how to get at the product at {uri}, into what the
    infrastructure needs in order to open it

    A grant may carry the keys themselves, the way an archive hands them out, or it may say
    how to get them: the {profile} to look them up under, and the {region} of the bucket. One
    that carries neither gets whatever the standard AWS credential chain comes up with, which
    is what an instance that runs next to the data, with its role already in place, expects.
    The keys this finds live in memory only: they are presented to the driver, and never
    become part of anybody's configuration
    """
    # normalize the location
    uri = qed.primitives.uri.parse(value=str(uri), scheme="file")
    # start with a copy of what is known, leaving out whatever was left blank
    resolved = {name: value for name, value in dict(grant).items() if value not in (None, "")}
    # only buckets need any of this
    if uri.scheme != "s3":
        # so everything else goes through as it is
        return resolved
    # if the keys are not there
    if "access_key" not in resolved:
        # look them up
        found = chain(profile=resolved.get("profile"), region=resolved.get("region"))
        # what was found fills in what is missing, and nothing else: whatever the grant
        # already says, e.g. a region, is what somebody chose
        resolved = {**found, **resolved}
    # the driver needs to know where the bucket lives
    resolved.setdefault("region", fallback)
    # and expects every field to be there, even when there is nothing to put in it, which is
    # how it is told that the bucket is open to everybody
    for field in s3:
        # so fill in the blanks
        resolved.setdefault(field, "")
    # all done
    return resolved


def chain(profile=None, region=None):
    """
    Ask the standard AWS credential chain for keys, under {profile} when there is one
    """
    # carefully, since this is an optional dependency
    try:
        # get the package
        import boto3
    # if it is not there
    except ImportError:
        # make a channel
        channel = journal.warning("qed.readers.access")
        # explain
        channel.line("could not locate the 'boto3' package")
        channel.line("so there is no way to look for AWS credentials")
        # flush
        channel.log()
        # and find nothing
        return {}
    # the session options
    options = {}
    # if there is a profile
    if profile:
        # look under it
        options["profile_name"] = profile
    # if there is a region
    if region:
        # pass it along
        options["region_name"] = region
    # make a session; a profile that does not exist is reported by the package, and the
    # complaint says which one, so it is left to travel
    session = boto3.Session(**options)
    # ask for the keys
    credentials = session.get_credentials()
    # a chain that comes up empty
    if credentials is None:
        # finds nothing; the bucket may well be open to everybody
        return {}
    # take a snapshot, since the keys may be the kind that gets refreshed behind the scenes
    frozen = credentials.get_frozen_credentials()
    # pack what was found
    found = {"access_key": frozen.access_key, "secret_key": frozen.secret_key}
    # temporary keys come with a token
    if frozen.token:
        # which travels with them
        found["token"] = frozen.token
    # the session may know the region, from the profile or from the environment
    if session.region_name:
        # which is better than guessing
        found["region"] = session.region_name
    # hand off what was found
    return found


# end of file
