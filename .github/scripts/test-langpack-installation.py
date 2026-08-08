#!/usr/bin/env python3

"""
Test langpack installation structure to prevent Bug 1994920 regression.

BACKGROUND - Bug 1994920:
Firefox 144.0-2 langpacks broke because the snap build script created
directory names like "locale-fr.xpi" instead of "locale-fr". This caused
Firefox's addon system to extract the wrong ID from the path and reject
langpacks with "incorrect ID" error, forcing users to English.

ROOT CAUSE:
The snap build script used `basename $XPI .langpack.xpi` but files were
named "fr.xpi" (not "fr.langpack.xpi"), so the suffix wasn't removed,
resulting in directories named "locale-fr.xpi" instead of "locale-fr".

HOW FIREFOX LOADS LANGPACKS (XPIProvider.sys.mjs):
1. Scans /distribution/extensions/locale-LANGCODE/ directories
2. For each .xpi file, extracts expected ID from filename (strips .xpi)
   Example: "langpack-fr@firefox.mozilla.org.xpi" → "langpack-fr@firefox.mozilla.org"
3. Opens the XPI (ZIP file) and reads manifest.json to get actual addon ID
4. Compares IDs: if expected_id != actual_id, REJECTS with error

EXAMPLE OF THE BUG:
Wrong: /distribution/extensions/locale-fr.xpi/langpack-fr@firefox.mozilla.org.xpi
       Firefox extracts ID: "langpack-fr.xpi@firefox.mozilla.org" ❌
       Manifest contains:   "langpack-fr@firefox.mozilla.org" ❌
       Result: ID mismatch → REJECTED!

Right: /distribution/extensions/locale-fr/langpack-fr@firefox.mozilla.org.xpi
       Firefox extracts ID: "langpack-fr@firefox.mozilla.org" ✅
       Manifest contains:   "langpack-fr@firefox.mozilla.org" ✅
       Result: Match → Loaded successfully!

WHAT THIS TEST VALIDATES:
1. Directory names are "locale-LANGCODE" (correct format exists)
2. File names are "langpack-LANGCODE@firefox.mozilla.org.xpi"
3. XPI files are valid ZIP archives
4. manifest.json exists and is valid JSON
5. Addon ID in manifest matches expected ID from filename
6. Firefox will successfully load the langpacks

USAGE:
  python3 test-langpack-installation.py [snap_directory]

  Default: /snap/firefox/current
  Example: python3 test-langpack-installation.py /snap/firefox/1234

TESTED LANGUAGES:
Tests the 10 most common Firefox locales: de, fr, es-ES, ja, zh-CN,
pt-BR, ru, it, pl, en-GB
"""

import json
import os
import sys
import zipfile
from pathlib import Path


# Primary languages to test (subset of most common languages)
PRIMARY_LANGCODES = [
    'de', 'fr', 'es-ES', 'ja', 'zh-CN', 'pt-BR', 'ru', 'it', 'pl', 'en-GB'
]


def test_langpack_installation(snap_dir='/snap/firefox/current'):
    """Test that langpacks are installed in correct directory structure."""

    extensions_dir = Path(snap_dir) / 'usr/lib/firefox/distribution/extensions'

    print("Testing langpack installation structure...")
    print(f"Extensions directory: {extensions_dir}")
    print()

    if not extensions_dir.exists():
        print(f"❌ ERROR: Extensions directory does not exist: {extensions_dir}")
        return False

    passed = 0
    failed = 0
    missing = 0
    errors = []

    for langcode in PRIMARY_LANGCODES:
        locale_dir = extensions_dir / f'locale-{langcode}'
        langpack_file = locale_dir / f'langpack-{langcode}@firefox.mozilla.org.xpi'

        # Check if locale directory exists (without .xpi suffix)
        if not locale_dir.is_dir():
            print(f"⚠️  SKIP: Directory {locale_dir} not found (langpack may not be built)")
            missing += 1
            continue

        # Check if langpack file exists
        if not langpack_file.is_file():
            error = f"Langpack {langpack_file} not found in locale directory"
            print(f"❌ FAIL: {error}")
            errors.append(error)
            failed += 1
            continue

        # Verify filename structure
        expected_id = f'langpack-{langcode}@firefox.mozilla.org'
        basename = langpack_file.stem  # filename without .xpi

        if basename != expected_id:
            error = f"Langpack has wrong name. Expected: {expected_id}, Got: {basename}"
            print(f"❌ FAIL: {error}")
            errors.append(error)
            failed += 1
            continue

        # Verify addon ID in manifest matches filename
        try:
            with zipfile.ZipFile(langpack_file, 'r') as xpi:
                manifest_data = xpi.read('manifest.json')
                manifest = json.loads(manifest_data)

                # Extract addon ID from manifest
                addon_id = manifest.get('browser_specific_settings', {}).get('gecko', {}).get('id')
                if not addon_id:
                    # Try legacy applications field
                    addon_id = manifest.get('applications', {}).get('gecko', {}).get('id')

                if not addon_id:
                    error = f"Could not find addon ID in manifest for {langcode}"
                    print(f"❌ FAIL: {error}")
                    errors.append(error)
                    failed += 1
                    continue

                # Compare with expected ID
                if addon_id != expected_id:
                    error = f"Addon ID mismatch for {langcode}. Expected: {expected_id}, Got: {addon_id}"
                    print(f"❌ FAIL: {error}")
                    print(f"        Firefox will reject this langpack")
                    errors.append(error)
                    failed += 1
                    continue

        except zipfile.BadZipFile:
            error = f"Langpack {langpack_file} is not a valid ZIP file"
            print(f"❌ FAIL: {error}")
            errors.append(error)
            failed += 1
            continue
        except json.JSONDecodeError as e:
            error = f"Could not parse manifest.json for {langcode}: {e}"
            print(f"❌ FAIL: {error}")
            errors.append(error)
            failed += 1
            continue
        except Exception as e:
            error = f"Error reading {langpack_file}: {e}"
            print(f"❌ FAIL: {error}")
            errors.append(error)
            failed += 1
            continue

        print(f"✅ PASS: {langcode} langpack correctly installed")
        print(f"        Directory: locale-{langcode}/")
        print(f"        File: langpack-{langcode}@firefox.mozilla.org.xpi")
        print(f"        Addon ID: {addon_id}")
        passed += 1

    # Print summary
    print()
    print("=" * 60)
    print("Results:")
    print(f"  ✅ Passed:  {passed}")
    print(f"  ❌ Failed:  {failed}")
    print(f"  ⚠️  Skipped: {missing} (langpacks not built for these locales)")
    print("=" * 60)

    if failed > 0:
        print()
        print("❌ LANGPACK INSTALLATION TEST FAILED")
        print()
        print("This indicates a regression of Bug 1994920 or similar issue.")
        print("Firefox requires:")
        print("  1. Directory names: locale-LANGCODE (no .xpi suffix)")
        print("  2. File names: langpack-LANGCODE@firefox.mozilla.org.xpi")
        print("  3. Addon ID (from manifest): langpack-LANGCODE@firefox.mozilla.org")
        print()
        print("Errors encountered:")
        for error in errors:
            print(f"  - {error}")
        print()
        return False

    if passed == 0:
        print()
        print("⚠️  WARNING: No langpacks found to test")
        print("This may indicate the langpacks part did not build correctly")
        return False

    print()
    print("✅ ALL LANGPACK INSTALLATION TESTS PASSED")
    return True


if __name__ == '__main__':
    snap_dir = sys.argv[1] if len(sys.argv) > 1 else '/snap/firefox/current'

    success = test_langpack_installation(snap_dir)
    sys.exit(0 if success else 1)
