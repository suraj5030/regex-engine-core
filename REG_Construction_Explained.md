# REG Node Construction — Step-by-Step Walkthrough

This document explains how the parser builds an NFA (Non-deterministic Finite Automaton) from a regular expression, using `((0)|(1))*` as the running example.

---

## Key Data Structures

- **REG_node** — A single state (circle) in the NFA. Has up to two outgoing edges, each with a label (`'0'`, `'1'`, or `'_'` for ε).
- **REG** — A sub-NFA defined by a start node and an accept node.

---

## Building Blocks

### 1. `create_REG_char(c)` — Character REG

Creates the simplest NFA: two nodes connected by a single character edge.

### 2. `OR_REGS(reg1, reg2)` — Union / Alternation

Wraps two REGs with a new start and accept, branching via ε-transitions.

### 3. `concat_REGS(reg1, reg2)` — Concatenation

Chains two REGs by connecting reg1's accept to reg2's start with ε.

### 4. `kleene_star_REG(reg)` — Kleene Star

Wraps a REG with loop-back and skip edges.

---

## Full Example: `((0)|(1))*`

The parser processes the expression recursively. Here is every step in order.

---

### Step 1 — Parse `0` → `create_REG_char('0')`

Two nodes are created: **N0** (start) and **N1** (accept).

**REG_0** = `{ start: N0, accept: N1 }`

![Step 1 — create_REG_char('0')](images/step1_char_0.png)

---

### Step 2 — Parse `1` → `create_REG_char('1')`

Two more nodes: **N2** (start) and **N3** (accept).

**REG_1** = `{ start: N2, accept: N3 }`

![Step 2 — create_REG_char('1')](images/step2_char_1.png)

---

### Step 3 — Apply `|` → `OR_REGS(REG_0, REG_1)`

Two new outer nodes: **N4** (outer start), **N5** (outer accept).

Edges added:
- N4 —ε→ N0  (branch to `0` path)
- N4 —ε→ N2  (branch to `1` path)
- N1 —ε→ N5  (`0` path merges to accept)
- N3 —ε→ N5  (`1` path merges to accept)

**REG_OR** = `{ start: N4, accept: N5 }`

![Step 3 — OR_REGS](images/step3_or.png)

---

### Step 4 — Apply `*` → `kleene_star_REG(REG_OR)`

Two new outer nodes: **N6** (final start), **N7** (final accept).

Edges added:
- N6 —ε→ N4  (enter the loop)
- N6 —ε→ N7  (skip — accept empty string)
- N5 —ε→ N4  (loop back for another iteration)
- N5 —ε→ N7  (exit the loop)

**REG_STAR** = `{ start: N6, accept: N7 }` — this is the final NFA.

![Step 4 — kleene_star_REG](images/step4_star.png)

---

## Complete NFA

![Final NFA for ((0)|(1))*](images/final_nfa.png)

---

## Summary Table

### All 8 Nodes

| Node | Created By | Role |
|------|------------|------|
| N0 | `create_REG_char('0')` | Start of `0` sub-NFA |
| N1 | `create_REG_char('0')` | Accept of `0` sub-NFA |
| N2 | `create_REG_char('1')` | Start of `1` sub-NFA |
| N3 | `create_REG_char('1')` | Accept of `1` sub-NFA |
| N4 | `OR_REGS` | Outer start of `(0\|1)` |
| N5 | `OR_REGS` | Outer accept of `(0\|1)` |
| N6 | `kleene_star_REG` | **Final start** of `(0\|1)*` |
| N7 | `kleene_star_REG` | **Final accept** of `(0\|1)*` |

### All 10 Edges

| From | Label | To | Created By |
|------|-------|----|------------|
| N0 | `'0'` | N1 | `create_REG_char('0')` |
| N2 | `'1'` | N3 | `create_REG_char('1')` |
| N4 | ε | N0 | `OR_REGS` — first_neighbor |
| N4 | ε | N2 | `OR_REGS` — second_neighbor |
| N1 | ε | N5 | `OR_REGS` — reg1.accept → outer_accept |
| N3 | ε | N5 | `OR_REGS` — reg2.accept → outer_accept |
| N6 | ε | N4 | `kleene_star_REG` — enter loop |
| N6 | ε | N7 | `kleene_star_REG` — skip (accept ε) |
| N5 | ε | N4 | `kleene_star_REG` — loop back |
| N5 | ε | N7 | `kleene_star_REG` — exit loop |

---

## What Strings Does This Accept?

The language is **{0, 1}\*** — all binary strings including the empty string.

| Input | Accepted? | Path Through NFA |
|-------|-----------|-------------------|
| ε (empty) | ✅ | N6 →ε→ N7 |
| `"0"` | ✅ | N6 →ε→ N4 →ε→ N0 →'0'→ N1 →ε→ N5 →ε→ N7 |
| `"1"` | ✅ | N6 →ε→ N4 →ε→ N2 →'1'→ N3 →ε→ N5 →ε→ N7 |
| `"01"` | ✅ | N6 →ε→ N4 →ε→ N0 →'0'→ N1 →ε→ N5 →ε→ N4 →ε→ N2 →'1'→ N3 →ε→ N5 →ε→ N7 |
| `"110"` | ✅ | Loop twice through `1`-branch, once through `0`-branch |
| `"a"` | ❌ | No edge labeled `'a'` exists |
