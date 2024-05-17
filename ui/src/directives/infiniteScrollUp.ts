import { nextTick } from 'vue'

import { throttle } from 'lodash-unified'
import { getScrollContainer } from 'element-plus/es/utils/index'
import type { App } from 'vue'
export const SCOPE = 'InfiniteScrollUP'
export const CHECK_INTERVAL = 50
export const DEFAULT_DELAY = 200
export const DEFAULT_DISTANCE = 0

const attributes = {
  delay: {
    type: Number,
    default: DEFAULT_DELAY
  },
  distance: {
    type: Number,
    default: DEFAULT_DISTANCE
  },
  disabled: {
    type: Boolean,
    default: false
  },
  immediate: {
    type: Boolean,
    default: true
  }
}

type Attrs = typeof attributes
type ScrollOptions = { [K in keyof Attrs]: Attrs[K]['default'] }
type InfiniteScrollCallback = () => void
type InfiniteScrollEl = HTMLElement & {
  [SCOPE]: {
    container: HTMLElement | Window
    containerEl: HTMLElement
    instance: any
    delay: number // export for test
    lastScrollTop: number
    cb: InfiniteScrollCallback
    onScroll: () => void
    observer?: MutationObserver
  }
}

const getScrollOptions = (el: HTMLElement, instance: any): ScrollOptions => {
  return Object.entries(attributes).reduce((acm: any, [name, option]) => {
    const { type, default: defaultValue } = option
    const attrVal: any = el.getAttribute(`infinite-scroll-up-${name}`)
    let value = instance[attrVal] ?? attrVal ?? defaultValue
    value = value === 'false' ? false : value
    value = type(value)
    acm[name] = Number.isNaN(value) ? defaultValue : value
    return acm
  }, {} as ScrollOptions)
}

const destroyObserver = (el: InfiniteScrollEl) => {
  const { observer } = el[SCOPE]

  if (observer) {
    observer.disconnect()
    delete el[SCOPE].observer
  }
}

const handleScroll = (el: InfiniteScrollEl, cb: InfiniteScrollCallback) => {
  const { container, containerEl, instance, observer, lastScrollTop } = el[SCOPE]
  const { disabled } = getScrollOptions(el, instance)
  const { scrollTop } = containerEl

  el[SCOPE].lastScrollTop = scrollTop

  // trigger only if full check has done and not disabled and scroll down

  if (observer || disabled || scrollTop > 0) return

  if (scrollTop == 0) {
    cb.call(instance)
  }
}

function checkFull(el: InfiniteScrollEl, cb: InfiniteScrollCallback) {
  const { containerEl, instance } = el[SCOPE]
  const { disabled } = getScrollOptions(el, instance)

  if (disabled || containerEl.clientHeight == 0) return

  if (containerEl.scrollTop <= 0) {
    cb.call(instance)
  } else {
    destroyObserver(el)
  }
}

const InfiniteScroll = {
  async mounted(el: any, binding: any) {
    const { instance, value: cb } = binding

    // ensure parentNode mounted
    await nextTick()

    const { delay, immediate } = getScrollOptions(el, instance)
    const container = getScrollContainer(el, true)
    const containerEl = container === window ? document.documentElement : (container as HTMLElement)
    const onScroll = throttle(handleScroll.bind(null, el, cb), delay)

    if (!container) return

    el[SCOPE] = {
      instance,
      container,
      containerEl,
      delay,
      cb,
      onScroll,
      lastScrollTop: containerEl.scrollTop
    }

    if (immediate) {
      const observer = new MutationObserver(throttle(checkFull.bind(null, el, cb), CHECK_INTERVAL))
      el[SCOPE].observer = observer
      observer.observe(el, { childList: true, subtree: true })
      checkFull(el, cb)
    }

    container.addEventListener('scroll', onScroll)
  },
  unmounted(el: any) {
    if (!el[SCOPE]) return
    const { container, onScroll } = el[SCOPE]

    container?.removeEventListener('scroll', onScroll)
    destroyObserver(el)
  },
  async updated(el: any) {
    if (!el[SCOPE]) {
      await nextTick()
    } else {
      const { containerEl, cb, observer } = el[SCOPE]
      if (containerEl.clientHeight && observer) {
        checkFull(el, cb)
      }
    }
  }
}
export default {
  install: (app: App) => {
    app.directive('infinite-scroll-up', InfiniteScroll)
  }
}
