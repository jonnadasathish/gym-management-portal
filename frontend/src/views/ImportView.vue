<script setup>
import { computed, onMounted, ref } from "vue";

import { migrationApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const jobs = ref([]);
const job = ref(null);
const rawCsv = ref("");
const entityType = ref("MEMBERS");
const error = ref("");
const message = ref("");

function asList(value) {
  return Array.isArray(value) ? value : value || [];
}

const canPreview = computed(() => Boolean(job.value?.id));
const canConfirm = computed(() => job.value?.status === "PREVIEW_READY");

async function loadJobs() {
  jobs.value = asList(await migrationApi.list());
}

async function load() {
  error.value = "";
  try {
    await loadJobs();
  } catch (err) {
    error.value = err.message;
  }
}

function applyJob(next) {
  job.value = next;
  if (next?.raw_csv) rawCsv.value = next.raw_csv;
  if (next?.entity_type) entityType.value = next.entity_type;
}

async function createJob() {
  error.value = "";
  message.value = "";
  try {
    const created = await migrationApi.createJob({
      raw_csv: rawCsv.value,
      entity_type: entityType.value || "MEMBERS",
    });
    applyJob(created);
    message.value = "Job created. Preview before confirming.";
    await loadJobs();
  } catch (err) {
    error.value = err.message;
  }
}

async function previewJob() {
  error.value = "";
  message.value = "";
  if (!job.value?.id) return;
  try {
    const previewed = await migrationApi.preview(job.value.id);
    applyJob(previewed);
    message.value = "Preview ready. Confirm only if the counts look correct.";
    await loadJobs();
  } catch (err) {
    error.value = err.message;
  }
}

async function confirmJob() {
  error.value = "";
  message.value = "";
  if (!canConfirm.value) return;
  try {
    const confirmed = await migrationApi.confirm(job.value.id);
    applyJob(confirmed);
    message.value = "Import confirmed.";
    await loadJobs();
  } catch (err) {
    error.value = err.message;
  }
}

function selectJob(row) {
  applyJob(row);
  error.value = "";
  message.value = "";
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Migration" title="Import" lede="Preview CSV rows, then confirm. Unvalidated rows are never inserted." />
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="message" class="ok">{{ message }}</p>
    <p class="note">Preview never writes members. Confirm only after you review valid and error rows.</p>

    <label>
      Entity
      <select v-model="entityType">
        <option value="MEMBERS">MEMBERS</option>
      </select>
    </label>
    <label>
      CSV
      <textarea
        v-model="rawCsv"
        rows="10"
        placeholder="full_name,phone,home_branch_name,joining_date"
      />
    </label>
    <div class="row">
      <button type="button" :disabled="!rawCsv.trim()" @click="createJob">Create job</button>
      <button type="button" :disabled="!canPreview" @click="previewJob">Preview</button>
      <button type="button" :disabled="!canConfirm" @click="confirmJob">Confirm</button>
    </div>

    <div v-if="job">
      <h2>Current job</h2>
      <p>
        Status {{ job.status }} · valid {{ job.valid_rows ?? 0 }} · errors {{ job.error_rows ?? 0 }}
      </p>
      <ul>
        <li v-for="row in asList(job.row_errors)" :key="`${row.row_number}-${(row.error_messages || []).join(',')}`">
          Row {{ row.row_number }}: {{ (row.error_messages || []).join("; ") }}
        </li>
        <li v-if="!asList(job.row_errors).length">No row errors.</li>
      </ul>
    </div>

    <h2>Jobs</h2>
    <table>
      <thead>
        <tr>
          <th>Status</th>
          <th>Valid</th>
          <th>Errors</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in jobs" :key="row.id">
          <td><span :data-status="row.status">{{ row.status }}</span></td>
          <td>{{ row.valid_rows }}</td>
          <td>{{ row.error_rows }}</td>
          <td>
            <button type="button" @click="selectJob(row)">Open</button>
          </td>
        </tr>
      </tbody>
    </table>
  </AppShell>
</template>
