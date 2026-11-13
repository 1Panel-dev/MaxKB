/** 沙箱内容通过已有 snapshot 协议序列化，随后在禁用脚本的临时 iframe 中截图。 */
function requestSnapshot(iframe: HTMLIFrameElement): Promise<string> {
  return new Promise((resolve, reject) => {
    const target = iframe.contentWindow
    if (!target) return reject(new Error('内容尚未加载'))
    const requestId = crypto.randomUUID()
    const timer = window.setTimeout(() => finish(), 5000)
    function finish(html?: string) {
      clearTimeout(timer)
      window.removeEventListener('message', onMessage)
      if (html) resolve(html)
      else reject(new Error('内容快照失败'))
    }
    function onMessage(event: MessageEvent) {
      if (event.source === target && event.data?.type === 'snapshot:response' && event.data.requestId === requestId) finish(event.data.html)
    }
    window.addEventListener('message', onMessage)
    target.postMessage({ type: 'snapshot', requestId }, '*')
  })
}

export async function captureMessages(element: HTMLElement): Promise<HTMLCanvasElement> {
  const { toCanvas } = await import('html-to-image')
  await document.fonts.ready
  const replacements: { iframe: HTMLIFrameElement; image: HTMLImageElement; display: string }[] = []
  const temporaryFrames: HTMLIFrameElement[] = []
  try {
    const frames = Array.from(element.querySelectorAll('iframe')).filter((frame) => frame.offsetWidth && frame.offsetHeight)
    for (const iframe of frames) {
      const html = await requestSnapshot(iframe)
      const frame = document.createElement('iframe')
      temporaryFrames.push(frame)
      frame.setAttribute('sandbox', 'allow-same-origin')
      Object.assign(frame.style, { position: 'fixed', left: '-100000px', width: `${iframe.offsetWidth}px`, height: `${iframe.offsetHeight}px` })
      await new Promise<void>((resolve, reject) => {
        const timer = window.setTimeout(() => reject(new Error('快照加载超时')), 10000)
        frame.onload = () => {
          clearTimeout(timer)
          resolve()
        }
        frame.srcdoc = html
        document.body.appendChild(frame)
      })
      const root = frame.contentDocument?.documentElement
      if (!root) throw new Error('无法读取快照')
      await frame.contentDocument?.fonts.ready
      const canvas = await toCanvas(root, { pixelRatio: 2, width: iframe.offsetWidth, height: iframe.offsetHeight })
      const image = new Image()
      image.src = canvas.toDataURL()
      image.style.cssText = iframe.style.cssText
      image.style.width = `${iframe.offsetWidth}px`
      image.style.height = `${iframe.offsetHeight}px`
      await image.decode()
      replacements.push({ iframe, image, display: iframe.style.display })
      iframe.after(image)
      iframe.style.display = 'none'
    }
    return await toCanvas(element, {
      pixelRatio: 2,
      backgroundColor: '#ffffff',
      filter: (node) =>
        !(node instanceof HTMLElement && (node.matches('button, .mk-conversation-export-exclude') || node.getAttribute('role') === 'button')),
    })
  } finally {
    replacements.forEach(({ iframe, image, display }) => {
      iframe.style.display = display
      image.remove()
    })
    temporaryFrames.forEach((frame) => frame.remove())
  }
}
