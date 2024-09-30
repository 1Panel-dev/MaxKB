export default {
  applicationList: {
    title: '应用',
    searchBar: {
      placeholder: '按名称搜索'
    },
    card: {
      createApplication: '创建应用',
      overview: '概览',
      demo: '演示',
      setting: '设置',
      delete: {
        tooltip: '删除',
        confirmTitle: '是否删除应用：',
        confirmMessage: '删除后该应用将不再提供服务，请谨慎操作。',
        confirmButton: '删除',
        cancelButton: '取消',
        successMessage: '删除成功'
      }
    },
    tooltips: {
      demo: '演示',
      setting: '设置',
      delete: '删除'
    }
  },
  applicationForm: {
    title: {
      create: '创建应用',
      edit: '设置',
      info: '应用信息',
      copy: '复制应用'
    },
    form: {
      appName: {
        label: '应用名称',
        placeholder: '请输入应用名称',
        requiredMessage: '请输入应用名称'
      },
      appDescription: {
        label: '应用描述',
        placeholder: '描述该应用的应用场景及用途，如：XXX 小助手回答用户提出的 XXX 产品使用问题'
      },
      aiModel: {
        label: 'AI 模型',
        placeholder: '请选择 AI 模型',
        unavailable: '（不可用）'
      },
      prompt: {
        label: '提示词',
        placeholder: '请输入提示词',
        tooltip:
          '通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头。可以使用变量：{data} 是携带知识库中已知信息；{question} 是用户提出的问题。'
      },
      multipleRoundsDialogue: '多轮对话',
      relatedKnowledgeBase: '关联知识库',
      relatedKnowledgeBaseWhere: '关联知识库展示在这里',
      prologue: '开场白',
      problemOptimization: {
        label: '问题优化',
        tooltip: '根据历史聊天优化完善当前问题，更利于匹配知识点。'
      },
      addModel: '添加模型',
      paramSetting: '参数设置',
      add: '添加',
      apptest: '调试预览'
    },
    buttons: {
      confirm: '确认',
      cancel: '取消',
      create: '创建',
      createSuccess: '创建成功',
      save: '保存',
      saveSuccess: '保存成功',
      copy: '复制',
      copySuccess: '复制成功'
    },
    dialogues: {
      addDataset: '添加关联知识库',
      removeDataset: '移除知识库',
      paramSettings: '参数设置',
      refresh: '刷新',
      selectSearchMode: '检索模式',
      vectorSearch: '向量检索',
      vectorSearchTooltip: '向量检索是一种基于向量相似度的检索方式，适用于知识库中的大数据量场景。',
      fullTextSearch: '全文检索',
      fullTextSearchTooltip:
        '全文检索是一种基于文本相似度的检索方式，适用于知识库中的小数据量场景。',
      hybridSearch: '混合检索',
      hybridSearchTooltip:
        '混合检索是一种基于向量和文本相似度的检索方式，适用于知识库中的中等数据量场景。',
      similarityThreshold: '相似度高于',
      topReferences: '引用分段数 TOP',
      maxCharacters: '最多引用字符数',
      noReferencesAction: '无引用知识库分段时',
      continueQuestioning: '继续向 AI 模型提问',
      provideAnswer: '指定回答内容',
      prompt: '提示词',
      promptPlaceholder: '请输入提示词',
      concent: '内容',
      concentPlaceholder: '请输入内容',
      designated_answer:
        '你好，我是 XXX 小助手，我的知识库只包含了 XXX 产品相关知识，请重新描述您的问题。'
    }
  },
  prompt: {
    defaultPrompt: `已知信息：{data}
用户问题：{question}
回答要求：
 - 请使用中文回答用户问题`,
    defaultPrologue:
      '您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务'
  }
}
