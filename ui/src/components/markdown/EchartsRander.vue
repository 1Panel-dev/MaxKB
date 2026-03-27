<template>
  <div class="charts-container">
    <iframe
      v-show="false"
      ref="iframeRef"
      sandbox="allow-scripts"
      :srcdoc="iframeHtml"
      @load="onIframeLoad"
    ></iframe>
    <div ref="chartsRef" :style="style" v-resize="onResize"></div>
  </div>
</template>
<script lang="ts" setup>
import { onMounted, onBeforeUnmount, nextTick, watch, ref } from 'vue'
import * as echarts from 'echarts'

// ── props ──────────────────────────────────────────────────────────────────
const props = defineProps<{ option: string }>()

// ── refs ───────────────────────────────────────────────────────────────────
const chartsRef = ref<HTMLDivElement>()
const iframeRef = ref<HTMLIFrameElement>()
const style = ref({ height: '220px', width: '100%' })

const iframeHtml = /* html */ `
<!DOCTYPE html><html><head><meta charset="UTF-8"/></head><body><script>
  window.parent.postMessage({ type: 'IFRAME_READY' }, '*')
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

let iframeReady = false
let pendingOption: any = null

const onIframeLoad = () => {
  iframeReady = true
  if (pendingOption) {
    runEval(pendingOption)
    pendingOption = null
  }
}

let evalSeq = 0
const EVAL_TIMEOUT_MS = 5000

const evalInSandbox = (option_json: any): Promise<{ option: any; style: any }> => {
  return new Promise((resolve, reject) => {
    const id = ++evalSeq
    let settled = false

    const timer = setTimeout(() => {
      if (settled) return
      settled = true
      window.removeEventListener('message', handler)
      reject(new Error(`evalInSandbox timeout (id=${id})`))
    }, EVAL_TIMEOUT_MS)

    function handler(event: MessageEvent) {
      const { type, id: rid, result_str, error } = event.data || {}
      if (rid !== id) return // 忽略其他实例或旧请求的消息
      if (type !== 'EVAL_RESULT' && type !== 'EVAL_ERROR') return
      settled = true
      clearTimeout(timer)
      window.removeEventListener('message', handler)
      if (type === 'EVAL_RESULT') {
        try {
          resolve(JSON.parse(result_str))
        } catch (e) {
          reject(e)
        }
      } else {
        reject(new Error(error))
      }
    }

    window.addEventListener('message', handler)
    iframeRef.value?.contentWindow?.postMessage(
      { type: 'EVAL_OPTION', id, option_str: JSON.stringify(option_json) },
      '*',
    )
  })
}

const ensureChart = (): echarts.ECharts | null => {
  if (!chartsRef.value) return null
  return echarts.getInstanceByDom(chartsRef.value) ?? echarts.init(chartsRef.value)
}

const runEval = (option: any) => {
  const chart = ensureChart()
  if (!chart) return
  evalInSandbox(option)
    .then(({ option: opt, style: s }) => {
      if (s) style.value = s
      chart.setOption(opt, true)
    })
    .catch((e) => console.error('[ECharts EVAL error]', e))
}

const applyOption = (raw: any) => {
  if (raw.actionType === 'EVAL') {
    if (iframeReady) runEval(raw)
    else pendingOption = raw
    return
  }
  const chart = ensureChart()
  if (!chart) return
  if (raw.style) style.value = raw.style
  chart.setOption(raw.option ?? raw, true)
}

const initChart = () => {
  if (!chartsRef.value || !props.option) return
  try {
    applyOption(JSON.parse(props.option))
  } catch (e) {
    console.error('[ECharts] invalid option JSON', e)
  }
}

// ── resize 防抖 ────────────────────────────────────────────────────────────
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const onResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    echarts.getInstanceByDom(chartsRef.value!)?.resize()
  }, 100)
}

// ── 生命周期 ───────────────────────────────────────────────────────────────
watch(
  () => props.option,
  (val) => {
    if (val) nextTick(initChart)
  },
)

onMounted(() => nextTick(initChart))

onBeforeUnmount(() => {
  if (resizeTimer) clearTimeout(resizeTimer)
  if (chartsRef.value) echarts.getInstanceByDom(chartsRef.value)?.dispose()
})
</script>
<style lang="scss" scoped>
.charts-container {
  overflow-x: auto;
}
.charts-container::-webkit-scrollbar-track-piece {
  background-color: rgba(0, 0, 0, 0);
  border-left: 1px solid rgba(0, 0, 0, 0);
}
.charts-container::-webkit-scrollbar {
  width: 5px;
  height: 5px;
  -webkit-border-radius: 5px;
  -moz-border-radius: 5px;
  border-radius: 5px;
}
.charts-container::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.5);
  background-clip: padding-box;
  -webkit-border-radius: 5px;
  -moz-border-radius: 5px;
  border-radius: 5px;
  min-height: 28px;
}
.charts-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.5);
  -webkit-border-radius: 5px;
  -moz-border-radius: 5px;
  border-radius: 5px;
}
</style>
