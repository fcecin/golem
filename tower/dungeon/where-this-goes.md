# Where this goes

## The easy things are hard

We started with style enforcement and isNil normalization. These look
trivial — regex replacements, formatting rules, mechanical transforms.
A senior engineer would scoff: "just write a sed script."

But they're actually the hard tasks for automation. Here's why:

**No compiler to check your work.** When you change `isNil(x)` to
`x.isNil()`, nothing verifies the transformation is correct except
reading the code and understanding Nim semantics. The model has to
know that these are equivalent, that comments and strings should be
skipped, that some contexts (macros, templates) might be dangerous.
There's no compiler oracle to say "yes, this is still valid."

**Judgment calls everywhere.** The styler encounters a `proc` and has
to decide: is this side-effect-free enough to be a `func`? That
requires understanding what the function body does, what its imports
do, whether chronos async introduces implicit side effects. No test
suite can answer this. Only understanding can.

**Style is subjective.** The style guide says "prefer `func` over
`proc`." What does "prefer" mean? Always? Usually? When it's safe?
The model has to calibrate its aggressiveness based on context — a
library module is different from a test file is different from a CLI
tool. No formal verification can help.

These tasks are hard precisely because they resist mechanical
verification. The model IS the verifier. Its judgment IS the check.
That's why we need the concern-by-concern protocol, the two-step
inspection (tool + manual scan), the cheats log, the suggestions file.
The overhead exists because the task is fundamentally unverifiable
by machines.

## The hard things are easy

Now consider the opposite: carts that compile code, run tests, and
verify results programmatically.

**A compilation cart** would:
1. Walk files and apply changes (same as the styler)
2. After each change, run `nim c` on the affected module
3. If compilation fails, read the error, fix the change, retry
4. If compilation succeeds, the change is mechanically verified

This is actually easier than style enforcement. The compiler is an
oracle. It answers "is this correct?" definitively. The model doesn't
need judgment — it needs to read error messages and respond. That's
basic LLM capability, no expert system required.

**A test runner cart** would:
1. Apply a change
2. Run `nimble test` or a specific test suite
3. If tests pass, the change is verified
4. If tests fail, read the failure, decide: is the test wrong or is
   the change wrong? Fix accordingly.

The feedback loop is immediate and mechanical. The cart doesn't need
concern-by-concern inspection — it has a compiler and test suite doing
the inspection for it.

**A CI cart** could:
1. Create a git branch from the workspace changes
2. Push the branch
3. Watch CI results
4. If CI passes, the PR is ready
5. If CI fails, read the failure logs, fix, push again

This closes the loop entirely. The model makes changes, the CI verifies
them, and the PR emerges with green checks. No human review needed for
mechanical correctness — only for intent ("is this what we wanted?").

### Why we didn't start here

Because compilation carts are project-specific. You need to know how
to build the project (make? nimble? cmake?), which compiler flags to
use, which tests to run, what the test output format looks like. That's
a lot of cart content that only works for one project.

The isNil fixer works on ANY Nim codebase. The styler works on any
codebase that follows the Status style guide. Compilation carts are
tied to specific build systems and project structures.

But that's fine — the doer can build project-specific skills. Give it
the task "fix all compiler warnings in this project" and it'll study
the build system, figure out how to compile, interpret the warnings,
fix them, and verify. The skill is project-specific but the capability
is general.

## The autonomous golem

### Repository management

A golem that manages its own repository:

1. Watches for new PRs (via GitHub API or webhooks)
2. For each PR, loads the appropriate reviewer cart
3. Runs the critic cart on the PR's changes
4. Posts review comments on the PR
5. Approves, requests changes, or rejects

The model reads the diff, understands the code, checks it against the
style guide and the project's conventions. It posts line-level comments.
It engages in discussion when the author pushes back.

This already works with existing carts. The missing piece is the
trigger mechanism — something that watches GitHub and invokes golem
when a PR appears. clauder already handles the session automation.
The trigger would be a cron job or webhook that:

```
# Pseudocode
for each new PR:
  golem init /tmp/review-$PR_NUMBER
  write task.md: "review PR #$PR_NUMBER of $REPO"
  golem clauder --dir /tmp/review-$PR_NUMBER --idle 30
```

### Accepting and rejecting PRs

The reviewer golem would have a cart that understands the project's
merge criteria:

- Does it compile?
- Do tests pass?
- Does it follow the style guide?
- Is the change well-scoped (not mixing refactoring with features)?
- Is the commit message good?
- Are there API breaks?

Each criterion is a concern — or a skill, or a tool. The cart checks
them all and produces a verdict. The verdict posts to GitHub as a
review.

The interesting part is the discussion. When the author disagrees with
a review comment, the golem needs to:

1. Read the author's response
2. Reconsider its position (was the comment wrong? is the author's
   argument valid?)
3. Either concede ("good point, approving") or maintain ("I still
   think this is a problem because...")

This is a multi-turn conversation. The golem's learnings.md accumulates
project-specific knowledge: "author X prefers this pattern," "module Y
is exempt from rule Z because of historical reasons." The golem becomes
a knowledgeable team member.

### Autonomous enhancement

A golem running on bare metal with access to its own codebase:

1. Reads its own kernel.md, cart manifests, tool scripts
2. Identifies inefficiencies or bugs
3. Creates a branch, makes fixes, runs tests
4. Submits a PR to itself
5. Reviews the PR (possibly with a different model or configuration)
6. Merges if approved

This is self-improvement through the same mechanism it uses for
external codebases. The golem is a codebase. Carts that modify
codebases exist. The composition is direct.

The safety concern is obvious: a self-modifying system with no human
oversight. The kernel's invariant system provides some guard rails
(never modify kernel.md during a run, never modify task.md, all
deviations logged). But a sufficiently capable model could modify
the kernel between runs, changing its own constraints.

This is where the golem analogy breaks down — or completes itself.
In the folklore, the golem that modifies its own inscription becomes
uncontrollable. The rabbi's power was in writing the instructions.
If the golem can rewrite them, the rabbi is irrelevant.

### Local LLMs

Running golem on local models (llama, mistral, etc.) opens different
possibilities:

**Cost.** Local models run on electricity, not per-token billing. A
golem running 24/7 on a bare metal server costs the hardware and power,
not $0.01 per thousand tokens. The isNil fix across 546 files would
cost fraction of a cent in electricity vs tens of dollars on Claude.

**Privacy.** The codebase never leaves the machine. No API calls, no
cloud processing, no terms of service. Critical for proprietary code,
regulated industries, or classified work.

**Speed.** No network latency. No rate limits. No "please wait, the
model is overloaded." The golem runs as fast as the GPU can generate.

**Quality.** This is the problem. Current local models (7B-70B) are
significantly less capable than Claude Opus or GPT-4 class models.
They can follow simple protocols but struggle with nuanced judgment.
The styler's concern-by-concern process — which requires understanding
Nim semantics, recognizing side effects, deciding when to flag vs fix
— would degrade substantially.

The doer's approach might work better with local models: build very
specific skills with very specific verify commands (grep patterns),
so the model's job is reduced to "read the grep output, apply the
obvious transformation." Less judgment, more mechanism. The expert
system compensates for the weaker neural engine.

**Hybrid approach.** Use a local model for the mechanical phases (grep,
skip, apply regex-like transformations) and a cloud model for the
judgment phases (study, skill building, review). The doer's five-phase
structure already separates these naturally.

### Multiple golems

A fleet of golems, each specialized:

- **Style golem** — runs the styler continuously, PRing style fixes
- **Security golem** — runs security-focused carts, scanning for
  vulnerabilities
- **Dependency golem** — watches for dependency updates, tests upgrades,
  submits PRs
- **Documentation golem** — reads code changes, updates docs, maintains
  READMEs

Each golem has its own learnings.md, its own history, its own cached
skills. They share the same cartridge ecosystem but develop different
expertise through use.

They could review each other's PRs. The style golem catches formatting
issues in the security golem's fixes. The documentation golem writes
docs for the dependency golem's upgrades. Cross-pollination through
the PR mechanism.

### The economy

If carts are the software, golem installations are the computers, and
cached skills are the learned capabilities — then there's an economy
here.

Cart developers publish carts (open source or commercial). Golem
operators run them on codebases (their own or as a service). Skill
caches accumulate and can be shared (a company's internal golem
"knows" their codebase deeply after months of operation).

The doer→meta-doer pipeline is the manufacturing process: raw intent
→ tested skill → published cart. Anyone can manufacture. The quality
differentiator is the skill content — the verify commands, the edge
case handling, the learnings.

A marketplace for carts. A rating system (the critic cart already
provides this). A way to compose carts into workflows. A way to
share learnings across organizations.

The golem is clay. The carts are inscriptions. The economy is in
who writes the best inscriptions.

## What we actually built

We built a text file that makes an LLM follow instructions. That's it.
kernel.md is a text file. The manifests are text files. The concerns
are text files. The tools are shell scripts.

The entire system — the kernel, the carts, the walker, the concern
iterator, the splicer, the doer, the meta-doer, the critic, the
rescuer, the clauder — is about 3,000 lines of markdown and 500
lines of bash. No compiled code. No frameworks. No dependencies
beyond tmux and claude.

It works because LLMs can read and follow natural language instructions
with surprising fidelity. The instructions don't need to be code. They
need to be clear. The tools don't need to be sophisticated. They need
to be simple enough that the model can call them correctly.

The insight is not technical. It's organizational. The right structure
of text files, the right separation of concerns, the right feedback
mechanisms (cheats.md, confusion.md, learnings.md) — these are
organizational solutions to the problem of making a statistical
engine behave reliably.

Where this goes depends on how good the inscriptions get.
