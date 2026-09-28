<script setup>
import { onMounted, ref } from "vue";

import { notificationsApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const logs = ref([]);
const error = ref("");

function asList(value) {
  return Array.isArray(value) ? value : value || [];
}

function when(row) {
  return row.sent_at || row.created_at || "";
}

async function load() {
  error.value = "";
  try {
    logs.value = asList(await notificationsApi.logs());
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Insights" title="Notifications" lede="In-app and console delivery log. WhatsApp and SMS vendors are not connected." />
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <table>
      <thead>
        <tr>
          <th>Event</th>
          <th>Channel</th>
          <th>Status</th>
          <th>When</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in logs" :key="row.id">
          <td>{{ row.event_type }}</td>
          <td>{{ row.channel }}</td>
          <td><span :data-status="row.status">{{ row.status }}</span></td>
          <td>{{ when(row) }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="!error && !logs.length">No notifications yet.</p>
  </AppShell>
</template>
