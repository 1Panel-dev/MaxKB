import assert from 'node:assert/strict'
import { test } from 'node:test'
import { formatKnowledgeApiExample, formatKnowledgeMcpConfig } from '../src/views/knowledge/external-retrieval-config.ts'

const connection = {
  url: 'http://internal:8080/custom/chat/api/v3/knowledge/example/mcp?source=copy',
  transport: 'streamable_http',
  headers: { Authorization: 'Bearer <CHAT_USER_API_KEY>' },
  timeout: 30,
}

for (const origin of ['https://public.example', 'https://public.example:8443', 'http://127.0.0.1:3000']) {
  test(`MCP 配置使用访问入口 ${origin}，保留部署路径和连接参数`, () => {
    const original = { knowledge_example: { ...connection } }
    const formatted = JSON.parse(formatKnowledgeMcpConfig(original, origin))
    assert.deepEqual(formatted.knowledge_example, {
      ...connection,
      url: `${origin}/custom/chat/api/v3/knowledge/example/mcp?source=copy`,
    })
    assert.equal(original.knowledge_example.url, connection.url)
  })
}

test('相对 MCP 地址与多个服务均按当前浏览器入口解析', () => {
  const config = { first: connection, second: { ...connection, url: '/chat/api/v3/knowledge/second/mcp' } }
  const result = JSON.parse(formatKnowledgeMcpConfig(config, 'https://public.example'))
  assert.equal(result.second.url, 'https://public.example/chat/api/v3/knowledge/second/mcp')
  assert.equal(Object.keys(result).length, 2)
})

test('API 示例只替换端点，保留鉴权头、请求体和换行', () => {
  const api_url = 'http://internal:8080/custom/chat/api/v3/knowledge/example/retrieve'
  const suffix = ' \\\n  -H \'Authorization: Bearer <CHAT_USER_API_KEY>\' \\\n  -d \'{"query_text":"如何使用知识库？","top_number":5}\''
  const api_example = `curl -X POST ${api_url}${suffix}`
  assert.equal(
    formatKnowledgeApiExample({ api_url, api_example }, 'https://public.example'),
    `curl -X POST https://public.example/custom/chat/api/v3/knowledge/example/retrieve${suffix}`,
  )
})
