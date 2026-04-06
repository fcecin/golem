# How concerns.txt was built

The concerns.txt file in cart-logos-delivery-styler was extracted from the
Status Nim style guide (status-im/nim-style-guide) in a semi-manual process.

## Process used

1. Cloned the style guide repo into the cart's material/nim-style-guide/
2. Read SUMMARY.md to get the chapter list
3. Used a Claude agent to read every .md file and extract actionable,
   per-file-checkable rules — skipping tooling/interop chapters
4. Each rule became one line in concerns.txt with:
   - A short name
   - A description referencing the source file
   - A verify command (grep pattern) where mechanically checkable
5. Manual review to remove duplicates and add verify commands

## Format

```
<name> | <description> [<source file>] | <verify command using {file}>
```

## What should be automated

A cart-concern-extractor could:
1. Walk style guide files (using cart-code-processor)
2. For each section, ask: "is this a per-file checkable rule?"
3. If yes, generate the concern line with name, description, source reference
4. For mechanical rules, generate a verify command
5. Output concerns.txt

The tricky part is the verify commands — generating correct grep patterns
from natural language rules requires judgment. A two-pass approach might work:
first pass generates concerns without verify, second pass adds verify commands
and tests them against sample files.

## Maintenance

When the style guide updates, concerns.txt needs to be regenerated or
manually updated. Diffing the old and new guide can identify which sections
changed, and only those concerns need updating.
