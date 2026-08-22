import { fileURLToPath, URL } from 'node:url'
import fs from 'node:fs'
import path from 'node:path'
import type { Plugin, ProxyOptions, ViteDevServer } from 'vite'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import tailwindcss from '@tailwindcss/vite'
import Components from 'unplugin-vue-components/vite'

const envDir = './env'
const defaultBackendTarget = 'http://47.120.55.164:9090/'
const projectRoot = fileURLToPath(new URL('.', import.meta.url))

const renameHtmlPlugin = (outDir: string, entry: string) => {
  return {
    name: 'rename-html',
    closeBundle: () => {
      if (entry === 'index.html') {
        return
      }

      const buildDir = path.resolve(projectRoot, outDir)
      const oldFile = path.join(buildDir, entry)
      const newFile = path.join(buildDir, 'index.html')

      if (!fs.existsSync(oldFile)) {
        return
      }

      if (fs.existsSync(newFile)) {
        fs.unlinkSync(newFile)
      }

      fs.renameSync(oldFile, newFile)
    },
  }
}

const devEntryFallbackPlugin = (entry: string, basePath?: string): Plugin => {
  return {
    name: 'dev-entry-fallback',
    configureServer(server: ViteDevServer) {
      const normalizedBasePath = normalizeBasePath(basePath)

      server.middlewares.use((req, _res, next) => {
        if (!req.url) {
          next()
          return
        }

        const pathname = new URL(req.url, 'http://localhost').pathname

        // 相对 favicon 地址会随当前路由加深，开发环境统一回退到 public/favicon.ico。
        if (pathname.endsWith('/favicon.ico')) {
          req.url = '/favicon.ico'
          next()
          return
        }

        if (entry === 'index.html') {
          next()
          return
        }

        const acceptsHtml = req.headers.accept?.includes('text/html')
        const isAppRoute =
          pathname === '/' ||
          pathname === normalizedBasePath ||
          (Boolean(normalizedBasePath) && pathname.startsWith(normalizedBasePath))

        // History 模式下，刷新任意前端路由都需要返回当前应用的 HTML 入口。
        if (acceptsHtml && isAppRoute && !path.extname(pathname)) {
          req.url = `/${entry}`
        }

        next()
      })
    },
  }
}

const normalizeBasePath = (basePath?: string) => {
  if (!basePath || basePath === './') {
    return ''
  }

  return basePath.startsWith('/') ? basePath : `/${basePath}`
}

const stripBasePath = (urlPath: string, basePath: string) => {
  const normalizedBasePath = normalizeBasePath(basePath)

  if (!normalizedBasePath) {
    return urlPath
  }

  return urlPath.replace(normalizedBasePath, '/')
}

const createProxyConfig = (env: Record<string, string>) => {
  const backendTarget = env.VITE_API_TARGET || defaultBackendTarget
  const basePath = normalizeBasePath(env.VITE_BASE_PATH)
  const appPort = Number(env.VITE_APP_PORT || 5173)
  const proxy: Record<string, string | ProxyOptions> = {
    '/admin/api': {
      target: backendTarget,
      changeOrigin: true,
    },
    '/chat/api': {
      target: backendTarget,
      changeOrigin: true,
    },
    '/doc': {
      target: backendTarget,
      changeOrigin: true,
      rewrite: (path) => stripBasePath(path, basePath),
    },
    '/schema': {
      target: backendTarget,
      changeOrigin: true,
      rewrite: (path) => stripBasePath(path, basePath),
    },
    '/static': {
      target: backendTarget,
      changeOrigin: true,
      rewrite: (path) => stripBasePath(path, basePath),
    },
  }

  if (basePath) {
    proxy[`^${basePath}.+/oss/file/.*$`] = {
      target: backendTarget,
      changeOrigin: true,
    }
    proxy[`^${basePath}oss/file/.*$`] = {
      target: backendTarget,
      changeOrigin: true,
    }
    proxy[`^${basePath}oss/get_url/.*$`] = {
      target: backendTarget,
      changeOrigin: true,
    }
  }

  return proxy
}

const createOutDir = (basePath?: string) => {
  const normalizedBasePath = normalizeBasePath(basePath)

  if (!normalizedBasePath) {
    return 'dist'
  }

  return `dist${normalizedBasePath}`
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, envDir, '')
  const entry = env.VITE_ENTRY || 'index.html'
  const port = Number(env.VITE_APP_PORT || 5173)

  return {
    base: './',
    envDir,
    plugins: [
      tailwindcss(),
      Components({
        dirs: ['src/components/global'],
        dts: 'src/components.d.ts',
      }),
      vue(),
      vueJsx(),
      devEntryFallbackPlugin(entry, env.VITE_BASE_PATH),
      renameHtmlPlugin(createOutDir(env.VITE_BASE_PATH), entry),
    ],
    server: {
      cors: true,
      host: '0.0.0.0',
      port,
      strictPort: true,
      proxy: createProxyConfig(env),
    },
    build: {
      outDir: createOutDir(env.VITE_BASE_PATH),
      target: 'es2022',
      rollupOptions: {
        input: entry,
      },
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  }
})
