export default {
  title: '知識庫',
  createDataset: '建立知識庫',
  general: '通用型',
  web: 'Web 站點',
  lark: '飛書',
  yuque: '語雀',
  relatedApplications: '關聯應用',
  document_count: '文檔數',
  relatedApp_count: '關聯應用',
  searchBar: {
    placeholder: '按名稱搜尋'
  },
  setting: {
    vectorization: '向量化',
    sync: '同步'
  },
  tip: {
    professionalMessage: '社群版最多支援 50 個知識庫，如需擁有更多知識庫，請升級為專業版。',
    syncSuccess: '同步任務發送成功',
    updateModeMessage: '修改知識庫向量模型後，需要對知識庫向量化，是否繼續保存？'
  },
  delete: {
    confirmTitle: '是否刪除知識庫：',
    confirmMessage1: '此知識庫關聯',
    confirmMessage2: '個應用，刪除後無法恢復，請謹慎操作。'
  },
  datasetForm: {
    title: {
      info: '基本資訊'
    },
    form: {
      datasetName: {
        label: '知識庫名稱',
        placeholder: '請輸入知識庫名稱',
        requiredMessage: '請輸入知識庫名稱'
      },
      datasetDescription: {
        label: '知識庫描述',
        placeholder:
          '描述知識庫的內容，詳盡的描述將幫助AI能深入理解該知識庫的內容，能更準確的檢索到內容，提高該知識庫的命中率。',
        requiredMessage: '請輸入知識庫描述'
      },
      EmbeddingModel: {
        label: '向量模型',
        placeholder: '請選擇向量模型',
        requiredMessage: '請輸入Embedding模型'
      },
      datasetType: {
        label: '知識庫類型',
        generalInfo: '透過上傳檔案或手動錄入建置知識庫',
        webInfo: '透過網站連結建立知識庫',
        larkInfo: '透過飛書文檔建構知識庫',
        yuqueInfo: '透過語雀文件建構知識庫'
      },
      source_url: {
        label: 'Web 根位址',
        placeholder: '請輸入 Web 根位址',
        requiredMessage: '請輸入 Web 根位址'
      },
      user_id: {
        requiredMessage: '請輸入 User ID'
      },
      token: {
        requiredMessage: '請輸入 Token'
      },
      selector: {
        label: '選擇器',
        placeholder: '預設為 body，可輸入 .classname/#idname/tagname'
      }
    }
  },
  ResultSuccess: {
    title: '知識庫建立成功',
    paragraph: '段落',
    paragraph_count: '個段落',
    documentList: '文件列表',
    loading: '正在導入',
    buttons: {
      toDataset: '返回知識庫列表',
      toDocument: '前往文件'
    }
  },
  syncWeb: {
    title: '同步知識庫',
    syncMethod: '同步方式',
    replace: '替換同步',
    replaceText: '重新獲取 Web 站點文件，覆蓋替換本地知識庫中的文件',
    complete: '完整同步',
    completeText: '先刪除本地知識庫所有文件，重新獲取 Web 站點文件',
    tip: '注意：所有同步都會刪除現有數據並重新獲取新數據，請謹慎操作。'
  }
}
