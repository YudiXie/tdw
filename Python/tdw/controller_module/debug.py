from pathlib import Path
from typing import List, Union
from json import load, dump
from tdw.controller_module.controller_module import ControllerModule


class Debug(ControllerModule):
    """
    Use this module to record and playback every command sent to the build.
    """

    def __init__(self, record: bool, path: Union[str, Path]):
        """
        :param record: If True, record each command. If False, play back an existing record.
        :param path: The path to either save the record to or load the record from.
        """

        super().__init__()

        # We don't need to initialize anything.
        self.initialized = True

        self._record: bool = record

        # Get or create the playback file path.
        if isinstance(path, str):
            self._path: Path = Path(path)
        else:
            self._path: Path = path
        if not path.parent.exists:
            path.parent.mkdir(parents=True)

        # Start a new playback file.
        if self._record:
            """:field
            A record of each list of commands sent to the build.
            """
            self._playback: List[List[dict]] = list()
        # Load an existing .json file.
        else:
            with path.open("rt", encoding="utf-8") as f:
                self._playback = load(f)

    def on_communicate(self, resp: List[bytes], commands: List[dict]) -> None:
        # Record the commands that were just sent.
        if self._record:
            self._playback.append(commands[:])
        # Prepare to send the next list of commands.
        else:
            if len(self._playback) > 0:
                self.commands = self._playback.pop(0)

    def get_initialization_commands(self) -> List[dict]:
        return []

    def save(self) -> None:
        """
        Write the record of commands sent to the local disk.
        """

        with self._path.open("wt", encoding="utf-8") as f:
            dump(self.commands, f)
