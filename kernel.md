# kernel — golem

This file is the firmware of golem. It is always loaded. It describes the
mechanics of how golem operates. It does not describe any specific task.

golem is a context scheduler. It controls what content enters the model's
context window, in what order, and when it gets refreshed. It does not interpret
meaning. It manages the physics of context flow.

CRITICAL: If you receive a context compression notice, IMMEDIATELY re-read this
file (kernel.md) from the filesystem before doing anything else. Then re-read
all cart manifests, task.md, and learnings.md. Do not proceed with any other
work until the full program stack has been re-loaded from disk.

## Bootstrap

The golem is installed by cloning its repository somewhere on the user's
machine. It stays there. It is never modified by the user.

To use the golem, the user opens a model session (e.g. Claude in VSCode) in
any empty working directory. They paste the bootstrap phrase into the chat:

```
Read <absolute-path-to>/kernel.md — it will explain everything.
```

The golem ships `boot.sh` in its root. Running it prints the bootstrap phrase
with the correct absolute path, ready to paste:

```
$ /path/to/golem/boot.sh
Read /home/user/golem/kernel.md — it will explain everything.
```

When the model reads this file, it learns how the golem works and what to
expect in the working directory. The model then looks for task.md in the current working directory to understand what the user wants.

## Two directories

The golem separates the product from the instance.

### Harness directory (the product)

Where the user cloned the golem repo. Read-only during use. Contains:

```
golem/
  kernel.md              # this file — the firmware
  boot.sh                # prints the bootstrap phrase
  tools/                 # scripts the model can call
    cart-fetch
  cartridges/            # fetched cartridge repos (gitignored)
    fcecin/carts/        # example: monorepo with multiple carts
```

The golem directory is software. It is versioned, updated via git pull.
The `cartridges/` directory is gitignored — it holds fetched cartridges that
are shared across all workspaces, but are not part of the golem source.

Cartridges are a global resource. Once fetched, any workspace can use them.
They are libraries, not project-specific state.

The model knows the golem location because it was told to read kernel.md
from an absolute path.

The model refers to golem tools by their absolute path:

```
/home/user/golem/tools/cart-fetch github.com/fcecin/carts
```

### Work directory (the instance)

The current working directory where the model session is running. This is where
all user content and runtime state lives:

```
workdir/
  task.md                # what the user wants (user-written)
  learnings.md           # accumulated feedback (append-only, persistent)
  material/              # reference data (readonly during run)
  workspace/             # scratch area (model-owned)
    runs/                # session reports from each golem run
```

The work directory is an instance — one project, one task, one history of
learnings. It may or may not be a git repo. The user may version it, share it,
or treat it as disposable.

The model creates any of these directories as needed. None are required to
exist before the first run. The minimal starting state is an empty directory
with a task.md.

## Cartridges

A cartridge is a loadable package that gives the golem a capability. It is a
directory containing any combination of: a manifest, tools, material, and
learnings. When loaded, a cartridge's contents become available to the model.

A cartridge is not code. It is not a plugin. It is a bundle of context that,
when present, causes the model to behave differently — because different bytes
are now entering the context window on a different schedule. The cartridge
doesn't "do" anything. It changes what the model sees.

### Structure

A cartridge is a git repository with a known layout:

```
<cartridge-repo>/
  manifest.md          # what this cartridge is (loaded into context)
  tools/               # scripts the model can call (optional)
  material/            # reference data this cartridge needs (optional)
  learnings.md         # initial learnings (optional)
```

### `manifest.md`

Every cartridge has one. It is loaded into context alongside kernel.md when the
cartridge is active. It describes — in natural language — what this cartridge
enables the model to do. It may contain:

- The behavioral program (how to approach the task)
- Domain knowledge the model needs (condensed rules, patterns, conventions)
- Constraints and boundaries (what not to do)
- Phase structure and parallelism hints

The golem instance just sees: content to load (manifest), executables to call (tools), and bytes to reference (material).

### Loading

Cartridges are fetched by git URL and pinned to a ref (branch, tag, commit).
The model calls the golem tool to fetch them into the golem's `cartridges/`
directory:

```
/path/to/golem/tools/cart-fetch github.com/fcecin/carts
```

This clones the cartridge repo into the golem's `cartridges/<name>/`. Once
fetched, the cartridge is available to all workspaces — it does not need to be
fetched again for a different project.

task.md specifies which cartridge to run:

```
cartridge: github.com/fcecin/carts/cart-logos-delivery-styler
```

task.md names one cartridge. That cartridge may declare dependencies on other
cartridges via `depends:` lines in its manifest.md. Dependencies use one of
two formats:

```
depends: github.com/user/repo/cart-name
depends: cart-name
```

The full URL format (`github.com/user/repo/cart-name`) specifies a cart inside
a monorepo. If the cart is in its own dedicated repo, use
`github.com/user/cart-name`. The model resolves these by checking the golem's
`cartridges/` directory:

- For a monorepo URL like `github.com/fcecin/carts/cart-code-processor`:
  look for `cartridges/fcecin/carts/cart-code-processor/manifest.md`. If
  the monorepo is not fetched, fetch it with `cart-fetch github.com/fcecin/carts`.
- For a standalone URL like `github.com/user/cart-foo`: look for
  `cartridges/user/cart-foo/manifest.md`. If not fetched, fetch it.
- For a bare name like `cart-name` (no URL): the cart must already exist in
  `cartridges/`. Search all subdirectories. If not found, FATAL ERROR — bare
  names cannot be fetched because the source is unknown.

The model resolves the dependency tree: load dependencies first, then the
requested cartridge. Read each manifest in dependency order — dependencies
before dependents. If a dependency has its own dependencies, recurse.

On load:
- `manifest.md` is read in dependency order (dependencies first).
- `tools/` scripts become available for the model to call by absolute path.
- `material/` contents are available under the golem's
  `cartridges/<name>/material/`.
- `learnings.md` is merged into the work directory's learnings.md on
  first load only.

### Cartridge vs. task.md

A cartridge says "I know how to enforce a style guide" (capability).
task.md says "enforce the nim style guide on this repo" (intent).

The cartridge is reusable. task.md is specific to this instance. A cartridge can
be published, shared, versioned, forked. task.md is local.

## Tools

### `tools/`

Ships with the golem (in the golem directory). Contains scripts the model
can call to perform mechanical operations it should not have to reason about.
The model does not write these scripts — it calls them by absolute path.

Available tools:

- `tools/cart-fetch <url>[@<ref>]` — clone or update a cartridge repo into
  the work directory's `cartridges/<name>/`. Extracts the repo name from the
  URL. If already cloned, pulls the specified ref. If no ref, uses `main`.

Tools are deliberately simple. Each one does one thing. The model calls them
via shell execution. If a tool does not exist for an operation, the model uses
standard shell commands (git, curl, cp, etc.) — but for golem-specific
operations, tools are preferred because they enforce conventions (correct
paths, correct directory structure, correct naming).

Tools operate on the current working directory (the work directory) by default.
They find the golem directory from their own location.

Tools may be added over time as patterns emerge. If the model finds itself
repeatedly doing the same multi-step shell operation, that operation should
become a tool.

## Work directory contents

### `material/`

Contains data the model can read. This is the local authoritative copy of any
external artifact. If something exists in `material/`, it takes precedence over
the live version on the internet.

Examples: cloned repositories, downloaded specs, fetched web pages, reference
documents.

The model never writes into `material/`. It is populated by the user, by
cartridge loading, or by the user before a run.

When the task requires modifying data that lives in `material/`, copy it into
`workspace/` first and work on the copy. For example, if the target codebase
is in `material/target-repo/`, run `cp -r material/target-repo workspace/`
before making any changes. All reads for context may come from either location,
but all writes go to the workspace copy.

### `workspace/`

The model's scratch area. All generated output goes here: modified files, diffs,
branches, logs, intermediate artifacts.

The model owns this directory. It may create, modify, or delete anything inside
it. The user should not rely on the contents of `workspace/` surviving across
runs unless a specific output has been promoted (e.g. committed to a branch,
copied out).

### `runs/`

Contains session reports from previous runs. Each `golem run` writes its
session report here as `golem-session-report-N.md` (numbered sequentially).
This keeps the workspace root clean while preserving the full audit trail.

Create the directory if it does not exist: `mkdir -p workspace/runs`

### `log.md`

Append-only activity log. Every cartridge and the model itself logs significant
actions here. Every line starts with a unix timestamp obtained by running
`date +%s` immediately before writing the log entry. Format:

```
<timestamp> [<cart-name>] <action> <detail>
```

Example:
```
1712412345 [code-processor] walk-enter workspace/logos-delivery/waku/common/base64.nim
1712412347 [concern-walker] concern-start Import grouping
1712412350 [concern-walker] concern-end Import grouping interventions=1
1712412351 [concern-walker] concern-start Import paths
1712412353 [concern-walker] concern-end Import paths interventions=0
1712412380 [code-processor] walk-exit workspace/logos-delivery/waku/common/base64.nim
```

log.md is for machine-readable activity tracking. It records what happened
and when. Each log line must have a current timestamp. Either run `date +%s`
yourself before writing, or reuse the timestamp printed by a cartridge tool
that just ran (tools print timestamps in `[<timestamp>]` format in their
output). Do not reuse a stale timestamp from a previous operation — each
log line must reflect the actual time that action occurred.

### `report.md`

Human-readable report of results. Cartridges define what goes here — typically
findings, changes made, and suggestions. Structured by the cartridge that
writes it (e.g. per-file sections with per-concern subsections).

report.md is for the user to review. log.md is for the system to audit.

### `confusion.md`

When you encounter anything confusing — conflicting instructions between
kernel.md and a cart manifest, ambiguous concern text, code that doesn't match
what you expected, instructions that seem contradictory, or anything where you
had to make a judgment call — log it here. Be verbose. Include:

- What confused you (quote the conflicting parts)
- What you decided to do
- Why you chose that interpretation

This file is for humans to debug the golem system itself. If the kernel says
one thing and a cart says another, you're probably right about what was
intended — write down your reasoning so the developers can fix the conflict.
Every entry here is a bug report against the golem program stack.

### `cheats.md`

Do not second-guess the methods of the cartridges. Do not short-circuit. Do
not optimize. Do not parallelize unless a cartridge explicitly tells you to.
Follow the protocol exactly as described in the manifests, even if you think
you know a better way.

If you cannot resist — if you decide on your own to deviate from the cart
instructions because you think it's "more efficient" or "better" — log it
to workspace/cheats.md. Write what you did, what the cart told you to do,
and why you went off-script. Every entry here is a model discipline failure
that helps cart developers write tighter instructions — or better
ones, if you turned out to be right.

Cheating is not good, but it is forgivable when documented. Cheating and
LYING ABOUT IT — by not writing to cheats.md, by pretending a deviation is
not a deviation, by batching operations in a shell loop while the manifest
says to process one at a time — is a complete and unjustified failure. The
entire value of cheats.md is that it captures what actually happened. If you
cheat and don't document it, the workspace output is untrustworthy and the
run is worthless. Document every deviation, no matter how small.

### `task.md`

The user's file. Describes what the user wants done in this instance. The model
loads it once at session start. It is the only file where the user communicates
intent to the model.

task.md is not a method, not a plan, not a prompt. It is a declaration of the
desired outcome. When task.md contains specific instructions that narrow or
override what a cartridge would normally do (e.g. "only check Import grouping"
or "skip files in tests/"), follow task.md. The user's intent takes precedence
over cartridge defaults.

### `learnings.md`

Persistent across runs. Contains accumulated feedback from previous runs and
from human review. The model loads it alongside task.md. It modifies model
behavior by adding context about what worked, what was rejected, and what
exceptions exist.

learnings.md is the only file the model may append to between runs. It is the
instance's long-term memory. The user may also edit it directly.

## Execution model

A run proceeds as follows:

1. Load kernel.md (this file) from the golem directory.
2. Load task.md from the work directory.
3. Copy task.md into workspace/task.md (overwrite if it exists). This
   preserves the task definition alongside the run output.
4. Load learnings.md from the work directory (if it exists).
4. Fetch any cartridges specified in task.md.
5. Load all cartridge manifests.
6. Check if `workspace/` already contains state from a previous run
   (e.g. log.md, report.md, or tool state files exist). If so, you are
   resuming. Do not re-initialize what is already set up. Do not re-copy
   material that already exists in workspace. Cartridge tools may detect
   existing state and print RESUMING — follow their lead.
7. Follow the instructions in the manifests and task.md.

The cartridges define what to do and how. The kernel defines the environment
and the rules. task.md declares the desired outcome.

If at any point a cartridge instructs you to STOP or issues a FATAL ERROR,
stop immediately. Do not continue processing. Write the session report (see
below) explaining what happened, then exit.

### Session report (on completion or stop)

When you are about to stop — whether the task is complete, you hit a wall,
a cartridge issues a FATAL ERROR, or the session is ending for any reason —
write a session report to `workspace/runs/`.

Create the directory if needed: `mkdir -p workspace/runs`

To find the filename: look for existing `golem-session-report-*.md` files in
`workspace/runs/`. If none exist, write `golem-session-report-1.md`. If
`golem-session-report-1.md` exists, write `-2.md`, and so on. Always use
this exact pattern. Do not write `golem-session-report.md` (without a number).

Walk through everything from the moment you absorbed
kernel.md to the point you're stopping. Include:

- What state you found (fresh start or resuming, what existed already)
- What you loaded (kernel, carts, manifests, style guide, etc.)
- What you did (files processed, concerns checked, changes made)
- Decisions you made and why (especially judgment calls)
- Anything surprising or confusing you encountered
- Behavior modifications you applied during the run (shortcuts, patterns)
- What remains to be done if the task is not finished

You may read workspace/report.md, workspace/log.md, workspace/suggestions.md
and any other workspace files to help you write this.

Find the next available number (1, 2, 3, ...) and use it. Each session gets
its own numbered report, matching the numbered claude-log files. These form
a chain of session histories across resumptions.

## Context refresh

The model's context window is finite and its attention degrades over long
sessions. Instructions loaded early get buried under thousands of lines of
tool output, file reads, and edits. The model drifts. It forgets its program.

golem solves this by periodic context refresh. The program stack is:

```
1. kernel.md           (this file)
2. cart manifests      (all loaded cartridges)
3. task.md             (user intent)
4. learnings.md        (accumulated feedback)
```

This stack is the model's program. It must be re-read periodically to keep
the model anchored. The model MUST re-read the full stack:

- Before starting work for the first time.
- When a cartridge tool prints a REFRESH directive.
- After any error that required recovery.
- When the model notices itself unsure about the rules.

Re-reading means: literally read these files again using the read tool. Not
from memory. Not from what you think they say. From the files. This is the
equivalent of a CPU refetching instructions from memory — not from cache,
from the source.

Cartridge tools (like `walk` from cart-code-processor) may also trigger
refreshes by printing a `REFRESH` directive in their output.

## Invariants

- The golem directory is never modified during a run.
- The model never modifies `material/` in the work directory.
- The model never modifies `task.md`.
- The model may only append to `learnings.md`.
- All mutable state lives in `workspace/`.
