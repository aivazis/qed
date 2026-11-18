// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Foundation
import Testing


/// The state of a server with one view, as qed answers {qedStateQuery}
let stateAnswer = """
    {"data": {"qed": {"views": [{
        "name": "5f94ab5c",
        "selections": [
            {"name": "band", "value": "L"},
            {"name": "frequency", "value": "A"},
            {"name": "cov", "value": "HHHH"}
        ],
        "reader": {"name": "gcov-033_166_D_069-P05023"},
        "dataset": {
            "shape": [17280, 17496], "origin": [0, 0],
            "channels": [{"tag": "covariance"}, {"tag": "covarianceMasked"}]
        },
        "channel": {"tag": "covarianceMasked"},
        "zoom": {"vertical": -2.0, "horizontal": -2.0, "coupled": true}
    }]}}}
    """

/// The answer to the state query reads into its types, field by field
@Test func decodesTheState() throws {
    // read the answer
    let answer = try Client.decode(StateQuery.Answer.self, from: Data(stateAnswer.utf8))
    // there is one view
    let views = answer.qed?.views ?? []
    try #require(views.count == 1)
    let view = try #require(views[0])
    // and it shows what the server said it shows
    #expect(view.name == "5f94ab5c")
    #expect(view.selections?.compactMap { $0?.name } == ["band", "frequency", "cov"])
    #expect(view.selections?.compactMap { $0?.value } == ["L", "A", "HHHH"])
    #expect(view.reader?.name == "gcov-033_166_D_069-P05023")
    #expect(view.channel?.tag == "covarianceMasked")
    #expect(view.dataset?.shape == [17280, 17496])
    #expect(view.dataset?.channels?.compactMap { $0?.tag } == ["covariance", "covarianceMasked"])
    #expect(view.zoom?.vertical == -2 && view.zoom?.horizontal == -2 && view.zoom?.coupled == true)
}

/// A view that shows nothing yet still reads, with its missing parts left empty
@Test func decodesAnEmptyView() throws {
    // a server with a view that has not been given anything to show
    let text = #"{"data": {"qed": {"views": [{"name": "v", "reader": null, "dataset": null, "channel": null, "zoom": null}]}}}"#
    // reads
    let answer = try Client.decode(StateQuery.Answer.self, from: Data(text.utf8))
    let view = try #require(answer.qed?.views?.first ?? nil)
    // with nothing in it
    #expect(view.name == "v")
    #expect(view.reader == nil && view.dataset == nil && view.channel == nil && view.zoom == nil)
}

/// A server that reports errors has not answered, and its messages are passed on
@Test func reportsErrors() {
    // an answer made of errors
    let text = #"{"data": null, "errors": [{"message": "no such field"}]}"#
    // is a refusal that carries them
    #expect(throws: ClientError.refused(["no such field"])) {
        try Client.decode(StateQuery.Answer.self, from: Data(text.utf8))
    }
}

/// A server that sends neither data nor errors has said nothing
@Test func reportsEmptyAnswers() {
    // an answer with nothing in it
    let text = #"{"data": null}"#
    // is empty
    #expect(throws: ClientError.empty) {
        try Client.decode(StateQuery.Answer.self, from: Data(text.utf8))
    }
}


// end of file
