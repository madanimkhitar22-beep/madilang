# MadiLang — Strategic Roadmap

> This is the public plan for MadiLang's evolution. Authoritative rules live
> in [SPEC.md](SPEC.md); the ethics and signature contracts are defined in
> sections 5–8 there.

---

## The one-line goal

**MadiLang is the deterministic, auditable compiler for intent-driven backends.**

Not "describe code and get code" — every chat model does that. The scarce good
is *reproducibility and provenance*: the same intent produces the same bytes,
and every artifact can be traced back to the intent that created it, by a
third party, without trusting the author.

Every roadmap item below is judged against that sentence.

---

## Phase 1 — Make every claim true

Nothing in the README may exceed what the code does.

- [x] Ethics layer repaired, wired, and gated (`madi check` exits non-zero)
- [x] `plugins/__init__.py`; 5 regression tests
- [x] UTF-8 BOM robustness in the parser
- [x] `SPEC.md` — grammar, determinism contract, threat model, escape hatch
- [x] `ROADMAP.md` — this document
- [x] One-command verification (`scripts/verify.py`)
- [x] `madi build` command for compilation without execution
- [x] `.gitattributes` for cross-platform determinism
- [ ] Wire `security_hook` the same way the ethics layer was wired
- [ ] README truth pass: replace "cryptographic proof of origin" with an
      accurate statement until asymmetric signing lands (SPEC §6)
- [ ] Describe the ethics gate as a **linter**, not a moral reasoner
- [ ] Close the open Dependabot alerts
- [ ] Honest CI badge: report the real matrix, not "10/10"

**Exit criterion:** every bullet in the README maps to a test or a section of
SPEC.md.

---

## Phase 2 — The two provable properties

This is the phase that makes the project different from every other generator.

- [ ] `madi build --reproducible`: byte-identical output across runs
- [ ] Determinism test in CI (`build` twice, `diff -r`)
- [ ] Ed25519 signing; no compiled-in fallback secret; fail closed when no key
- [ ] `madi verify` recomputes the signature and rejects a one-byte change
- [ ] Tamper test in CI

**Exit criterion:** two claims, two tests, both failing loudly when violated.

---

## Phase 3 — The five-minute proof

- [ ] `demo/` — one command that generates, boots, and curls a live endpoint
- [ ] A 90-second screen recording whose script is committed verbatim
- [ ] README's first screen shows the working demo, not the philosophy

**Exit criterion:** a stranger reproduces the demo without asking a question.

---

## Phase 4 — The wall has a door

- [ ] `native <target>:` escape hatch, emitted verbatim (SPEC §7)
- [ ] Round-trip test: escaped code survives byte-for-byte
- [ ] Structured errors with line/column and a suggestion
- [ ] `madi check --explain` lists every escape used

**Exit criterion:** a real request that the language cannot express no longer
requires abandoning the language.

---

## Phase 5 — Ship v1.0

- [ ] Version 1.0.0, CHANGELOG, annotated tag, GitHub release
- [ ] PyPI release that actually contains the fixed wheel
- [ ] All conceptual projects consolidated under `research/` (one repo,
      clearly labelled as conceptual) — or moved to a separate repository

**Exit criterion:** one living repository that a reviewer can read in an hour.

---

## Phase 6 — People

Deliberately last. Tooling follows users; it does not create them.

- [ ] Language server (diagnostics first, completion later)
- [ ] Three external users with a real use case
- [ ] Contribution guide that a first-time contributor actually completes

---

## Non-goals for 1.0

A Go target, a plugin marketplace, and a package registry are all good ideas
that would each cost a month. 1.0 means: **two targets, reproducible, signed,
with an escape hatch.**