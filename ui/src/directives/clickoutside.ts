import type { App } from 'vue'
import { ClickOutside as vClickOutside } from 'element-plus'
export default {
  install: (app: App) => {
    app.directive('click-outside', vClickOutside)
  }
}
