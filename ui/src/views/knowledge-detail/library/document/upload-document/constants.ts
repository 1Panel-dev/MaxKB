import { computed, reactive } from 'vue'
import { t } from '@/locales'
/** 文档上传入口及文件选择范围，仅用于本页面。 */
export const DOCUMENT_UPLOAD_OPTIONS = reactive({
  text: {
    title: computed(() => t('knowledge.document.upload.textTitle')),
    accept: '.txt,.md,.markdown,.pdf,.docx,.html,.htm,.xls,.xlsx,.csv,.zip',
    formats: ['TXT', 'Markdown', 'PDF', 'DOCX', 'HTML', 'XLS', 'XLSX', 'CSV', 'ZIP'],
  },
  table: {
    title: computed(() => t('knowledge.document.upload.tableTitle')),
    accept: '.xls,.xlsx,.csv',
    formats: ['XLS', 'XLSX', 'CSV'],
  },
  qa: {
    title: computed(() => t('knowledge.document.upload.qaTitle')),
    accept: '.xls,.xlsx,.csv,.zip',
    formats: ['XLS', 'XLSX', 'CSV', 'ZIP'],
  },
} as const)

export type DocumentUploadMode = keyof typeof DOCUMENT_UPLOAD_OPTIONS
