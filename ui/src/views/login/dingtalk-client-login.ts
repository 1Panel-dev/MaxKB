/** 提供 Admin 与 Chat 登录页使用的钉钉客户端免登授权码。 */

import type { LocationQuery } from 'vue-router'
import { MsgError } from '@/utils/message'

/** 仅在钉钉客户端入口请求授权；失败后保留普通登录入口，API 登录由各入口自行处理。 */
export async function getDingTalkClientAuthCode(query: LocationQuery): Promise<string | undefined> {
  const { client, corpId } = query
  if (client !== 'dingtalk' || typeof corpId !== 'string' || !corpId.trim()) return

  try {
    const { default: dd } = await import('dingtalk-jsapi')
    if (dd.env.platform === 'notInDingTalk') return
    const { code } = await dd.runtime.permission.requestAuthCode({ corpId })
    if (!code) throw new Error('钉钉未返回授权码')
    return code
  } catch {
    MsgError('钉钉免密授权失败，请使用其他方式登录')
  }
}
