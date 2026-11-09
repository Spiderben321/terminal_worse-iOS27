#!/bin/bash
# Reference signing pass: sign every framework with the same team, then the
# app with the supplied entitlements and provisioning profile.
#
# Usage:
#   IDENTITY=... KEYCHAIN=... PROFILE=... ./sign_all.sh work/Terminal.app
set -euo pipefail
APP="${1:-work/Terminal.app}"
IDENTITY="${IDENTITY:?set IDENTITY}"
KEYCHAIN="${KEYCHAIN:-$HOME/Library/Keychains/login.keychain-db}"
ENT="${ENT:-scripts/ent.plist}"
PROFILE="${PROFILE:?set PROFILE}"

find "$APP/Frameworks" "$APP/usr" "$APP/Library" -type f \
  \( -name '*.dylib' -o -name '*.so' -o -perm -111 \) -print0 2>/dev/null |
while IFS= read -r -d '' f; do
  file -b "$f" | grep -q 'Mach-O' || continue
  codesign --force --sign "$IDENTITY" --keychain "$KEYCHAIN" --timestamp=none "$f"
done

find "$APP/Frameworks" -type d -name '*.framework' -print |
  awk '{ print length($0) "\t" $0 }' | sort -rn | cut -f2- |
while IFS= read -r fw; do
  codesign --force --sign "$IDENTITY" --keychain "$KEYCHAIN" --timestamp=none "$fw"
done

for appex in "$APP"/PlugIns/*.appex; do
  [ -d "$appex" ] || continue
  cp "$PROFILE" "$appex/embedded.mobileprovision"
  codesign --force --sign "$IDENTITY" --keychain "$KEYCHAIN" \
    --entitlements "$ENT" --generate-entitlement-der --timestamp=none "$appex"
done

cp "$PROFILE" "$APP/embedded.mobileprovision"
codesign --force --sign "$IDENTITY" --keychain "$KEYCHAIN" \
  --entitlements "$ENT" --generate-entitlement-der --timestamp=none "$APP"
codesign --verify --strict --verbose=2 "$APP"
