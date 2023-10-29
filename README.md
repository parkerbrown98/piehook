# PieHook - A Simple Hook Library

This is a library / lightweight framework intended to help supplement the development
of event-driven software in Python. Using a simple decorator, you can define
a function hook that can be called anywhere within your code base.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Basic Usage](#basic-usage)

## Features

- Simple decorator for defining function hooks
- Call hooks from anywhere in your code base
- Set hook priority level
- Pass *args and **kwargs
- Basic logging and verbose mode for debugging
- CLI for running, testing, and creating hooks
- **Coming soon:** Async support

## Installation

`pip install piehook`

## Basic Usage

All hooks are registered using the current project directory (unless otherwise specified). See `import_hooks` for options.

Files suffixed with `_hooks.py` will automatically be registered with the hook system when `import_hooks` is called. 

The default file suffix can be changed via the `file_suffix` argument when using `import_hooks`.

### Creating Hooks

```py
# example_hooks.py
from piehook import hooks

@hooks.add('my_event')
def some_event(a, b):
  print('some_event:', a + b)

@hooks.add('my_event', priority=20)
def some_other_event(a, b):
  print('some_other_event:', a - b)
```

Distribute hooks across modules for better organization:

```py
# another_example_hooks.py
from piehook import hooks

@hooks.add('my_event', priority=5)
def another_event(a, b):
  print('another_event:', a * b)
```

### Calling Hooks

```py
# main.py
from piehook import hooks

# Only required once
hooks.import_hooks()

# Optionally set vorbose flag
hooks.set_verbose(True)

print('Calling my_event hooks:')

# Call hooks from anywhere
hooks.run('my_event', 5, 3)
```

### Sample Output

```
Calling my_event hooks:
some_other_event: 2
another_event: 15
some_event: 8
```

