# In the beginning

## Origin (April 6, 2026)

golem started as a style enforcement bot for nwaku (logos-delivery), a Nim
codebase with 546 source files following the Status Nim style guide. The
original ask: create a bot that reads the style guide, applies it to the
codebase, and wraps the result into a PR.

## Key realizations (in order of discovery)

### 1. The harness is the product, not the styler

The first insight was that the styler is just one use case. What matters is
the generic engine that drives a model through a task. Richard (a colleague)
had demonstrated this by generating a C libp2p implementation: create a plan,
feed it to sub-agents, iterate. That method could be formalized. The styler
was just the first cartridge.

### 2. Stop naming files by meaning

Early design had MEMORY.md, METHOD.md, STYLE.md. This was wrong. The harness
doesn't deal with meaning — it deals with the order in which content gets
refreshed into the model. The "physics" of context flow, not the "meaning"
of files. This led to the slot system (later removed) and eventually to the
much simpler cartridge model.

### 3. Cartridges are repos

Initially cartridges were directories inside the harness. Making them git
repos was obvious in retrospect: they're shared, versioned, forked, and
contributed to via PRs. Just like any open source library.

### 4. Two directories, not one

The harness (golem) and the work directory must be separate. golem is software
you install. The work directory is an instance you create for a specific task.
Mixing them caused .gitignore gymnastics and conceptual confusion.

### 5. The slot system was a phantom

We designed an elaborate slot system (source, refresh, position, budget,
depends) for scheduling content into the model's context. None of it was
executable — there was no scheduler. The model was supposed to read the slot
definitions and self-schedule, which is asking a model to be its own OS.

The walker tool replaced all of it. A simple bash script with a cursor file
turned out to be more effective than any amount of declarative scheduling.
The lesson: real tools beat theoretical frameworks.

### 6. Don't digest the style guide

The first attempt distilled the style guide into bullet points in the manifest.
The model fixated on the most obvious rules (proc→func) and missed nuance.
The fix: force the model to read every raw style guide file before touching
code. No summaries. Raw tokens in, full understanding.

### 7. Concerns are prompts formatted as a script

The concerns.txt file is a list of one-line instructions, one per concern.
Comments and blank lines get stripped by the tool. Each remaining line is
both a human-readable concern name AND the prompt the model receives. The
concern walker is just a cursor over a prompt list. Brilliant in its
simplicity.

### 8. File-first, not concern-first

Initial design had the outer loop over concerns (for each rule, check all
files). This means revisiting each file 53 times. Flipping it (for each file,
check all concerns) means each file is opened once and fully processed.
Much more efficient.

### 9. Context refresh is the core problem

The model's context window is finite and attention degrades. In a long session
(500+ files), early instructions get buried. The kernel's real job is forcing
periodic re-reads of the program stack. Two mechanisms:

- The walker prints REFRESH every N files (deterministic, tool-driven)
- The kernel tells the model to re-read on context compression (opportunistic)

Neither is guaranteed to work perfectly. But together they're the best we have.

### 10. confusion.md is a bug tracker

When the model encounters conflicting instructions or ambiguity, it logs to
confusion.md with full context and its resolution. Every entry is a bug report
against the golem program stack. This turns the model into a QA engineer for
its own instructions.

### 11. Learnings is the hot-patch mechanism

manifest.md is the cart's source code (deliberate changes, reviewed via PR).
learnings.md is the runtime patch (immediate fixes from field experience).
Good learnings get folded back into the manifest over time. This separation
lets you fix behavior without breaking the cart's reviewed codebase.

### 12. Tools verify, models don't guess

The concern walker tells the model to use grep and other unix tools to verify
concerns mechanically instead of guessing from memory. "No alloca" should
trigger `grep -n alloca file.nim`, not a memory-based judgment. Every tool
invocation is logged with the full command line and output size.

## What we chose not to build

- No external scheduler or orchestrator — the model IS the runtime
- No plugin system — carts are content, not code
- No CI integration (yet) — manual runs first, automation later
- No PR submission (yet) — generate the branch, human reviews and submits
- No multi-model coordination — single model session per run

## Open questions after day one

- Will the model stay disciplined for 500+ files in one session?
- Does the compression re-read instruction actually survive compression?
- Is 53 concerns × 34 files too many iterations for one session?
- Should the walker split work across multiple sessions automatically?
- How do we handle concerns that require cross-file changes (e.g. renames)?
