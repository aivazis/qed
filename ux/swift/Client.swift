// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Foundation


/// Run GraphQL operations against a qed server
struct Client: Sendable {
    // the server that answers
    let server: Server

    /// Run {operation} and hand back its answer
    func run<Answer>(_ operation: Operation<Answer>) async throws -> Answer {
        // spell out the request
        let body = try JSONEncoder().encode(
            Request(operationName: operation.name, query: operation.text))
        // post it, and read the answer
        return try Client.decode(Answer.self, from: try await post(body))
    }

    /// Run {mutation} on {input} and hand back its answer
    func run<Input, Answer>(_ mutation: Mutation<Input, Answer>, input: Input) async throws -> Answer {
        // spell out the request, post it, and read the answer
        return try Client.decode(
            Answer.self, from: try await post(Client.encode(mutation, input: input)))
    }

    /// Spell out the request that runs {mutation} on {input}
    static func encode<Input, Answer>(
        _ mutation: Mutation<Input, Answer>, input: Input
    ) throws -> Data {
        // the input travels as the variable {input}, which is how every mutation declares it
        return try JSONEncoder().encode(
            Change(
                operationName: mutation.name, query: mutation.text,
                variables: Variables(input: input)))
    }

    /// Post the request in {body} to the server and hand back what it sends
    private func post(_ body: Data) async throws -> Data {
        // post the request, as json, asking for json back
        var request = server.request(for: "graphql", accept: "application/json")
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = body
        // send it
        let (data, response) = try await URLSession.shared.data(for: request)
        // anything other than a plain success has no answer to read
        let status = (response as? HTTPURLResponse)?.statusCode ?? 0
        guard status == 200 else {
            throw ClientError.status(status)
        }
        // all done
        return data
    }

    /// Read the answer of type {answer} out of the {data} a server sent back
    static func decode<Answer: Decodable>(_ answer: Answer.Type, from data: Data) throws -> Answer {
        // unpack the envelope every GraphQL answer comes in
        let envelope = try JSONDecoder().decode(Envelope<Answer>.self, from: data)
        // a server that reports errors has not answered
        if let errors = envelope.errors, !errors.isEmpty {
            throw ClientError.refused(errors.map(\.message))
        }
        // and one that sent no data has nothing to say
        guard let answer = envelope.data else {
            throw ClientError.empty
        }
        // all done
        return answer
    }

    // what a request carries
    private struct Request: Encodable {
        let operationName: String
        let query: String
    }

    // what a request for a change carries: the request, and the input of the mutation
    private struct Change<Input: Encodable>: Encodable {
        let operationName: String
        let query: String
        let variables: Variables<Input>
    }

    // the variables of a mutation: its input, under the name every mutation gives it
    private struct Variables<Input: Encodable>: Encodable {
        let input: Input
    }

    // what an answer comes in
    private struct Envelope<Answer: Decodable>: Decodable {
        let data: Answer?
        let errors: [Problem]?
    }

    // an error the server reports, of which the app reads the message
    private struct Problem: Decodable {
        let message: String
    }
}


/// The ways an operation can fail to get an answer
enum ClientError: Error, Equatable {
    // the server answered with something other than a plain success
    case status(Int)
    // the server reported errors instead of an answer
    case refused([String])
    // the server sent neither an answer nor errors
    case empty
}


// end of file
