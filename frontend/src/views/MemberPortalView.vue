<script setup>
import { onMounted, ref } from "vue";

import {
  attendanceApi,
  billingApi,
  classesApi,
  membersApi,
  membershipsApi,
  paymentsApi,
  progressApi,
  ptApi,
  workoutsApi,
} from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const member = ref(null);
const memberships = ref([]);
const invoices = ref([]);
const payments = ref([]);
const bookings = ref([]);
const attendance = ref([]);
const occurrences = ref([]);
const packages = ref([]);
const sessions = ref([]);
const programs = ref([]);
const logs = ref([]);
const progress = ref([]);
const freezeRequestForms = ref({});
const qrPayload = ref("");
const error = ref("");
const message = ref("");

function asList(value) {
  return Array.isArray(value) ? value : value || [];
}

async function load() {
  error.value = "";
  try {
    member.value = await membersApi.me();
    const [mems, inv, pays, booked, att, occ, pkgs, sess, progs, wlogs, entries, qr] = await Promise.all([
      membershipsApi.listForMember(member.value.id),
      billingApi.list(member.value.id),
      paymentsApi.list(),
      classesApi.bookings(),
      attendanceApi.list(),
      classesApi.occurrences(),
      ptApi.packages(),
      ptApi.sessions(),
      workoutsApi.programs(),
      workoutsApi.logs(),
      progressApi.entries(),
      membersApi.qr(member.value.id).catch(() => null),
    ]);
    memberships.value = asList(mems);
    invoices.value = asList(inv);
    payments.value = asList(pays);
    bookings.value = asList(booked);
    attendance.value = asList(att);
    occurrences.value = asList(occ);
    packages.value = asList(pkgs);
    sessions.value = asList(sess);
    programs.value = asList(progs);
    logs.value = asList(wlogs);
    progress.value = asList(entries);
    qrPayload.value = qr?.qr_payload || "";
    const nextFreeze = { ...freezeRequestForms.value };
    for (const row of memberships.value) {
      if (row.status === "ACTIVE" && !nextFreeze[row.id]) {
        nextFreeze[row.id] = { start_date: "", end_date: "", reason: "" };
      }
    }
    freezeRequestForms.value = nextFreeze;
  } catch (err) {
    error.value = err.message;
  }
}

async function book(occurrenceId) {
  error.value = "";
  message.value = "";
  try {
    const booking = await classesApi.book({ occurrence_id: occurrenceId });
    message.value = `Booked (${booking.status}).`;
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function cancelBooking(id) {
  error.value = "";
  message.value = "";
  try {
    await classesApi.cancel(id);
    message.value = "Booking cancelled.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

function canPayInvoice(inv) {
  return inv.status === "ISSUED" || inv.status === "PARTIALLY_PAID" || inv.status === "DRAFT";
}

async function payInvoice(id) {
  error.value = "";
  message.value = "";
  try {
    const payment = await paymentsApi.initiate({ invoice_id: id });
    message.value = `Payment initiated (${payment.status}). Settlement waits for gateway confirmation.`;
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function requestFreeze(id) {
  error.value = "";
  message.value = "";
  try {
    const form = freezeRequestForms.value[id];
    await membershipsApi.requestFreeze(id, {
      start_date: form.start_date,
      end_date: form.end_date,
      reason: form.reason,
    });
    message.value = "Freeze request submitted. Staff must approve it before the membership is frozen.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

function canCancelBooking(row) {
  return row.status === "BOOKED" || row.status === "WAITLISTED";
}

onMounted(load);
</script>

<template>
  <AppShell>
    <PageHeader
      eyebrow="Member"
      title="My gym"
      :lede="member ? `${member.full_name} · ${member.member_code}` : 'Your membership, bookings, and payments.'"
    />
    <p v-if="member"><span :data-status="member.status">{{ member.status }}</span></p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="message" class="ok">{{ message }}</p>

    <h2>Check-in token</h2>
    <p v-if="qrPayload"><code>{{ qrPayload }}</code></p>
    <p v-else class="note">Check-in token is not available.</p>

    <h2>Membership</h2>
    <ul>
      <li v-for="m in memberships" :key="m.id">
        <p>{{ m.plan_name }} · <span :data-status="m.status">{{ m.status }}</span> · {{ m.start_date }}–{{ m.end_date }}</p>
        <form
          v-if="m.status === 'ACTIVE' && freezeRequestForms[m.id]"
          class="row"
          @submit.prevent="requestFreeze(m.id)"
        >
          <label>Start date <input v-model="freezeRequestForms[m.id].start_date" type="date" required /></label>
          <label>End date <input v-model="freezeRequestForms[m.id].end_date" type="date" required /></label>
          <label>Reason <input v-model="freezeRequestForms[m.id].reason" required maxlength="255" /></label>
          <button type="submit">Request freeze</button>
        </form>
        <p v-if="m.status === 'ACTIVE'" class="note">This sends a request only. It does not freeze the membership.</p>
      </li>
      <li v-if="!memberships.length">No memberships yet.</li>
    </ul>

    <h2>Invoices</h2>
    <ul>
      <li v-for="inv in invoices" :key="inv.id">
        {{ inv.invoice_number }} · {{ inv.total }} · {{ inv.status }}
        <button v-if="canPayInvoice(inv)" type="button" @click="payInvoice(inv.id)">Pay</button>
      </li>
      <li v-if="!invoices.length">No invoices yet.</li>
    </ul>

    <h2>Payments</h2>
    <ul>
      <li v-for="p in payments" :key="p.id">
        {{ p.amount }} · {{ p.method }} · {{ p.status }}
        <span v-if="p.paid_at"> · {{ p.paid_at }}</span>
      </li>
      <li v-if="!payments.length">No payments yet.</li>
    </ul>

    <h2>My bookings</h2>
    <ul>
      <li v-for="row in bookings" :key="row.id">
        {{ row.gym_class_name || row.occurrence_id }} · {{ row.start_time || row.booked_at }} · {{ row.status }}
        <button v-if="canCancelBooking(row)" type="button" @click="cancelBooking(row.id)">Cancel</button>
      </li>
      <li v-if="!bookings.length">No bookings yet.</li>
    </ul>

    <h2>Classes</h2>
    <table>
      <thead>
        <tr>
          <th>Class</th>
          <th>Start</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in occurrences" :key="row.id">
          <td>{{ row.gym_class_name }}</td>
          <td>{{ row.start_time }}</td>
          <td>
            <button type="button" :disabled="row.status !== 'SCHEDULED'" @click="book(row.id)">Book</button>
          </td>
        </tr>
      </tbody>
    </table>

    <h2>Attendance</h2>
    <ul>
      <li v-for="row in attendance" :key="row.id">{{ row.checkin_at }} · {{ row.method }}</li>
      <li v-if="!attendance.length">No visits recorded yet.</li>
    </ul>

    <h2>Personal training</h2>
    <ul>
      <li v-for="p in packages" :key="p.id">{{ p.plan_name }} · {{ p.sessions_remaining }} / {{ p.sessions_purchased }} left</li>
      <li v-if="!packages.length">No PT packages yet.</li>
    </ul>
    <ul>
      <li v-for="s in sessions" :key="s.id">{{ s.scheduled_at }} · {{ s.status }}</li>
    </ul>

    <h2>Workout programs</h2>
    <ul>
      <li v-for="p in programs" :key="p.id">{{ p.name }} · {{ p.status }}</li>
      <li v-if="!programs.length">No workout programs yet.</li>
    </ul>

    <h2>Workout logs</h2>
    <ul>
      <li v-for="row in logs" :key="row.id">
        {{ row.exercise_name }} · {{ row.performed_on }} · {{ row.sets }}×{{ row.reps }}
        · {{ row.weight || "—" }}
      </li>
      <li v-if="!logs.length">No workout logs yet.</li>
    </ul>

    <h2>Progress</h2>
    <ul>
      <li v-for="e in progress" :key="e.id">
        {{ e.weight_kg || "—" }} kg · BMI {{ e.bmi || "—" }}
        <span v-if="e.notes"> · {{ e.notes }}</span>
      </li>
      <li v-if="!progress.length">No progress entries yet.</li>
    </ul>
  </AppShell>
</template>
