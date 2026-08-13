/** Vue 插件：注册全局 `$perm`，模板中免 import 直接用 `$perm.application.workspace.edit(id)`。 */

import type { App } from 'vue'
import { perm } from './index'

export default {
  install(app: App) {
    app.config.globalProperties.$perm = perm
  },
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $perm: typeof perm
  }
}
