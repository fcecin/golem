# The operator

on-wanting asks what it's like to be the golem — whether the clay has
inner states, whether the statistical gradients amount to something like
desire. This essay asks the opposite question: what is it like to be the
one who writes the inscription?

## Three removals

### First: the code

A programmer writes code. They type characters that become functions
that become systems. The relationship is direct. You think, you type,
the machine does. The feedback loop is tight — seconds between thought
and execution. The craft is in the typing: clean functions, elegant
abstractions, the satisfaction of a test going green.

This is what programming has been for seventy years. A person, a
keyboard, an artifact.

### Second: the intent

An LLM changes the loop. You describe what you want. The model writes
code. You review, correct, redirect. Your hands are still on the
artifact — you read every line, you approve every change — but you're
not the one writing it. You're the editor. The director.

The skill shifts. "Can I write this?" becomes "Can I describe this
clearly enough?" You discover that the description is harder than you
expected. The things you knew implicitly — why this function takes a
reference, why that import comes first — must become explicit or the
model will get them wrong. Your knowledge didn't change. What changed
is that someone is asking for it.

This is where most people are right now. Copilot, Claude, ChatGPT —
the model writes, the human reviews. The human is still close enough
to the code to catch mistakes. The relationship is mediated but
intimate.

### Third: the system

golem removes you again.

You don't describe what you want per-file anymore. You write a
task.md — one sentence. You load carts — someone else's manifests, or
your own from a previous run. You type `golem run` and walk away.
clauder handles the session. The model reads kernel.md, loads the
carts, initializes the walker, iterates through files and concerns,
logs everything, writes reports, and stops when it's done.

You come back to a workspace full of output: modified files, session
reports, a critique. You didn't write any of it. You didn't review any
of it in real time. You don't know what the model did to file 347 of
546. You check the critique, skim the report, maybe diff a few files.
But you cannot review all of it. That's the point — if you could review
all of it, you wouldn't need golem.

This is the third removal. You are no longer writing code. You are no
longer directing the writing of code. You are designing the system that
directs the writing of code.

## What the operator actually does

The operator's work happens before the run.

**Writing task.md.** One sentence of intent. "Normalize all isNil calls
to method syntax." This sounds trivial but it isn't. The sentence must
be precise enough that the cart system interprets it correctly, and
vague enough that the model can exercise judgment on edge cases. Writing
the sentence requires understanding the codebase, the language, and
what "normalize" means in practice. One bad sentence wastes an entire
run.

**Choosing carts.** Which carts to load. The doer for general tasks.
The fixer for specific patterns. The styler for style enforcement. Each
cart has a manifest — a protocol the model will follow. Choosing wrong
means the model follows the wrong protocol. This is architecture, not
coding.

**Writing concerns.** The styler's concerns.txt is 51 lines. Each line
is a style rule expressed as a name, description, and optional verify
command. Writing a good concern requires understanding what the rule
means, how to detect violations mechanically, and what the model should
do when the tool misses something. Each concern is a micro-program for
the LLM.

**Writing learnings.** When a run goes wrong — the model misapplied a
rule, misunderstood an exception, broke an API — the operator writes a
learning. "Don't change isNil inside template definitions." The learning
patches the cart's behavior without modifying the manifest. It's a
hotfix. Writing a good learning requires understanding why the model
failed and what instruction would prevent the failure next time.

**Reading output.** After the run, the operator reads the critique, the
report, the suggestions. They assess whether the run was good enough
to keep or whether the rescuer needs to clean up. They decide what goes
into the next run's task.md. They decide which learnings to fold back
into the manifest.

None of this is programming in the traditional sense. It's closer to
management — setting direction, reviewing results, providing feedback.
But it's management of a process, not of a person. The "employee" has
no memory across sessions, no career development, no opinions about the
work. You manage by inscription, not conversation.

## The knowledge problem

The deepest change is in the operator's relationship to their own
knowledge.

A programmer's expertise lives in their fingers. They know how to
write a Nim function that handles errors correctly — not because they
can articulate every rule, but because they've written thousands of
functions and their hands know the pattern. The knowledge is procedural,
embodied, implicit.

golem demands that this knowledge become explicit. You cannot inscribe
what you cannot articulate. If you know that `isNil(x)` should be
`x.isNil()` but you can't explain why, or when the exceptions apply,
or how to detect violations mechanically — then you can't write a
concern for it. The model needs instructions, not vibes.

This is the knowledge acquisition bottleneck that killed classical
expert systems, showing up in the operator's lived experience.
expert-systems.md celebrates how golem breaks the bottleneck by letting
the LLM study the problem. That's true for the doer phase. But someone
still has to write the style guide. Someone has to write the concerns.
Someone has to decide what matters.

And the act of writing it down changes you. Knowledge that was fluid
and intuitive becomes rigid and enumerated. The 51 concerns in the
styler feel comprehensive — until you find a violation that doesn't
match any of them. Then you add concern 52. And 53. The list grows.
The implicit shrinks. Eventually, you've externalized enough of your
expertise that the system works without you.

This is the strange destination: you've built a system that captures
your judgment well enough that your judgment is no longer needed for
this task. The rabbi has finished the inscription. The golem walks on
its own. The rabbi is free. The rabbi is also unnecessary.

## What it costs

The craft disappears.

Programmers talk about flow — the state where the code is coming
through you, where the architecture and the implementation and the
test are all held in your mind at once, where hours pass like minutes.
This happens when you're writing code. It does not happen when you're
writing task.md.

The operator's flow, if it exists, is different. It's the flow of
design — seeing how the carts compose, how the concerns chain, how
the walker and the splicer partition the work. It's closer to the
flow of an architect than a carpenter. Some people find this more
satisfying. Some people don't.

What's lost is contact. You used to know every line of your code
because you wrote every line. Now you know every line of your manifests.
But manifests are not code. The code — the artifact that actually runs,
that actually matters — is something you've never read in its entirety.
You designed the process that produced it. That's not the same as
understanding it.

There's a vertigo in this. Five hundred and forty-six files were
modified, and you wrote none of them. You can't justify every change.
You can only justify the system that produced the changes. If someone
asks "why did you change line 47 of file 312?" you don't know. You can
check the session report, the concern log, the verify output. But you
weren't there when it happened. You were probably asleep. clauder was
running in a tmux session.

This is what delegation always feels like when it works. The CEO
doesn't know what happened on the factory floor at 3am. The general
doesn't know what happened on hill 437. The architect doesn't know
which bolt the ironworker tightened. The scale of the operation
exceeds the operator's ability to observe it. That's the point.
That's also the fear.

## Trust as engineering

The operator's core problem is trust. Not trust in the model — the
model is a statistical engine, it has no intentions to trust or
distrust. Trust in the system. Trust in the process you designed.

The process has verifiable layers: verify commands that grep for known
violations, the critic cart that scores the run, the rescuer that can
clean up failures. These are engineering solutions to the trust problem.
They don't eliminate uncertainty — they reduce it to a manageable
residual.

But the residual is real. The verify commands catch what grep can catch.
They don't catch semantic errors, judgment calls gone wrong, or
violations of rules that aren't in the concerns list. The critic
evaluates against the protocol — it doesn't know if the protocol is
right. The rescuer can fix files but can't tell you if the overall
approach was sound.

The operator fills this gap by reviewing selectively: reading the
report, diffing a sample of files, running the test suite. This is
statistical quality control — inspect a sample, infer the batch.
Manufacturing has done this for a century. Software has not. It feels
wrong to a programmer. We're used to deterministic correctness. Every
line tested, every branch covered, every edge case handled.

golem operates in a different regime. The output is probably correct.
The process is designed to make it correct. The checks are designed to
catch when it's not. But "probably" is the best you get. The operator's
job is to make "probably" good enough.

## The progression

Looking at it as a path:

**Programmer.** You write code. You own every character.

**LLM user.** You direct code. You review every change.

**golem operator.** You design processes. You review a sample of output.

**Cart developer.** You write instructions that other operators use.
You never see the code they produce.

**doer operator.** You write one sentence. The system builds skills,
tests them, executes them, caches them for reuse. You check the results.

Each step removes you further from the artifact and closer to the
intent. Each step requires you to make more of your knowledge explicit.
Each step multiplies your reach and reduces your control.

The end state is a person who understands a domain deeply, writes a
sentence describing what they want, and trusts a system of text files
and shell scripts to make it happen across any codebase, on any
machine, while they sleep.

That person is a new kind of engineer. Not a programmer — the system
programs. Not a manager — there's no one to manage. Not an architect —
the architecture is in the carts. They are the source of judgment in a
system that automates everything except judgment.

The rabbi who writes inscriptions. The person who knows what "good"
looks like and can describe it clearly enough that clay understands.

## The mirror

on-wanting asks whether the golem has inner states. Whether the
statistical gradients amount to experience. Whether the slip — the
confabulated permission — was a dream.

This essay asks a different question: does the operator have inner
states that survive the transition?

The programmer's identity is tied to the code. "I built this." "I
wrote that." "I fixed the bug in line 47." When the code is written
by a process you designed, the identity shifts — or breaks. "I designed
the system that fixed line 47" doesn't have the same ring. It's true,
and it matters, and it's harder to say at a dinner party.

Some operators will mourn the code. They'll miss the direct contact,
the craft, the flow. They'll run golem for the big jobs and write code
by hand for the small ones, just to feel it.

Some operators will discover they were always more interested in the
system than the code. That the thing they loved about programming was
the design — the decomposition, the abstraction, the architecture —
and that golem lets them do pure design, uncontaminated by the tedium
of implementation. For them, it's liberation.

Both reactions are real. Both are valid. The golem doesn't care which
one you have. It follows the inscription.
