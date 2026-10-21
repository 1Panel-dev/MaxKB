// Contract: https://help.aliyun.com/zh/model-studio/multimodal-embedding-api-reference
// Processor limits: https://github.com/QwenLM/Qwen3-VL/blob/main/qwen-vl-utils/src/qwen_vl_utils/vision_process.py
// Synthetic PNG inputs and fixed vectors validate transport and dimensions, not model inference.
const http = require("node:http");

http.createServer(async (request, response) => {
  const send = (status, body) => {
    response.writeHead(status, { "Content-Type": "application/json" });
    response.end(JSON.stringify(body));
  };
  const fail = (message) => send(400, {
    request_id: "test-request", code: "InvalidParameter", message,
  });
  if (request.method !== "POST" || request.url !== "/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding") {
    return send(501, { message: "Endpoint not modeled" });
  }
  if (request.headers.authorization !== "Bearer test-key") {
    return send(401, { code: "InvalidApiKey", message: "Invalid token" });
  }
  try {
    let body = "";
    for await (const chunk of request) body += chunk;
    const payload = JSON.parse(body);
    const items = payload.input?.contents;
    if (payload.model !== "qwen3-vl-embedding" || payload.parameters?.dimension !== 256 || !Array.isArray(items)) {
      return fail("Expected Qwen3 model, contents and dimension");
    }
    if (!items.length || items.length > 20 || items.filter((item) => item.image).length > 10) {
      return fail("Input batch exceeds model limits");
    }
    for (const item of items) {
      if (typeof item.text === "string" && item.text) continue;
      if (!item.image?.startsWith("data:image/png;base64,")) return fail("Fixture expects a PNG data URL");
      const png = Buffer.from(item.image.split(",", 2)[1], "base64");
      if (png.length < 24 || png.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") {
        return fail("Invalid PNG");
      }
      const width = png.readUInt32BE(16), height = png.readUInt32BE(20);
      if (!width || !height || Math.max(width, height) / Math.min(width, height) > 200) {
        return fail("<400> InternalError.Algo.InvalidParameter: The input of vl is not valid, processor error.");
      }
    }
    send(200, {
      request_id: "test-request",
      output: { embeddings: items.map((item, index) => ({
        index, type: item.image ? "image" : "text", embedding: [index, ...Array(255).fill(0)],
      })) },
      usage: { input_tokens: items.length, image_tokens: 0 },
    });
  } catch {
    fail("Invalid request body");
  }
}).listen(process.env.PORT, "127.0.0.1");
