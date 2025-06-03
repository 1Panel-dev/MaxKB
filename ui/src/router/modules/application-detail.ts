const ApplicationDetailRouter = {
  path: '/application/:id/:type',
  name: 'ApplicationDetail',
  meta: { title: 'views.applicationOverview.title', activeMenu: '/application', breadcrumb: true },
  component: () => import('@/layout/layout-template/MainLayout.vue'),
  hidden: true,
  children: [
    {
      path: 'overview',
      name: 'AppOverview',
      meta: {
        icon: 'app-all-menu',
        iconActive: 'app-all-menu-active',
        title: 'views.applicationOverview.title',
        active: 'overview',
        parentPath: '/application/:id/:type',
        parentName: 'ApplicationDetail',
      },
      component: () => import('@/views/application-overview/index.vue'),
    },
    {
      path: 'setting',
      name: 'AppSetting',
      meta: {
        icon: 'app-setting',
        iconActive: 'app-setting-active',
        title: 'common.setting',
        active: 'setting',
        parentPath: '/application/:id/:type',
        parentName: 'ApplicationDetail',
      },
      component: () => import('@/views/application/ApplicationSetting.vue'),
    },
    {
      path: 'access',
      name: 'AppAccess',
      meta: {
        icon: 'app-access',
        iconActive: 'app-access-active',
        title: 'views.application.applicationAccess.title',
        active: 'access',
        parentPath: '/application/:id/:type',
        parentName: 'ApplicationDetail',
        // permission: new ComplexPermission([], ['x-pack'], 'OR'),
      },
      component: () => import('@/views/application/ApplicationAccess.vue'),
    },
    {
      path: 'hit-test',
      name: 'AppHitTest',
      meta: {
        icon: 'app-hit-test',
        title: 'views.application.hitTest.title',
        active: 'hit-test',
        parentPath: '/application/:id/:type',
        parentName: 'ApplicationDetail',
      },
      component: () => import('@/views/hit-test/index.vue'),
    },
    // {
    //   path: 'log',
    //   name: 'Log',
    //   meta: {
    //     icon: 'app-document',
    //     iconActive: 'app-document-active',
    //     title: 'views.log.title',
    //     active: 'log',
    //     parentPath: '/application/:id/:type',
    //     parentName: 'ApplicationDetail'
    //   },
    //   component: () => import('@/views/log/index.vue')
    // }
  ],
}

export default ApplicationDetailRouter
