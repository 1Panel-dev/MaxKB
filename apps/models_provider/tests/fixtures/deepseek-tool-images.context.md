# DeepSeek tool image simulation

Created 2026-10-28 from the v2 tool-image adaptation and the installed OpenAI SDK's
chat completion message format. The local handler is `deepseek-tool-images.js`.

## Purpose

Verify that DeepSeekChatModel sends tool images as user vision blocks while retaining
textual tool responses, parallel-call ordering and reasoning metadata. Responses echo
the received structure; they do not perform inference.

## Execution

Run the simulation and tests using `../README.md`. `--output ndjson` prints the bound
address and request events; when using `--port auto`, set the test URL from that address.
Stop this simulation with Ctrl-C or `pkill -INT -f 'simulation run .*deepseek-tool-images.sim.yaml'`.

## Assumptions

- 2026-10-28: The target gateway must support image_url blocks on user messages.
  This fixture does not establish vision support for any real DeepSeek model.
- 2026-10-28: Postman CLI 1.74.0 is signed out; owner-mock discovery returned
  "No authorization data found". The fixture follows local code rather than a published mock.
- 2026-10-28: The integration-checkout run redirected `maxkb.const.LOG_DIR` to a
  temporary directory and disabled the unrelated Redis message-bus subscriber during
  Django startup. These SimpleTestCase tests require no database or Redis service.

## Observations

<!-- begin:observations -->
2026-10-28: All 31 targeted tests passed. The sole `deepseek` member received both
synchronous and asynchronous streaming requests and returned 200. Request logs showed
both tool responses before the user image blocks, with reasoning metadata preserved.
<!-- end:observations -->

## What didn't work

- 2026-10-28: The restricted sandbox rejected the server with `listen EPERM` on
  loopback. The local simulation and HTTP regression ran with permission to bind/connect.
