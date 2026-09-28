<script setup>
import { onMounted, ref } from "vue";

import { classesApi, membersApi, workoutsApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const exercises = ref([]);
const programs = ref([]);
const members = ref([]);
const trainers = ref([]);
const error = ref("");
const message = ref("");
const exForm = ref({ name: "Squat", muscle_group: "legs" });
const progForm = ref({ name: "Beginner", member_id: "", trainer_id: "", start_date: new Date().toISOString().slice(0, 10) });

function asList(v) {
  return Array.isArray(v) ? v : v || [];
}

async function load() {
  try {
    exercises.value = asList(await workoutsApi.exercises());
    programs.value = asList(await workoutsApi.programs());
    members.value = asList(await membersApi.list());
    trainers.value = asList(await classesApi.trainers());
    if (members.value[0] && !progForm.value.member_id) progForm.value.member_id = members.value[0].id;
    if (trainers.value[0] && !progForm.value.trainer_id) progForm.value.trainer_id = trainers.value[0].id;
  } catch (err) {
    error.value = err.message;
  }
}

async function addExercise() {
  error.value = "";
  try {
    await workoutsApi.createExercise(exForm.value);
    message.value = "Exercise added.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function addProgram() {
  error.value = "";
  try {
    await workoutsApi.createProgram({
      name: progForm.value.name,
      member_id: progForm.value.member_id,
      trainer_id: progForm.value.trainer_id,
      start_date: progForm.value.start_date,
    });
    message.value = "Program assigned.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Studio" title="Workouts" lede="Catalog exercises and assign programs. No AI coaching." />
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="ok">{{ message }}</p>
    <form class="row" @submit.prevent="addExercise">
      <input v-model="exForm.name" required placeholder="Exercise" />
      <input v-model="exForm.muscle_group" placeholder="Muscle group" />
      <button type="submit">Add exercise</button>
    </form>
    <ul>
      <li v-for="e in exercises" :key="e.id">{{ e.name }} · {{ e.muscle_group }}</li>
    </ul>
    <h2>Assign program</h2>
    <form class="row" @submit.prevent="addProgram">
      <input v-model="progForm.name" required />
      <select v-model="progForm.member_id" required>
        <option disabled value="">Member</option>
        <option v-for="m in members" :key="m.id" :value="m.id">{{ m.full_name }}</option>
      </select>
      <select v-model="progForm.trainer_id" required>
        <option disabled value="">Trainer</option>
        <option v-for="t in trainers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
      </select>
      <input v-model="progForm.start_date" type="date" required />
      <button type="submit">Assign</button>
    </form>
    <ul>
      <li v-for="p in programs" :key="p.id">{{ p.name }} · {{ p.status }}</li>
    </ul>
  </AppShell>
</template>
