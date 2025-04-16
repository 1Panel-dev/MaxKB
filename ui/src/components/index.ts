import { type App } from 'vue'
import LogoFull from './logo/LogoFull.vue'
import LogoIcon from './logo/LogoIcon.vue'
import SendIcon from './logo/SendIcon.vue'
export default {
  install(app: App) {
    app.component('LogoFull', LogoFull)
    app.component('LogoIcon', LogoIcon)
    app.component('SendIcon', SendIcon)
  },
}
