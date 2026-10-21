// Synthetic website and S3 object storage for the actual workflow import pipeline.
// HTTP image downloads use ordinary GET; S3 PutObject/GetObject uses path-style bucket keys.
const http = require("node:http");
const png = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aS1EAAAAASUVORK5CYII=", "base64");

http.createServer(async (request, response) => {
  const path = new URL(request.url, "http://localhost").pathname;
  const send = (status, type, body) => {
    response.writeHead(status, { "Content-Type": type });
    response.end(body);
  };
  if (request.method === "GET" && path === "/page.html") {
    return send(200, "text/html; charset=utf-8", '<html><body><h1>Chart</h1><p>Imported text</p><img src="chart.png" alt="first"><img src="chart.png" alt="again"></body></html>');
  }
  if (request.method === "GET" && path === "/missing.html") {
    return send(200, "text/html; charset=utf-8", '<html><body><p>Keep this text</p><img src="missing.png" alt="missing"></body></html>');
  }
  if (request.method === "GET" && path === "/chart.png") return send(200, "image/png", png);
  if (request.method === "GET" && path === "/missing.png") return send(404, "text/plain", "Not found");
  return send(501, "text/plain", "Endpoint not modeled");
}).listen(process.env.PORT, "127.0.0.1");
