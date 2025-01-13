export default {
  title: '模型设置',
  provider: '供应商',
  providerPlaceholder: '选择供应商',
  addModel: '添加模型',
  searchBar: {
    placeholder: '按名称搜索'
  },
  delete: {},
  setting: {},
  tip: {
    createSuccessMessage: '创建模型成功',
    createErrorMessage: '基础信息有填写错误',
    errorMessage:'变量已存在: '
  },
  model: {
    allModel: '全部模型',
    publicModel: '公有模型',
    privateModel: '私有模型',
    LLM: '大语言模型',
    EMBEDDING: '向量模型',
    RERANKER: '重排模型',
    STT: '语音识别',
    TTS: '语音合成',
    IMAGE: '图片理解',
    TTI: '图片生成'
  },
  templateForm: {
    title: {
      baseInfo: '基础信息',
      advancedInfo: '高级设置'
    },
    form: {
      templateName: {
        label: '模型名称',
        placeholder: '请给基础模型设置一个名称',
        tooltip: 'MaxKB 中自定义的模型名称',
        requiredMessage: '模型名称不能为空'
      },
      permissionType: {
        label: '权限',
        placeholder: '请给基础模型设置一个名称',
        tooltip: 'MaxKB 中自定义的模型名称',
        requiredMessage: '权限不能为空'
      },
      model_type: {
        label: '模型类型',
        placeholder: '请选择模型类型',
        tooltip1: '大语言模型：在应用中与AI对话的推理模型。',
        tooltip2: '向量模型：在知识库中对文档内容进行向量化的模型。',
        tooltip3: '语音识别：在应用中开启语音识别后用于语音转文字的模型。',
        tooltip4: '语音合成：在应用中开启语音播放后用于文字转语音的模型。',
        tooltip5: '重排模型：在高级编排应用中使用多路召回时，对候选分段进行重新排序的模型。',
        tooltip6: '图片理解：在高级编排应用中用于图片理解的视觉模型。',
        tooltip7: '图片生成：在高级编排应用中用于图片生成的视觉模型。',
        requiredMessage: '模型类型不能为空',
        warningMessage: '模型类型不能为空'
      }
    }
  }
}
