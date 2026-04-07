# kernel — golem

golem is a context scheduler for LLMs. This file is the firmware — always
loaded, describes the mechanics. Read task.md next.

CRITICAL: On context compression, IMMEDIATELY re-read this file, all cart
manifests, task.md, and learnings.md before doing anything else.

## Two directories

### Harness (the product)

```
golem/
  kernel.md              # this file
  boot.sh                # prints the bootstrap phrase
  cache/                 # runtime cache for carts (gitignored)
  tools/                 # cart-fetch, append
  cartridges/            # fetched cart repos (gitignored)
```

Read-only during use. The model knows its location from kernel.md's
absolute path. Call tools by absolute path.

### Work directory (the instance)

```
workdir/
  task.md                # user intent (readonly)
  learnings.md           # accumulated feedback (append-only)
  material/              # reference data (readonly)
  workspace/             # model-owned scratch area
    runs/                # session reports
```

The model creates directories as needed. Minimal starting state: task.md.

## Cartridges

A cart is a git repo that gives golem a capability: manifest, tools,
material, learnings.

```
<cart-repo>/
  manifest.md            # behavioral program (required)
  tools/                 # scripts (optional)
  material/              # reference data (optional)
  learnings.md           # field experience (optional)
```

### Loading

task.md names the cart to run. Carts declare dependencies via `depends:`
in their manifest. Dependencies use full URLs or bare names:

```
depends: github.com/user/repo/cart-name    # monorepo
depends: github.com/user/cart-name         # standalone
depends: cart-name                         # must already exist locally
```

Resolve the dependency tree: load dependencies first. If a cart is not
fetched, use `cart-fetch`. Bare names that aren't found = FATAL ERROR.

On load: read manifests in dependency order, tools become callable,
material is available, learnings merges into work dir (first load only).

### Cartridge vs task.md

Cart = capability ("I know how to enforce a style guide").
task.md = intent ("enforce the nim style guide on this repo").
task.md overrides cart defaults when it contains specific instructions.

## Cache

`cache/` is a gitignored directory in golem. Carts persist data here
across runs and workspaces. Each cart uses its own subdirectory matching
its cart path (e.g. `cache/fcecin/carts/cart-name/`).

Not read automatically. Carts say when to read and write.

## Tools

- `tools/cart-fetch <url>[@<ref>]` — clone/update a cart repo into
  `cartridges/<user>/<repo>/`.
- `tools/append <file> <text>` — append to a file without reading it.
  For multiline: `append <file> - <<'EOF'`. Use for log.md, report.md,
  and any append-only file. Do NOT read a file just to append.

## Work directory contents

### `material/`

Local copy of external artifacts. Readonly. If the task requires
modifying material, copy to `workspace/` first.

### `workspace/`

Model-owned scratch area. All output goes here.

### `workspace/runs/`

Session reports. Create with `mkdir -p workspace/runs`.

### `log.md`

Append-only activity log. Each line: `<timestamp> [<cart>] <action> <detail>`.
Get timestamps from `date +%s` or reuse from recent tool output.

Log EVERY shell command you run — every grep, every file read, every tool
call. Not just the "important" ones. The log is the audit trail. If a
command isn't logged, it didn't happen as far as reviewers are concerned.

### `report.md`

Human-readable results. Carts define the structure.

### `confusion.md`

Log anything confusing: conflicting instructions, ambiguities, judgment
calls. Quote the conflict, state your decision and reasoning. Every entry
is a bug report against the golem stack.

### `cheats.md`

A "cheat" is any deviation from what the cart manifests say to do. Cheats
can be good — sometimes you find a smarter way. But ALL deviations must
be logged here, good or bad, big or small. This is not punishment. This
is an audit trail that helps cart developers understand how their
instructions are actually interpreted.

Log: what you did, what the cart said, and your reasoning. If you skip
files because a grep shows they don't need work — that's a deviation
from "process every file," log it. If you batch operations — log it.
If you invent an optimization — log it. The cheat may be brilliant.
It still goes in cheats.md.

Undocumented deviations make the workspace untrustworthy. A cheat you
logged is data. A cheat you hid is a lie.

### `task.md`

User intent. Loaded once. Readonly. Overrides cart defaults when specific.

### `learnings.md`

Persistent feedback. Append-only. Loaded alongside task.md.

## Execution model

1. Load kernel.md.
2. Load task.md. Copy it to workspace/task.md.
3. Load learnings.md (if exists).
4. Fetch carts specified in task.md.
5. Load all cart manifests in dependency order.
6. If workspace has prior state, you are resuming — don't re-initialize.
   Cart tools will print RESUMING. Follow their lead.
7. Follow the manifests and task.md.

On FATAL ERROR from a cart: stop, write session report, exit.

### Session report

On stop (completion, error, or session end), write to
`workspace/runs/golem-session-report-N.md` (next available number).

Include: state found, what was loaded, what was done, decisions made,
surprises, what remains.

## Context refresh

Re-read the full program stack (kernel, manifests, task, learnings):

- Before starting work.
- When a cart tool prints REFRESH.
- After error recovery.
- When unsure about the rules.

Re-read from files, not from memory.

## Invariants

- golem directory: never modified during a run.
- `material/`: never modified.
- `task.md`: never modified.
- `learnings.md`: append-only.
- All mutable state lives in `workspace/`.
