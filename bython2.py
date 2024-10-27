#!/usr/bin/env python3

# Bython2 - A sequel to a very nice syntax.

import re
import sys
import os
import traceback
from pathlib import Path

# If you cant understand this then dont touch it
tokens = r"[rfm]?\"(?:.*?)\"|-?\d+(?:\.\d+)?|#[^\n]+|==?|!=|->|::|->|,|(?:>|<)=?|//?|\*\*?|\+|\-|\(|\)|\[|\]|{|}|\w+|;"

simple_builtins = {
    "print":print, "input":input,
    "str":str, "int":int, "float":float, "dict":dict,
    "map":map, "any":any, "filter":filter, "dir":dir
}

macros = {
    ":=": "=",
    "::": ".",
    "->": ":",
    "begin":"{",
    "end":("raw_insert", "}"),
    "module":"class",
    "constructor":"def __init__",
    "deconstructor":"def __del__",
    "__include_comments__":True # this is to add context to the generated python code
                                # use `#unset: __include_comments__` to disable it
}

def get_this(code):
    global tokens
    res = []
    for line, i in enumerate(code.split("\n"), 1):
        i = i.strip()
        if i.startswith("#macro:"):
            try:
                source, end = eval(i[7:].strip(), {'__builtins__':simple_builtins})
                if source == "print":
                    print(f"Macro Processing: Debug [line {line}]: {end}")
                else:
                    macros[source] = end
            except Exception as e:
                print(f"Macro Processing: MacroDef [line {line}]: {repr(e)}\nMake sure its: (\"macro_name\", \"macro\") or (\"macro_name\", (\"macro_action\", \"args\"))\nThis line: {i}")
        elif i.startswith("#def:"):
            source = i[5:].strip()
            macros[source] = True
        elif i.startswith("#unset:"):
            name = i[7:].strip()
            if name in macros:
                print(f"Macro Processing: Unset [line {line}]: {name}")
                macros.pop(name)
            else:
                print(f"Macro Processing [line {line}]: Tried to unset {name} but it wasnt defined.")
        elif i.startswith("#ADD_REGEX:"):
            result = eval(f"{repr(i[11:].strip())}", {'__builtins__':simple_builtins})
            tokens += "|" + result
        else:
            res.append(i)
    return "\n".join(res)

def tokenize(code):
    return re.findall(tokens, code, re.DOTALL)

setup_code = """#!/usr/bin/env python$version$
### THIS IS BIOLER PLATE TO BE ABLE TO IMPORT BYTHON2 DIRECTLY AND FOR BYTHON2 TO FUNCTION ###
import importlib.util
import sys
import os
import subprocess
_bython2_path = os.getenv("BYTHON2PATH");_python_major_version = $version$
if _bython2_path is None: raise Exception("BYTHON2PATH environment variable was not set.")
_bython2_cache_dir = os.path.join(os.getcwd(), "__by2cache__")
if not os.path.isdir(_bython2_cache_dir): os.mkdir(_bython2_cache_dir)
def import_module_by_path(module_path):
  if not os.path.isfile(module_path): raise FileNotFoundError(f"No such file: '{module_path}'")
  module_name = os.path.splitext(os.path.basename(module_path))[0];spec = importlib.util.spec_from_file_location(module_name, module_path);module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module);sys.modules[module_name] = module
  return module
bython_dependencies = []
class Bython2Importer:
  def __init__(self): self.search_paths = sys.path;self.module_cache = {};self.os = os;self.subprocess = subprocess;self.importlib = importlib
  def find_spec(self, fullname, path=None, target=None):
    module_name = fullname.split('.')[-1]
    if module_name in self.module_cache: return self.module_cache[module_name]
    by2_file = f"{module_name}.by2"
    py_file = f"{_bython2_cache_dir}{self.os.sep}{module_name}.py"
    if self.os.path.exists(by2_file):
      try: self.subprocess.run(['python3', _bython2_path, by2_file, py_file], check=True, stdout=self.subprocess.PIPE, stderr=self.subprocess.PIPE)
      except subprocess.CalledProcessError as e: print(f"Error compiling {by2_file}: {e}"); return None
      mod = self.module_cache[module_name] = self.importlib.util.spec_from_file_location(fullname, py_file);bython_dependencies.append(f"{module_name!r} is {py_file!r} in {_bython2_cache_dir!r}");return mod
    return None
sys.meta_path.insert(0, Bython2Importer())
### clean up so user doesnt f things up ###
del sys, Bython2Importer, os, importlib, subprocess
### BYTHON2 CONSTANTS ###
true=True;false=False;null=None;import __main__ as this
def safe_cast(type, might_be_type, default=None):
  try: return type(might_be_type)
  except: return default
### END OF SETUP CODE ###""".replace("$version$", str(sys.version).split(".", 1)[0])

def translate(code):
    code = tokenize(code)
    res = []
    line = []
    ind = 0
    for i in code:
        if i.startswith("#"): # preserve any comments to make the generated output somewhat readable
            # keeping this separate is very important.
            # this will avoid the need to "close" the comment with a semi.
            # # comment
            # code;
            # Instead of
            # # comment;
            # code;
            if "__include_comments__" in macros:
                res.append((ind, i))
        elif i == "{":
            line.append(":")
            res.append(((ind, ' '.join(line))))
            line.clear()
            ind += 1
        elif i == "}":
            # This is for when a case like
            # while True {print("Print forever!")}
            # Happens.
            # We add the line then we dedent.
            # See how we dont need a semi to denote the end of the line?
            if line:
                res.append(((ind, ' '.join(line))))
            if res[-1][0] != ind: # handle empty stuff
                res.append((ind, "pass"))
            line.clear()
            ind -= 1
        elif i == ";":
            if line:
                res.append(((ind, ' '.join(line))))
                line.clear()
        else:
            item = macros.get(i, i)
            if hasattr(item, "__call__"):
                item = str(item(i))
            if isinstance(item, tuple):
                match (item):
                    case ["indent"]:
                        ind += 1
                    case ["indent", "insert", thing]:
                        line.append(thing)
                        res.append((ind, " ".join(line)))
                        line.clear()
                        ind += 1
                    case ["insert", thing]:
                        line.append(thing)
                    case ["unindent"]:
                        res.append((ind, " ".join(line)))
                        line.clear()
                        ind -= 1
                    case ["unindent", "insert", thing]:
                        res.append((ind, " ".join(line)))
                        line.clear()
                        ind -= 1
                        res.append((ind, thing))
                        line.clear()
                        res.append((ind, " ".join(line)))
                    case ["raw_insert", thing]:
                        line.append(thing)
                        res.append((ind, " ".join(line)))
                        line.clear()
                    case ["line_end"]:
                        res.append((ind, " ".join(line)))
                        line.clear()
                    case _:
                        print(f"Translation: Translate Warning: Unknown macro action for {i}")
            else:
                if item.startswith('m"') and item.endswith('"'):
                    print(item)
                else:
                    line.append(item)
    if line:
        print("Translation: Translate Warning: The final line in the module level didnt end with a semi colon!")

    result = ""
    for indent, line in res:
        result += "\n"+"  "*indent+line
    if "__entry__" in macros:
        result += f"\n### GENERATED FROM __entry__ MACRO ###\nimport sys\nsys.exit({macros['__entry__']}(len(temp:=sys.argv), temp))"
    if "__standalone__" in macros:
        return f"#!/usr/bin/env python{str(sys.version).split('.', 1)[0]}\n### __standalone__ WAS SET AND THIS IS A NEAR PURE PYTHON SETUP ###\ntrue=True;false=False;null=None;import __main__ as this ### END OF SETUP CODE ###"+result
    else:
        return setup_code+result

def isby(file): # least straight forward function here
    return file.endswith(".by2")

def to_py(file):
    if isby(file):
        path = os.path.dirname(file)
        file = os.path.basename(file)
        new_file = os.path.join(path, file.rsplit(".", 1)[0]+".py")
        return new_file
    else:
        print(f"CLI: File `{file}` didnt end with `.by2` are you sure this is the right file?")
        return None

def main():
    if len(sys.argv) == 1:
        print("Bython2.0 - Python is cool but C is cooler.\nWant OOP? Dont use C++ use this instead!\nbython2.py [file] [output?]\n  If the output file is not given it will output to `file.py`\nFiles must have the `.by2` extension or it will reject it.")
    elif (argc:=len(sys.argv)) in {2, 3}:
        if argc == 3:
            _, name, output = sys.argv
            if not os.path.isfile(name):
                print(f"CLI: `{name}` is not a file!")
                return 1
        else:
            _, name = sys.argv
            if not os.path.isfile(name):
                print(f"CLI: `{name}` is not a file!")
                return 1
            output = to_py(name)
            if output is None:
                exit(2)
        try:
            with open(name, "r") as input_file:
                code = get_this(input_file.read())
                with open(output, "w") as output_file:
                    output_file.write(translate(code).strip())
        except:
            print("CLI: An error occurred:\n"+traceback.format_exc())
            return 2

if __name__ == "__main__":
    sys.exit(main())