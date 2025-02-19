# Bython2

Bython2 is a Python preprocessor that allows the use of curly braces `{}` to define code blocks, providing an alternative to Python's traditional indentation. This makes it easier for developers accustomed to other languages that use braces to delimit blocks.

## Features

- **Curly braces syntax**: Uses `{}` instead of indentation to define code blocks.
- **Compatibility**: Fully compatible with existing Python modules and libraries.
- **Bidirectional conversion**: Included tools to convert Python code to Bython and vice versa.

## Installation

You can install Bython2 directly from PyPI using pip:

```bash
pip install bython2
```

## Basic Usage

Once installed, you can execute `.by` files with the following command:

```bash
bython file.by
```

For example, if you have an `example.by` file:

```python
# example.by
def greet(name) {
  print(f"Hello, {name}!")
}

if __name__ == "__main__" {
  greet("World")
}
```

Run:

```bash
bython example.by
```

## File Conversion

Bython2 includes tools to convert Python code to Bython and vice versa.

- **From Python to Bython**:

  ```bash
  py2by file.py
  ```

  This will generate a `file.by` with Bython syntax.

- **From Bython to Python**:

  ```bash
  by2py file.by
  ```

  This will generate a `file.py` with standard Python syntax.

## Module Import

Bython2 handles module imports efficiently:

- **Importing Bython modules in Bython code**: Simply use the standard `import` statement. Bython2 will detect and process the corresponding `.by` modules.

- **Importing Python modules in Bython code**: No additional steps required; you can import Python modules as you would normally.

- **Importing Bython modules in Python code**: Use the `bython_import` function from the `bython.importing` module:

  ```python
  from bython.importing import bython_import
  module = bython_import("module_name")
  ```

