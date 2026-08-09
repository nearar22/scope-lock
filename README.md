# ScopeLock

ScopeLock is a reusable semantic change-control primitive for GenLayer. A client and contractor sign one immutable project baseline. Every later work request is judged against that baseline and becomes either immediately authorized included work, a bilateral change order, or a rejected out-of-scope request.

**Bradbury deployment:** [`0x2247...7796`](https://explorer-bradbury.genlayer.com/address/0x2247105dcE242fDE249e0b994245440ab57C7796) · [deployment transaction](https://explorer-bradbury.genlayer.com/tx/0xee0d08958c46ea1f9dbd9b902371a3256a4c2dacac049b38891688ab08ece513)

**Verified live lifecycle:** [create project](https://explorer-bradbury.genlayer.com/tx/0x2a53eb8025114caa9fa74d360629ff1323d2c39df9a0137b747ad6158bd28b01) · [contractor acceptance](https://explorer-bradbury.genlayer.com/tx/0xfe06c37d8f29154bce7ea11127b0c0922df5cc27f78ede62f04811605d91c201) · [consensus change order](https://explorer-bradbury.genlayer.com/tx/0x4273c0ae144c6b6197d1a591c016a6379a329230304ea7070120ca5b3769e994) · [client approval](https://explorer-bradbury.genlayer.com/tx/0x8161e28dc6fd39dded2ee7ee2a91643bc812eda258c9462e004a560b7b9bdb96) · [contractor approval](https://explorer-bradbury.genlayer.com/tx/0x9f86d287f2d19a78bd75ca25faf4bd6699d7b3771aec536a77bdefff0479c683) · [single-use consumption](https://explorer-bradbury.genlayer.com/tx/0x3cc826c3a101e05b0211bfb22ee264e782fdec8fe321d53976d885a91144fd33)

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

Set `GENLAYER_PRIVATE_KEY` in the shared `.env`, then run `python scripts/deploy.py`. For the two-party live verification, also set a separately funded `GENLAYER_SECONDARY_PRIVATE_KEY`, then run `python scripts/verify_live.py`. The scripts target Bradbury.

ScopeLock does not hold funds or enforce payment. It produces auditable work authorization receipts that other contracts, agents, or off-chain workflows can consume.

## License

MIT
