import { type App } from 'vue'
import LogoFull from './logo/LogoFull.vue'
import LogoIcon from './logo/LogoIcon.vue'
import SendIcon from './logo/SendIcon.vue'
import dynamicsForm from './dynamics-form'
import AppIcon from './app-icon/AppIcon.vue'
import LayoutContainer from './layout-container/index.vue'
import ContentContainer from './layout-container/ContentContainer.vue'
import CardBox from './card-box/index.vue'
export default {
  install(app: App) {
    app.component('LogoFull', LogoFull)
    app.component('LogoIcon', LogoIcon)
    app.component('SendIcon', SendIcon)
    app.use(dynamicsForm)
    app.component('AppIcon', AppIcon)
    app.component('LayoutContainer', LayoutContainer)
    app.component('ContentContainer', ContentContainer)
    app.component('CardBox', CardBox)
  },
}
