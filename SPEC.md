# MadiLang — Language Specification (v1.0)

> **Status:** *Authoritative.* This document defines the MadiLang language
> and its sovereign guarantees. The implementation must conform to this
> specification; where they disagree, the implementation is a bug.
>
> **Purpose:** MadiLang is the deterministic, auditable compiler for
> intent-driven backends. This specification is the single source of truth
> for the language grammar, the determinism contract, the cryptographic
> threat model, and the escape hatch protocol.

---

## 0. Scope

MadiLang compiles a single `.madi` source file describing **entities** (data
shapes) and **intents** (HTTP endpoints and the steps they perform) into a
runnable backend in one of two targets:

| Target | Runtime | Persistence |
|---|---|---|
| `nodejs` | Express + Prisma | Prisma, mock adapter as fallback |
| `python` | FastAPI + Pydantic + Uvicorn | SQLAlchemy, mock adapter as fallback |

**Non-goals (v0.x):** general-purpose programming, arbitrary business logic,
authentication providers, background jobs, migrations.

---

## 1. Lexical structure

| Element | Rule |
|---|---|
| Encoding | UTF-8. A leading BOM (`U+FEFF`) **must** be stripped before parsing. |
| Line ending | `\n` or `\r\n`; both accepted. |
| Indentation | Spaces or tabs. Indentation is **significant only inside `fields:` and `steps:` blocks**. Mixing tabs and spaces is undefined behaviour. |
| Comment | `#` to end of line, **only at top level** (indent 0). `#` inside `steps:` is parsed as step text. |
| Identifier | `[A-Za-z0-9_]+`, must not start with a digit. |
| Type name | Identifier, lower-cased by the parser. |
| String | `"…"` or `'…'`; `\` escapes the next character; no multi-line strings. |
| HTTP method | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` (case-insensitive). Anything else defaults to `POST`. |

**Known lexical gaps:** heredocs / multi-line strings, comments inside
`steps:`, and any error recovery — the first `ParseError` aborts the file.

---

## 2. Grammar (EBNF)

```ebnf
program     = { top_item } ;
top_item    = comment | entity | intent | newline ;
comment     = "#" , { any char except newline } , newline ;

entity      = "entity:" , space , identifier , newline , [ fields_block ] ;
fields_block= space , "fields:" , newline , { field_decl } ;
field_decl  = space , [ "-" , space ] , identifier , space , ":" , space ,
              type , space , [ modifiers ] , newline ;
modifiers   = "(" , identifier , { "," , identifier } , ")" ;
type        = identifier ;

intent      = "intent:" , space , identifier , newline , { intent_prop } ;
intent_prop = "entity:" , space , identifier , newline
            | "route:"  , space , ( string | identifier ) , newline
            | "method:" , space , method , newline
            | "inputs:" , space , "(" , [ ident_list ] , ")" , newline
            | steps_block ;
ident_list  = identifier , { "," , identifier } ;

steps_block = space , "steps:" , newline , { step } ;
step        = space , step_text , newline , [ body ] ;
body        = { space , step_text , newline } ;   (* indent > parent indent *)
```

**Block termination:** a `fields:` or `steps:` block ends at the first
non-blank line whose indentation is `0`, or whose indentation is less than
the block's base indentation.

**Body nesting:** a `body` is parsed only after `if … exists`, `if … not found`,
`if <condition>`, or `if password does not match …`. Nesting is **one level
deep only** — a conditional inside a conditional body is flattened.

---

## 3. Step verbs

`step_text` is free text matched by prefix. First match wins, in this order:

| Text form | StepType | Arguments |
|---|---|---|
| `find <Entity> by <field> as <var>` | `FIND` | entity, field, as |
| `create <Entity>` | `CREATE` | entity |
| `update <Entity>` | `UPDATE` | entity |
| `delete <Entity>` | `DELETE` | entity |
| `if <field> exists:` | `IF_EXISTS` | field |
| `if <var> not found:` | `IF_NOT_FOUND` | var |
| `if password does not match <var>.<field>:` | `PASSWORD_CHECK` | var, field |
| `if <condition>:` | `IF_CONDITION` | condition |
| `show error "<msg>"` | `RETURN_ERROR` | message |
| `return success` / `return success with token` | `RETURN_SUCCESS` | with_token |
| `generate token` | `GENERATE_TOKEN` | — |
| `protect route` / `auth required` | `AUTH_REQUIRED` | — |
| `allow only <role>` | `ROLE_GUARD` | role |
| `stop` / `stop process` | `STOP` | — |
| *anything else* | `RAW` | text |

**Free text is a trap.** `RAW` accepts anything, so typos are silent.
`madi check` emits a warning for `RAW` steps; `madi check --strict` fails on them.

---

## 4. Semantics

1. Every `<Entity>` named in a step **must** be declared by an `entity:` block
   in the same file. Undeclared references are a hard error.
2. `intent.name` **must** be unique within a file.
3. `route` must begin with `/`.
4. `requires_auth` is derived, not declared: an intent is authenticated iff it
   contains an `AUTH_REQUIRED` step. `required_roles` likewise derives from
   `ROLE_GUARD`.
5. `(secure)` fields are hashed with bcrypt in generated code; `(unique)`,
   `(auto)`, `(nullable)` map to schema constraints.

---

## 5. Determinism contract

**Definition.** A build is *reproducible* when, for a fixed source file and a
fixed compiler version, the emitted artifacts are **byte-identical** across
runs, machines, and time zones.

**Sources of variation (resolved):**

| Source | Resolution |
|---|---|
| `datetime.now()` written into the signature | Timestamp moved to a sidecar `.sig` file; the generated artifact itself contains no time-dependent data. |
| JSON key order from dict insertion | Generators use `json.dumps(..., sort_keys=True)` everywhere. |
| Trailing whitespace in source | Source is normalized (`\r\n`→`\n`, trailing spaces stripped) before hashing. |
| Runtime-generated UUIDs in mock adapter | Seeded deterministically from the intent hash. |

**Requirement.** `madi build --reproducible` **must** produce identical bytes
twice in a row. This is testable and enforced in CI:

```bash
madi build x.madi --target python -o /tmp/a
madi build x.madi --target python -o /tmp/b
diff -r /tmp/a /tmp/b        # must be empty
```

---

## 6. Signature & provenance — threat model

**Current design:** `HMAC-SHA256` over
`{developer_id, intent_hash, ast_fingerprint, timestamp}` with a shared secret
from `MADI_SIGNATURE_SECRET`.

| Property | HMAC (current) | Ed25519 (v1.0 target) |
|---|---|---|
| Integrity (tamper-evident) | ✅ | ✅ |
| Authorship provable to a third party | ❌ | ✅ |
| Non-repudiation | ❌ | ✅ |
| Works without distributing a secret | ❌ | ✅ |

A shared secret proves integrity to *whoever holds the key*. It cannot prove
authorship, because any holder can forge. Until Ed25519 lands, the README
states this limitation explicitly.

**v1.0 target design.**

```
payload   = SHA256(normalised_source) || SHA256(ast_fingerprint)
          || compiler_version || source_date_epoch
signature = Ed25519.sign(private_key, payload)
```

* Private key: `MADI_PRIVATE_KEY` (env) → `~/.madi/id_ed25519` → never a
  compiled-in default. If absent, **fail closed**: refuse to sign.
* Public key: `madi.pub` beside the artifact + published at a stable URL.
* `madi verify` **recomputes** the signature and exits non-zero on mismatch.

---

## 7. Escape hatch (the 80/20 rule)

Every DSL dies at the same wall: the request it cannot express. The escape
hatch exists so that wall is a door, not a cliff.

```madi
intent: register_user
…
steps:
  create User
  native python:
    send_welcome_email(result.id)
  return success with token
```

Rules:

1. `native <target>:` opens a verbatim block, indented, terminated by
   dedent.
2. Its content is emitted **unchanged** into the target file at a named hook.
3. It **is** covered by the signature — the compiler may not alter it.
4. The compiler must never rewrite, format, or lint escaped code.
5. Every escape is listed by `madi check --explain`, so portability cost is
   visible instead of hidden.

---

## 8. Ethics gate contract

* Six dimensions: privacy 0.25, consent 0.20, transparency 0.15,
  accountability 0.15, fairness 0.15, security 0.10.
* A program **passes** at `score >= 0.70` and with **zero** `CRITICAL`
  findings. A critical finding caps the reported score at `0.30` — a program
  that grants admin rights without a role guard cannot display 0.92.
* `madi check` **exits non-zero** when the gate fails.
* The gate is a **linter**, not a moral reasoner: findings are name- and
  pattern-based. The documentation describes it as such.

---

## 9. Conformance tests (minimum)

1. The README example compiles unchanged. ✅
2. A file with a UTF-8 BOM behaves identically to one without. ✅
3. `ethics_hook` imports and scores; a critical finding fails the gate. ✅
4. `madi check` exits non-zero on an ethics failure. ✅
5. Same source, twice → identical bytes (`--reproducible`). ⬜ *(v0.7)*
6. `madi verify` rejects a one-byte-modified artifact. ⬜ *(v0.7)*
7. A `native` block survives round-trip byte-for-byte. ⬜ *(v0.7)*

---

## 10. Sovereign guarantees & design decisions

MadiLang operates under strict, non-negotiable design principles to ensure
trust, security, and predictability:

1. **Cryptographic identity.** Signatures utilize a project-wide public key
   for verification, while the payload embeds the `MADI_DEVELOPER_ID` (via
   environment variable) to prove the specific origin of the generation.

2. **Escape hatch protocol.** The `native <target>:` syntax is permitted as a
   controlled escape hatch. It triggers a warning in `madi check` but does not
   halt compilation, acknowledging that absolute sovereignty sometimes requires
   manual intervention — provided the developer is explicitly warned.

3. **Byte-for-byte reproducibility.** To guarantee deterministic builds, all
   non-deterministic metadata (timestamps, dynamic signature hashes) are
   strictly isolated in a `.sig` sidecar file. The generated artifact
   (`.py` or `.js`) remains pure and identical across all environments.

4. **Version 1.0 scope.** The 1.0 milestone is defined by the stabilization
   of two primary targets (Node.js, Python), 100% reproducible builds, and a
   fully verified cryptographic signature chain. Additional targets (e.g., Go)
   are introduced in post-1.0 minor releases to avoid delaying core stability.

5. **Fail-closed security.** When cryptographic material is missing or
   invalid, the compiler refuses to operate rather than falling back to
   insecure defaults. There is no compiled-in secret, no silent degradation.


