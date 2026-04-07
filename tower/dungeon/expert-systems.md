# Expert systems and golem

## What is an expert system

An expert system is a program that encodes human decision-making into
rules. It doesn't learn. It doesn't generalize. It follows a decision
tree written by someone who understood the domain. The knowledge is
explicit — you can read it, audit it, edit it.

Expert systems dominated AI from the 1970s to the 1990s. MYCIN diagnosed
infections. XCON configured VAX computers. DENDRAL identified chemical
compounds. They worked well within their domains. They failed outside
them. They were brittle, expensive to maintain, and couldn't handle
ambiguity.

The knowledge acquisition bottleneck killed them: extracting rules from
human experts and encoding them into formal logic was slow, error-prone,
and never complete. The expert always knew more than the rules captured.

## Neural networks: the other path

Neural networks took the opposite approach. Instead of encoding rules,
you train a statistical model on data. The model discovers its own
patterns. No rules to write. No knowledge to extract. Just data in,
behavior out.

The problem: the model is opaque. You can't read its rules. You can't
audit its reasoning. You can't edit its knowledge. When it's wrong, you
don't know why. When it's right, you don't know why either.

For decades, neural networks were too small and too slow to compete with
expert systems on practical tasks. That changed around 2012 (deep
learning), accelerated in 2017 (transformers), and exploded in 2022-2023
(large language models).

## The hybrid dream

Combining expert systems with neural networks has been an academic pursuit
since the 1990s. The idea: use the neural network for perception and
pattern matching (what it's good at), and the expert system for reasoning
and decision-making (what it's good at).

Various approaches were tried:

- **Neuro-symbolic AI**: embed symbolic reasoning inside neural
  architectures. Promising in theory, fragile in practice.
- **Neural network rule extraction**: train a network, then extract
  rules from its weights. Worked for small networks, collapsed at scale.
- **Knowledge-guided learning**: use expert rules to constrain or
  initialize neural network training. Helped with small data problems.
- **LLM + tool use**: give a language model access to structured tools
  (calculators, databases, APIs). The model decides when to call which
  tool. This is the approach that actually worked at scale.

The breakthrough was that LLMs could act as the glue between rigid tools
and fuzzy intent. You don't need to formalize the decision logic — the
model handles that. You just need to give it the right tools and enough
context.

## Humans are expert systems

Before any of this existed, there was the original expert system: a human
being. A senior engineer doesn't consult a decision tree. They have
internalized thousands of rules through experience, many of which they
can't articulate. They have intuition — pattern matching trained on years
of data. They have judgment — the ability to weigh competing concerns and
choose.

When a human drives an LLM, the results are fantastic. This is not a
coincidence. The human provides what the LLM lacks: domain expertise,
quality judgment, context about what matters and what doesn't. The LLM
provides what the human lacks: tireless execution, massive context
windows, instant recall, and the ability to process 546 files without
getting bored.

The human is the expert system. The LLM is the compute engine. Together
they produce results neither could achieve alone.

But the human gets tired. The human has a job, a family, limited hours.
The human can't sit at a terminal pasting boot phrases 546 times.

## golem is an expert system for LLMs

This is what golem is. It's the attempt to encode the human expert's
knowledge — not into formal logic, but into natural language documents
that an LLM can read and follow.

The kernel is the operating system rules. The cart manifests are the
domain knowledge. The concerns.txt files are the checklists. The verify
commands are the automated checks. The learnings.md is the accumulated
experience. The cheats.md is the audit trail.

None of this is code in the traditional sense. It's all text — markdown
files that a human wrote and an LLM reads. The "expert system" is a
collection of documents that, when loaded into a model's context window,
cause it to behave as if it had the human's expertise.

This solves the knowledge acquisition bottleneck that killed classical
expert systems. You don't need to formalize the expert's knowledge into
production rules and inference engines. You write it in English. The LLM
is the inference engine. The natural language IS the formalism.

## Cart development is expert system development

Writing a cart is writing an expert system. The manifest is the knowledge
base. The tools are the sensors and actuators. The concerns are the rules.
The learnings are the maintenance patches.

When the doer cart builds a skill at runtime, it's doing automated
knowledge acquisition — the thing that killed classical expert systems.
The LLM studies the problem, identifies the patterns, writes the rules
(verify commands), tests them, and caches them for reuse. The knowledge
acquisition bottleneck is broken because the knowledge engineer is the
same entity as the expert: the LLM.

When the meta-doer promotes a skill into a cart, it's publishing an
expert system. The cart can be installed by anyone, on any golem instance,
and the LLM that runs it gains that expertise instantly. "I know kung fu."

## The loop

The full loop is:

1. Human has expertise ("isNil should be normalized to method syntax")
2. Human writes a task.md (one sentence of intent)
3. golem + doer cart builds skills (automated knowledge acquisition)
4. LLM executes the skills across a codebase (automated application)
5. meta-doer promotes skills into a cart (knowledge packaging)
6. Cart is published (knowledge distribution)
7. Any LLM can now do what the human expert knew

Step 1 took years of Nim experience. Steps 2-7 took 20 minutes.

The human is still the source of expertise. But the encoding, testing,
application, and distribution of that expertise is automated. The expert
system builds itself from a single sentence of human intent.

## What's different this time

Classical expert systems failed because:

- Knowledge acquisition was manual and expensive
- Rules were brittle and couldn't handle edge cases
- Maintenance was a nightmare as the domain evolved
- They couldn't reason about things outside their rules

golem's approach sidesteps all of these:

- Knowledge acquisition is automated (the LLM studies the problem)
- Edge cases are handled by the LLM's judgment (not rigid rules)
- Maintenance is just editing markdown files
- The LLM can reason about anything it encounters

The expert system doesn't need to be complete. It just needs to be good
enough to guide the LLM. The LLM fills in the gaps. The verify commands
catch the obvious cases. The manual scan catches the subtle ones. The
suggestions.md catches the ones nobody should auto-fix.

This is not the old dream of perfect formal reasoning. This is "good
enough" expert knowledge, amplified by a statistical engine that can
handle ambiguity. It works because it doesn't try to be perfect. It
tries to be useful.

## The name

A golem is a creature from Jewish folklore — an animated being made from
clay, brought to life by inscribing instructions on it. The golem follows
its instructions literally. It is powerful but not intelligent. It does
exactly what the inscription says, for better or worse.

The analogy is precise. kernel.md is the inscription. The LLM is the
clay. The carts are additional inscriptions that give it new capabilities.
The human is the rabbi who writes the instructions and takes responsibility
for what the golem does.

The golem doesn't understand. It executes. The understanding is in the
instructions. The instructions are written by humans, for a machine that
can read natural language as if it were code.

That's what we built.

HUMAN NOTE (one of the very few hand-crafted lines in this entire repo): Claude Opus guessed the significance of "golem" on its own. I guess it was too on the nose.

