import { ref } from 'vue'
import { ConversationStream } from '../../../stream'

export function useStreamManager() {
  const streams = new Map<string, ConversationStream>()
  const loadingSet = ref(new Set<string>())

  const getStreamLoading = (cid: string) => loadingSet.value.has(cid)

  const startStream = (opts: {
    cid: string
    request: () => Promise<any>
    onStream: (chunk: any) => void
    onFinish?: () => void
    onFailure?: (e: any) => void
  }) => {
    loadingSet.value.add(opts.cid)

    opts.request().then((response: any) => {
      const stream = new ConversationStream(
        response,
        opts.onStream,
        () => {
          loadingSet.value.delete(opts.cid)
          streams.delete(opts.cid)
          opts.onFinish?.()
        },
        (e: any) => {
          loadingSet.value.delete(opts.cid)
          streams.delete(opts.cid)
          opts.onFailure?.(e)
        },
      )
      streams.set(opts.cid, stream)
      stream.start()
    }).catch((e: any) => {
      loadingSet.value.delete(opts.cid)
      opts.onFailure?.(e)
    })
  }

  const cancelStream = (cid: string) => {
    const stream = streams.get(cid)
    if (stream) {
      stream.cancel()
      streams.delete(cid)
      loadingSet.value.delete(cid)
    }
  }

  const cancelAll = () => {
    streams.forEach((s) => s.cancel())
    streams.clear()
    loadingSet.value.clear()
  }

  return {
    getStreamLoading,
    startStream,
    cancelStream,
    cancelAll,
  }
}
