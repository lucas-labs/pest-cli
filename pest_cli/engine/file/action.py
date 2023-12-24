from pathlib import Path
from typing import Callable, Literal, Required, Self, TypeAlias, TypedDict, TypeGuard

__ID: int = 1


class UnknownActionException(Exception):
    def __init__(self, action: 'Action'):
        kind = action.get('kind')
        super().__init__(f'Unknown action: "{kind}".')


class ActionBase(TypedDict, total=False):
    id: int | None
    parent: int
    path: Required[Path]


class CreateFileAction(ActionBase, TypedDict):
    kind: Literal['c']
    content: bytes


class OverwriteFileAction(ActionBase, TypedDict):
    kind: Literal['o']
    content: bytes


class RenameFileAction(ActionBase, TypedDict):
    kind: Literal['r']
    to: Path


class DeleteFileAction(ActionBase, TypedDict):
    kind: Literal['d']


def is_create_action(action: 'Action') -> TypeGuard[CreateFileAction]:
    return action['kind'] == 'c'


def is_overwrite_action(action: 'Action') -> TypeGuard[OverwriteFileAction]:
    return action['kind'] == 'o'


def is_rename_action(action: 'Action') -> TypeGuard[RenameFileAction]:
    return action['kind'] == 'r'


def is_delete_action(action: 'Action') -> TypeGuard[DeleteFileAction]:
    return action['kind'] == 'd'


def is_content_action(action: 'Action') -> TypeGuard[CreateFileAction | OverwriteFileAction]:
    return is_create_action(action) or is_overwrite_action(action)


Action: TypeAlias = CreateFileAction | OverwriteFileAction | RenameFileAction | DeleteFileAction


class ActionList:
    def __init__(self) -> None:
        self._actions: list[Action] = []

    def _action(self, action: Action) -> None:
        global __ID
        __ID += 1
        act: Action = action.copy()
        parent = self._actions[-1].get('id', 0) or 0 if self._actions else 0
        act.update(
            {
                'id': __ID,
                'parent': parent,
            }
        )

        self._actions.append(act)

    def __iter__(self) -> Self:
        self._index = 0
        return self

    def __next__(self) -> Action:
        if self._index < len(self._actions):
            result = self._actions[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration

    def create(self, path: Path, content: bytes) -> None:
        self._action({'kind': 'c', 'path': path, 'content': content})

    def overwrite(self, path: Path, content: bytes) -> None:
        self._action({'kind': 'o', 'path': path, 'content': content})

    def rename(self, path: Path, to: Path) -> None:
        self._action({'kind': 'r', 'path': path, 'to': to})

    def delete(self, path: Path) -> None:
        self._action({'kind': 'd', 'path': path})

    def optimize(self) -> None:
        toCreate = {}
        toRename = {}
        toOverwrite = {}
        toDelete = set()

        for action in self._actions:
            path = action['path']
            if is_create_action(action):
                toCreate[path] = action['content']
            elif is_overwrite_action(action):
                if path in toCreate:
                    toCreate[path] = action['content']
                else:
                    toOverwrite[path] = action['content']
            elif is_delete_action(action):
                toDelete.add(path)
            elif is_rename_action(action):
                if path in toCreate:
                    toCreate.pop(path)
                    toCreate[action['to']] = toCreate[path]
                if path in toOverwrite:
                    toOverwrite.pop(path)
                    toOverwrite[action['to']] = toOverwrite[path]

                for from_, to in toRename.items():
                    if to == path:
                        toRename[from_] = action['to']
                        break
                else:
                    toRename[path] = action['to']
            else:
                raise UnknownActionException(action)

        self._actions = []
        for path in toDelete:
            self.delete(path)

        for from_, to in toRename.items():
            self.rename(from_, to)

        for path, content in toCreate.items():
            self.create(path, content)

        for path, content in toOverwrite.items():
            self.overwrite(path, content)

    def push(self, action: Action) -> None:
        self._actions.append(action)

    def get(self, i: int) -> Action:
        return self._actions[i]

    def has(self, action: Action) -> bool:
        action_id = action.get('id')
        if not action_id:
            return False
        for i in range(len(self._actions)):
            i_action_id = self._actions[i].get('id')
            if not i_action_id:
                continue
            if i_action_id == action_id:
                return True
            if i_action_id > action_id:
                return False
        return False

    def find(self, predicate: Callable[[Action], bool]) -> Action | None:
        return next(filter(predicate, self._actions), None)

    def for_each(self, fn: Callable[[Action, int, list[Action]], None]) -> None:
        for i, action in enumerate(self._actions):
            fn(action, i, self._actions)

    def __len__(self) -> int:
        return len(self._actions)

    def __getitem__(self, index: int) -> Action:
        return self._actions[index]

    def __setitem__(self, index: int, value: Action) -> None:
        self._actions[index] = value

    def __delitem__(self, index: int) -> None:
        del self._actions[index]

    def __contains__(self, action: Action) -> bool:
        return self.has(action)

    def __reversed__(self) -> Self:
        self._actions.reverse()
        return self

    def __add__(self, other: Self) -> 'ActionList':
        result = ActionList()
        result._actions = self._actions + other._actions
        return result

    def __iadd__(self, other: Self) -> Self:
        self._actions += other._actions
        return self
