// Contracts:
// https://intl.cloud.tencent.com/document/product/1300/81297
// https://docs.volcengine.com/docs/ark/multimodal-vectorization-api?lang=zh
// Synthetic vectors report PNG dimensions to verify transport, not model inference.
const http = require("node:http");

http.createServer(async (request, response) => {
  const send = (status, body) => {
    response.writeHead(status, { "Content-Type": "application/json" });
    response.end(JSON.stringify(body));
  };
  const tencent = request.url === "/v1/embeddings/multimodal";
  if (request.method !== "POST" || (!tencent && request.url !== "/api/v3/embeddings/multimodal")) {
    return send(501, { error: { message: "Endpoint not modeled" } });
  }
  if (request.headers.authorization !== "Bearer test-key") {
    return send(401, { error: { message: "Invalid token" } });
  }
  try {
    let body = "";
    for await (const chunk of request) body += chunk;
    const payload = JSON.parse(body);
    const expectedModel = tencent ? "kinfra-vl-embedding-2b" : "doubao-embedding-vision-251215";
    if (payload.model !== expectedModel || payload.encoding_format !== "float" || payload.input?.length !== 1) {
      return send(400, { error: { message: "Invalid model, encoding or input" } });
    }
    const item = payload.input[0];
    let embedding;
    if (item.type === "text" && typeof item.text === "string") {
      embedding = item.text === "second" ? [0.75, 0.25] : [0.25, 0.75];
    } else if (item.type === "image_url" && typeof item.image_url?.url === "string") {
      const image = item.image_url.url;
      if (image.startsWith("https://")) {
        embedding = [1, 0];
      } else {
        if (tencent ? image.startsWith("data:") : !image.startsWith("data:image/png;base64,")) {
          return send(400, { error: { message: "Unexpected provider image encoding" } });
        }
        const png = Buffer.from(tencent ? image : image.split(",", 2)[1], "base64");
        if (png.length < 24 || png.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") {
          return send(400, { error: { message: "Expected rendered PNG" } });
        }
        const width = png.readUInt32BE(16), height = png.readUInt32BE(20);
        if (tencent && (width * height < 4096 || width * height > 1843200)) {
          return send(400, { error: { message: "Image area is outside TokenHub limits" } });
        }
        embedding = [width, height];
      }
    }
    if (!embedding) return send(400, { error: { message: "Unsupported input" } });
    const data = { object: "embedding", embedding };
    send(200, {
      id: "test-request", created: 1, object: "list", model: payload.model,
      data: tencent ? [{ ...data, index: 0 }] : data,
      usage: { prompt_tokens: 1, total_tokens: 1 },
    });
  } catch {
    send(400, { error: { message: "Invalid request body" } });
  }
}).listen(process.env.PORT, "127.0.0.1");
