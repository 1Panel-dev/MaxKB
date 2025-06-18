const DocumentRouter = {
  path: '/knowledge/resource/:id/',
  name: 'KnowledgeDetailResourceManagement',
  meta: { title: 'common.fileUpload.document', activeMenu: '/knowledge', breadcrumb: true },
  component: () => import('@/layout/layout-template/MainLayout.vue'),
  hidden: true,
  children: [
    {
      path: 'documentResource',
      name: 'DocumentResourceManagement',
      meta: {
        icon: 'app-document',
        iconActive: 'app-document-active',
        title: 'common.fileUpload.document',
        active: 'documentResource',
        parentPath: '/knowledge/resource/:id/',
        parentName: 'KnowledgeDetailResourceManagement',
      },
      component: () => import('@/views/resource-management/document/index.vue'),
    },
    {
      path: 'problemResource',
      name: 'ProblemResourceManagement',
      meta: {
        icon: 'app-problems',
        iconActive: 'QuestionFilled',
        title: 'views.problem.title',
        active: 'problemResource',
        parentPath: '/knowledge/resource/:id/',
        parentName: 'KnowledgeDetailResourceManagement',
      },
      component: () => import('@/views/resource-management/problem/index.vue'),
    },
    {
      path: 'hit-test-Resource',
      name: 'KnowledgeHitTestResourceManagement',
      meta: {
        icon: 'app-hit-test',
        title: 'views.application.hitTest.title',
        active: 'hit-test-Resource',
        parentPath: '/knowledge/resource/:id/',
        parentName: 'KnowledgeDetailResourceManagement',
      },
      component: () => import('@/views/resource-management/hit-test/index.vue'),
    },
    {
      path: 'settingResource',
      name: 'settingResourceManagement',
      meta: {
        icon: 'app-setting',
        iconActive: 'app-setting-active',
        title: 'common.setting',
        active: 'settingResource',
        parentPath: '/knowledge/resource/:id/',
        parentName: 'KnowledgeDetailResourceManagement',
      },
      component: () => import('@/views/resource-management/knowledge/KnowledgeSetting.vue'),
    }
  ],
}

export default DocumentRouter
