import nuke
import nukescripts


class Callbacks(object):
    """
    Disable `Nuke` callbacks, once the action is complete re-enable the `Nuke`
    callbacks.
    """
    __slots__ = ("__backup", )
    _BACKUP_VARIABLE = "__backup"

    def __init__(self):
        self.__backup = getattr(nuke, self._BACKUP_VARIABLE, dict())

    def __call__(self, func):
        """ Method, Disable callback, execute function and re-enable callbacks"""
        if not callable(func):
            raise TypeError("Parem {} is not callable, please parse a callable object".format(func))

        with self:
            status = func()

        return status

    def __enter__(self):
        """ Disable callbacks. """
        for callback, functions in nuke.callbacks.__dict__.items():
            # We dont want to remove hidden attributes, also continue
            # if there are no functions assigned
            if callback.startswith("_") or not functions:
                continue

            # Adding to the back and setting empty callback
            self.__backup[callback] = functions
            setattr(nuke.callbacks, callback, {})

        # Save the backup data under the nuke module
        setattr(nuke, self._BACKUP_VARIABLE, self.__backup)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for callback, items in self.__backup.items():
            setattr(nuke.callbacks, callback, items)

        # Clear the backup and remove the nuke variable
        self.__backup = dict()
        # setattr(nuke, self._BACKUP_VARIABLE, {})
        del nuke.__dict__["__backup"]

    def begin(self):
        self.__enter__()

    def end(self):
        self.__exit__(None, None, None)

    def run(self, func):
        self.__call__(func)

    @staticmethod
    def decorator(func):
        return lambda: Callbacks().run(func)


class KeepSelected(object):
    """
    When running a snipped of code or an executable operation to maintain
    the current selected nodes, this class method will aid in the task.
    """
    __slots__ = ("append_node", "__selected")

    def __init__(self):
        self.append_node = False
        self.__selected = list()

    def __call__(self, func):
        """
        Method, runs the function and then maintain the original selected nodes
        unless the flag to append has been set to `True`
        """
        if not callable(func):
            raise TypeError("Parem {} is not callable, please parse a callable object".format(func))

        with self:
            status = func()

        return status

    def __enter__(self):
        """ Method, entering class."""
        self.__selected = nuke.selectedNodes()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Method, closing a class."""
        if self.append_node:
            self.__selected.extend(nuke.selectedNodes())

        for node in nuke.root().nodes():
            if node in self.__selected:
                node.setSelected(True)
            else:
                node.setSelected(False)

    def do(self, func):
        """ Method, same as `__call__`"""
        return self.__call__(func)
