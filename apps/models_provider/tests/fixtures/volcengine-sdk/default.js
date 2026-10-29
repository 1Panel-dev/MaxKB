// Request/response shapes: official volcenginesdkarkruntime resources and types.
// Synthetic outputs validate transport and parsing, not generated media or model quality.
const http = require("node:http");
http.createServer(async (req, res) => {
  const send = (status, body) => {
    res.writeHead(status, { "Content-Type": "application/json" });
    res.end(JSON.stringify(body));
  };
  const body = req.body || {};
  if (req.headers.authorization !== "Bearer fixture-key") {
    return send(401, { error: { code: "AuthenticationError", message: "Synthetic invalid API key" } });
  }
  if (req.method === "POST" && req.url === "/api/v3/embeddings") {
    if (body.model?.startsWith("fixture-error-")) {
      const status = Number(body.model.split("-").at(-1));
      return send(status, { error: { code: "FixtureError", message: "Synthetic SDK failure" } });
    }
    if (!Array.isArray(body.input) || body.dimensions !== 2) return send(400, { error: { message: "Invalid embedding request" } });
    return send(200, { object: "list", model: body.model,
      data: body.input.map((text, index) => ({ object: "embedding", index, embedding: [text.length, index] })),
      usage: { prompt_tokens: body.input.length, total_tokens: body.input.length } });
  }
  if (req.method === "POST" && req.url === "/api/v3/images/generations") {
    if (body.prompt !== "测试图片" || body.size !== "1024x1024" || body.watermark !== false) {
      return send(400, { error: { message: "Invalid image parameters" } });
    }
    return send(200, { model: body.model, created: 1,
      data: body.response_format === "b64_json" ? [{ b64_json: "aW1hZ2U=" }] : [{ url: "https://fixture.invalid/image.png" }],
      usage: { generated_images: 1 } });
  }
  const tasks = await pm.state.get("volcengine.tasks") || {};
  if (req.method === "POST" && req.url === "/api/v3/contents/generations/tasks") {
    if (body.content?.[0]?.text !== "测试视频" || body.content?.[1]?.role !== "first_frame" ||
        body.content?.[1]?.image_url?.url !== "https://fixture.invalid/first.png" ||
        body.duration !== 5 || body.seed !== 42 || body.camera_fixed !== true) {
      return send(400, { error: { message: "Invalid video parameters" } });
    }
    const id = "fixture-" + require("node:crypto").randomUUID();
    tasks[id] = { model: body.model, reads: 0 };
    await pm.state.set("volcengine.tasks", tasks);
    return send(200, { id });
  }
  const match = req.url.match(/^\/api\/v3\/contents\/generations\/tasks\/([^/?]+)$/);
  if (match && ["GET", "DELETE"].includes(req.method)) {
    const id = match[1], task = tasks[id];
    if (!task) return send(404, { error: { code: "NotFound", message: "Unknown task" } });
    if (req.method === "DELETE") {
      if (task.reads < 2) return send(409, { error: { message: "Task is not finished" } });
      delete tasks[id];
      await pm.state.set("volcengine.tasks", tasks);
      return send(200, {});
    }
    task.reads += 1;
    await pm.state.set("volcengine.tasks", tasks);
    return send(200, { id, model: task.model, status: task.reads < 2 ? "running" : "succeeded",
      content: task.reads < 2 ? null : { video_url: `https://fixture.invalid/${id}.mp4` },
      usage: { completion_tokens: 1, total_tokens: 1 }, created_at: 1, updated_at: 2 });
  }
  send(501, { error: { message: "Endpoint not modeled" } });
}).listen(process.env.PORT, "127.0.0.1");
