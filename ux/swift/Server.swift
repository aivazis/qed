// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Foundation


/// A qed server: where it is, and the token that admits the app when one is needed
struct Server: Sendable {
    // the address every request is resolved against; it ends with a slash, so the paths qed
    // serves land under it
    let base: URL
    // the hub token that admits the app, when the server sits behind a hub
    let token: String?

    /// Make a server at {base}, admitted by {token} when there is one
    init(base: URL, token: String? = nil) {
        // record the address
        self.base = base
        // and the credential
        self.token = token
    }

    /// Make a request for {path} with the parameters in {query}, asking for an answer of the
    /// {accept} kind when one is given
    func request(
        for path: String, query: [URLQueryItem] = [], accept: String? = nil
    ) -> URLRequest {
        // resolve the path against the address of the server, and attach the parameters
        var url = base.appending(path: path)
        if !query.isEmpty {
            url.append(queryItems: query)
        }
        // make the request
        var request = URLRequest(url: url)
        // ask for the kind of answer the caller wants; some proxies decide by it whether to
        // stream the answer or hold it until it is complete
        if let accept {
            request.setValue(accept, forHTTPHeaderField: "Accept")
        }
        // and present the token, if there is one
        if let token {
            request.setValue("token \(token)", forHTTPHeaderField: "Authorization")
        }
        // all done
        return request
    }
}


// end of file
