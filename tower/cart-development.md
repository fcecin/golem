# Cart development guide

## What is a cartridge

A cartridge is a git repository that gives golem a capability. It contains
natural language instructions (manifest.md) and optionally tools, material,
and learnings. When loaded, the model reads the manifest and gains that
capability — "I know kung fu."

A cart is pure content. No compiled code. No plugins. Just text files that
shape what the model sees and does.

## Cart structure

```
my-cart/
  manifest.md       # required — the behavioral program
  tools/            # optional — scripts the model calls
  material/         # optional — reference data
  learnings.md      # optional — accumulated field experience
  concerns.txt      # optional — if using cart-concern-walker
  *.md              # optional — any additional files the manifest references
```

## manifest.md vs learnings.md

These serve different purposes and both exist for good reason.

**manifest.md** is the cart's source code. It is written by the cart developer,
version-controlled, reviewed via PRs, and shared. It defines what the cart is
and how it works. Changing the manifest is a software change — it should be
deliberate and tested.

**learnings.md** is the cart's runtime patches. It accumulates from actual use:
feedback from PR reviewers, edge cases the model discovered, exceptions to
rules that only became apparent in practice. It exists so you can fix the
cart's behavior immediately without touching the manifest.

The model reads both — manifest first, learnings after. Learnings override
the manifest where they conflict. This is by design: the manifest is theory,
learnings is practice.

Over time, good learnings should be folded back into the manifest (or into
concerns.txt) and removed from learnings.md. Learnings is a staging area,
not a permanent home.

## Dependencies

A cart declares dependencies on other carts with `depends:` lines in its
manifest.md:

```
depends: cart-code-processor
depends: cart-concern-walker
```

The model resolves these recursively and reads manifests in dependency order
(dependencies first). This means your cart's manifest can reference tools and
protocols established by its dependencies.

## Concerns files

If your cart uses cart-concern-walker, you provide a `concerns.txt` file.
Each non-blank, non-comment line is one atomic concern — a focused instruction
that the model will check against each file.

The concern text IS the prompt. Write it as an instruction. Include the source
reference so the model can look up the full rule if needed.

```
# Comments start with #
Import grouping — imports must be grouped: std/ first, then external, then local [language.import.md]
No alloca — do not use alloca [language.memory.md]
```

The concern walker strips comments and blank lines, then feeds one concern at
a time to the model. The model processes one concern × one file, then moves on.

## Tools

Carts can ship tools in a `tools/` directory. These are shell scripts the model
calls by absolute path. Tools should be:

- Simple — one job each
- Deterministic — same input, same output
- State-aware — store state in `workspace/` in the work directory

Tools drive the model, not the other way around. The walker tools (walk,
concern) are the canonical example: they tell the model what to process next.
The model follows, not leads.

## Testing a cart

1. Create a work directory with a task.md pointing at your cart
2. Put test material in material/
3. Run golem (bootstrap a Claude session)
4. Check workspace/report.md, workspace/log.md, workspace/confusion.md
5. confusion.md entries are bug reports against your cart — fix them
6. Good learnings from the run go into your cart's learnings.md
7. Once stable, fold learnings into manifest.md

## Publishing

A cart is a git repo. Push it, share the URL. Users load it with:

```
cart-fetch <url>@<ref>
```

Or reference it by name in task.md if it's already fetched.
