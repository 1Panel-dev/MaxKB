/** 文档上传入口及文件选择范围，仅用于本页面。 */
export const DOCUMENT_UPLOAD_OPTIONS = {
  text: {
    titleKey: 'knowledge.document.upload.textTitle',
    accept: '.txt,.md,.markdown,.pdf,.docx,.html,.htm,.xls,.xlsx,.csv,.zip',
    formats: ['TXT', 'Markdown', 'PDF', 'DOCX', 'HTML', 'XLS', 'XLSX', 'CSV', 'ZIP'],
  },
  table: {
    titleKey: 'knowledge.document.upload.tableTitle',
    accept: '.xls,.xlsx,.csv',
    formats: ['XLS', 'XLSX', 'CSV'],
  },
  qa: {
    titleKey: 'knowledge.document.upload.qaTitle',
    accept: '.xls,.xlsx,.csv,.zip',
    formats: ['XLS', 'XLSX', 'CSV', 'ZIP'],
  },
} as const

export type DocumentUploadMode = keyof typeof DOCUMENT_UPLOAD_OPTIONS
