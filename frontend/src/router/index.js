import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '../views/ProjectsView.vue'
import DocumentsView from '../views/DocumentsView.vue'
import DocumentDetailView from '../views/DocumentDetailView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/projects'
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectsView
    },
    {
      path: '/projects/:projectId/documents',
      name: 'documents',
      component: DocumentsView
    },
    {
      path: '/documents/:documentId',
      name: 'document-detail',
      component: DocumentDetailView
    }
  ]
})

export default router

