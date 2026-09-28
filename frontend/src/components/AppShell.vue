<script setup>
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const titles = {
  home: "Home",
  dashboard: "Analytics",
  members: "Members",
  "member-detail": "Member profile",
  "check-in": "Check-in",
  classes: "Classes",
  pt: "Personal training",
  workouts: "Workouts",
  progress: "Progress",
  leads: "Leads",
  import: "Import",
  subscriptions: "Subscriptions",
  staff: "Staff",
  notifications: "Notifications",
  portal: "My gym",
};

async function onLogout() {
  await auth.logout();
  await router.replace({ name: "login" });
}
</script>

<template>
  <div class="shell">
    <aside class="rail">
      <div class="brand">
        <strong>Apex Pulse</strong>
        <span>Gym operations</span>
      </div>
      <nav>
        <RouterLink to="/" active-class="" exact-active-class="router-link-active">Home</RouterLink>
        <p v-if="auth.canSeeStaffNav()" class="nav-group">Front desk</p>
        <RouterLink v-if="auth.canSeeStaffNav()" to="/check-in">Check-in</RouterLink>
        <RouterLink v-if="auth.canSeeStaffNav()" to="/members">Members</RouterLink>
        <RouterLink v-if="auth.canSeeStaffNav()" to="/classes">Classes</RouterLink>
        <RouterLink v-if="auth.canSeeStaffNav()" to="/pt">PT</RouterLink>
        <p v-if="auth.canSeeStaffNav()" class="nav-group">Studio</p>
        <RouterLink v-if="auth.canSeeStaffNav()" to="/workouts">Workouts</RouterLink>
        <RouterLink v-if="auth.canSeeStaffNav()" to="/progress">Progress</RouterLink>
        <p v-if="auth.canSeeFrontDeskNav() || auth.role === 'OWNER'" class="nav-group">Growth</p>
        <RouterLink v-if="auth.canSeeStaffNav()" to="/leads">Leads</RouterLink>
        <RouterLink v-if="auth.canSeeFrontDeskNav()" to="/import">Import</RouterLink>
        <RouterLink v-if="auth.canSeeFrontDeskNav()" to="/subscriptions">Subscriptions</RouterLink>
        <RouterLink v-if="auth.canSeeFrontDeskNav()" to="/staff">Staff</RouterLink>
        <p v-if="auth.role === 'OWNER' || auth.canSeeStaffNav() || auth.role === 'MEMBER'" class="nav-group">
          Insights
        </p>
        <RouterLink v-if="auth.role === 'OWNER'" to="/dashboard">Dashboard</RouterLink>
        <RouterLink v-if="auth.canSeeStaffNav() || auth.role === 'MEMBER'" to="/notifications">Notifications</RouterLink>
        <p v-if="auth.role === 'MEMBER'" class="nav-group">Member</p>
        <RouterLink v-if="auth.role === 'MEMBER'" to="/portal">My gym</RouterLink>
      </nav>
    </aside>
    <div class="workspace">
      <header class="command">
        <p class="label-caps">{{ titles[route.name] || "Apex Pulse" }}</p>
        <div class="who">
          <span>{{ auth.user?.full_name }} · {{ auth.user?.role }}</span>
          <button type="button" @click="onLogout">Sign out</button>
        </div>
      </header>
      <main class="page">
        <slot />
      </main>
    </div>
  </div>
</template>
