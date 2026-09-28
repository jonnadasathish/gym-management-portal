<script setup>
import { onMounted, ref } from "vue";

import { branchesApi, crmApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const leads = ref([]);
const branches = ref([]);
const error = ref("");
const form = ref({ name: "", phone: "", branch_id: "", source: "WALK_IN" });

function asList(v) {
  return Array.isArray(v) ? v : v || [];
}

async function load() {
  try {
    leads.value = asList(await crmApi.leads());
    branches.value = asList(await branchesApi.list());
    if (branches.value[0] && !form.value.branch_id) form.value.branch_id = branches.value[0].id;
  } catch (err) {
    error.value = err.message;
  }
}

async function add() {
  error.value = "";
  try {
    await crmApi.createLead(form.value);
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function convert(id) {
  error.value = "";
  try {
    await crmApi.convert(id);
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Growth" title="Leads" lede="Capture walk-ins and convert them to members." />
    <p v-if="error" class="error">{{ error }}</p>
    <form class="row" @submit.prevent="add">
      <input v-model="form.name" required placeholder="Name" />
      <input v-model="form.phone" required placeholder="Phone" />
      <select v-model="form.branch_id" required>
        <option disabled value="">Branch</option>
        <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <button type="submit">Add lead</button>
    </form>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in leads" :key="row.id">
          <td>{{ row.name }}</td>
          <td><span :data-status="row.status">{{ row.status }}</span></td>
          <td>
            <button v-if="row.status !== 'CONVERTED'" type="button" @click="convert(row.id)">Convert</button>
          </td>
        </tr>
      </tbody>
    </table>
  </AppShell>
</template>
