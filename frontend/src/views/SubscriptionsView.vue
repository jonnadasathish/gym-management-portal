<script setup>
import { onMounted, ref } from "vue";

import { paymentsApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const subscriptions = ref([]);
const error = ref("");

function asList(value) {
  return Array.isArray(value) ? value : value || [];
}

async function load() {
  error.value = "";
  try {
    subscriptions.value = asList(await paymentsApi.subscriptions());
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader
      eyebrow="Billing"
      title="Subscriptions"
      lede="Recurring billing status only. Charging and retries are not available here."
    />
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-else-if="!subscriptions.length" class="note">No subscriptions yet.</p>
    <table v-else>
      <thead>
        <tr>
          <th>Plan</th>
          <th>Status</th>
          <th>Next billing</th>
          <th>Retries</th>
          <th>Gateway</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in subscriptions" :key="row.id">
          <td>{{ row.plan_name }}</td>
          <td><span :data-status="row.status">{{ row.status }}</span></td>
          <td>{{ row.next_billing_date || "—" }}</td>
          <td>{{ row.retry_count }}</td>
          <td>{{ row.gateway }}</td>
        </tr>
      </tbody>
    </table>
  </AppShell>
</template>
