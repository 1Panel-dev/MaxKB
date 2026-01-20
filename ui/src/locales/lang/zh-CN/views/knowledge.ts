export default {
  title: '知识库',
  document_count: '文档数',
  relatedApp_count: '关联智能体',
  setting: {
    vectorization: '向量化',
    sync: '同步',
  },

  tip: {
    professionalMessage: '社区版最多支持 50 个知识库，如需拥有更多知识库，请升级为专业版。',
    syncSuccess: '同步任务发送成功',
    updateModeMessage: '修改知识库向量模型后，需要对知识库向量化，是否继续保存？',
  },
  delete: {
    confirmTitle: '是否删除知识库：',
    confirmMessage1: '此知识库关联',
    confirmMessage2: '个智能体，删除后无法恢复，请谨慎操作。',
    resourceCountMessage: '此知识库关联 {count} 个资源，删除后无法使用，请谨慎操作。',
  },
  knowledgeType: {
    label: '知识库类型',
    generalKnowledge: '通用知识库',
    webKnowledge: 'Web 知识库',
    larkKnowledge: '飞书知识库',
    workflowKnowledge: '工作流知识库',
    yuqueKnowledge: '语雀知识库',
    generalInfo: '通过上传文件或手动录入构建知识库',
    webInfo: '通过网站链接构建知识库',
    larkInfo: '通过飞书文档构建知识库',
    yuqueInfo: '通过语雀文档构建知识库',
    createGeneralKnowledge: '创建通用知识库',
    createWebKnowledge: '创建 Web 知识库',
    createLarkKnowledge: '创建飞书知识库',
    createYuqueKnowledge: '创建语雀知识库',
    createWorkflowKnowledge: '创建工作流知识库',
    workflowInfo: '通过自定义工作流方式构建知识库',
  },
  form: {
    knowledgeName: {
      label: '知识库名称',
      placeholder: '请输入知识库名称',
      requiredMessage: '请输入知识库名称',
    },
    knowledgeDescription: {
      label: '知识库描述',
      placeholder:
        '描述知识库的内容，详尽的描述将帮助AI能深入理解该知识库的内容，能更准确的检索到内容，提高该知识库的命中率。',
      requiredMessage: '请输入知识库描述',
    },
    EmbeddingModel: {
      label: '向量模型',
      placeholder: '请选择向量模型',
      requiredMessage: '请选择向量模型',
    },

    source_url: {
      label: 'Web 根地址',
      placeholder: '请输入 Web 根地址',
      requiredMessage: ' 请输入 Web 根地址',
    },
    user_id: {
      requiredMessage: '请输入 User ID',
    },
    token: {
      requiredMessage: '请输入 Token',
    },
    selector: {
      label: '选择器',
      placeholder: '默认为 body，可输入 .classname/#idname/tagname',
    },
    file_count_limit: {
      label: '每次上传最多文件数',
    },
    file_size_limit: {
      label: '上传的每个文档最大(MB)',
      placeholder: '建议根据服务器配置调整，否则可能会造成服务宕机',
    },
    appTemplate: {
      blank: {
        title: '空白创建',
      },
      basic: {
        title: '基础模板',
        description: '支持本地文件、飞书文档、Web 站点数据源的基础工作流模板',
      },
    },
  },

  ResultSuccess: {
    title: '知识库创建成功',
    paragraph: '分段',
    paragraph_count: '个分段',
    documentList: '文档列表',
    loading: '导入中',
    buttons: {
      toKnowledge: '返回知识库列表',
      toDocument: '前往文档',
    },
  },
  syncWeb: {
    title: '同步知识库',
    syncMethod: '同步方式',
    replace: '替换同步',
    replaceText: '重新获取 Web 站点文档，覆盖替换本地知识库中的文档',
    complete: '整体同步',
    completeText: '先删除本地知识库所有文档，重新获取 Web 站点文档',
    tip: '注意：所有同步都会删除已有数据重新获取新数据，请谨慎操作。',
  },
}
