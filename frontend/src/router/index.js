import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '../views/ProjectsView.vue'
import DocumentsView from '../views/DocumentsView.vue'
import DocumentDetailView from '../views/DocumentDetailView.vue'
import UploadDetailView from '../views/UploadDetailView.vue'

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
    },
    {
      path: '/documents/:documentId/upload/:uploadId',
      name: 'upload-detail',
      component: UploadDetailView
    }
  ]
})

export default router

