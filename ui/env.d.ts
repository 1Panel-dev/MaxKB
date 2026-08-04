/// <reference types="vite/client" />

interface MaxKBRuntimeConfig {
  prefix?: string
  chatPrefix?: string
}

interface Window {
  MaxKB?: MaxKBRuntimeConfig
}
