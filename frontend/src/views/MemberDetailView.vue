<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { billingApi, membersApi, membershipsApi, paymentsApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const route = useRoute();
const member = ref(null);
const plans = ref([]);
const memberships = ref([]);
const invoices = ref([]);
const payments = ref([]);
const qrPayload = ref("");
const error = ref("");
const planForm = ref({ name: "Monthly", duration_days: 30, price: "2000.00", billing_frequency: "MONTHLY" });
const sell = ref({ plan_id: "", start_date: new Date().toISOString().slice(0, 10) });
const portal = ref({ email: "", password: "" });
const freezeForms = ref({});
const renewForms = ref({});
const message = ref("");

function asList(value) {
  return Array.isArray(value) ? value : value || [];
}

async function loadQr() {
  try {
    const qr = await membersApi.qr(route.params.id);
    qrPayload.value = qr?.qr_payload || "";
  } catch {
    qrPayload.value = "";
  }
}

async function load() {
  error.value = "";
  try {
    member.value = await membersApi.get(route.params.id);
    await loadQr();
    const planPage = await membershipsApi.listPlans();
    plans.value = asList(planPage);
    const memPage = await membershipsApi.listForMember(route.params.id);
    memberships.value = asList(memPage).filter((row) => row.member === route.params.id);
    const nextForms = { ...freezeForms.value };
    const nextRenew = { ...renewForms.value };
    for (const row of memberships.value) {
      if (row.status === "ACTIVE" && !nextForms[row.id]) {
        nextForms[row.id] = { start_date: "", end_date: "", reason: "" };
      }
      if ((row.status === "ACTIVE" || row.status === "EXPIRED") && !nextRenew[row.id]) {
        nextRenew[row.id] = { start_date: new Date().toISOString().slice(0, 10), plan_id: "" };
      }
    }
    freezeForms.value = nextForms;
    renewForms.value = nextRenew;
    const invPage = await billingApi.list(route.params.id);
    invoices.value = asList(invPage).filter((row) => row.member === route.params.id);
    const invoiceIds = new Set(invoices.value.map((row) => row.id));
    const payPage = await paymentsApi.list();
    payments.value = asList(payPage).filter((row) => invoiceIds.has(row.invoice));
    if (plans.value[0]) sell.value.plan_id = plans.value[0].id;
    if (member.value?.email) portal.value.email = member.value.email;
  } catch (err) {
    error.value = err.message;
  }
}

async function createPlan() {
  error.value = "";
  try {
    const plan = await membershipsApi.createPlan(planForm.value);
    plans.value = [...plans.value, plan];
    sell.value.plan_id = plan.id;
  } catch (err) {
    error.value = err.message;
  }
}

async function sellMembership() {
  error.value = "";
  try {
    const membership = await membershipsApi.create({
      member_id: route.params.id,
      plan_id: sell.value.plan_id,
      start_date: sell.value.start_date,
    });
    const invoice = await billingApi.createInvoice({
      member_id: route.params.id,
      issue_date: sell.value.start_date,
      discount: "0.00",
      line_items: [
        {
          description: membership.plan_name || "Membership",
          quantity: "1.00",
          unit_price: membership.price,
          tax_rate: "0.00",
          related_membership_id: membership.id,
        },
      ],
    });
    await paymentsApi.cash({
      invoice_id: invoice.id,
      amount: invoice.total,
      method: "CASH",
    });
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function provisionPortal() {
  error.value = "";
  try {
    member.value = await membersApi.provisionLogin(route.params.id, portal.value);
  } catch (err) {
    error.value = err.message;
  }
}

async function freezeMembership(id) {
  error.value = "";
  try {
    const form = freezeForms.value[id];
    await membershipsApi.freeze(id, {
      start_date: form.start_date,
      end_date: form.end_date,
      reason: form.reason,
    });
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function unfreezeMembership(id) {
  error.value = "";
  try {
    await membershipsApi.unfreeze(id);
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

function pendingFreezeRequests(membership) {
  return (membership.freeze_requests || []).filter((row) => row.status === "PENDING");
}

async function approveFreezeRequest(id) {
  error.value = "";
  message.value = "";
  try {
    await membershipsApi.approveFreezeRequest(id);
    message.value = "Freeze request approved.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function rejectFreezeRequest(id) {
  error.value = "";
  message.value = "";
  try {
    await membershipsApi.rejectFreezeRequest(id);
    message.value = "Freeze request rejected.";
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

async function renewMembership(id) {
  error.value = "";
  message.value = "";
  try {
    const form = renewForms.value[id];
    const body = { start_date: form.start_date };
    if (form.plan_id) body.plan_id = form.plan_id;
    const membership = await membershipsApi.renew(id, body);
    try {
      const invoice = await billingApi.createInvoice({
        member_id: route.params.id,
        issue_date: form.start_date,
        discount: "0.00",
        line_items: [
          {
            description: membership.plan_name || "Membership renewal",
            quantity: "1.00",
            unit_price: membership.price,
            tax_rate: "0.00",
            related_membership_id: membership.id,
          },
        ],
      });
      await paymentsApi.cash({
        invoice_id: invoice.id,
        amount: invoice.total,
        method: "CASH",
      });
      message.value = "Membership renewed and cash recorded.";
    } catch {
      message.value = "Membership renewed. Invoice skipped (GST is not configured).";
    }
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(load);
</script>

<template>
  <AppShell>
    <div v-if="member">
      <PageHeader
        eyebrow="Member profile"
        :title="member.full_name"
        :lede="`${member.member_code} · ${member.phone}`"
      />
      <p><span :data-status="member.status">{{ member.status }}</span></p>
      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <p v-if="message" class="ok">{{ message }}</p>

      <h2>Check-in token</h2>
      <p v-if="qrPayload"><code>{{ qrPayload }}</code></p>
      <p v-else class="note">Check-in token is not available.</p>

      <h2>Sell membership + collect cash</h2>
      <form class="row" @submit.prevent="createPlan">
        <input v-model="planForm.name" placeholder="Plan name" />
        <input v-model="planForm.price" />
        <button type="submit">Add plan</button>
      </form>
      <form @submit.prevent="sellMembership">
        <label>
          Plan
          <select v-model="sell.plan_id" required>
            <option disabled value="">Select plan</option>
            <option v-for="p in plans" :key="p.id" :value="p.id">{{ p.name }} ({{ p.price }})</option>
          </select>
        </label>
        <label>Start date <input v-model="sell.start_date" type="date" required /></label>
        <button type="submit">Sell and collect cash</button>
      </form>

      <h2>Memberships</h2>
      <ul>
        <li v-for="m in memberships" :key="m.id">
          <p>{{ m.plan_name }} · <span :data-status="m.status">{{ m.status }}</span> · {{ m.start_date }}–{{ m.end_date }}</p>
          <form v-if="m.status === 'ACTIVE' && freezeForms[m.id]" class="row" @submit.prevent="freezeMembership(m.id)">
            <label>Start date <input v-model="freezeForms[m.id].start_date" type="date" required /></label>
            <label>End date <input v-model="freezeForms[m.id].end_date" type="date" required /></label>
            <label>Reason <input v-model="freezeForms[m.id].reason" required maxlength="255" /></label>
            <button type="submit">Freeze</button>
          </form>
          <p v-else-if="m.status === 'FROZEN'">
            <button type="button" @click="unfreezeMembership(m.id)">Unfreeze</button>
          </p>
          <div v-if="pendingFreezeRequests(m).length" class="row">
            <p v-for="req in pendingFreezeRequests(m)" :key="req.id">
              Pending freeze {{ req.start_date }}–{{ req.end_date }} · {{ req.reason }}
              <button type="button" @click="approveFreezeRequest(req.id)">Approve</button>
              <button type="button" @click="rejectFreezeRequest(req.id)">Reject</button>
            </p>
          </div>
          <form
            v-if="(m.status === 'ACTIVE' || m.status === 'EXPIRED') && renewForms[m.id]"
            class="row"
            @submit.prevent="renewMembership(m.id)"
          >
            <label>
              Plan
              <select v-model="renewForms[m.id].plan_id">
                <option value="">Keep current plan</option>
                <option v-for="p in plans" :key="p.id" :value="p.id">{{ p.name }} ({{ p.price }})</option>
              </select>
            </label>
            <label>Start date <input v-model="renewForms[m.id].start_date" type="date" required /></label>
            <button type="submit">Renew</button>
          </form>
        </li>
      </ul>
      <h2>Invoices</h2>
      <ul>
        <li v-for="inv in invoices" :key="inv.id">{{ inv.invoice_number }} · {{ inv.total }} · <span :data-status="inv.status">{{ inv.status }}</span></li>
      </ul>

      <h2>Payment history</h2>
      <p v-if="!payments.length" class="note">No payments recorded for this member.</p>
      <ul v-else>
        <li v-for="p in payments" :key="p.id">
          {{ p.amount }} · {{ p.method }} · <span :data-status="p.status">{{ p.status }}</span>
          <span v-if="p.paid_at"> · {{ p.paid_at }}</span>
        </li>
      </ul>

      <h2>Portal login</h2>
      <p v-if="member.has_portal_login" class="ok">Portal login is enabled.</p>
      <form v-else class="row" @submit.prevent="provisionPortal">
        <input v-model="portal.email" type="email" placeholder="Member email" required />
        <input v-model="portal.password" type="password" placeholder="Initial password" required minlength="8" />
        <button type="submit">Enable portal</button>
      </form>
    </div>
  </AppShell>
</template>
