import { type App } from 'vue'
import LogoFull from './logo/LogoFull.vue'
import LogoIcon from './logo/LogoIcon.vue'
import SendIcon from './logo/SendIcon.vue'
import dynamicsForm from './dynamics-form'
import AppIcon from './app-icon/AppIcon.vue'
import LayoutContainer from './layout-container/index.vue'
import ContentContainer from './layout-container/ContentContainer.vue'
import CardBox from './card-box/index.vue'
import FolderTree from './folder-tree/index.vue'
import CommonList from './common-list/index.vue'
import BackButton from './back-button/index.vue'
import AppTable from './app-table/index.vue'
import CodemirrorEditor from './codemirror-editor/index.vue'
import InfiniteScroll from './infinite-scroll/index.vue'
import ModelSelect from './model-select/index.vue'
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
    app.component('FolderTree', FolderTree)
    app.component('CommonList', CommonList)
    app.component('BackButton', BackButton)
    app.component('AppTable', AppTable)
    app.component('CodemirrorEditor', CodemirrorEditor)
    app.component('InfiniteScroll', InfiniteScroll)
    app.component('ModelSelect', ModelSelect)
  },
}
