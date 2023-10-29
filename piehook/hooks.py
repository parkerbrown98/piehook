import heapq
import importlib
import os
import sys
import logging
import asyncio

from collections import defaultdict


class HookManager:
    """
    A manager for synchronous and asynchronous hooks in a Python application.
    """

    def __init__(self, verbose=False):
        """
        Initialize the HookManager.

        Args:
            verbose (bool): If True, set the logging level to DEBUG, otherwise set to INFO.
        """
        self.imported_hooks = set()
        self._hooks = defaultdict(list)
        self._async_hooks = defaultdict(list)
        self._index = 0

        # Setup logging
        self.logger = logging.getLogger('piehook')
        self.logger.setLevel(logging.INFO if not verbose else logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO if not verbose else logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def set_verbose(self, verbose):
        """
        Set the verbose level of the logger.

        Args:
            verbose (bool): If True, set the logging level to DEBUG, otherwise set to INFO.
        """
        self.logger.setLevel(logging.INFO if not verbose else logging.DEBUG)
        handler = self.logger.handlers[0]
        handler.setLevel(logging.INFO if not verbose else logging.DEBUG)

    def run(self, id, *args, **kwargs):
        """
        Run all hooks (both synchronous and asynchronous) associated with the given id.

        Args:
            id (str): The identifier for the hooks to be run.
            *args: Positional arguments to be passed to the hooks.
            **kwargs: Keyword arguments to be passed to the hooks.
        """
        funcs = [func for _, _, func in sorted(self._hooks[id], reverse=True)]
        async_funcs = [func for _, _, func in sorted(self._async_hooks[id], reverse=True)]

        self.logger.info(f"Running {len(funcs) + len(async_funcs)} hooks for {id}")

        for func in funcs:
            func(*args, **kwargs)

        if async_funcs:
            asyncio.run(self._run_async_hooks(async_funcs, *args, **kwargs))
        
    async def _run_async_hooks(self, hooks, *args, **kwargs):
        """
        Run all asynchronous hooks.

        Args:
            hooks (list): A list of asynchronous hooks to be run.
            *args: Positional arguments to be passed to the hooks.
            **kwargs: Keyword arguments to be passed to the hooks.
        """
        await asyncio.gather(*(hook(*args, **kwargs) for hook in hooks))

    def add(self, id, priority=0, is_async=False):
        """
        Add a hook with the given id and priority. The hook can be either synchronous or asynchronous.

        Args:
            id (str): The identifier for the hook.
            priority (int): The priority of the hook. Hooks with lower priority values are run first.
            is_async (bool): If True, the hook is asynchronous, otherwise it is synchronous.

        Returns:
            function: A decorator that adds the decorated function as a hook.
        """
        def decorator(func):
            if is_async:
                heapq.heappush(self._async_hooks[id], (priority, self._index, func))
            else:
                heapq.heappush(self._hooks[id], (priority, self._index, func))
            self._index += 1
            return func
        return decorator

    def remove(self, id, func):
        """
        Remove a hook with the given id and function.

        Args:
            id (str): The identifier for the hook.
            func (function): The function to be removed as a hook.
        """
        self._hooks[id] = [hook for hook in self._hooks[id] if hook[2] != func]
        self._async_hooks[id] = [hook for hook in self._async_hooks[id] if hook[2] != func]

    def import_hooks(self, root_path=None, file_suffix='_hooks'):
        """
        Import all hooks from files with a given suffix in a directory.

        Args:
            root_path (str): The root path to search for hook files. If None, use the path of the main module.
            file_suffix (str): The suffix for hook files. Files with names ending in this suffix will be imported.
        """
        if root_path is None:
            main_module = sys.modules['__main__']
            root_path = os.path.dirname(os.path.abspath(main_module.__file__))

        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith(f'{file_suffix}.py'):
                    mod_name = os.path.relpath(os.path.join(root, file), root_path).replace(os.sep, '.')[:-3]
                    old_hook_count = len(self.imported_hooks)
                    if mod_name not in self.imported_hooks:
                        importlib.import_module(mod_name)
                        self.imported_hooks.add(mod_name)
                        new_hook_count = len(self.imported_hooks)
                        self.logger.info(f"Imported {new_hook_count - old_hook_count} hook(s) from {mod_name}")


hooks = HookManager()
