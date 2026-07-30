// Contract: https://milvus.io/api-reference/restful/v2.6.x/v2/Collection%20(v2)/Create.md
// JSON field names: https://github.com/milvus-io/milvus/blob/v2.6.0/internal/distributed/proxy/httpserver/request_v2.go
// Synthetic state and failure controls exercise the real Python HTTP client, not vector search quality.
const http = require("node:http");
const prefix = "/v2/vectordb/";

http.createServer(async (request, response) => {
  const path = new URL(request.url, "http://localhost").pathname;
  const send = (status, body, raw = false) => {
    response.writeHead(status, { "Content-Type": raw ? "text/html" : "application/json" });
    response.end(raw ? body : JSON.stringify(body));
  };
  try {
    if (path === "/__test/reset" && request.method === "POST") {
      await pm.state.set("milvus:state", { collections: {}, calls: [], failure: null, ...request.body });
      return send(200, { code: 0 });
    }
    const state = await pm.state.get("milvus:state");
    if (path === "/__test/state" && request.method === "GET") return send(200, state);
    if (request.method !== "POST" || !path.startsWith(prefix)) return send(501, { message: "Endpoint not modeled" });
    if (request.headers.authorization !== "Bearer regression-token") return send(401, { code: 1800, message: "Unauthorized" });
    const body = request.body;
    const operation = path.slice(prefix.length);
    state.calls.push({ operation, body });
    await pm.state.set("milvus:state", state);
    const failure = state.failure;
    if (failure?.operation === operation && state.calls.filter(call => call.operation === operation).length === (failure.at || 1)) {
      if (failure.disconnect) return request.socket.destroy();
      return send(failure.status || 200, failure.body, failure.raw);
    }
    const collection = state.collections[body.collectionName];
    const fail = message => send(200, { code: 1100, message });
    if (operation === "collections/has") return send(200, { code: 0, data: { has: !!collection } });
    if (operation === "collections/create") {
      const schema = body.schema;
      if (!schema || schema.autoID !== false || schema.enableDynamicField !== false) return fail("Invalid collection schema");
      const fields = schema.fields || [];
      const primary = fields.find(field => field.isPrimary);
      const vector = fields.find(field => field.dataType === "FloatVector");
      if (primary?.fieldName !== "id" || primary.dataType !== "VarChar") return fail("Expected VarChar primary key");
      if (!vector || !Number.isInteger(Number(vector.elementTypeParams?.dim)) || Number(vector.elementTypeParams.dim) <= 0) {
        return fail("FloatVector requires elementTypeParams.dim");
      }
      for (const field of fields) {
        if ("dim" in field || "maxLength" in field) return fail("Field parameters must be nested in elementTypeParams");
        if (field.dataType === "VarChar" && !(Number(field.elementTypeParams?.max_length) > 0)) {
          return fail("VarChar requires elementTypeParams.max_length");
        }
      }
      if (collection) return fail("Collection already exists");
      state.collections[body.collectionName] = { schema, dim: Number(vector.elementTypeParams.dim), loaded: false, records: {} };
    } else if (operation === "collections/load") {
      if (!collection) return fail("Collection not found");
      collection.loaded = true;
    } else if (operation === "entities/upsert") {
      if (!collection) return fail("Collection not found");
      if (!Array.isArray(body.data) || !body.data.length) return fail("Missing entities");
      for (const record of body.data) {
        if (typeof record.id !== "string" || record.embedding?.length !== collection.dim) return fail("Entity schema mismatch");
        collection.records[record.id] = record;
      }
      await pm.state.set("milvus:state", state);
      return send(200, { code: 0, data: { upsertCount: body.data.length, upsertIds: body.data.map(record => record.id) } });
    } else if (operation === "collections/drop") {
      delete state.collections[body.collectionName];
    } else {
      return send(501, { message: "Endpoint not modeled" });
    }
    await pm.state.set("milvus:state", state);
    return send(200, { code: 0, data: {} });
  } catch (error) {
    return send(500, { code: 65535, message: error.message });
  }
}).listen(process.env.PORT, "127.0.0.1");
