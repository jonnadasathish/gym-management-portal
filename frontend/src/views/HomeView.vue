<script setup>
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
</script>

<template>
  <AppShell>
    <PageHeader
      eyebrow="Command"
      title="Home"
      :lede="`Signed in as ${auth.user?.full_name || ''} · ${auth.user?.role || ''}`"
    />
    <div v-if="auth.canSeeStaffNav()" class="quick-grid">
      <RouterLink to="/check-in"><strong>Check-in</strong><small>Search or scan a member</small></RouterLink>
      <RouterLink to="/members"><strong>Members</strong><small>Register and sell memberships</small></RouterLink>
      <RouterLink to="/classes"><strong>Classes</strong><small>Schedule and book seats</small></RouterLink>
      <RouterLink to="/pt"><strong>Personal training</strong><small>Packages and sessions</small></RouterLink>
      <RouterLink to="/leads"><strong>Leads</strong><small>Follow the sales pipeline</small></RouterLink>
      <RouterLink v-if="auth.role === 'OWNER'" to="/dashboard"><strong>Dashboard</strong><small>Revenue and membership telemetry</small></RouterLink>
    </div>
    <div v-else class="quick-grid">
      <RouterLink to="/portal"><strong>My gym</strong><small>Membership, classes, payments, PT</small></RouterLink>
      <RouterLink to="/notifications"><strong>Notifications</strong><small>In-app delivery log</small></RouterLink>
    </div>
  </AppShell>
</template>
