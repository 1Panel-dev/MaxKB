import { type App } from 'vue'
import AppIcon from './icons/AppIcon.vue'
import LoginLayout from './login-layout/index.vue'
import LoginContainer from './login-container/index.vue'
import LayoutContent from './content-container/LayoutContent.vue'

export default {
  install(app: App) {
    app.component(AppIcon.name, AppIcon)
    app.component(LoginLayout.name, LoginLayout)
    app.component(LoginContainer.name, LoginContainer)
    app.component(LayoutContent.name, LayoutContent)
  }
}
