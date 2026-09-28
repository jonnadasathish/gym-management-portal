<script setup>
import { onMounted, ref } from "vue";

import { membersApi, progressApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const entries = ref([]);
const members = ref([]);
const error = ref("");
const form = ref({ member_id: "", weight_kg: "", height_cm: "" });

function asList(v) {
  return Array.isArray(v) ? v : v || [];
}

async function load() {
  try {
    entries.value = asList(await progressApi.entries());
    members.value = asList(await membersApi.list());
    if (members.value[0] && !form.value.member_id) form.value.member_id = members.value[0].id;
  } catch (err) {
    error.value = err.message;
  }
}

async function add() {
  error.value = "";
  try {
    await progressApi.createEntry({
      member_id: form.value.member_id,
      weight_kg: form.value.weight_kg || null,
      height_cm: form.value.height_cm || null,
    });
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Studio" title="Progress" lede="Record weight, height, and BMI history." />
    <p v-if="error" class="error">{{ error }}</p>
    <form class="row" @submit.prevent="add">
      <select v-model="form.member_id" required>
        <option disabled value="">Member</option>
        <option v-for="m in members" :key="m.id" :value="m.id">{{ m.full_name }}</option>
      </select>
      <input v-model="form.weight_kg" placeholder="Weight kg" />
      <input v-model="form.height_cm" placeholder="Height cm" />
      <button type="submit">Record</button>
    </form>
    <ul>
      <li v-for="e in entries" :key="e.id">{{ e.weight_kg }} kg · BMI {{ e.bmi || "—" }}</li>
    </ul>
  </AppShell>
</template>
