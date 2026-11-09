import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import AppLayout from "@/layouts/AppLayout.vue";
import DashboardView from "@/pages/DashboardView.vue";
import CoverLetterWorkspace from "@/pages/CoverLetterWorkspace.vue";
import JobAnalyzerView from "@/pages/JobAnalyzerView.vue";
import ResumeMatchingView from "@/pages/ResumeMatchingView.vue";
import DraftsView from "@/pages/DraftsView.vue";
import TemplatesView from "@/pages/TemplatesView.vue";
import SettingsView from "@/pages/SettingsView.vue";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    component: AppLayout,
    children: [
      {
        path: "",
        name: "Dashboard",
        component: DashboardView
      },
      {
        path: "workspace",
        name: "Cover Letter Workspace",
        component: CoverLetterWorkspace
      },
      {
        path: "analyzer",
        name: "Job Description Analyzer",
        component: JobAnalyzerView
      },
      {
        path: "matching",
        name: "Resume Matching",
        component: ResumeMatchingView
      },
      {
        path: "drafts",
        name: "My Drafts",
        component: DraftsView
      },
      {
        path: "templates",
        name: "Document Templates",
        component: TemplatesView
      },
      {
        path: "settings",
        name: "Settings & System Health",
        component: SettingsView
      }
    ]
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/"
  }
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

export default router;
