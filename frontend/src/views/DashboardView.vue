<script setup>
import { onMounted, ref } from "vue";

import { reportsApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const dash = ref(null);
const error = ref("");

function triggerCsvDownload(csv, filename) {
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

async function downloadCsv() {
  error.value = "";
  try {
    const csv = await reportsApi.dashboardCsv();
    triggerCsvDownload(csv, "dashboard.csv");
  } catch (err) {
    error.value = err.message;
  }
}

async function downloadExpiredMembersCsv() {
  error.value = "";
  try {
    const csv = await reportsApi.expiredMembersCsv();
    triggerCsvDownload(csv, "expired-members.csv");
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(async () => {
  try {
    dash.value = await reportsApi.dashboard();
  } catch (err) {
    error.value = err.message;
  }
});
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Analytics" title="Owner dashboard" lede="Revenue, membership, attendance, and PT from live records." />
    <p class="row">
      <button type="button" @click="downloadCsv">Download CSV</button>
      <button type="button" @click="downloadExpiredMembersCsv">Download expired members CSV</button>
    </p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <div v-if="dash">
      <div class="kpi-grid">
        <article class="kpi">
          <p class="label-caps">Today</p>
          <p class="telemetry">{{ dash.revenue.today_collection }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">This month</p>
          <p class="telemetry">{{ dash.revenue.monthly_collection }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">Pending dues</p>
          <p class="telemetry">{{ dash.revenue.pending_dues }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">Refunds</p>
          <p class="telemetry">{{ dash.revenue.refunds_month }}</p>
        </article>
      </div>
      <h2>Membership</h2>
      <div class="kpi-grid">
        <article class="kpi">
          <p class="label-caps">Active</p>
          <p class="telemetry">{{ dash.membership.active }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">Expired</p>
          <p class="telemetry">{{ dash.membership.expired }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">Expiring 7d</p>
          <p class="telemetry">{{ dash.membership.expiring_7 }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">Frozen</p>
          <p class="telemetry">{{ dash.membership.frozen }}</p>
        </article>
      </div>
      <h2>By branch</h2>
      <ul>
        <li v-for="row in dash.revenue.by_branch || []" :key="row.branch_id">
          {{ row.branch_name }} · {{ row.monthly_collection }}
        </li>
      </ul>
      <h2>Attendance &amp; PT</h2>
      <div class="kpi-grid">
        <article class="kpi">
          <p class="label-caps">Today check-ins</p>
          <p class="telemetry">{{ dash.attendance.today_checkins }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">PT scheduled</p>
          <p class="telemetry">{{ dash.pt.scheduled_sessions }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">PT completed</p>
          <p class="telemetry">{{ dash.pt.completed_sessions }}</p>
        </article>
        <article class="kpi">
          <p class="label-caps">Sessions remaining</p>
          <p class="telemetry">{{ dash.pt.remaining_package_sessions }}</p>
        </article>
      </div>
    </div>
  </AppShell>
</template>
