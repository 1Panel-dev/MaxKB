import { fileURLToPath, URL } from 'node:url'
import type { ProxyOptions } from 'vite'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import DefineOptions from 'unplugin-vue-define-options/vite'
import path from 'path'
import { createHtmlPlugin } from 'vite-plugin-html'
import fs from 'fs'
// import vueDevTools from 'vite-plugin-vue-devtools'
const envDir = './env'
// 自定义插件：重命名入口文件
const renameHtmlPlugin = (outDir: string, entry: string) => {
  return {
    name: 'rename-html',
    closeBundle: () => {
      const buildDir = path.resolve(__dirname, outDir)
      const oldFile = path.join(buildDir, entry)
      const newFile = path.join(buildDir, 'index.html')

      // 检查文件是否存在
      if (fs.existsSync(oldFile)) {
        // 删除已存在的 index.html
        if (fs.existsSync(newFile)) {
          fs.unlinkSync(newFile)
        }
        // 重命名文件
        fs.renameSync(oldFile, newFile)
      }
    },
  }
}
// https://vite.dev/config/
export default defineConfig((conf: any) => {
  const mode = conf.mode
  const ENV = loadEnv(mode, envDir)
  const proxyConf: Record<string, string | ProxyOptions> = {}
  
  // ===== API 代理 =====
  // 管理后台API
  proxyConf['/admin/api'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
  }
  
  // 聊天API
  proxyConf['/chat/api'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
  }
  
  // ===== 文档和Schema =====
  // Swagger-UI静态文件特殊处理
  proxyConf['/doc/swagger-ui-dist'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
    rewrite: (path: string) => path.replace('/doc/swagger-ui-dist', '/static/drf_spectacular_sidecar/swagger-ui-dist'),
  }
  
  // API文档
  proxyConf['/doc'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
  }
  
  // API Schema
  proxyConf['/schema'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
  }
  
  // ===== 静态资源代理 =====
  // 直接代理/static路径（用于直接访问）
  proxyConf['/static'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
  }
  
  // 代理所有/admin/路径下的静态文件（通过文件扩展名识别）
  proxyConf['^/admin/.*\\.(png|jpg|jpeg|gif|svg|ico|css|js|woff|woff2|ttf|eot|mp4|webm)$'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
    rewrite: (path: string) => path.replace('/admin', '/static'),
  }
  
  // 代理/admin/路径下的特定目录
  proxyConf['/admin/theme'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
    rewrite: (path: string) => path.replace('/admin', '/static'),
  }
  
  proxyConf['/admin/tool'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
    rewrite: (path: string) => path.replace('/admin', '/static'),
  }
  
  proxyConf['/admin/assets'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
    rewrite: (path: string) => path.replace('/admin', '/static'),
  }
  
  // ===== OSS文件代理 =====
  // OSS文件上传/下载
  proxyConf['/oss'] = {
    target: 'http://jin-Virtual-Machine:8080',
    changeOrigin: true,
  }

  return {
    preflight: false,
    lintOnSave: false,
    base: './',
    envDir: envDir,
    plugins: [
      vue(),
      vueJsx(),
      DefineOptions(),
      createHtmlPlugin({ template: ENV.VITE_ENTRY }),
      renameHtmlPlugin(`dist${ENV.VITE_BASE_PATH}`, ENV.VITE_ENTRY),
    ],
    server: {
      cors: true,
      host: '0.0.0.0',
      port: Number(ENV.VITE_APP_PORT),
      strictPort: true,
      proxy: proxyConf,
    },
    build: {
      outDir: `dist${ENV.VITE_BASE_PATH}`,
      rollupOptions: {
        input: ENV.VITE_ENTRY,
      },
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  }
})
