export default {
  uploadDocument: '上传文档',
  importDocument: '导入文档',
  syncDocument: '同步文档',
  selected: '已选',
  items: '项',
  searchBar: {
    placeholder: '按 文档名称 搜索'
  },
  setting: {
    migration: '迁移',
    cancelGenerateQuestion: '取消生成问题',
    cancelVectorization: '取消向量化',
    cancelGenerate: '取消生成',
    export: '导出'
  },
  tip: {
    saveMessage: '当前的更改尚未保存，确认退出吗?',
    cancelSuccess: '批量取消成功',
    sendMessage: '发送成功',
    vectorizationSuccess: '批量向量化成功',
    nameMessage: '文件名称不能为空！',
    importMessage: '导入成功',
    migrationSuccess: '迁移成功'
  },
  upload: {
    selectFile: '选择文件',
    selectFiles: '选择文件夹',
    uploadMessage: '拖拽文件至此上传或',
    formats: '支持格式：',
    requiredMessage: '请上传文件',
    errorMessage1: '文件大小超过 100MB',
    errorMessage2: '文件格式不支持',
    errorMessage3: '文件不能为空',
    errorMessage4: '每次最多上传50个文件',
    template: '模版',
    download: '下载'
  },

  fileType: {
    txt: {
      label: '文本文件',
      tip1: '1、文件上传前，建议规范文件的分段标识',
      tip2: '2、每次最多上传 50 个文件，每个文件不超过 100MB'
    },
    table: {
      label: '表格',
      tip1: '1、点击下载对应模版并完善信息：',
      tip2: '2、第一行必须是列标题，且列标题必须是有意义的术语，表中每条记录将作为一个分段',
      tip3: '3、上传的表格文件中每个 sheet 会作为一个文档，sheet名称为文档名称',
      tip4: '4、每次最多上传 50 个文件，每个文件不超过 100MB'
    },
    QA: {
      label: 'QA 问答对',
      tip1: '1、点击下载对应模版并完善信息',
      tip2: '2、上传的表格文件中每个 sheet 会作为一个文档，sheet名称为文档名称',
      tip3: '3、每次最多上传 50 个文件，每个文件不超过 100MB'
    },
    lark: {}
  },
  setRules: {
    title: {
      setting: '设置分段规则',
      preview: '分段预览'
    },
    intelligent: {
      label: '智能分段（推荐)',
      text: '不了解如何设置分段规则推荐使用智能分段'
    },
    advanced: {
      label: '高级分段',
      text: '用户可根据文档规范自行设置分段标识符、分段长度以及清洗规则'
    },
    patterns: {
      label: '分段标识',
      tooltip: '按照所选符号先后顺序做递归分割，分割结果超出分段长度将截取至分段长度。',
      placeholder: '请选择'
    },
    limit: {
      label: '分段长度'
    },
    with_filter: {
      label: '自动清洗',
      text: '去掉重复多余符号空格、空行、制表符'
    },
    checkedConnect: {
      label: '导入时添加分段标题为关联问题（适用于标题为问题的问答对）'
    }
  },
  buttons: {
    prev: '上一步',
    next: '下一步',
    import: '开始导入',
    preview: '生成预览'
  },
  table: {
    name: '文件名称',
    char_length: '字符数',
    paragraph: '分段',
    all: '全部',
    updateTime: '更新时间'
  },
  fileStatus: {
    label: '文件状态',
    SUCCESS: '成功',
    FAILURE: '失败',
    EMBEDDING: '索引中',
    PENDING: '排队中',
    GENERATE: '生成中',
    SYNC: '同步中',
    REVOKE: '取消中',
    finish: '完成'
  },
  enableStatus: {
    label: '启用状态',
    enable: '开启',
    close: '关闭'
  },
  sync: {
    label: '同步',
    confirmTitle: '确认同步文档?',
    confirmMessage1: '同步将删除已有数据重新获取新数据，请谨慎操作。',
    confirmMessage2: '无法同步，请先去设置文档 URL地址',
    successMessage: '同步文档成功'
  },
  delete: {
    confirmTitle1: '是否批量删除',
    confirmTitle2: '个文档?',
    confirmMessage: '所选文档中的分段会跟随删除，请谨慎操作。',
    successMessage: '批量删除成功',
    confirmTitle3: '是否删除文档：',
    confirmMessage1: '此文档下的',
    confirmMessage2: '个分段都会被删除，请谨慎操作。'
  },
  form: {
    source_url: {
      label: '文档地址',
      placeholder: '请输入文档地址，一行一个，地址不正确文档会导入失败。',
      requiredMessage: '请输入文档地址'
    },
    selector: {
      label: '选择器',
      placeholder: '默认为 body，可输入 .classname/#idname/tagname'
    },
    hit_handling_method: {
      label: '命中处理方式',
      tooltip: '用户提问时，命中文档下的分段时按照设置的方式进行处理。'
    },
    similarity: {
      label: '相似度高于',
      placeholder: '直接返回分段内容',
      requiredMessage: '请输入相似度'
    }
  },
  hitHandlingMethod: {
    optimization: '模型优化',
    directly_return: '直接回答'
  },
  generateQuestion: {
    title: '生成问题',
    successMessage: '生成问题成功',
    tip1: '提示词中的 {data} 为分段内容的占位符，执行时替换为分段内容发送给 AI 模型；',
    tip2: 'AI 模型根据分段内容生成相关问题，请将生成的问题放至',
    tip3: '标签中，系统会自动关联标签中的问题；',
    tip4: '生成效果依赖于所选模型和提示词，用户可自行调整至最佳效果。',
    prompt1: `内容：{data}\n\n请总结上面的内容，并根据内容总结生成 5 个问题。\n回答要求：\n- 请只输出问题；\n- 请将每个问题放置`,
    prompt2: `标签中。`
  },
  feishu: {
    selectDocument: '选择文档',
    tip1: '支持文档和表格类型，包含TXT、Markdown、PDF、DOCX、HTML、XLS、XLSX、CSV、ZIP格式；',
    tip2: '系统不存储原始文档，导入文档前，建议规范文档的分段标识。',
    allCheck: '全选',
    errorMessage1: '请选择文档'
  }
}
