/**
 * 工作流国际化扩展预留。
 * 当前节点及菜单直接使用中文文案，后续接入 i18n 时在此集中处理。
 */
// function defineLocaleGetter(target: any, prop: string, key: string, fallback?: string) {
//   let overrideValue: string | undefined
//   Object.defineProperty(target, prop, {
//     configurable: true,
//     enumerable: true,
//     get: () => overrideValue || t(key, fallback as any),
//     set: (value) => {
//       overrideValue = value || undefined
//     },
//   })
// }

// function bindLocale(target: any, path: string, key: string, fallback?: string) {
//   const parts = path.split('.')
//   const prop = parts.pop() as string
//   const owner = parts.reduce((obj, part) => obj?.[part], target)
//   if (owner) {
//     defineLocaleGetter(owner, prop, key, fallback)
//   }
// }

// function bindFieldLabels(fields: Array<any> | undefined, keys: string[]) {
//   const refresh = () => {
//     fields?.forEach((field, index) => {
//       if (keys[index]) {
//         field.label = t(keys[index])
//       }
//     })
//   }
//   refresh()
//   watch(i18n.global.locale, refresh)
// }

// function bindNodeLocale(node: any, textKey: string, labelKey: string, stepNameKey = labelKey) {
//   defineLocaleGetter(node, 'text', textKey)
//   defineLocaleGetter(node, 'label', labelKey)
//   bindLocale(node, 'properties.stepName', stepNameKey)
// }

// bindLocale(startNode, 'properties.stepName', 'workflow.nodes.startNode.label')
// bindFieldLabels(startNode.properties.config.fields, ['workflow.nodes.startNode.question'])
// bindFieldLabels(startNode.properties.config.globalFields, [
//   'workflow.nodes.startNode.currentTime',
//   'views.application.form.historyRecord.label',
//   'aiChat.chatId',
// ])
// bindFieldLabels(startNode.properties.fields, ['workflow.nodes.startNode.question'])
// bindFieldLabels(startNode.properties.globalFields, ['workflow.nodes.startNode.currentTime'])
// ;[baseNode, knowledgeBaseNode].forEach((node) => {
//   bindLocale(node, 'properties.stepName', 'common.info')
//   bindLocale(node, 'properties.node_data.prologue', 'views.application.form.defaultPrologue')
//   bindLocale(node, 'properties.user_input_config.title', 'aiChat.userInput')
// })
// bindLocale(toolBaseNode, 'properties.stepName', 'common.info')
// bindLocale(toolBaseNode, 'properties.user_input_config.title', 'aiChat.userInput')
// bindLocale(toolStartNode, 'properties.stepName', 'workflow.nodes.startNode.label')
// bindLocale(toolStartNode, 'properties.user_input_config.title', 'aiChat.userInput')
// const nodeLocaleBindings: Array<[any, string, string]> = [
//   [
//     dataSourceLocalNode,
//     'workflow.nodes.dataSourceLocalNode.text',
//     'workflow.nodes.dataSourceLocalNode.label',
//   ],
//   [
//     dataSourceWebNode,
//     'workflow.nodes.dataSourceWebNode.text',
//     'workflow.nodes.dataSourceWebNode.label',
//   ],
//   [
//     knowledgeWriteNode,
//     'workflow.nodes.knowledgeWriteNode.text',
//     'workflow.nodes.knowledgeWriteNode.label',
//   ],
//   [aiChatNode, 'workflow.nodes.aiChatNode.text', 'workflow.nodes.aiChatNode.label'],
//   [
//     searchKnowledgeNode,
//     'workflow.nodes.searchKnowledgeNode.text',
//     'workflow.nodes.searchKnowledgeNode.label',
//   ],
//   [
//     searchDocumentNode,
//     'workflow.nodes.searchDocumentNode.text',
//     'workflow.nodes.searchDocumentNode.label',
//   ],
//   [questionNode, 'workflow.nodes.questionNode.text', 'workflow.nodes.questionNode.label'],
//   [
//     variableSplittingNode,
//     'workflow.nodes.variableSplittingNode.text',
//     'workflow.nodes.variableSplittingNode.label',
//   ],
//   [
//     parameterExtractionNode,
//     'workflow.nodes.parameterExtractionNode.text',
//     'workflow.nodes.parameterExtractionNode.label',
//   ],
//   [conditionNode, 'workflow.nodes.conditionNode.text', 'workflow.nodes.conditionNode.label'],
//   [replyNode, 'workflow.nodes.replyNode.text', 'workflow.nodes.replyNode.label'],
//   [rerankerNode, 'workflow.nodes.rerankerNode.text', 'workflow.nodes.rerankerNode.label'],
//   [formNode, 'workflow.nodes.formNode.text', 'workflow.nodes.formNode.label'],
//   [
//     documentExtractNode,
//     'workflow.nodes.documentExtractNode.text',
//     'workflow.nodes.documentExtractNode.label',
//   ],
//   [
//     documentSplitNode,
//     'workflow.nodes.documentSplitNode.text',
//     'workflow.nodes.documentSplitNode.label',
//   ],
//   [
//     imageUnderstandNode,
//     'workflow.nodes.imageUnderstandNode.text',
//     'workflow.nodes.imageUnderstandNode.label',
//   ],
//   [
//     videoUnderstandNode,
//     'workflow.nodes.videoUnderstandNode.text',
//     'workflow.nodes.videoUnderstandNode.label',
//   ],
//   [
//     variableAggregationNode,
//     'workflow.nodes.variableAggregationNode.text',
//     'workflow.nodes.variableAggregationNode.label',
//   ],
//   [
//     variableAssignNode,
//     'workflow.nodes.variableAssignNode.text',
//     'workflow.nodes.variableAssignNode.label',
//   ],
//   [mcpNode, 'workflow.nodes.mcpNode.text', 'workflow.nodes.mcpNode.label'],
//   [
//     imageGenerateNode,
//     'workflow.nodes.imageGenerateNode.text',
//     'workflow.nodes.imageGenerateNode.label',
//   ],
//   [
//     speechToTextNode,
//     'workflow.nodes.speechToTextNode.text',
//     'workflow.nodes.speechToTextNode.label',
//   ],
//   [
//     textToSpeechNode,
//     'workflow.nodes.textToSpeechNode.text',
//     'workflow.nodes.textToSpeechNode.label',
//   ],
//   [toolNode, 'workflow.nodes.toolNode.text', 'workflow.nodes.toolNode.label'],
//   [intentNode, 'workflow.nodes.intentNode.text', 'workflow.nodes.intentNode.label'],
//   [loopNode, 'workflow.nodes.loopNode.text', 'workflow.nodes.loopNode.label'],
//   [
//     imageToVideoNode,
//     'workflow.nodes.imageToVideoGenerate.text',
//     'workflow.nodes.imageToVideoGenerate.label',
//   ],
//   [loopBodyNode, 'workflow.nodes.loopBodyNode.text', 'workflow.nodes.loopBodyNode.label'],
//   [
//     loopContinueNode,
//     'workflow.nodes.loopContinueNode.text',
//     'workflow.nodes.loopContinueNode.label',
//   ],
//   [
//     textToVideoNode,
//     'workflow.nodes.textToVideoGenerate.text',
//     'workflow.nodes.textToVideoGenerate.label',
//   ],
//   [loopBreakNode, 'workflow.nodes.loopBreakNode.text', 'workflow.nodes.loopBreakNode.label'],
//   [toolLibNode, 'workflow.nodes.toolNode.text', 'workflow.nodes.toolNode.label'],
//   [applicationNode, 'workflow.nodes.applicationNode.label', 'workflow.nodes.applicationNode.label'],
// ]
// nodeLocaleBindings.forEach(([node, textKey, labelKey]) => bindNodeLocale(node, textKey, labelKey))

// defineLocaleGetter(
//   toolWorkflowLibNode,
//   'text',
//   'workflow.nodes.toolWorlflowNode.text',
//   '工作流工具',
// )
// defineLocaleGetter(
//   toolWorkflowLibNode,
//   'label',
//   'workflow.nodes.toolWorlflowNode.label',
//   '工作流工具',
// )
// bindLocale(
//   toolWorkflowLibNode,
//   'properties.stepName',
//   'workflow.nodes.toolWorlflowNode.label',
//   '工作流工具',
// )

// bindLocale(loopStartNode, 'properties.stepName', 'workflow.nodes.loopStartNode.label')
// bindFieldLabels(loopStartNode.properties.config.fields, [
//   'workflow.nodes.loopStartNode.loopIndex',
//   'workflow.nodes.loopStartNode.loopItem',
// ])
// bindLocale(
//   loopNode,
//   'properties.workflow.nodes.0.properties.stepName',
//   'workflow.nodes.startNode.label',
// )
// {
//   let overrideValue: string | undefined
//   Object.defineProperty(formNode.properties.node_data, 'form_content_format', {
//     configurable: true,
//     enumerable: true,
//     get: () =>
//       overrideValue ??
//       `${t('workflow.nodes.formNode.form_content_format1')}
// {{form}}
// ${t('workflow.nodes.formNode.form_content_format2')}`,
//     set: (value) => {
//       overrideValue = value
//     },
//   })
// }

// ;[
//   [dataSourceLocalNode.properties.config.fields, ['workflow.nodes.dataSourceLocalNode.fileList']],
//   [dataSourceWebNode.properties.config.fields, ['workflow.nodes.dataSourceWebNode.field_label']],
//   [
//     aiChatNode.properties.config.fields,
//     [
//       'workflow.nodes.aiChatNode.answer',
//       'workflow.nodes.aiChatNode.think',
//       'workflow.nodes.aiChatNode.historyMessage',
//     ],
//   ],
//   [
//     searchKnowledgeNode.properties.config.fields,
//     [
//       'workflow.nodes.searchKnowledgeNode.paragraph_list',
//       'workflow.nodes.searchKnowledgeNode.is_hit_handling_method_list',
//       'workflow.nodes.searchKnowledgeNode.result',
//       'workflow.nodes.searchKnowledgeNode.directly_return',
//     ],
//   ],
//   [
//     searchDocumentNode.properties.config.fields,
//     [
//       'workflow.nodes.searchDocumentNode.knowledgeList',
//       'workflow.nodes.searchDocumentNode.documentList',
//     ],
//   ],
//   [questionNode.properties.config.fields, ['workflow.nodes.questionNode.result']],
//   [variableSplittingNode.properties.config.fields, ['common.result']],
//   [parameterExtractionNode.properties.config.fields, ['common.result']],
//   [conditionNode.properties.config.fields, ['workflow.nodes.conditionNode.branch_name']],
//   [replyNode.properties.config.fields, ['common.content']],
//   [
//     rerankerNode.properties.config.fields,
//     [
//       'workflow.nodes.rerankerNode.result_list',
//       'workflow.nodes.rerankerNode.result',
//       'workflow.nodes.searchKnowledgeNode.is_hit_handling_method_list',
//     ],
//   ],
//   [formNode.properties.config.fields, ['workflow.nodes.formNode.form_data']],
//   [
//     documentExtractNode.properties.config.fields,
//     ['workflow.nodes.documentExtractNode.content', 'workflow.nodes.dataSourceWebNode.field_label'],
//   ],
//   [documentSplitNode.properties.config.fields, ['workflow.nodes.documentSplitNode.paragraphList']],
//   [imageUnderstandNode.properties.config.fields, ['workflow.nodes.imageUnderstandNode.answer']],
//   [videoUnderstandNode.properties.config.fields, ['workflow.nodes.videoUnderstandNode.answer']],
//   [mcpNode.properties.config.fields, ['common.result']],
//   [
//     imageGenerateNode.properties.config.fields,
//     ['workflow.nodes.imageGenerateNode.answer', 'common.fileUpload.image'],
//   ],
//   [speechToTextNode.properties.config.fields, ['common.result']],
//   [textToSpeechNode.properties.config.fields, ['common.result']],
//   [toolNode.properties.config.fields, ['common.result']],
//   [intentNode.properties.config.fields, ['common.classify', 'common.reason']],
//   [imageToVideoNode.properties.config.fields, ['common.fileUpload.video']],
//   [textToVideoNode.properties.config.fields, ['common.fileUpload.video']],
//   [toolLibNode.properties.config.fields, ['common.result']],
//   [applicationNode.properties.config.fields, ['common.result']],
// ].forEach(([fields, keys]) => bindFieldLabels(fields as Array<any>, keys as string[]))
// ;[
//   [
//     knowledgeMenuNodes,
//     [
//       'views.tool.dataSource.title',
//       'views.knowledge.title',
//       'workflow.nodes.classify.aiCapability',
//       'workflow.nodes.classify.businessLogic',
//       'workflow.nodes.classify.dataProcessing',
//       'common.other',
//     ],
//   ],
//   [
//     knowledgeLoopMenuNodes,
//     [
//       'views.tool.dataSource.title',
//       'views.knowledge.title',
//       'workflow.nodes.classify.aiCapability',
//       'workflow.nodes.classify.businessLogic',
//       'workflow.nodes.classify.dataProcessing',
//       'common.other',
//     ],
//   ],
//   [
//     toolLoopMenuNodes,
//     [
//       'views.tool.dataSource.title',
//       'views.knowledge.title',
//       'workflow.nodes.classify.aiCapability',
//       'workflow.nodes.classify.businessLogic',
//       'workflow.nodes.classify.dataProcessing',
//       'common.other',
//     ],
//   ],
//   [
//     menuNodes,
//     [
//       'workflow.nodes.classify.aiCapability',
//       'views.knowledge.title',
//       'workflow.nodes.classify.businessLogic',
//       'workflow.nodes.classify.dataProcessing',
//       'common.other',
//     ],
//   ],
//   [
//     applicationLoopMenuNodes,
//     [
//       'workflow.nodes.classify.aiCapability',
//       'views.knowledge.title',
//       'workflow.nodes.classify.businessLogic',
//       'workflow.nodes.classify.dataProcessing',
//       'common.other',
//     ],
//   ],
//   [
//     toolMenuNodes,
//     [
//       'workflow.nodes.classify.aiCapability',
//       'views.knowledge.title',
//       'workflow.nodes.classify.businessLogic',
//       'workflow.nodes.classify.dataProcessing',
//       'common.other',
//     ],
//   ],
// ].forEach(([nodes, keys]) => bindFieldLabels(nodes as Array<any>, keys as string[]))
// ;[
//   'workflow.compare.is_null',
//   'workflow.compare.is_not_null',
//   'workflow.compare.contain',
//   'workflow.compare.not_contain',
//   'workflow.compare.eq',
//   'workflow.compare.not_eq',
//   'workflow.compare.ge',
//   'workflow.compare.gt',
//   'workflow.compare.le',
//   'workflow.compare.lt',
//   'workflow.compare.len_eq',
//   'workflow.compare.len_ge',
//   'workflow.compare.len_gt',
//   'workflow.compare.len_le',
//   'workflow.compare.len_lt',
//   'workflow.compare.is_true',
//   'workflow.compare.is_not_true',
// ].forEach((key, index) => defineLocaleGetter(compareList[index], 'label', key))
// defineLocaleGetter(compareList[19], 'label', 'workflow.compare.regex')
// defineLocaleGetter(compareList[20], 'label', 'workflow.compare.wildcard')
