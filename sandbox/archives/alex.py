#! /usr/bin/env python3

# support
import journal
import earthaccess


# a polygon
crete = [
    (23.3547, 34.7211),
    (26.4923, 34.7211),
    (26.4923, 35.7146),
    (23.3547, 35.7146),
    (23.3547, 34.7211),
]


# the list of NISAR data collections
def collections():
    # make a channel
    channel = journal.info("nisar.datasets")
    # search
    datasets = earthaccess.search_datasets(platform="NISAR")
    # go through them
    for idx, dataset in enumerate(datasets):
        # get the summary
        summary = dataset.summary()
        # sign on
        channel.line(f"{idx:03}: {dataset.concept_id()}")
        # indent
        channel.indent()
        # report
        channel.line(f"concept id: {summary['concept-id']}")
        channel.line(f"short name: {summary['short-name']}")
        # outdent
        channel.outdent()

    # flush
    channel.log()
    # all done
    return datasets


def search(**kwds):
    # make a channel
    channel = journal.info("nisar.datasets")
    # search
    granules = earthaccess.search_data(
        count=10,
        # daac="ASF",
        #
        # L0A
        # short_name=NISAR_L0A_RRST_BETA_V1,
        # concept_id="C2850223384-ASF",
        #
        # L0B
        short_name="NISAR_L0B_RRSD_BETA_V1",
        # concept_id="C3622228339-ASF",
        # granule_name="NISAR_L0_PR_RRSD*",
        #
        # L0A
        # short_name="NISAR_L0A_RRST_PROVISIONAL_V1",
        # concept_id="C2853086824-ASF",
        #
        # L0B
        # short_name="NISAR_L0B_RRSD_PROVISIONAL_V1",
        # concept_id="C2853089814-ASF",
        # granule_name="NISAR_*",
        # clockwise
        polygon=crete,
        **kwds,
    )
    channel.line(f"found: {len(granules)} granules")
    # go through them
    for idx, granule in enumerate(granules):
        # sign on
        channel.line(f"{idx:03}: {granule.uuid}")
        # indent
        channel.indent()
        # report
        channel.line(f"size: {granule.size()}")
        channel.line(f"links: {granule.data_links(access='direct')}")
        channel.line(
            f"s3 credentials endpoint: {granule.get_s3_credentials_endpoint()}"
        )
        channel.line(f"umm: keys={tuple(granule['umm'].keys())}")
        # channel.line(f"umm:")
        channel.indent()
        channel.line(f"ur: {granule['umm']['GranuleUR']}")

        # get all the urls related to this granule
        for url in granule["umm"]["RelatedUrls"]:
            interesting = url["Type"].lower().startswith(
                "get data via direct access"
            ) and url["Format"].lower().startswith("binary")
            if interesting:
                channel.line(f"url: {url['URL']}")
        # channel.line(f"related urls: {granule['umm']['RelatedUrls']}")
        # channel.line(f"data granule: keys={tuple(granule['umm']['DataGranule'].keys())}")
        channel.line(f"data granule:")
        channel.indent()
        # channel.line(f"archive: {granule['umm']['DataGranule']['ArchiveAndDistributionInformation']}")
        # channel.line(f"day/night: {granule['umm']['DataGranule']['DayNightFlag']}")
        channel.line(
            f"production date: {granule['umm']['DataGranule']['ProductionDateTime']}"
        )
        # channel.line(f"identifiers: {granule['umm']['DataGranule']['Identifiers']}")
        channel.outdent()
        channel.outdent()
        channel.line(f"meta: keys={tuple(granule['meta'].keys())}")
        # channel.line(f"meta:")
        channel.indent()
        channel.line(f"provider id: {granule['meta']['provider-id']}")
        channel.line(f"native id: {granule['meta']['native-id']}")
        channel.line(f"concept id: {granule['meta']['concept-id']}")
        channel.line(f"concept type: {granule['meta']['concept-type']}")
        channel.line(
            f"collection concept id: {granule['meta']['collection-concept-id']}"
        )
        channel.outdent()
        # outdent
        channel.outdent()
        # bail
        break
    # flush
    channel.log()
    # all done
    return granules


# bootstrap
if __name__ == "__main__":
    # login
    auth = earthaccess.login(persist=True)
    # show me the nisar collections
    collections()
    # search
    search()


# end of file
