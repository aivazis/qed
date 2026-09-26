# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import errno
import functools
import socket

# support
import qed

# the channel that carries the requests
from pyre.ipc.SocketTCP import SocketTCP

# the unit of the deadlines
from pyre.units.SI import second


# declaration
class TileClient:
    """
    One of the concurrent clients of a swarm: it fetches the tiles it takes off a shared
    {queue} one at a time, each over a connection of its own, on the pyre event loop, and
    keeps the latency of every tile it gets and a count of the ones it does not
    """

    # interface
    def start(self) -> "TileClient":
        """
        Take the first tile off the queue
        """
        # get going
        self._next()
        # all done
        return self

    # metamethods
    def __init__(
        self,
        *,
        index: int,
        host: str,
        port: int,
        selector,
        queue,
        patience: float,
        onDone,
        **kwds,
    ) -> None:
        # chain up
        super().__init__(**kwds)
        # the server
        self.host = host
        self.port = port
        # the event loop that drives me
        self.selector = selector
        # the tiles, as request paths, shared with the other clients
        self.queue = queue
        # how long a tile may take, in seconds, before it counts as a failure
        self.patience = patience
        # whom to tell when the queue runs dry
        self.onDone = onDone
        # my clock; the registry shares a timer by name, so each client has a name of its own
        self.clock = qed.timers.wall(f"qed.measure.swarm.client{index}")
        # the latencies of the tiles i got, in milliseconds
        self.latencies = []
        # and the number of tiles i did not get
        self.failures = 0
        # the connection of the tile in flight, if any
        self._socket = None
        # the bytes of the request still to send, and of the response received so far
        self._request = b""
        self._response = b""
        # the length of the body, once the headers say
        self._length = None
        # and the offset of the body in the response, once the headers are in
        self._body = None
        # the number of the tile in flight, so a deadline can tell whether it is stale
        self._serial = 0
        # all done
        return

    # implementation details
    def _next(self) -> None:
        """
        Take the next tile off the queue and connect to the server for it, or report that
        the queue ran dry
        """
        # if there is nothing left to fetch
        if not self.queue:
            # say i am done
            self.onDone(self)
            # and stop
            return
        # take the next tile
        path = self.queue.popleft()
        # assemble its request; the connection carries this tile only
        self._request = (
            f"GET {path} HTTP/1.1\r\nHost: {self.host}:{self.port}\r\n" "Connection: close\r\n\r\n"
        ).encode("ascii")
        # forget the previous response
        self._response = b""
        self._length = None
        self._body = None
        # number the tile
        self._serial += 1
        # the latency covers the whole round trip, connection included
        self.clock.reset()
        self.clock.start()
        # make a connection
        self._socket = SocketTCP()
        # that does not block
        self._socket.setblocking(False)
        # start connecting
        status = self._socket.connect_ex((self.host, self.port))
        # anything but a connection under way is a failure
        if status not in (0, errno.EINPROGRESS, errno.EWOULDBLOCK):
            # so record it
            self._finish(ok=False)
            # and move on
            return
        # send the request once the connection can take it
        self.selector.whenWriteReady(channel=self._socket, call=self._send)
        # and give up on the tile if it takes too long
        self.selector.alarm(
            interval=self.patience * second,
            call=functools.partial(self._overdue, serial=self._serial),
        )
        # all done
        return

    def _send(self, channel, **kwds) -> bool:
        """
        Send what is left of the request, and wait for the response once it is all out
        """
        # a connection that failed to come up says so here
        if channel.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR):
            # so record the failure
            self._finish(ok=False)
            # and stop watching
            return False
        # attempt to
        try:
            # send as much as the connection will take
            sent = channel.send(self._request)
        # if it will take nothing right now
        except BlockingIOError:
            # try again later
            return True
        # if the connection broke
        except OSError:
            # record the failure
            self._finish(ok=False)
            # and stop watching
            return False
        # keep what did not make it
        self._request = self._request[sent:]
        # if some of the request is left
        if self._request:
            # send it when there is room
            return True
        # otherwise, wait for the response
        self.selector.whenReadReady(channel=channel, call=self._receive)
        # and stop watching for room
        return False

    def _receive(self, channel, **kwds) -> bool:
        """
        Collect the response, and finish the tile once it is complete
        """
        # attempt to
        try:
            # read what has arrived
            chunk = channel.recv(1 << 16)
        # if nothing has, after all
        except BlockingIOError:
            # wait for more
            return True
        # if the connection broke
        except OSError:
            # record the failure
            self._finish(ok=False)
            # and stop watching
            return False
        # if the server closed the connection
        if not chunk:
            # the response is whatever arrived, and it is good if it is whole
            self._finish(ok=self._whole(closed=True))
            # and there is nothing more to watch
            return False
        # otherwise, add it to the response
        self._response += chunk
        # if the response is whole
        if self._whole(closed=False):
            # the tile is in
            self._finish(ok=True)
            # and there is nothing more to watch
            return False
        # otherwise, wait for more
        return True

    def _whole(self, closed: bool) -> bool:
        """
        Decide whether the response is a complete, successful answer; a server that {closed}
        the connection has said all it will say
        """
        # if the headers are not in yet
        if self._body is None:
            # look for their end
            end = self._response.find(b"\r\n\r\n")
            # if they are still not in
            if end < 0:
                # the response is not whole
                return False
            # the body starts past them
            self._body = end + 4
            # split them into lines
            lines = self._response[:end].decode("latin-1").split("\r\n")
            # an answer other than a success is not a tile
            if lines[0].split()[1:2] != ["200"]:
                # so mark the response as a failure
                self._length = -1
                # that is complete
                return True
            # go through the headers
            for line in lines[1:]:
                # split each one
                name, _, value = line.partition(":")
                # the length of the body, if the server says
                if name.strip().lower() == "content-length":
                    # remember it
                    self._length = int(value.strip())
        # an answer that is not a success is complete as soon as its headers are in
        if self._length == -1:
            # and {_finish} records it as a failure
            return True
        # the body so far
        got = len(self._response) - self._body
        # with a stated length, the body is whole when it is all there
        if self._length is not None:
            # so compare
            return got >= self._length
        # without one, the body is whatever arrived before the server closed the connection
        return closed

    def _finish(self, ok: bool) -> None:
        """
        Record the tile in flight as a success or a failure, and move on to the next one
        """
        # a response whose status was not a success is a failure, however it ended
        ok = ok and self._length != -1
        # stop the clock
        self.clock.stop()
        # if the tile came in
        if ok:
            # record its latency
            self.latencies.append(self.clock.ms())
        # otherwise
        else:
            # count the failure
            self.failures += 1
        # let go of the connection
        self._socket.close()
        # and forget it
        self._socket = None
        # take the next tile
        self._next()
        # all done
        return

    def _overdue(self, timestamp, serial: int) -> None:
        """
        The deadline of tile number {serial} has passed

        N.B.: this is an alarm handler; returning {None} keeps it from being rescheduled
        """
        # if the tile in flight is a different one, this deadline is moot
        if serial != self._serial or self._socket is None:
            # so leave it alone
            return None
        # otherwise, the tile took too long, which is a failure; the event loop forgets the
        # registrations of the connection once it is closed
        self._finish(ok=False)
        # and the alarm is done
        return None


# end of file
