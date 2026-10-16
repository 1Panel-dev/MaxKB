// Contract: https://api-docs.siliconflow.cn/docs/api/embeddings-post
// Stateless protocol fixture; vectors are test values, not model inference results.
const http = require("node:http");

http.createServer(async (request, response) => {
  const send = (status, body) => {
    response.writeHead(status, { "Content-Type": "application/json" });
    response.end(JSON.stringify(body));
  };
  if (request.method !== "POST" || request.url !== "/v1/embeddings") {
    return send(501, { message: "Endpoint not modeled" });
  }
  if (request.headers.authorization !== "Bearer test-key") {
    return send(401, "Invalid token");
  }
  try {
    let body = "";
    for await (const chunk of request) body += chunk;
    const payload = JSON.parse(body);
    if (payload.model !== "Qwen/Qwen3-VL-Embedding-8B" || payload.dimensions !== 2) {
      return send(400, { code: 20012, message: "Invalid model or dimensions", data: null });
    }
    let embedding;
    if (typeof payload.input === "string" && payload.input.length) {
      embedding = payload.input === "second text" ? [0.75, 0.25] : [0.25, 0.75];
    } else if (typeof payload.input?.image === "string") {
      if (payload.input.image.startsWith("https://")) embedding = [1.0, 0.0];
      else if (payload.input.image.startsWith("data:image/")) embedding = [0.0, 1.0];
    }
    if (!embedding) {
      return send(400, { code: 20012, message: "Expected text or an image content object", data: null });
    }
    send(200, {
      object: "list",
      model: payload.model,
      data: [{ object: "embedding", index: 0, embedding }],
      usage: { prompt_tokens: 1, total_tokens: 1 },
    });
  } catch {
    send(400, { code: 20012, message: "Invalid request body", data: null });
  }
}).listen(process.env.PORT, "127.0.0.1");
