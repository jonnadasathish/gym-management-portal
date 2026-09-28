<script setup>
import { onMounted, ref } from "vue";

import { branchesApi, classesApi, membersApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const occurrences = ref([]);
const catalog = ref([]);
const members = ref([]);
const trainers = ref([]);
const branches = ref([]);
const selectedMember = ref("");
const message = ref("");
const error = ref("");
const classForm = ref({ name: "", branch_id: "", trainer_id: "", capacity: 10 });
const occForm = ref({ gym_class_id: "", start_time: "", end_time: "" });

function asList(value) {
  return Array.isArray(value) ? value : value || [];
}

async function load() {
  error.value = "";
  try {
    const [occ, classes, memberList, trainerList, branchList] = await Promise.all([
      classesApi.occurrences(),
      classesApi.catalog(),
      membersApi.list(),
      classesApi.trainers(),
      branchesApi.list(),
    ]);
    occurrences.value = asList(occ);
    catalog.value = asList(classes);
    members.value = asList(memberList);
    trainers.value = asList(trainerList);
    branches.value = asList(branchList);
    if (members.value[0] && !selectedMember.value) selectedMember.value = members.value[0].id;
    if (catalog.value[0] && !occForm.value.gym_class_id) occForm.value.gym_class_id = catalog.value[0].id;
    if (branches.value[0] && !classForm.value.branch_id) classForm.value.branch_id = branches.value[0].id;
    if (trainers.value[0] && !classForm.value.trainer_id) classForm.value.trainer_id = trainers.value[0].id;
  } catch (err) {
    error.value = err.message;
  }
}

async function createClass() {
  error.value = "";
  message.value = "";
  try {
    const created = await classesApi.createClass({
      name: classForm.value.name,
      branch_id: classForm.value.branch_id,
      trainer_id: classForm.value.trainer_id || null,
      capacity: Number(classForm.value.capacity),
    });
    message.value = `Created class ${created.name}.`;
    classForm.value.name = "";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function createOccurrence() {
  error.value = "";
  message.value = "";
  try {
    await classesApi.createOccurrence({
      gym_class_id: occForm.value.gym_class_id,
      start_time: new Date(occForm.value.start_time).toISOString(),
      end_time: new Date(occForm.value.end_time).toISOString(),
    });
    message.value = "Scheduled class session.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function book(occurrenceId) {
  error.value = "";
  message.value = "";
  try {
    const booking = await classesApi.book({ occurrence_id: occurrenceId, member_id: selectedMember.value });
    message.value = `Booked ${booking.member_name} (${booking.status}).`;
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Studio" title="Classes" lede="Create classes, schedule sessions, and book seats." />
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="message" class="ok">{{ message }}</p>

    <h2>Add class</h2>
    <form class="row" @submit.prevent="createClass">
      <input v-model="classForm.name" placeholder="Class name" required />
      <select v-model="classForm.branch_id" required>
        <option disabled value="">Branch</option>
        <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model="classForm.trainer_id">
        <option value="">No trainer</option>
        <option v-for="t in trainers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
      </select>
      <input v-model="classForm.capacity" type="number" min="1" required />
      <button type="submit">Create class</button>
    </form>

    <h2>Schedule session</h2>
    <form class="row" @submit.prevent="createOccurrence">
      <select v-model="occForm.gym_class_id" required>
        <option disabled value="">Class</option>
        <option v-for="c in catalog" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <input v-model="occForm.start_time" type="datetime-local" required />
      <input v-model="occForm.end_time" type="datetime-local" required />
      <button type="submit">Schedule</button>
    </form>

    <label>
      Book for member
      <select v-model="selectedMember">
        <option disabled value="">Select member</option>
        <option v-for="m in members" :key="m.id" :value="m.id">{{ m.full_name }} ({{ m.member_code }})</option>
      </select>
    </label>
    <table>
      <thead>
        <tr>
          <th>Class</th>
          <th>Start</th>
          <th>Capacity</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in occurrences" :key="row.id">
          <td>{{ row.gym_class_name }}</td>
          <td>{{ row.start_time }}</td>
          <td>{{ row.booked_count }} / {{ row.capacity }}</td>
          <td>
            <button type="button" :disabled="!selectedMember || row.status !== 'SCHEDULED'" @click="book(row.id)">
              Book
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </AppShell>
</template>
