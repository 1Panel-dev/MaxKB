// Synthetic wire responses for the installed OpenAI and Anthropic SDKs.
// Qwen's empty continuation IDs mirror the compatibility patch in agent.py.
const http = require("node:http");

function json(response, status, body) {
  response.writeHead(status, { "Content-Type": "application/json" });
  response.end(JSON.stringify(body));
}

async function events(response, values, named = false) {
  response.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" });
  for (const value of values) {
    if (named) response.write(`event: ${value.type}\n`);
    response.write(`data: ${JSON.stringify(value)}\n\n`);
    await new Promise(resolve => setImmediate(resolve));
  }
  response.end(named ? "" : "data: [DONE]\n\n");
}

function openai(payload, response) {
  if (payload.model === "fixture-error") {
    return json(response, 429, { error: { message: "Synthetic rate limit", type: "rate_limit_error", code: "rate_limit_exceeded" } });
  }
  const common = { id: "chatcmpl-fixture", created: 1, model: payload.model };
  const replies = payload.messages.filter(message => message.role === "tool");
  const toolRound = ["fixture-tools", "fixture-agent"].includes(payload.model) && replies.length === 0;
  if (toolRound && !payload.tools?.some(tool => tool.function?.name === "lookup")) {
    return json(response, 400, { error: { message: "Expected lookup tool schema" } });
  }
  if (replies.length) {
    const expected = { call_sh: "上海:晴", call_bj: "北京:晴" };
    const calls = payload.messages.flatMap(message => message.tool_calls || []);
    if (replies.length !== 2 || calls.length !== 2 ||
        replies.some(reply => expected[reply.tool_call_id] !== reply.content) ||
        new Set(replies.map(reply => reply.tool_call_id)).size !== 2 ||
        calls.some(call => `${JSON.parse(call.function.arguments).city}:晴` !== expected[call.id])) {
      return json(response, 400, { error: { message: "Tool calls or results were duplicated, lost or corrupted" } });
    }
  }
  const content = replies.length ? "查询完成" : "你好";
  const usage = {
    prompt_tokens: replies.length ? 20 : 12,
    completion_tokens: toolRound ? 6 : replies.length ? 4 : 3,
    total_tokens: toolRound ? 18 : replies.length ? 24 : 15,
    prompt_tokens_details: { cached_tokens: 4 },
    completion_tokens_details: { reasoning_tokens: 1 },
  };
  if (!payload.stream) {
    return json(response, 200, {
      ...common, object: "chat.completion",
      choices: [{ index: 0, message: { role: "assistant", content }, finish_reason: "stop" }], usage,
    });
  }
  if (!payload.stream_options?.include_usage) {
    return json(response, 400, { error: { message: "Expected stream_options.include_usage" } });
  }
  const chunk = (delta, finish_reason = null) => ({
    ...common, object: "chat.completion.chunk", choices: [{ index: 0, delta, finish_reason }],
  });
  const output = [chunk({ role: "assistant", content: "" })];
  if (toolRound) {
    const fragments = [
      [0, "call_sh", "lookup", '{"city":"'], [1, "call_bj", "lookup", '{"city":"'],
      [0, "", null, "上海"], [1, "", null, "北京"],
      [0, "", null, '"}'], [1, "", null, '"}'],
    ];
    for (const [index, id, name, args] of fragments) {
      output.push(chunk({ tool_calls: [{ index, id, type: "function", function: { name, arguments: args } }] }));
    }
  } else {
    if (!replies.length) output.push(chunk({ reasoning_content: "思考", content: "" }));
    for (const character of content) output.push(chunk({ content: character }));
  }
  output.push(chunk({}, toolRound ? "tool_calls" : "stop"));
  output.push({ ...common, object: "chat.completion.chunk", choices: [], usage });
  return events(response, output);
}

function anthropic(payload, response) {
  if (!payload.stream || !payload.tools?.some(tool => tool.name === "lookup")) {
    return json(response, 400, { type: "error", error: { type: "invalid_request_error", message: "Expected streaming lookup tool" } });
  }
  return events(response, [
    { type: "message_start", message: {
      id: "msg_fixture", type: "message", role: "assistant", model: payload.model,
      content: [], stop_reason: null, stop_sequence: null,
      usage: { input_tokens: 10, output_tokens: 0, cache_creation_input_tokens: 2, cache_read_input_tokens: 3 },
    } },
    { type: "content_block_start", index: 0, content_block: { type: "tool_use", id: "toolu_city", name: "lookup", input: {} } },
    { type: "content_block_delta", index: 0, delta: { type: "input_json_delta", partial_json: '{"city":"' } },
    { type: "content_block_delta", index: 0, delta: { type: "input_json_delta", partial_json: '上海"}' } },
    { type: "content_block_stop", index: 0 },
    { type: "message_delta", delta: { stop_reason: "tool_use", stop_sequence: null },
      usage: { input_tokens: 10, output_tokens: 4, cache_creation_input_tokens: 2, cache_read_input_tokens: 3 } },
    { type: "message_stop" },
  ], true);
}

// AWS event-stream frames have a prelude CRC and a CRC covering the whole message.
function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function awsEvent(value) {
  const headers = Buffer.concat(Object.entries({
    ":message-type": "event", ":event-type": "chunk", ":content-type": "application/json",
  }).map(([name, value]) => {
    const prefix = Buffer.from([name.length]);
    const size = Buffer.alloc(3);
    size[0] = 7; // String header value.
    size.writeUInt16BE(Buffer.byteLength(value), 1);
    return Buffer.concat([prefix, Buffer.from(name), size, Buffer.from(value)]);
  }));
  const payload = Buffer.from(JSON.stringify({ bytes: Buffer.from(JSON.stringify(value)).toString("base64") }));
  const prelude = Buffer.alloc(12);
  prelude.writeUInt32BE(16 + headers.length + payload.length, 0);
  prelude.writeUInt32BE(headers.length, 4);
  prelude.writeUInt32BE(crc32(prelude.subarray(0, 8)), 8);
  const message = Buffer.concat([prelude, headers, payload]);
  const checksum = Buffer.alloc(4);
  checksum.writeUInt32BE(crc32(message));
  return Buffer.concat([message, checksum]);
}

async function bedrock(payload, request, response) {
  if (payload.anthropic_version !== "bedrock-2023-05-31" || !payload.max_tokens ||
      !request.headers.authorization?.startsWith("AWS4-HMAC-SHA256 Credential=test-access-key/")) {
    return json(response, 400, { message: "Expected signed Bedrock Claude request" });
  }
  if (payload.system === "fixture-error") {
    response.setHeader("x-amzn-errortype", "ThrottlingException");
    return json(response, 429, { message: "Synthetic Bedrock rate limit" });
  }
  const blocks = payload.messages.flatMap(message => Array.isArray(message.content) ? message.content : []);
  const replies = blocks.filter(block => block.type === "tool_result");
  if (replies.length && (replies.length !== 1 || replies[0].tool_use_id !== "toolu_bedrock" ||
      !JSON.stringify(replies[0].content).includes("上海:晴"))) {
    return json(response, 400, { message: "Invalid Bedrock tool result" });
  }
  if (payload.system === "fixture-vision" && !blocks.some(block =>
      block.type === "image" && block.source?.type === "base64" && block.source?.media_type === "image/png" &&
      Buffer.from(block.source.data, "base64").subarray(1, 4).toString() === "PNG")) {
    return json(response, 400, { message: "Expected unchanged inline PNG" });
  }
  const useTool = Boolean(payload.tools?.length) && !replies.length;
  if (useTool && !payload.tools.some(tool => tool.name === "lookup" && tool.input_schema?.properties?.city)) {
    return json(response, 400, { message: "Expected Bedrock lookup schema" });
  }
  const content = replies.length ? "查询完成" : "你好";
  const usage = { input_tokens: 10, output_tokens: 4, cache_read_input_tokens: 3, cache_creation_input_tokens: 2 };
  if (request.url.endsWith("/invoke")) {
    response.setHeader("x-amzn-bedrock-input-token-count", "10");
    response.setHeader("x-amzn-bedrock-output-token-count", "4");
    response.setHeader("x-amzn-bedrock-cache-read-input-token-count", "3");
    response.setHeader("x-amzn-bedrock-cache-write-input-token-count", "2");
    return json(response, 200, {
      id: "msg_bedrock", type: "message", role: "assistant",
      content: useTool ? [{ type: "tool_use", id: "toolu_bedrock", name: "lookup", input: { city: "上海" } }] :
        [{ type: "text", text: content }],
      stop_reason: useTool ? "tool_use" : "end_turn", stop_sequence: null, usage,
    });
  }
  const output = [{ type: "message_start", message: {
    id: "msg_bedrock", type: "message", role: "assistant", content: [], usage,
  } }];
  output.push({ type: "content_block_start", index: 0, content_block: useTool ?
    { type: "tool_use", id: "toolu_bedrock", name: "lookup", input: {} } : { type: "text", text: "" } });
  for (const value of useTool ? ['{"city":"', '上海"}'] : [...content]) {
    output.push({ type: "content_block_delta", index: 0, delta: useTool ?
      { type: "input_json_delta", partial_json: value } : { type: "text_delta", text: value } });
  }
  output.push({ type: "content_block_stop", index: 0 });
  output.push({ type: "message_delta", delta: { stop_reason: useTool ? "tool_use" : "end_turn" }, usage });
  output.push({ type: "message_stop", "amazon-bedrock-invocationMetrics": {
    inputTokenCount: 10, outputTokenCount: 4, cacheReadInputTokenCount: 3, cacheWriteInputTokenCount: 2,
  } });
  response.writeHead(200, {
    "Content-Type": "application/vnd.amazon.eventstream", "x-amzn-bedrock-content-type": "application/json",
  });
  for (const value of output) {
    response.write(awsEvent(value));
    await new Promise(resolve => setImmediate(resolve));
  }
  response.end();
}

http.createServer(async (request, response) => {
  try {
    const isBedrock = /^\/model\/[^/]+\/invoke(?:-with-response-stream)?$/.test(request.url);
    if (request.method !== "POST" || (!isBedrock && !["/v1/chat/completions", "/v1/messages"].includes(request.url))) {
      return json(response, 501, { error: { message: "Endpoint not modeled" } });
    }
    const isAnthropic = request.url === "/v1/messages";
    if (!isBedrock && (isAnthropic ? request.headers["x-api-key"] : request.headers.authorization) !==
        (isAnthropic ? "test-key" : "Bearer test-key")) {
      return json(response, 401, { error: { message: "Expected synthetic test credentials" } });
    }
    let payload = request.body;
    if (!payload) {
      let raw = "";
      for await (const chunk of request) raw += chunk;
      payload = JSON.parse(raw);
    }
    if (typeof payload === "string") payload = JSON.parse(payload);
    if (!Array.isArray(payload.messages) || !payload.messages.length) {
      return json(response, 400, { error: { message: "Expected messages" } });
    }
    if (isBedrock) await bedrock(payload, request, response);
    else await (isAnthropic ? anthropic(payload, response) : openai(payload, response));
  } catch {
    if (!response.headersSent) json(response, 400, { error: { message: "Invalid fixture request" } });
    else response.end();
  }
}).listen(process.env.PORT, "127.0.0.1");
