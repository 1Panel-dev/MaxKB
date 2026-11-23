/** 提供 Admin 与 Chat 登录页使用的飞书客户端免登授权码。 */
import type { LocationQuery } from 'vue-router'
import { MsgError } from '@/utils/message'
import { loadLoginScript } from '@/utils/script-loader'

interface LarkAuthResult {
  code: string
}

interface LarkAuthError {
  errno?: number
}

interface LarkClientSdk {
  requestAccess?: (options: {
    appID: string
    scopeList: string[]
    success: (result: LarkAuthResult) => void
    fail: (error: LarkAuthError) => void
  }) => void
  requestAuthCode?: (options: { appId: string; success: (result: LarkAuthResult) => void; fail: (error: LarkAuthError) => void }) => void
}

/** 仅在飞书客户端入口请求授权；兼容旧客户端，失败后保留普通登录入口。 */
export async function getLarkClientAuthCode(
  query: LocationQuery,
  messages: { missingCode: string; authorizationFailed: string },
): Promise<string | undefined> {
  const { client, appId } = query
  if (client !== 'lark' || typeof appId !== 'string' || !appId.trim()) return

  let authTimeout: ReturnType<typeof setTimeout> | undefined
  try {
    await loadLoginScript('https://lf-scm-cn.feishucdn.com/lark/op/h5-js-sdk-1.5.44.js', 'lark-client-sdk')
    const sdk = (window as Window & { tt?: LarkClientSdk }).tt
    if (!sdk) throw new Error(messages.authorizationFailed)

    const { code } = await new Promise<LarkAuthResult>((resolve, reject) => {
      authTimeout = setTimeout(() => reject(new Error(messages.authorizationFailed)), 30_000)
      const requestAuthCode = () => {
        if (!sdk.requestAuthCode) {
          reject(new Error(messages.authorizationFailed))
          return
        }
        sdk.requestAuthCode({ appId, success: resolve, fail: reject })
      }
      if (!sdk.requestAccess) {
        requestAuthCode()
        return
      }
      sdk.requestAccess({
        appID: appId,
        scopeList: [],
        success: resolve,
        fail: (error) => {
          if (error.errno === 103) requestAuthCode()
          else reject(error)
        },
      })
    })
    if (!code) throw new Error(messages.missingCode)
    return code
  } catch {
    MsgError(messages.authorizationFailed)
  } finally {
    if (authTimeout !== undefined) clearTimeout(authTimeout)
  }
}
