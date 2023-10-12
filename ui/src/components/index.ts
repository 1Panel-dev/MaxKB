import { type App } from 'vue'
import AppIcon from './icons/AppIcon.vue'
import LoginLayout from './layout/login-layout/index.vue'
import LoginContainer from './layout/login-container/index.vue'

export default {
  install(app: App) {
    app.component(AppIcon.name, AppIcon)
    app.component(LoginLayout.name, LoginLayout)
    app.component(LoginContainer.name, LoginContainer)
  }
}
