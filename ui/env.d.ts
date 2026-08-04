/// <reference types="vite/client" />

interface MaxKBRuntimeConfig {
  prefix?: string
  chatPrefix?: string
}

interface Window {
  MaxKB?: MaxKBRuntimeConfig
  DTFrameLogin?: (
    frame: { height: number; id: string; width: number },
    params: Record<string, string>,
    success: (result: { authCode: string }) => void,
    error: (message: string) => void,
  ) => void
  QRLogin?: (options: Record<string, string>) => {
    matchData: (data: unknown) => boolean
    matchOrigin: (origin: string) => boolean
  }
  tt?: {
    requestAuthCode: (options: {
      appId: string
      fail: (error: unknown) => void
      success: (result: { code: string }) => void
    }) => void
  }
}
