/** 知识库外部检索示例使用浏览器访问地址，避免反向代理内网协议进入复制结果。 */
import type { Dict, KnowledgeExternalRetrievalSetting } from '@/api/types'

function serviceUrl(url: string, origin: string): string {
  const endpoint = new URL(url, origin)
  return `${new URL(origin).origin}${endpoint.pathname}${endpoint.search}${endpoint.hash}`
}

/** 格式化服务端 MCP 配置，仅将服务地址的协议、域名和端口对齐当前访问入口。 */
export function formatKnowledgeMcpConfig(config: Dict<unknown>, origin: string): string {
  return JSON.stringify(
    Object.fromEntries(
      Object.entries(config).map(([name, connection]) => [
        name,
        typeof connection === 'object' && connection !== null && 'url' in connection && typeof connection.url === 'string'
          ? { ...connection, url: serviceUrl(connection.url, origin) }
          : connection,
      ]),
    ),
    null,
    2,
  )
}

/** 保留服务端生成的 curl 参数与请求体，仅修正检索端点的公开访问地址。 */
export function formatKnowledgeApiExample(setting: Pick<KnowledgeExternalRetrievalSetting, 'api_url' | 'api_example'>, origin: string): string {
  return setting.api_example.replace(setting.api_url, serviceUrl(setting.api_url, origin))
}
