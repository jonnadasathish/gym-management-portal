import { apiRequest } from "./client";

export const branchesApi = {
  list() {
    return apiRequest("/branches/");
  },
};

export const membersApi = {
  list(search = "") {
    const q = search ? `?search=${encodeURIComponent(search)}` : "";
    return apiRequest(`/members/${q}`);
  },
  get(id) {
    return apiRequest(`/members/${id}/`);
  },
  create(body) {
    return apiRequest("/members/", { method: "POST", body });
  },
  me() {
    return apiRequest("/members/me/");
  },
  provisionLogin(id, body) {
    return apiRequest(`/members/${id}/provision-login/`, { method: "POST", body });
  },
  qr(id) {
    return apiRequest(`/members/${id}/qr/`);
  },
};

export const membershipsApi = {
  listPlans() {
    return apiRequest("/memberships/plans/");
  },
  createPlan(body) {
    return apiRequest("/memberships/plans/", { method: "POST", body });
  },
  listForMember(memberId) {
    return apiRequest(`/memberships/?member=${encodeURIComponent(memberId)}`);
  },
  create(body) {
    return apiRequest("/memberships/", { method: "POST", body });
  },
  freeze(id, body) {
    return apiRequest(`/memberships/${id}/freeze/`, { method: "POST", body });
  },
  unfreeze(id) {
    return apiRequest(`/memberships/${id}/unfreeze/`, { method: "POST" });
  },
  renew(id, body) {
    return apiRequest(`/memberships/${id}/renew/`, { method: "POST", body });
  },
  requestFreeze(id, body) {
    return apiRequest(`/memberships/${id}/request-freeze/`, { method: "POST", body });
  },
  approveFreezeRequest(id, body) {
    return apiRequest(`/memberships/freeze-requests/${id}/approve/`, { method: "POST", body });
  },
  rejectFreezeRequest(id) {
    return apiRequest(`/memberships/freeze-requests/${id}/reject/`, { method: "POST" });
  },
};

export const attendanceApi = {
  checkIn(body) {
    return apiRequest("/attendance/check-in/", { method: "POST", body });
  },
  list() {
    return apiRequest("/attendance/");
  },
};

export const billingApi = {
  createInvoice(body) {
    return apiRequest("/billing/", { method: "POST", body });
  },
  list(memberId) {
    const q = memberId ? `?member=${encodeURIComponent(memberId)}` : "";
    return apiRequest(`/billing/${q}`);
  },
};

export const paymentsApi = {
  list() {
    return apiRequest("/payments/");
  },
  cash(body) {
    return apiRequest("/payments/cash/", { method: "POST", body });
  },
  subscriptions() {
    return apiRequest("/payments/subscriptions/");
  },
  initiate(body) {
    return apiRequest("/payments/initiate/", { method: "POST", body });
  },
};

export const classesApi = {
  catalog() {
    return apiRequest("/classes/catalog/");
  },
  trainers() {
    return apiRequest("/classes/trainers/");
  },
  createClass(body) {
    return apiRequest("/classes/catalog/", { method: "POST", body });
  },
  occurrences() {
    return apiRequest("/classes/occurrences/");
  },
  createOccurrence(body) {
    return apiRequest("/classes/occurrences/", { method: "POST", body });
  },
  book(body) {
    return apiRequest("/classes/bookings/book/", { method: "POST", body });
  },
  bookings() {
    return apiRequest("/classes/bookings/");
  },
  cancel(id) {
    return apiRequest(`/classes/bookings/${id}/cancel/`, { method: "POST" });
  },
};

function isLocalToday(iso) {
  if (!iso) return false;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return false;
  const now = new Date();
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate();
}

export const ptApi = {
  packages() {
    return apiRequest("/pt/packages/");
  },
  createPackage(body) {
    return apiRequest("/pt/packages/", { method: "POST", body });
  },
  sessions() {
    return apiRequest("/pt/sessions/");
  },
  schedule(body) {
    return apiRequest("/pt/sessions/schedule/", { method: "POST", body });
  },
  reschedule(id, body) {
    return apiRequest(`/pt/sessions/${id}/reschedule/`, { method: "POST", body });
  },
  complete(id) {
    return apiRequest(`/pt/sessions/${id}/complete/`, { method: "POST" });
  },
  cancel(id) {
    return apiRequest(`/pt/sessions/${id}/cancel/`, { method: "POST" });
  },
  today() {
    return this.sessions().then((rows) => (Array.isArray(rows) ? rows : []).filter((row) => isLocalToday(row.scheduled_at)));
  },
};

function asPath(base, extra = "") {
  return `${base}${extra}`;
}

export const staffApi = {
  list() {
    return apiRequest("/auth/staff/");
  },
  create(body) {
    return apiRequest("/auth/staff/", { method: "POST", body });
  },
  deactivate(id) {
    return apiRequest(`/auth/staff/${id}/deactivate/`, { method: "POST" });
  },
  activate(id) {
    return apiRequest(`/auth/staff/${id}/activate/`, { method: "POST" });
  },
  compensation(id, start, end) {
    const q = `?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;
    return apiRequest(`/trainers/${id}/compensation/${q}`);
  },
};

export const reportsApi = {
  dashboard() {
    return apiRequest("/reports/dashboard/");
  },
  dashboardCsv() {
    return apiRequest("/reports/dashboard.csv", { parseAs: "text" });
  },
  expiredMembersCsv() {
    return apiRequest("/reports/expired-members.csv", { parseAs: "text" });
  },
};

export const workoutsApi = {
  exercises() {
    return apiRequest("/workouts/exercises/");
  },
  createExercise(body) {
    return apiRequest("/workouts/exercises/", { method: "POST", body });
  },
  programs() {
    return apiRequest("/workouts/programs/");
  },
  createProgram(body) {
    return apiRequest("/workouts/programs/", { method: "POST", body });
  },
  logs() {
    return apiRequest("/workouts/logs/");
  },
  createLog(body) {
    return apiRequest("/workouts/logs/", { method: "POST", body });
  },
};

export const progressApi = {
  entries() {
    return apiRequest("/progress/entries/");
  },
  createEntry(body) {
    return apiRequest("/progress/entries/", { method: "POST", body });
  },
};

export const crmApi = {
  leads() {
    return apiRequest("/crm/leads/");
  },
  createLead(body) {
    return apiRequest("/crm/leads/", { method: "POST", body });
  },
  convert(id) {
    return apiRequest(`/crm/leads/${id}/convert/`, { method: "POST" });
  },
};

export const notificationsApi = {
  logs() {
    return apiRequest("/notifications/logs/");
  },
};

export const migrationApi = {
  list() {
    return apiRequest("/data-migration/jobs/");
  },
  createJob(body) {
    return apiRequest("/data-migration/jobs/", { method: "POST", body });
  },
  preview(id) {
    return apiRequest(asPath(`/data-migration/jobs/${id}/preview/`), { method: "POST" });
  },
  confirm(id) {
    return apiRequest(`/data-migration/jobs/${id}/confirm/`, { method: "POST" });
  },
};
