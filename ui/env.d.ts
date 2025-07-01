/// <reference types="vite/client" />
interface Window {
  sendMessage: ?((message: string, other_params_data: any) => void)
  MaxKB: {
    prefix: string
  }
}
