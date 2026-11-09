#!/bin/bash
# Build TerminalSBX.dylib for iOS arm64.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="$(xcrun --sdk iphoneos --show-sdk-path)"
mkdir -p "$ROOT/build"
xcrun --sdk iphoneos clang \
  -arch arm64 -miphoneos-version-min=15.0 -isysroot "$SDK" \
  -dynamiclib -fobjc-arc -fmodules -fblocks -O2 \
  -Wno-unused-parameter -Wno-arc-performSelector-leaks \
  -framework Foundation -framework Security -framework UIKit -framework Metal \
  -install_name @executable_path/Frameworks/TerminalSBX.dylib \
  -o "$ROOT/build/TerminalSBX.dylib" "$ROOT/src/TerminalSBX.m"
echo "$ROOT/build/TerminalSBX.dylib"
