import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "../stores/auth";
import CheckInView from "../views/CheckInView.vue";
import ClassesView from "../views/ClassesView.vue";
import DashboardView from "../views/DashboardView.vue";
import HomeView from "../views/HomeView.vue";
import ImportView from "../views/ImportView.vue";
import LeadsView from "../views/LeadsView.vue";
import PTView from "../views/PTView.vue";
import ProgressView from "../views/ProgressView.vue";
import StaffView from "../views/StaffView.vue";
import SubscriptionsView from "../views/SubscriptionsView.vue";
import LoginView from "../views/LoginView.vue";
import MemberDetailView from "../views/MemberDetailView.vue";
import MemberPortalView from "../views/MemberPortalView.vue";
import MembersView from "../views/MembersView.vue";
import NotificationsView from "../views/NotificationsView.vue";
import WorkoutsView from "../views/WorkoutsView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView, meta: { public: true } },
    { path: "/", name: "home", component: HomeView },
    { path: "/dashboard", name: "dashboard", component: DashboardView, meta: { owner: true } },
    { path: "/members", name: "members", component: MembersView, meta: { staff: true } },
    { path: "/members/:id", name: "member-detail", component: MemberDetailView, meta: { staff: true } },
    { path: "/check-in", name: "check-in", component: CheckInView, meta: { staff: true } },
    { path: "/classes", name: "classes", component: ClassesView, meta: { staff: true } },
    { path: "/pt", name: "pt", component: PTView, meta: { staff: true } },
    { path: "/portal", name: "portal", component: MemberPortalView, meta: { member: true } },
    { path: "/workouts", name: "workouts", component: WorkoutsView, meta: { staff: true } },
    { path: "/progress", name: "progress", component: ProgressView, meta: { staff: true } },
    { path: "/leads", name: "leads", component: LeadsView, meta: { staff: true } },
    { path: "/import", name: "import", component: ImportView, meta: { frontDesk: true } },
    { path: "/subscriptions", name: "subscriptions", component: SubscriptionsView, meta: { frontDesk: true } },
    { path: "/staff", name: "staff", component: StaffView, meta: { frontDesk: true } },
    { path: "/notifications", name: "notifications", component: NotificationsView },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.bootstrapped) {
    await auth.bootstrap();
  }
  if (to.meta.public) {
    if (auth.isAuthenticated && to.name === "login") return { name: "home" };
    return true;
  }
  if (!auth.isAuthenticated) {
    return { name: "login", query: { next: to.fullPath } };
  }
  if (to.meta.staff && !auth.canSeeStaffNav()) {
    return { name: "home" };
  }
  if (to.meta.frontDesk && !auth.canSeeFrontDeskNav()) {
    return { name: "home" };
  }
  if (to.meta.member && auth.role !== "MEMBER") {
    return { name: "home" };
  }
  if (to.meta.owner && auth.role !== "OWNER") {
    return { name: "home" };
  }
  return true;
});

export default router;
