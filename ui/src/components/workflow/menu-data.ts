const icons: any = import.meta.glob('./icons/**.vue', { eager: true })
function iconComponent(name: string) {
  const url = `./icons/${name}.vue`
  return icons[url]?.default || null
}
/**
 * 说明
 * type 与 nodes 文件对应
 */
const shapeList = [
  {
    type: 'ai-chat-node',
    text: '与 AI 大模型进行对话',
    label: 'AI 对话',
    icon: 'ai-chat-node-icon',
    properties: {
      height: '',
      stepName: 'AI 对话',
      input: [
        {
          key: '输入'
        }
      ],
      output: [
        {
          key: '输出'
        }
      ]
    }
  },
  {
    type: 'search-dataset-node',
    text: '关联知识库，查找与问题相关的分段',
    label: '知识检索',
    icon: 'search-dataset-node-icon',
    properties: {
      height: '',
      stepName: '知识检索',
      input: [
        {
          key: '输入'
        }
      ],
      output: [
        {
          key: '输出'
        }
      ]
    }
  }
]

export { shapeList, iconComponent }
