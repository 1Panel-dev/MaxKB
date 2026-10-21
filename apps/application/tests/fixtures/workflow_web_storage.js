// Minimal path-style S3 PutObject/GetObject fixture; stored bytes are synthetic test data.
const http = require("node:http");
const crypto = require("node:crypto");
http.createServer(async (request, response) => {
  const path = new URL(request.url, "http://localhost").pathname;
  const send = (status, type, body) => {
    response.writeHead(status, { "Content-Type": type });
    response.end(body);
  };
  if (path.startsWith("/bucket/")) {
    const key = "workflow-web-images:" + path;
    if (request.method === "PUT") {
      const chunks = [];
      for await (const chunk of request) chunks.push(chunk);
      const data = Buffer.concat(chunks);
      await pm.state.set(key, data.toString("base64"));
      response.writeHead(200, { ETag: '"' + crypto.createHash("md5").update(data).digest("hex") + '"' });
      return response.end();
    }
    if (request.method === "GET") {
      const data = await pm.state.get(key);
      if (data !== undefined && data !== null) return send(200, "application/octet-stream", Buffer.from(data, "base64"));
      return send(404, "application/xml", "<Error><Code>NoSuchKey</Code></Error>");
    }
    if (request.method === "DELETE") {
      await pm.state.set(key, null);
      response.writeHead(204);
      return response.end();
    }
  }
  return send(501, "text/plain", "Endpoint not modeled");
}).listen(process.env.PORT, "127.0.0.1");
