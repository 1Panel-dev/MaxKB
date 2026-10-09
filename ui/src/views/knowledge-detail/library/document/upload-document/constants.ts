/** 文档上传入口及文件选择范围，仅用于本页面。 */
export const DOCUMENT_UPLOAD_OPTIONS = {
  text: {
    label: '文本文件',
    title: '上传文本文件',
    icon: 'txt',
    accept: '.txt,.md,.markdown,.pdf,.docx,.html,.htm,.xls,.xlsx,.csv,.zip',
    formats: 'TXT、Markdown、PDF、DOCX、HTML、XLS、XLSX、CSV、ZIP',
  },
  table: { label: '表格', title: '上传表格', icon: 'xlsx', accept: '.xls,.xlsx,.csv', formats: 'XLS、XLSX、CSV' },
  qa: { label: 'QA 问答对', title: '上传 QA 问答对', icon: 'qa', accept: '.xls,.xlsx,.csv,.zip', formats: 'XLS、XLSX、CSV、ZIP' },
} as const

export type DocumentUploadMode = keyof typeof DOCUMENT_UPLOAD_OPTIONS
