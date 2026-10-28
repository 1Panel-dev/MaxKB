// Local vision-gateway contract used by DeepSeekChatModel and the OpenAI SDK.
// Models chat completions only; echoes request structure, not visual inference.
const http = require("node:http");

http.createServer(async (request, response) => {
  const send = (status, body) => {
    response.writeHead(status, { "Content-Type": "application/json" });
    response.end(JSON.stringify(body));
  };
  if (request.method !== "POST" || request.url !== "/v1/chat/completions") {
    return send(501, { error: { message: "Endpoint not modeled" } });
  }
  if (request.headers.authorization !== "Bearer test-key") {
    return send(401, { error: { message: "Invalid token" } });
  }
  try {
    let raw = "";
    for await (const chunk of request) raw += chunk;
    const payload = JSON.parse(raw);
    const pending = new Set();
    const received = { roles: [], tool_call_ids: [], images: [], reasoning: [] };
    for (const message of payload.messages) {
      received.roles.push(message.role);
      if (pending.size && message.role !== "tool") {
        return send(400, { error: { message: "Missing parallel tool responses before the next message" } });
      }
      if (message.role === "assistant" && message.tool_calls?.length) {
        if (typeof message.reasoning_content !== "string") {
          return send(400, { error: { message: "Missing tool-call reasoning_content" } });
        }
        received.reasoning.push(message.reasoning_content);
        for (const call of message.tool_calls) pending.add(call.id);
      }
      if (message.role === "tool") {
        if (!pending.delete(message.tool_call_id) || typeof message.content !== "string") {
          return send(400, { error: { message: "Invalid textual tool response" } });
        }
        if (message.content.includes('"image_url"')) {
          return send(400, { error: { message: "Tool images were encoded as ordinary text" } });
        }
        received.tool_call_ids.push(message.tool_call_id);
      }
      if (message.role === "user" && Array.isArray(message.content)) {
        for (const block of message.content) {
          if (block.type === "image_url") received.images.push(block.image_url.url);
        }
      }
    }
    if (pending.size) return send(400, { error: { message: "Missing tool responses" } });
    const content = JSON.stringify(received);
    const common = { id: "test-completion", created: 1, model: payload.model };
    if (payload.stream) {
      response.writeHead(200, { "Content-Type": "text/event-stream" });
      response.write(`data: ${JSON.stringify({ ...common, object: "chat.completion.chunk", choices: [{ index: 0, delta: { role: "assistant", content }, finish_reason: null }] })}\n\n`);
      response.write(`data: ${JSON.stringify({ ...common, object: "chat.completion.chunk", choices: [{ index: 0, delta: {}, finish_reason: "stop" }] })}\n\n`);
      response.end("data: [DONE]\n\n");
    } else {
      send(200, {
        ...common, object: "chat.completion",
        choices: [{ index: 0, message: { role: "assistant", content }, finish_reason: "stop" }],
        usage: { prompt_tokens: 1, completion_tokens: 1, total_tokens: 2 },
      });
    }
  } catch {
    send(400, { error: { message: "Invalid request body" } });
  }
}).listen(process.env.PORT, "127.0.0.1");
