# Aliyun image embedding simulation

## Purpose and execution

`aliyun.sim.yaml` reuses the existing `aliyun.js` protocol fixture. Commands and
the `ALIYUN_EMBEDDING_TEST_URL` variable are documented in `../README.md`.
Use `--output ndjson` to inspect request batch sizes; stop the server with Ctrl-C.

## Assumptions

- 2026-10-26: The fixture follows the official API linked in its header, including
  Qwen3's ten-image limit. Synthetic vectors encode image dimensions for ordering
  assertions; passing tests do not establish real-model inference quality or quotas.
- 2026-10-26: Reused the repository fixture because Postman CLI is signed out;
  no published owner mock was available. Tests use the real DashScope SDK.
- 2026-10-26: In this integration checkout, the local runner disabled file logging
  under `/opt/maxkb/logs` and unrelated URL checks. No database is needed.

## Observations

<!-- begin:observations -->
2026-10-26 (single-image calls): All 27 targeted tests passed after switching
every Aliyun multimodal model to sequential single-image requests. All image
traffic to `aliyun` contained exactly one image; the text request still contained
two texts. Image dimensions confirmed result order across requests.

2026-10-26: The `aliyun` member received all regression traffic. Before the fix,
11/15/20/21-image requests returned 400. After batching, all 27 targeted tests
passed; successful image requests contained at most ten items and preserved
image order across batches. Text requests and the expected thin-image rejection
were also exercised. There were no other members.
<!-- end:observations -->
