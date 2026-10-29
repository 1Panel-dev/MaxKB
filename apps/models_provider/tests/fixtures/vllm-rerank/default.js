// Cohere-compatible vLLM wire contract; scores are synthetic, not model inference.
const http = require("node:http");
const key = "vllm-rerank:state";
const json = (res, status, value) => {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(value));
};

async function body(req) {
  if (req.body !== undefined) return typeof req.body === "string" ? JSON.parse(req.body) : req.body;
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return chunks.length ? JSON.parse(Buffer.concat(chunks)) : {};
}

http.createServer(async (req, res) => {
  try {
    const input = body(req);
    const path = new URL(req.url, "http://localhost").pathname;
    if (req.method === "POST" && path === "/_test/reset") {
      await pm.state.set(key, { options: await input, calls: [] });
      return json(res, 200, { ok: true });
    }
    const state = await pm.state.get(key) || { options: {}, calls: [] };
    if (req.method === "GET" && path === "/_test/state") return json(res, 200, state);
    if (req.method !== "POST" || !["/v2/rerank", "/v1/rerank"].includes(path)) {
      return json(res, 501, { message: "Endpoint not modeled" });
    }
    const payload = await input;
    state.calls.push({ path, body: payload });
    await pm.state.set(key, state);
    if (req.headers.authorization !== "Bearer test-key") return json(res, 401, { message: "Invalid test key" });
    if (!payload.model || typeof payload.query !== "string" || !Array.isArray(payload.documents) ||
        payload.documents.some(value => typeof value !== "string") || !Number.isInteger(payload.top_n)) {
      return json(res, 400, { message: "Invalid rerank request" });
    }
    const status = state.options[path.startsWith("/v2") ? "v2_status" : "v1_status"] || 200;
    if (status !== 200) return json(res, status, { message: "Synthetic rerank error" });
    return json(res, 200, {
      id: "fixture-rerank", results: state.options.results ?? [
        { index: 2, relevance_score: 0.9 }, { index: 0, relevance_score: 0.4 },
      ], meta: { api_version: { version: path.includes("v2") ? "2" : "1" } },
    });
  } catch (error) {
    return json(res, 500, { message: String(error) });
  }
}).listen(process.env.PORT, "127.0.0.1");
