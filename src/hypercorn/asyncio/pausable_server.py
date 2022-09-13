import asyncio
import typing
from asyncio import AbstractEventLoop


class PausableServer(asyncio.base_events.Server):
    _loop: AbstractEventLoop
    _active_count: int = 0
    _max_connections: typing.Optional[int] = None
    _paused: bool = False
    _serving: bool = False

    def set_max_connections(self, value: int) -> None:
        self._max_connections = value

    def _attach(self):
        super()._attach() # noqa
        print("attached")
        if self._max_connections is not None and not self._paused and self._active_count >= self._max_connections:
            self.pause()

    def _detach(self):
        super()._detach() # noqa
        print("dettached")
        if self._paused and self._max_connections is not None and self._active_count < self._max_connections:
            self.resume()

    def pause(self):
        """Pause future calls to accept()."""
        assert not self._paused
        self._paused = True
        self._serving = False
        for sock in self.sockets:
            self._loop.remove_reader(sock.fileno())

    def resume(self):
        """Resume use of accept() on listening socket(s)."""
        assert self._paused
        self._paused = False
        self._start_serving() # noqa