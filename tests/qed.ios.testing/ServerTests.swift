// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Foundation
import Testing


/// A path is resolved under the address of the server, which may itself sit under a prefix
@Test func resolvesPathsUnderTheBase() {
    // a server behind a hub, under the prefix of its user
    let server = Server(base: URL(string: "https://example.org/ondemand/user/someone/qed/")!)
    // asks for its stream under that prefix
    let request = server.request(for: "events")
    #expect(request.url?.absoluteString == "https://example.org/ondemand/user/someone/qed/events")
}

/// A server reached without a token sends no credential
@Test func sendsNoCredentialWithoutAToken() {
    // a server on the local network
    let server = Server(base: URL(string: "http://localhost:8005/")!)
    // presents nothing
    let request = server.request(for: "graphql")
    #expect(request.value(forHTTPHeaderField: "Authorization") == nil)
}

/// A server reached with a token presents it the way the hub expects
@Test func presentsTheToken() {
    // a server behind a hub, with a token
    let server = Server(base: URL(string: "https://example.org/qed/")!, token: "secret")
    // presents it in the form the hub reads
    let request = server.request(for: "graphql")
    #expect(request.value(forHTTPHeaderField: "Authorization") == "token secret")
}

/// A request for the stream asks for exactly the kind of answer that proxies stream through
@Test func asksForAnEventStream() {
    // any server
    let server = Server(base: URL(string: "http://localhost:8005/")!)
    // asked for its stream as a stream
    let request = server.request(for: "events", accept: "text/event-stream")
    // names that kind and nothing else
    #expect(request.value(forHTTPHeaderField: "Accept") == "text/event-stream")
}


// end of file
