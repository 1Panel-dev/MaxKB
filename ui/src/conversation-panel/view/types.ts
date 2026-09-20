import type { ConversationListStore } from '../left-sidebar/conversation-list/index'
import type { MessageListStore } from '../components/message-list/index'
import type { MessageInputStore } from '../components/message-input/index'
import type { ExecutionDetailStore } from '../right-sidebar/execution-detail/index'

// view 组装出来的各组件 store 集合
export interface ConversationBundle {
  list: ConversationListStore
  msgs: MessageListStore
  input: MessageInputStore
  detail: ExecutionDetailStore
}
