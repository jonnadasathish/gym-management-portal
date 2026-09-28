<script setup>
import { computed, onMounted, ref } from "vue";

import { classesApi, membersApi, ptApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const packages = ref([]);
const sessions = ref([]);
const members = ref([]);
const trainers = ref([]);
const error = ref("");
const message = ref("");
const pkgForm = ref({
  member_id: "",
  trainer_id: "",
  plan_name: "10 sessions",
  sessions_purchased: 10,
  price: "15000.00",
});
const scheduleForm = ref({ package_id: "", scheduled_at: "", duration_minutes: 60 });
const rescheduleForms = ref({});

function asList(value) {
  return Array.isArray(value) ? value : value || [];
}

function toDatetimeLocal(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function isLocalToday(iso) {
  if (!iso) return false;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return false;
  const now = new Date();
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate();
}

const todaySessions = computed(() => sessions.value.filter((row) => isLocalToday(row.scheduled_at)));

async function load() {
  error.value = "";
  try {
    const [pkg, sess, memberList, trainerList] = await Promise.all([
      ptApi.packages(),
      ptApi.sessions(),
      membersApi.list(),
      classesApi.trainers(),
    ]);
    packages.value = asList(pkg);
    sessions.value = asList(sess);
    members.value = asList(memberList);
    trainers.value = asList(trainerList);
    const nextReschedule = { ...rescheduleForms.value };
    for (const row of sessions.value) {
      if (row.status === "SCHEDULED") {
        nextReschedule[row.id] = toDatetimeLocal(row.scheduled_at);
      }
    }
    rescheduleForms.value = nextReschedule;
    if (members.value[0] && !pkgForm.value.member_id) pkgForm.value.member_id = members.value[0].id;
    if (trainers.value[0] && !pkgForm.value.trainer_id) pkgForm.value.trainer_id = trainers.value[0].id;
    if (packages.value[0] && !scheduleForm.value.package_id) scheduleForm.value.package_id = packages.value[0].id;
  } catch (err) {
    error.value = err.message;
  }
}

async function createPackage() {
  error.value = "";
  message.value = "";
  try {
    const created = await ptApi.createPackage({
      ...pkgForm.value,
      sessions_purchased: Number(pkgForm.value.sessions_purchased),
    });
    message.value = `Created ${created.plan_name} for ${created.member_name}.`;
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function schedule() {
  error.value = "";
  message.value = "";
  try {
    await ptApi.schedule({
      package_id: scheduleForm.value.package_id,
      scheduled_at: new Date(scheduleForm.value.scheduled_at).toISOString(),
      duration_minutes: Number(scheduleForm.value.duration_minutes),
    });
    message.value = "PT session scheduled.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function reschedule(id) {
  error.value = "";
  message.value = "";
  try {
    await ptApi.reschedule(id, {
      scheduled_at: new Date(rescheduleForms.value[id]).toISOString(),
    });
    message.value = "Session rescheduled.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function complete(id) {
  error.value = "";
  message.value = "";
  try {
    const session = await ptApi.complete(id);
    message.value = `Completed session for ${session.member_name}.`;
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function cancel(id) {
  error.value = "";
  message.value = "";
  try {
    await ptApi.cancel(id);
    message.value = "Session cancelled (balance unchanged).";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Studio" title="Personal training" lede="Sell packages, schedule sessions, and reschedule today's calendar." />
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="message" class="ok">{{ message }}</p>

    <h2>Sell package</h2>
    <form class="row" @submit.prevent="createPackage">
      <select v-model="pkgForm.member_id" required>
        <option disabled value="">Member</option>
        <option v-for="m in members" :key="m.id" :value="m.id">{{ m.full_name }}</option>
      </select>
      <select v-model="pkgForm.trainer_id" required>
        <option disabled value="">Trainer</option>
        <option v-for="t in trainers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
      </select>
      <input v-model="pkgForm.plan_name" required />
      <input v-model="pkgForm.sessions_purchased" type="number" min="1" required />
      <input v-model="pkgForm.price" required />
      <button type="submit">Create package</button>
    </form>

    <table>
      <thead>
        <tr>
          <th>Member</th>
          <th>Trainer</th>
          <th>Plan</th>
          <th>Remaining</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in packages" :key="row.id">
          <td>{{ row.member_name }}</td>
          <td>{{ row.trainer_name }}</td>
          <td>{{ row.plan_name }}</td>
          <td>{{ row.sessions_remaining }} / {{ row.sessions_purchased }}</td>
        </tr>
      </tbody>
    </table>

    <h2>Schedule session</h2>
    <form class="row" @submit.prevent="schedule">
      <select v-model="scheduleForm.package_id" required>
        <option disabled value="">Package</option>
        <option v-for="p in packages" :key="p.id" :value="p.id">
          {{ p.member_name }} · {{ p.plan_name }} ({{ p.sessions_remaining }} left)
        </option>
      </select>
      <input v-model="scheduleForm.scheduled_at" type="datetime-local" required />
      <input v-model="scheduleForm.duration_minutes" type="number" min="15" required />
      <button type="submit">Schedule</button>
    </form>

    <h2>Today</h2>
    <p v-if="!todaySessions.length" class="note">No sessions scheduled for today.</p>
    <table v-else>
      <thead>
        <tr>
          <th>Member</th>
          <th>When</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in todaySessions" :key="`today-${row.id}`">
          <td>{{ row.member_name }}</td>
          <td>{{ row.scheduled_at }}</td>
          <td><span :data-status="row.status">{{ row.status }}</span></td>
          <td>
            <form v-if="row.status === 'SCHEDULED'" class="row" @submit.prevent="reschedule(row.id)">
              <input v-model="rescheduleForms[row.id]" type="datetime-local" required />
              <button type="submit">Reschedule</button>
            </form>
          </td>
        </tr>
      </tbody>
    </table>

    <table>
      <thead>
        <tr>
          <th>Member</th>
          <th>When</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in sessions" :key="row.id">
          <td>{{ row.member_name }}</td>
          <td>{{ row.scheduled_at }}</td>
          <td><span :data-status="row.status">{{ row.status }}</span></td>
          <td>
            <button v-if="row.status === 'SCHEDULED'" type="button" @click="complete(row.id)">Complete</button>
            <button v-if="row.status === 'SCHEDULED'" type="button" @click="cancel(row.id)">Cancel</button>
            <form v-if="row.status === 'SCHEDULED'" class="row" @submit.prevent="reschedule(row.id)">
              <input v-model="rescheduleForms[row.id]" type="datetime-local" required />
              <button type="submit">Reschedule</button>
            </form>
          </td>
        </tr>
      </tbody>
    </table>
  </AppShell>
</template>
