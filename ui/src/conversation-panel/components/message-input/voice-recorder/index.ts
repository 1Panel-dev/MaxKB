import { onBeforeUnmount, ref } from 'vue'
import Recorder from 'recorder-core'
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine'
import { MsgError } from '@/utils/message'

/** 单次录音最长秒数，到时自动结束并转写。 */
export const VOICE_RECORD_MAX_SECONDS = 60
/** 录音波形柱数量。 */
const WAVE_BAR_COUNT = 60

// 关闭 recorder-core 的控制台日志
Recorder.CLog = () => {}

/** recorder-core 只导出 any，这里声明本文件用到的实例方法。 */
interface RecorderInstance {
  open: (success: () => void, fail: (message: string, isUserNotAllow: boolean) => void) => void
  start: () => void
  stop: (success: (audio: Blob, duration: number) => void, fail: (message: string) => void) => void
  close: () => void
}

/**
 * 输入框语音录制：录制 16kHz MP3（与语音转文字模型的入参格式一致），结束后回调录音文件。
 * 录音期间记录音量用于绘制波形；组件卸载时释放麦克风。
 */
export function useVoiceRecorder(onRecorded: (audio: Blob) => void) {
  const recording = ref(false)
  const seconds = ref(0)
  const waveLevels = ref<number[]>(Array(WAVE_BAR_COUNT).fill(0))

  let recorder: RecorderInstance | null = null
  let timer: ReturnType<typeof setInterval> | null = null

  const stopTimer = () => {
    if (timer) clearInterval(timer)
    timer = null
  }

  const release = () => {
    stopTimer()
    recorder?.close()
    recorder = null
    recording.value = false
  }

  const start = () => {
    if (recorder) return
    const instance: RecorderInstance = new Recorder({
      type: 'mp3',
      bitRate: 128,
      sampleRate: 16000,
      onProcess: (_buffers: unknown, powerLevel: number) => {
        waveLevels.value = [...waveLevels.value.slice(1), powerLevel]
      },
    })
    recorder = instance
    instance.open(
      () => {
        // 打开权限期间已取消
        if (recorder !== instance) return instance.close()
        seconds.value = 0
        waveLevels.value = Array(WAVE_BAR_COUNT).fill(0)
        instance.start()
        recording.value = true
        timer = setInterval(() => {
          seconds.value++
          if (seconds.value >= VOICE_RECORD_MAX_SECONDS) stop()
        }, 1000)
      },
      (message: string) => {
        if (recorder === instance) recorder = null
        MsgError(`无法录音：${message}`)
      },
    )
  }

  /** 结束录音并回调录音文件。 */
  const stop = () => {
    const instance = recorder
    if (!instance || !recording.value) return
    stopTimer()
    instance.stop(
      (audio: Blob) => {
        release()
        onRecorded(audio)
      },
      (message: string) => {
        release()
        MsgError(`录音失败：${message}`)
      },
    )
  }

  /** 放弃本次录音，不转写。 */
  const cancel = release

  onBeforeUnmount(release)

  return { recording, seconds, waveLevels, start, stop, cancel }
}
