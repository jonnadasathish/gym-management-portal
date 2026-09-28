<script setup>
import { computed, onMounted, ref } from "vue";

import { branchesApi, staffApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const staff = ref([]);
const branches = ref([]);
const error = ref("");
const compensationById = ref({});
const form = ref({
  email: "",
  password: "",
  full_name: "",
  phone: "",
  role: "STAFF_ADMIN",
  home_branch_id: "",
});

function ymd(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function thisMonthRange() {
  const now = new Date();
  return {
    start: ymd(new Date(now.getFullYear(), now.getMonth(), 1)),
    end: ymd(new Date(now.getFullYear(), now.getMonth() + 1, 0)),
  };
}

const compRange = ref(thisMonthRange());
const isOwner = computed(() => auth.role === "OWNER");

function asList(value) {
  return Array.isArray(value) ? value : value || [];
}

function branchLabel(row) {
  if (row.home_branch && typeof row.home_branch === "object" && row.home_branch.name) {
    return row.home_branch.name;
  }
  const id = row.home_branch_id || row.home_branch;
  const match = branches.value.find((b) => b.id === id);
  return match?.name || id || "";
}

function compensationText(row) {
  const data = compensationById.value[row.id];
  if (!data) return "";
  if (data.computed_amount == null || data.computed_amount === "") {
    return "revenue share not calculated";
  }
  return String(data.computed_amount);
}

async function load() {
  error.value = "";
  try {
    const [list, branchList] = await Promise.all([staffApi.list(), branchesApi.list()]);
    staff.value = asList(list);
    branches.value = asList(branchList);
    if (branches.value[0] && !form.value.home_branch_id) {
      form.value.home_branch_id = branches.value[0].id;
    }
  } catch (err) {
    error.value = err.message;
  }
}

async function createStaff() {
  error.value = "";
  try {
    await staffApi.create({
      email: form.value.email,
      password: form.value.password,
      full_name: form.value.full_name,
      phone: form.value.phone,
      role: form.value.role,
      home_branch_id: form.value.home_branch_id,
    });
    form.value.email = "";
    form.value.password = "";
    form.value.full_name = "";
    form.value.phone = "";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function deactivate(id) {
  error.value = "";
  try {
    await staffApi.deactivate(id);
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function activate(id) {
  error.value = "";
  try {
    await staffApi.activate(id);
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function previewCompensation(id) {
  error.value = "";
  try {
    const data = await staffApi.compensation(id, compRange.value.start, compRange.value.end);
    compensationById.value = { ...compensationById.value, [id]: data };
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Team" title="Staff" lede="Create front-desk and trainer accounts. Compensation is a preview, not payroll." />
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <form v-if="isOwner" class="row" @submit.prevent="createStaff">
      <input v-model="form.email" type="email" required placeholder="Email" />
      <input v-model="form.password" type="password" required placeholder="Password" />
      <input v-model="form.full_name" required placeholder="Full name" />
      <input v-model="form.phone" required placeholder="Phone" />
      <select v-model="form.role" required>
        <option value="STAFF_ADMIN">STAFF_ADMIN</option>
        <option value="TRAINER">TRAINER</option>
      </select>
      <select v-model="form.home_branch_id" required>
        <option disabled value="">Branch</option>
        <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <button type="submit">Create staff</button>
    </form>

    <div v-if="isOwner" class="row">
      <label>Compensation from <input v-model="compRange.start" type="date" /></label>
      <label>to <input v-model="compRange.end" type="date" /></label>
    </div>

    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Role</th>
          <th>Active</th>
          <th>Branch</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in staff" :key="row.id">
          <td>{{ row.full_name }}</td>
          <td>{{ row.email }}</td>
          <td>{{ row.role }}</td>
          <td>{{ row.is_active ? "Yes" : "No" }}</td>
          <td>{{ branchLabel(row) }}</td>
          <td>
            <template v-if="isOwner">
              <button
                v-if="row.is_active && row.id !== auth.user?.id"
                type="button"
                @click="deactivate(row.id)"
              >
                Deactivate
              </button>
              <button v-if="!row.is_active" type="button" @click="activate(row.id)">Activate</button>
              <template v-if="row.role === 'TRAINER'">
                <button type="button" @click="previewCompensation(row.id)">Compensation</button>
                <span v-if="compensationById[row.id]">{{ compensationText(row) }}</span>
              </template>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </AppShell>
</template>
