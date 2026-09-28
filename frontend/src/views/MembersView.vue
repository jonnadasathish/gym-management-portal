<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { branchesApi, membersApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const router = useRouter();
const members = ref([]);
const branches = ref([]);
const search = ref("");
const error = ref("");
const form = ref({
  full_name: "",
  phone: "",
  home_branch_id: "",
  joining_date: new Date().toISOString().slice(0, 10),
});

async function load() {
  error.value = "";
  try {
    const [list, branchList] = await Promise.all([membersApi.list(search.value), branchesApi.list()]);
    members.value = Array.isArray(list) ? list : list || [];
    branches.value = Array.isArray(branchList) ? branchList : branchList || [];
  } catch (err) {
    error.value = err.message;
  }
}

async function register() {
  error.value = "";
  try {
    const created = await membersApi.create(form.value);
    await router.push({ name: "member-detail", params: { id: created.id } });
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Front desk" title="Members" lede="Search the directory or register a new member." />
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <form class="row" @submit.prevent="load">
      <input v-model="search" placeholder="Search name, phone, member ID" />
      <button type="submit">Search</button>
    </form>
    <table>
      <thead>
        <tr>
          <th>Code</th>
          <th>Name</th>
          <th>Phone</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="m in members" :key="m.id" @click="router.push({ name: 'member-detail', params: { id: m.id } })">
          <td>{{ m.member_code }}</td>
          <td>{{ m.full_name }}</td>
          <td>{{ m.phone }}</td>
          <td><span :data-status="m.status">{{ m.status }}</span></td>
        </tr>
      </tbody>
    </table>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <label>Full name <input v-model="form.full_name" required /></label>
      <label>Phone <input v-model="form.phone" required /></label>
      <label>
        Home branch
        <select v-model="form.home_branch_id" required>
          <option disabled value="">Select branch</option>
          <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </label>
      <label>Joining date <input v-model="form.joining_date" type="date" required /></label>
      <button type="submit">Create member</button>
    </form>
  </AppShell>
</template>
