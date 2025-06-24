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
import ReadWrite from './read-write/index.vue'
import AutoTooltip from './auto-tooltip/index.vue'
import MdEditor from './markdown/MdEditor.vue'
import MdPreview from './markdown/MdPreview.vue'
import MdEditorMagnify from './markdown/MdEditorMagnify.vue'
import TagEllipsis from './tag-ellipsis/index.vue'
import CardCheckbox from './card-checkbox/index.vue'
import AiChat from './ai-chat/index.vue'
import KnowledgeIcon from './app-icon/KnowledgeIcon.vue'
import TagGroup from './tag-group/index.vue'
import WorkspaceDropdown from './workspace-dropdown/index.vue'
import FolderBreadcrumb from './folder-breadcrumb/index.vue'
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
    app.component('ReadWrite', ReadWrite)
    app.component('AutoTooltip', AutoTooltip)
    app.component('MdPreview', MdPreview)
    app.component('MdEditor', MdEditor)
    app.component('MdEditorMagnify', MdEditorMagnify)
    app.component('TagEllipsis', TagEllipsis)
    app.component('CardCheckbox', CardCheckbox)
    app.component('AiChat', AiChat)
    app.component('KnowledgeIcon', KnowledgeIcon)
    app.component('TagGroup', TagGroup)
    app.component('WorkspaceDropdown', WorkspaceDropdown)
    app.component('FolderBreadcrumb', FolderBreadcrumb)
  },
}
