import type { MessageInputStore } from '../components/message-input/index'
import type { MessageListStore } from '../components/message-list/index'
import type { ConversationAppInfo } from '../core/types'
import type { ConversationListStore } from '../left-sidebar/conversation-list/index'
import type { RightSidebarStore } from '../right-sidebar/index'
import type { Ref } from 'vue'

// view 组装出来的各组件 store 集合
export interface ConversationBundle {
  /** 当前智能体信息，由 view 加载，各组件 store 只读共享。 */
  appInfo: Readonly<Ref<ConversationAppInfo | null>>
  list: ConversationListStore
  msgs: MessageListStore
  input: MessageInputStore
  rightSidebar: RightSidebarStore
}
