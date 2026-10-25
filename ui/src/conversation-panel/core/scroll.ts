/** 消息容器的底部跟随：用户上滑后停止跟随，回到底部附近恢复。 */
export class Scroll {
  private element: HTMLElement
  private bottomSuction = true
  private programmaticTop?: number
  private animationFrame?: number
  private destroyed = false

  constructor(element: HTMLElement) {
    this.element = element
    element.addEventListener('scroll', this.onScroll)
  }

  private onScroll = () => {
    if (this.programmaticTop !== undefined && Math.abs(this.element.scrollTop - this.programmaticTop) < 1) {
      this.programmaticTop = undefined
      return
    }
    this.programmaticTop = undefined
    this.bottomSuction = this.element.scrollHeight - this.element.scrollTop <= this.element.clientHeight + 15
    // 用户离开底部后，不再执行上一轮强制定位的动画帧。
    if (!this.bottomSuction) this.cancelFrame()
  }

  private cancelFrame() {
    if (this.animationFrame !== undefined) cancelAnimationFrame(this.animationFrame)
    this.animationFrame = undefined
  }

  /** 仅在用户仍位于底部附近时跟随新增内容。 */
  scrollBottom() {
    if (this.destroyed || !this.bottomSuction) return
    this.element.scrollTop = this.element.scrollHeight
    this.programmaticTop = this.element.scrollTop
  }

  /** 强制定位最新消息，并在下一帧补一次布局后的定位。 */
  forceBottom() {
    if (this.destroyed) return
    this.cancelFrame()
    this.bottomSuction = true
    this.scrollBottom()
    this.animationFrame = requestAnimationFrame(() => {
      this.animationFrame = undefined
      this.scrollBottom()
    })
  }

  /** 容器卸载或替换时释放滚动监听和待执行的动画帧。 */
  destroy() {
    this.destroyed = true
    this.element.removeEventListener('scroll', this.onScroll)
    this.cancelFrame()
  }
}
