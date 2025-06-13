const DocumentRouter = {
  path: '/knowledge/system/:id/',
  name: 'KnowledgeDetailSharedSystem',
  meta: { title: 'common.fileUpload.document', activeMenu: '/knowledge', breadcrumb: true },
  component: () => import('@/layout/layout-template/MainLayout.vue'),
  hidden: true,
  children: [
    {
      path: 'documentShared',
      name: 'DocumentSharedSystem',
      meta: {
        icon: 'app-document',
        iconActive: 'app-document-active',
        title: 'common.fileUpload.document',
        active: 'documentShared',
        parentPath: '/knowledge/system/:id/',
        parentName: 'KnowledgeDetailSharedSystem',
      },
      component: () => import('@/views/document-shared-system/index.vue'),
    },
    {
      path: 'problemShared',
      name: 'ProblemSharedSystem',
      meta: {
        icon: 'app-problems',
        iconActive: 'QuestionFilled',
        title: 'views.problem.title',
        active: 'problemShared',
        parentPath: '/knowledge/system/:id/',
        parentName: 'KnowledgeDetailSharedSystem',
      },
      component: () => import('@/views/problem-shared-system/index.vue'),
    },
    {
      path: 'hit-test-shared',
      name: 'KnowledgeHitTestSharedSystem',
      meta: {
        icon: 'app-hit-test',
        title: 'views.application.hitTest.title',
        active: 'hit-test-shared',
        parentPath: '/knowledge/system/:id/',
        parentName: 'KnowledgeDetailSharedSystem',
      },
      component: () => import('@/views/hit-test-shared-system/index.vue'),
    },
    {
      path: 'settingShared',
      name: 'settingSharedSystem',
      meta: {
        icon: 'app-setting',
        iconActive: 'app-setting-active',
        title: 'common.setting',
        active: 'settingShared',
        parentPath: '/knowledge/system/:id/',
        parentName: 'KnowledgeDetailSharedSystem',
      },
      component: () => import('@/views/knowledge-shared-system/KnowledgeSetting.vue'),
    }
  ],
}

export default DocumentRouter
