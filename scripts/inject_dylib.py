#!/usr/bin/env python3
"""Inject a weak LC_LOAD_DYLIB into the a-Shell main binary with LIEF."""
import sys
import lief

if len(sys.argv) != 3:
    raise SystemExit("usage: inject_dylib.py <main-binary> <dylib-path>")

path, dylib = sys.argv[1], sys.argv[2]
binary = lief.MachO.parse(path).at(0)
if dylib in [lib.name for lib in binary.libraries]:
    print("already present")
    raise SystemExit(0)
command = lief.MachO.DylibCommand.weak_lib(dylib)
result = binary.add(command)
binary.write(path)
print(result)
