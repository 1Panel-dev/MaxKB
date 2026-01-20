export default {
  title: '知識庫',
  relatedApplications: '關聯智能體',
  document_count: '文檔數',
  relatedApp_count: '關聯智能體',
  setting: {
    vectorization: '向量化',
    sync: '同步',
  },
  tip: {
    professionalMessage: '社群版最多支援 50 個知識庫，如需擁有更多知識庫，請升級為專業版。',
    syncSuccess: '同步任務發送成功',
    updateModeMessage: '修改知識庫向量模型後，需要對知識庫向量化，是否繼續保存？',
  },
  delete: {
    confirmTitle: '是否刪除知識庫：',
    confirmMessage1: '此知識庫關聯',
    confirmMessage2: '個智能體，刪除後無法恢復，請謹慎操作。',
    resourceCountMessage: '此知識庫關聯 {count} 個資源，刪除後無法使用，請謹慎操作。',
  },
  knowledgeType: {
    label: '知識庫類型',
    generalKnowledge: '通用知識庫',
    webKnowledge: 'Web 知識庫',
    larkKnowledge: '飛書知識庫',
    workflowKnowledge: '工作流知識庫',
    yuqueKnowledge: '語雀知識庫',
    generalInfo: '上傳本地檔案',
    webInfo: '同步 Web 網站文字資料',
    larkInfo: '通過飛書文檔構建知識庫',
    yuqueInfo: '通過語雀文檔構建知識庫',
    createWorkflowKnowledge: '建立工作流知識庫',
    workflowInfo: '通過自定義工作流管道構建知識庫',
  },
  form: {
    knowledgeName: {
      label: '知識庫名稱',
      placeholder: '請輸入知識庫名稱',
      requiredMessage: '請輸入知識庫名稱',
    },
    knowledgeDescription: {
      label: '知識庫描述',
      placeholder:
        '描述知識庫的內容，詳盡的描述將幫助AI能深入理解該知識庫的內容，能更準確的檢索到內容，提高該知識庫的命中率。',
      requiredMessage: '請輸入知識庫描述',
    },
    EmbeddingModel: {
      label: '向量模型',
      placeholder: '請選擇向量模型',
      requiredMessage: '請選擇向量模型',
    },

    source_url: {
      label: 'Web 根位址',
      placeholder: '請輸入 Web 根位址',
      requiredMessage: '請輸入 Web 根位址',
    },
    selector: {
      label: '選擇器',
      placeholder: '預設為 body，可輸入 .classname/#idname/tagname',
    },
    file_count_limit: {
      label: '每次上傳最多文件數',
    },
    file_size_limit: {
      label: '上傳的每個文件最大(MB)',
      placeholder: '建议根据服务器配置调整，否則會造成服務宕机',
    },
    appTemplate: {
      blank: {
        title: '空白創建',
      },
      basic: {
        title: '基礎模板',
        description: '支持本地文件、飛書文檔、Web 站點數據源的基礎工作流模板',
      },
    },
  },

  ResultSuccess: {
    title: '知識庫建立成功',
    paragraph: '段落',
    paragraph_count: '個段落',
    documentList: '文件列表',
    loading: '正在導入',
    buttons: {
      toKnowledge: '返回知識庫列表',
      toDocument: '前往文件',
    },
  },
  syncWeb: {
    title: '同步知識庫',
    syncMethod: '同步方式',
    replace: '替換同步',
    replaceText: '重新獲取 Web 站點文件，覆蓋替換本地知識庫中的文件',
    complete: '完整同步',
    completeText: '先刪除本地知識庫所有文件，重新獲取 Web 站點文件',
    tip: '注意：所有同步都會刪除現有數據並重新獲取新數據，請謹慎操作。',
  },
}
