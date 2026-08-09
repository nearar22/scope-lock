# ScopeLock

ScopeLock is a reusable semantic change-control primitive for GenLayer. A client and contractor sign one immutable project baseline. Every later work request is judged against that baseline and becomes either immediately authorized included work, a bilateral change order, or a rejected out-of-scope request.

**Bradbury deployment:** [`0x76Be...fEDD`](https://explorer-bradbury.genlayer.com/address/0x76Be273A43a5032dcc7Df16E97599E38fEf9fEDD) · [deployment transaction](https://explorer-bradbury.genlayer.com/tx/0x7707d4243c36a89a29b7c83c73ac0ac99b4359d5db25ba4b56e25e2b13f66a5c)

## Why this needs an Intelligent Contract

Real scope is written in meaning, not function selectors. "Add filters listed in the dashboard deliverables" and "build native mobile apps" may use the same technology but create completely different obligations. GenLayer validators independently compare each request with the signed scope, deliverables, and exclusions, then agree on the gate and bounded cost, time, and risk impacts.

## Authorization lifecycle

```text
IN_SCOPE     -> AUTHORIZED -> CONSUMED
CHANGE_ORDER -> PENDING_APPROVALS -> AUTHORIZED -> CONSUMED
OUT_OF_SCOPE -> REJECTED
```

An `IN_SCOPE` receipt is usable immediately. A `CHANGE_ORDER` cannot become authority until both the client and contractor sign it on-chain. Only the bound contractor can consume an authorization, and each authorization is single-use. Canceling the project invalidates every outstanding authorization without rewriting its history.

## Consensus and deterministic controls

The assessor returns `IN_SCOPE`, `CHANGE_ORDER`, or `OUT_OF_SCOPE`, three impact axes, a rationale, and proposed amendment language. Validators must agree on the gate exactly and each impact within 15 points. Deterministic code caps all `IN_SCOPE` impacts at 33, binds the two wallets, rejects request-id replay, requires bilateral change-order approval, prevents double signatures and double consumption, and checks project status whenever authority is queried or consumed.

## Interface

```text
create_project(contractor, title, scope, deliverables, exclusions)
accept_project(project_id)
request_change(project_id, request_id, description, reason)
approve_change_order(change_id)
consume_authorization(change_id)
cancel_project(project_id)
get_project(id) | get_change(id) | is_authorized(id)
list_changes(start) | get_stats()
```

## Test

```bash
python -m pytest -q
```

The suite covers party binding, single-use included-work authority, bilateral change orders, permanent rejection, replay prevention, wrong-wallet calls, and cancellation invalidation.

## Deploy

Set `GENLAYER_PRIVATE_KEY` in `.env`, then run `python scripts/deploy.py`. The script targets Bradbury, waits for a successful consensus status, and writes `deployment.json`.

ScopeLock does not hold funds or enforce payment. It produces auditable work authorization receipts that other contracts, agents, or off-chain workflows can consume.

## License

MIT
