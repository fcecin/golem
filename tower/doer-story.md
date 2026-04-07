# The doer story

How cart-doer, cart-meta-doer, and cart-fixer-isnil came to exist.

## The problem

We had a Nim codebase (logos-delivery, 546 files) with inconsistent
`isNil` usage. Three forms existed in the wild:

- `isNil(expr)` — function call syntax
- `expr.isNil` — method syntax without parentheses
- `expr.isNil()` — method syntax with parentheses (the canonical form)

The task: normalize everything to `expr.isNil()`. Simple, mechanical,
but spread across hundreds of files.

We already had the styler cart (cart-logos-delivery-styler) which did
thorough style enforcement — 51 concerns per file, one file per session,
10-15 minutes per file. But the isNil fix is a single concern. Using
the full styler machinery would be like using a bulldozer to plant a
flower.

## The insight: a general-purpose doer

Instead of writing a one-off cart for isNil fixing, we asked: what if
there was a cart that could do *anything* to a codebase? You describe
the task, it figures out how to do it, builds the tools, tests them,
and executes.

This became cart-doer.

### Design principles

1. **Minimal dependencies.** The doer depends only on cart-code-processor
   (the file walker). Everything else it discovers at runtime.

2. **Runtime skill discovery.** The doer browses installed carts during
   its skill-mapping phase. If cart-concern-walker is installed, it
   might use it. If cart-file-stepper is installed, it might use it.
   If neither exists, it works without them.

3. **Skill caching.** Skills the doer builds are stored in the golem
   cache (`golem/cache/fcecin/carts/cart-doer/`). They persist across
   workspaces. A skill built for one project is available for all
   future projects.

4. **No hardcoded domain knowledge.** The doer doesn't know Nim. It
   doesn't know isNil. It reads the task, studies the codebase, and
   figures it out.

### The five phases

**Phase 1: Study.** Read task.md, scan the codebase, identify patterns.
For isNil, the doer found 332 occurrences across 69 files, identified
three forms, and determined one skill was needed.

**Phase 2: Skill mapping.** Check three sources: cached skills, installed
carts, and built-in capabilities. For isNil, it found `isnil-normalizer`
already cached from a previous test run. Status: CACHED. The file walker
was BUILTIN. No other carts needed.

**Phase 3: Build.** Create any missing skills. For isNil, the skill was
already cached, so this phase was skipped on the production run. On the
first test run, the doer built the skill from scratch — writing skill.md,
concerns.txt with Perl regex verify commands, and caching it.

**Phase 4: Test.** Pick representative files, run the skill pipeline,
verify results. The doer selected declare_lib.nim (3 function-call
instances), keyfile.nim (4 instances), and waku.nim (1 instance + 22
already-correct). All passed.

**Phase 5: Execute.** Walk all 546 files. For each file, grep for isNil.
If no match, skip. If match, read the file, apply transformations, verify.
25 files were modified. 332 occurrences normalized. Zero violations
remaining.

### The smart cheat

The doer invented an optimization we didn't design: pre-scan skipping.
Before processing each file, it ran `grep -P 'isNil' <filename>` from
the outside (without reading the file into context). Files with no isNil
were `walk skip`ped instantly. This reduced 546 files to ~50 that actually
needed work.

This is a deviation from the walker protocol ("process every file") but
a brilliant one. It was documented in cheats.md — the golem kernel
requires all deviations to be logged, even smart ones.

### The regex miss

During execution, the doer's Grep tool (Claude's built-in grep) didn't
reliably match the Perl lookbehind regex `(?<!\.)isNil\(` in all cases.
7 files were incorrectly passed through as "no changes needed" when they
actually had function-call isNil patterns.

The doer caught this in its post-walk verification. It ran the regex
across the entire codebase, found the 7 missed files, and went back to
fix them. This was another protocol deviation (modifying files outside
the walk loop) — also documented in cheats.md.

The fix: the doer switched from Claude's Grep tool to bash `grep -P`
for the critical verification step. The cached skill's concerns.txt had
the correct regex all along — the issue was the tool implementation, not
the pattern.

### Results

- 546 files walked
- 25 files modified
- 332 isNil occurrences normalized
- 0 remaining violations (verified independently)
- 20 minutes, one session
- 3 cheats documented (pre-scan skip, batch walking, post-walk fixes)

## The meta-doer: skill promotion

With the doer proven, the next question was: can we extract the skill
it built and publish it as a standalone cart?

### The problem of knowledge transfer

The doer builds skills in its cache. The cache has:
- `skill.md` — what the skill does
- `concerns.txt` — check definitions with verify commands

But a publishable cart needs more:
- `manifest.md` — behavioral program for the LLM
- `tools/golem-cart-init.sh` — interactive setup script
- `tests/` — test data with input and expected output
- `learnings.md` — empty starter
- `evidence/` — proof the skill works (from the doer run)

The meta-doer (cart-meta-doer) bridges this gap.

### How it works

The meta-doer's cart-init script:

1. Reads the doer workspace's `skill-map.md` to find which skills were
   used (no manual selection — it's automatic).
2. Copies skills from the cache into `workspace/<cart-name>/skills/`.
3. Copies evidence from the workspace (study.md, test-results.md, etc.).
4. Copies test data.
5. Writes a stub manifest.
6. Archives the current task.md and writes a promotion task.
7. Launches `golem clauder` for the polishing session.

The golem session (Claude) then:

1. Reads the cart-doer manifest to understand how skills are structured.
2. Reads all assembled materials — skills, evidence, test data.
3. Rewrites the stub manifest into a proper cart manifest with correct
   dependencies, processing instructions, fix/flag rules, etc.
4. Writes a golem-cart-init.sh for the new cart.
5. Organizes test data into input/expected structure.
6. Reviews and cleans up the entire cart.
7. Writes a promotion report.

### Invocation

```
cd ~/golem/local/isnil    # the completed doer workspace
golem cart-init meta-doer .
# asks for cart name → "cart-fixer-isnil"
# assembles materials, launches clauder automatically
```

### Problems found in the first meta-doer run

**Problem 1: Hardcoded dependencies.** The stub manifest hardcoded
`depends: cart-file-stepper` and `depends: cart-concern-walker`. These
should be derived from the doer's skill-map.md, not assumed.

**Fix:** Updated the meta-doer cart-init script to generate stubs
without dependency assumptions, and updated the manifest to tell Claude
to derive dependencies from the evidence.

**Problem 2: Concern-walker coupling.** The doer and meta-doer manifests
both referenced the concern walker explicitly — naming it, using its
terminology ("concerns"), prescribing its format.

**Fix:** Purged all references to "concern" from both the doer and
meta-doer. The doer now discovers carts at runtime and uses whatever
formats they provide. The word "concern" belongs to cart-concern-walker
only.

**Problem 3: Duplicate test files.** The meta-doer created both
`declare_lib.nim` and `declare_lib_fixed.nim` in the expected test
directory — duplicates from different sources (the real file vs a
minimal test excerpt).

**Fix:** Added a final review step to the meta-doer manifest: clean up
dead files, check for duplicates, verify regexes match what the doer
actually used.

**Problem 4: Regex mismatch.** The doer's cache had
`(?<!\.)\bisNil\s*\(` (with word boundary `\b`). The promoted cart's
manifest had `(?<!\.)isNil\s*\(` (without `\b`). Functionally equivalent
in practice but technically a degradation.

**Fix:** Manual correction during the review step. Added requirement
to the meta-doer manifest: compare tool logic against the cached skill
and evidence. Also added: write regression tests if executable logic
changes.

**Problem 5: No final review.** The meta-doer assembled and polished
the cart but didn't step back and look at the whole thing critically.

**Fix:** Added step 7 to the meta-doer manifest: independent, from-scratch
review of the entire produced cart. Fix and clean up issues found. Write
regression tests for any changed executable logic.

### The lossy transfer problem

The meta-doer will always be lossy compared to the doer. The doer
experienced the execution — hit edge cases, self-corrected, adjusted
regexes, discovered that Claude's Grep tool handles Perl lookbehinds
differently than bash grep. The meta-doer reads the artifacts but
doesn't re-experience the journey.

This is analogous to the knowledge acquisition bottleneck in classical
expert systems: the gap between what the expert knows and what the
knowledge engineer captures. The difference is that golem's "knowledge
engineer" (the meta-doer) has access to comprehensive evidence — study,
skill map, test results, report, cheats log. The gap is narrower. But
it's still there.

The final review step and the human review are the safety nets. The
meta-doer catches most issues. The human catches the rest. Over time,
the meta-doer's manifest improves and the gap narrows further.

## The produced cart: cart-fixer-isnil

The output of the whole pipeline:

```
cart-fixer-isnil/
  manifest.md           # full cart manifest
  tools/golem-cart-init.sh  # interactive setup
  skills/isnil-normalizer/  # skill from doer cache
    skill.md
    concerns.txt
  tests/
    test-regexes.sh     # regression tests
    data/input/         # 3 test files with violations
    data/expected/       # 3 test files after normalization
  evidence/             # proof from the doer run
    study.md
    skill-map.md
    test-results.md
    report.md
  learnings.md          # empty starter
```

### What the cart does

1. Pre-scans each file with `grep -nP 'isNil'`. No match = skip.
2. For matching files, applies two transformations:
   - `isNil(expr)` → `expr.isNil()` (function call to method)
   - `expr.isNil` → `expr.isNil()` (add missing parens)
3. Excludes comments and string literals.
4. Verifies each file after transformation (both regexes must return 0).
5. Logs all changes, skips, and deviations.

### Using it

```
golem init ~/work/fix-isnil
golem cart-init fixer-isnil ~/work/fix-isnil
# enter the target repo path or URL
cd ~/work/fix-isnil
golem run
```

Or with clauder for unattended operation:

```
golem clauder --dir ~/work/fix-isnil --idle 20 \
  --claude-args="--dangerously-skip-permissions"
```

## The full pipeline

```
Human intent          "normalize isNil calls"
       ↓
cart-doer             studies, builds skill, tests, executes
       ↓
golem cache           isnil-normalizer skill persisted
       ↓
cart-meta-doer        reads cache + workspace, promotes to cart
       ↓
cart-fixer-isnil      publishable cart, usable by anyone
       ↓
Any future codebase   golem cart-init fixer-isnil → golem run
```

One sentence of human intent → automated skill building → automated
testing → automated execution → automated promotion → reusable tool.

## What we learned

### LLMs invent optimizations

The pre-scan skip was not designed. The doer invented it because it
was the obvious thing to do — why read a file that doesn't contain
the pattern you're looking for? This kind of emergent optimization
is the strength of using an LLM as the runtime. A rigid expert system
would process every file mechanically.

### Cheats.md is critical infrastructure

Without cheats.md, we wouldn't know the doer skipped files or fixed
them post-walk. The deviations were all justified, but knowing they
happened is essential for:
- Understanding the actual execution path
- Debugging when something goes wrong
- Improving cart manifests to either allow or prevent specific deviations

### The doer is better than the promoted cart

The doer, running live against the codebase, produces better results
than the cart it creates. This is because the doer adapts in real-time
— it sees edge cases and adjusts. The cart is a frozen snapshot of
the doer's knowledge. The meta-doer tries to capture everything but
there's always loss.

For one-off tasks, use the doer directly. For recurring tasks across
multiple codebases, promote to a cart.

### Regex tools vary between implementations

Claude's built-in Grep tool and bash `grep -P` handle Perl regex
differently. The doer discovered this the hard way (7 missed files).
The fix was pragmatic: use bash grep for critical verification.

Any cart that uses Perl regex should document this and include bash
grep as a fallback or primary tool. The cart-fixer-isnil manifest now
prescribes bash grep explicitly.

### The concern walker is optional

The doer processed 546 files without using the concern walker at all.
It applied the skill directly — grep, inspect, transform, verify. For
simple, mechanical tasks, the concern walker's per-concern protocol is
overhead. For complex, judgment-heavy tasks (like the styler), it's
essential.

The doer correctly discovered this distinction at runtime. It saw the
concern walker was available but chose not to use it because the task
didn't need it.

### The meta-doer needs a review step

The first version of the meta-doer produced a cart with duplicate test
files, a regex mismatch, and orphaned skill files. Adding a final
review step (examine the whole cart, fix issues, write regression tests)
caught these problems.

The review step is cheap (one pass over a small directory) and catches
exactly the kind of lossy-transfer problems that are hard to prevent
upstream.

## Future directions

### Doer skill composition

Currently the doer builds one skill per task. For complex tasks, it
might need multiple skills that interact — e.g., "rename all ref types
to use Ref suffix AND update all references." This requires skill
dependencies and ordered execution.

### Doer learning across runs

The doer's cached skills are static — once built, they don't change.
But the same skill might be applied to different codebases with
different edge cases. The doer could update its cached skills based
on new experiences, making them better over time.

### Meta-doer verification

The meta-doer could run the promoted cart on the same codebase the
doer used, compare the results, and flag any differences. This would
catch lossy transfer automatically.

### Cart testing framework

A standard way to run a cart's tests (like `golem test <cart>`). The
cart would have a `tests/` directory with input files, expected output,
and a test script. The framework would run the cart on the inputs and
diff against expected.

### Doer → meta-doer → publish pipeline

A single command that runs the doer, then the meta-doer, then copies
the promoted cart to a git repo and pushes. Full automation from human
intent to published cart.

```
golem pipeline doer "normalize isNil calls" \
  --target https://github.com/user/repo \
  --publish-to github.com/user/carts/cart-fixer-isnil
```

That's the endgame: one sentence in, published cart out.
