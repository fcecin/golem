# golem

__NOTE: This is experimental software.__

A context scheduler for LLMs. `golem` drives a model through complex tasks by controlling what content enters the context window and when.

## WARNING

(HUMAN NOTE:) I guess it's better to make this explicit, even if it's obvious. The only way to make this safe is to run this on its own dedicated computer. There's no way to add "security" to a bot on your personal machine where you have all your stuff. Even if you design correct security procedures, you'll just breach them yourself when you're having all that fun. If you want security run bots in dedicated boxes and don't give them any credentials you don't want leaked. That's it. 

## What it does

`golem` is a harness. You install it once, then create work directories for specific tasks. Capabilities are loaded via cartridges — git repos containing natural language instructions, tools, and reference material that shape the model's behavior.

The model is the runtime. The cartridges are the program. `golem` is the OS.

## Install

The following creates a `golem` executable shell script in `~/.local/bin/` and appends a PATH export to your shell profile (bashrc/zshrc).

```
git clone https://github.com/fcecin/golem
cd golem
./install.sh
```

If you don't want your shell profile modified, use `./install-no-path.sh` instead and add `~/.local/bin` to your PATH manually.

## Quick start

```
golem init ~/work/my-task
golem fetch github.com/fcecin/carts
golem cart-init styler ~/work/my-task
cd ~/work/my-task
# edit task.md
golem run
```

Paste the boot phrase into the chat when prompted.

## Concepts

**kernel.md** — the firmware. Always loaded. Describes how `golem` works: the two-directory model, cartridge loading, context refresh, workspace conventions.

**Cartridges** — git repos that give the model capabilities. A cartridge contains a manifest (natural language instructions), optional tools (shell scripts), optional material (reference data), and learnings (accumulated field experience). Cartridges declare dependencies on other cartridges.

**Work directory** — where a task runs. Contains task.md (user intent), material/ (input data), workspace/ (scratch area and output). Disposable and reproducible.

**task.md** — declares what you want done and which cartridge to use.

**learnings.md** — accumulated feedback from previous runs. The model reads this to avoid repeating mistakes.

## Workspace output files

After a run, the workspace/ directory contains:

- `report.md` — human-readable results
- `log.md` — timestamped activity log (dual-logged by tools and model)
- `suggestions.md` — items flagged but not fixed
- `confusion.md` — ambiguities the model encountered
- `cheats.md` — protocol deviations the model made
- `golem-session-report-N.md` — rich session summary

## Writing cartridges

See `tower/cart-development.md` for the full guide. A cartridge is a git repo with:

```
manifest.md       # required — behavioral program
tools/            # optional — shell scripts the model calls
material/         # optional — reference data
learnings.md      # optional — field experience
```

Cartridges can be standalone repos or grouped in monorepos.

## Architecture

```
golem/                    # installed once, never modified during use
  kernel.md               # the firmware
  tools/                  # cart-fetch
  cartridges/             # fetched cart repos (gitignored)
    fcecin/carts/         # example monorepo
      cart-code-processor/
      cart-concern-walker/
      cart-logos-delivery-styler/

~/work/my-task/           # a work directory (one per task)
  task.md                 # what to do
  learnings.md            # what was learned
  material/               # input data (readonly)
  workspace/              # output and scratch (model-owned)
```

## Context refresh

Long sessions cause the model to drift. `golem` addresses this with:

1. Cartridge tools print REFRESH directives periodically
2. kernel.md instructs the model to re-read the full program stack on context compression
3. Tools embed timestamps in their output so the model uses real times

## Contributing

Since `golem` is basically text, LLMs are actually pretty good at composing and optimizing that text.

You can contribute PRs to the `golem` repo or just fork/clone your own golem and figure out a way to make it better. LLM PRs welcome (if they make sense -- `golem` will be reviewing them at some point...).

## License

Unlicense
