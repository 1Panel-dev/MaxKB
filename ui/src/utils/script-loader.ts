/** 加载登录提供商的外部 SDK，并避免重复插入相同脚本。 */

/** 加载指定外部脚本。 */
export function loadLoginScript(source: string, id: string) {
  return new Promise<void>((resolve, reject) => {
    const existing = document.getElementById(id) as HTMLScriptElement | null
    if (existing?.dataset.loaded === 'true') {
      resolve()
      return
    }
    existing?.remove()
    const script = document.createElement('script')
    script.id = id
    script.src = source
    script.onload = () => {
      script.dataset.loaded = 'true'
      resolve()
    }
    script.onerror = () => reject(new Error(`登录 SDK 加载失败：${source}`))
    document.head.appendChild(script)
  })
}
