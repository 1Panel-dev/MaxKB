<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { randomId } from '@/utils/common'

defineOptions({ name: 'MarkdownEchartsRender' })

const props = defineProps<{ option: string }>()

// 后端下发的图表配置：actionType 为 EVAL 时 option 是一段脚本，需在沙箱 iframe 中执行得到真实 option
type ChartStyle = Record<string, string>
interface ChartOptionPayload {
  actionType?: string
  option?: unknown
  style?: ChartStyle
}
interface EvalResult {
  option: echarts.EChartsOption
  style: ChartStyle | null
}

const chartsRef = ref<HTMLDivElement>()
const iframeRef = ref<HTMLIFrameElement>()
const style = ref<ChartStyle>({ height: '220px', width: '100%' })

const iframeHtml = /* html */ `
<!DOCTYPE html><html><head><meta charset="UTF-8"/></head><body><script>
  window.addEventListener('message', ({ data, source, origin }) => {
    if (data?.type !== 'EVAL_OPTION') return
    try {
      const option_json = JSON.parse(data.option_str)
      const style = { value: null }
      if (option_json.style) style.value = option_json.style
      let option = {}
      eval(option_json.option)
      source.postMessage(
        { type: 'EVAL_RESULT', id: data.id, result_str: JSON.stringify({ option, style: style.value }) },
        origin || '*'
      )
    } catch (e) {
      source.postMessage({ type: 'EVAL_ERROR', id: data.id, error: e.message }, origin || '*')
    }
  })
<\/script></body></html>`

// ── 沙箱执行 ───────────────────────────────────────────────────────────────
const EVAL_TIMEOUT_MS = 5000
let iframeReady = false
let pendingPayload: ChartOptionPayload | null = null

function evalInSandbox(payload: ChartOptionPayload): Promise<EvalResult> {
  return new Promise((resolve, reject) => {
    const id = randomId()
    const timer = setTimeout(() => {
      window.removeEventListener('message', handler)
      reject(new Error(`evalInSandbox timeout (id=${id})`))
    }, EVAL_TIMEOUT_MS)

    function handler(event: MessageEvent) {
      // 只接收本实例沙箱对本次请求的回复
      if (event.source !== iframeRef.value?.contentWindow) return
      const { type, id: responseId, result_str, error } = event.data || {}
      if (responseId !== id || (type !== 'EVAL_RESULT' && type !== 'EVAL_ERROR')) return
      clearTimeout(timer)
      window.removeEventListener('message', handler)
      if (type === 'EVAL_ERROR') return reject(new Error(error))
      try {
        resolve(JSON.parse(result_str))
      } catch (e) {
        reject(e)
      }
    }

    window.addEventListener('message', handler)
    iframeRef.value?.contentWindow?.postMessage({ type: 'EVAL_OPTION', id, option_str: JSON.stringify(payload) }, '*')
  })
}

function onIframeLoad() {
  iframeReady = true
  if (pendingPayload) {
    runEval(pendingPayload)
    pendingPayload = null
  }
}

// ── 渲染 ───────────────────────────────────────────────────────────────────
function ensureChart() {
  if (!chartsRef.value) return null
  return echarts.getInstanceByDom(chartsRef.value) ?? echarts.init(chartsRef.value)
}

function runEval(payload: ChartOptionPayload) {
  const chart = ensureChart()
  if (!chart) return
  evalInSandbox(payload)
    .then(({ option, style: evalStyle }) => {
      if (evalStyle) style.value = evalStyle
      chart.setOption(option, true)
    })
    .catch((e) => console.error('[ECharts EVAL error]', e))
}

function applyOption(payload: ChartOptionPayload & echarts.EChartsOption) {
  if (payload.actionType === 'EVAL') {
    if (iframeReady) runEval(payload)
    else pendingPayload = payload
    return
  }
  const chart = ensureChart()
  if (!chart) return
  if (payload.style) style.value = payload.style
  chart.setOption((payload.option ?? payload) as echarts.EChartsOption, true)
}

function initChart() {
  if (!chartsRef.value || !props.option) return
  try {
    applyOption(JSON.parse(props.option))
  } catch (e) {
    console.error('[ECharts] invalid option JSON', e)
  }
}

// ── 尺寸与生命周期 ─────────────────────────────────────────────────────────
let resizeTimer: ReturnType<typeof setTimeout> | undefined
let resizeObserver: ResizeObserver | undefined
function onResize() {
  clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (chartsRef.value) echarts.getInstanceByDom(chartsRef.value)?.resize()
  }, 100)
}

watch(
  () => props.option,
  (option) => {
    if (option) nextTick(initChart)
  },
)

onMounted(() => {
  nextTick(initChart)
  if (!chartsRef.value) return
  resizeObserver = new ResizeObserver(onResize)
  resizeObserver.observe(chartsRef.value)
})

onBeforeUnmount(() => {
  clearTimeout(resizeTimer)
  resizeObserver?.disconnect()
  if (chartsRef.value) echarts.getInstanceByDom(chartsRef.value)?.dispose()
})
</script>

<template>
  <div class="overflow-x-auto">
    <iframe v-show="false" ref="iframeRef" sandbox="allow-scripts" :srcdoc="iframeHtml" @load="onIframeLoad" />
    <div ref="chartsRef" :style="style" />
  </div>
</template>
