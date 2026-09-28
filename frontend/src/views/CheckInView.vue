<script setup>
import { onMounted, onUnmounted, ref } from "vue";

import { attendanceApi, branchesApi, membersApi } from "../api/domain";
import AppShell from "../components/AppShell.vue";
import PageHeader from "../components/PageHeader.vue";

const search = ref("");
const members = ref([]);
const branches = ref([]);
const selectedMember = ref("");
const selectedBranch = ref("");
const qrPayload = ref("");
const message = ref("");
const error = ref("");
const videoEl = ref(null);
const scanning = ref(false);
const canScanQr = typeof window !== "undefined" && Boolean(window.BarcodeDetector);

let mediaStream = null;
let scanFrame = 0;
let detector = null;
let qrCheckInBusy = false;

async function loadBranches() {
  const list = await branchesApi.list();
  branches.value = Array.isArray(list) ? list : list || [];
  if (branches.value[0]) selectedBranch.value = branches.value[0].id;
}

async function findMembers() {
  error.value = "";
  const list = await membersApi.list(search.value);
  members.value = Array.isArray(list) ? list : list || [];
}

function stopCamera() {
  scanning.value = false;
  if (scanFrame) {
    cancelAnimationFrame(scanFrame);
    scanFrame = 0;
  }
  if (mediaStream) {
    for (const track of mediaStream.getTracks()) {
      track.stop();
    }
    mediaStream = null;
  }
  if (videoEl.value) {
    videoEl.value.srcObject = null;
  }
}

async function applyCheckIn(row) {
  message.value = `Checked in ${row.member_name} at ${row.branch_name}.`;
}

async function checkIn() {
  error.value = "";
  message.value = "";
  try {
    const row = await attendanceApi.checkIn({
      member_id: selectedMember.value,
      branch_id: selectedBranch.value,
      method: "STAFF_SEARCH",
    });
    await applyCheckIn(row);
  } catch (err) {
    error.value = err.message;
  }
}

async function checkInFromToken(payload) {
  if (qrCheckInBusy) return;
  const token = String(payload ?? qrPayload.value).trim();
  error.value = "";
  message.value = "";
  if (!token || !selectedBranch.value) return;
  qrCheckInBusy = true;
  try {
    const row = await attendanceApi.checkIn({
      qr_payload: token,
      branch_id: selectedBranch.value,
      method: "QR",
    });
    qrPayload.value = token;
    await applyCheckIn(row);
  } catch (err) {
    error.value = err.message;
  } finally {
    qrCheckInBusy = false;
  }
}

async function scanFrameLoop() {
  if (!scanning.value || !detector || !videoEl.value) return;
  try {
    if (videoEl.value.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
      const codes = await detector.detect(videoEl.value);
      const value = codes.find((code) => code.rawValue)?.rawValue;
      if (value) {
        stopCamera();
        qrPayload.value = value;
        await checkInFromToken(value);
        return;
      }
    }
  } catch {
    /* keep scanning until a frame decodes or the staff stops the camera */
  }
  if (scanning.value) {
    scanFrame = requestAnimationFrame(scanFrameLoop);
  }
}

async function startScan() {
  error.value = "";
  message.value = "";
  if (!canScanQr || !selectedBranch.value) return;
  stopCamera();
  try {
    detector = new window.BarcodeDetector({ formats: ["qr_code"] });
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } },
      audio: false,
    });
    scanning.value = true;
    if (videoEl.value) {
      videoEl.value.srcObject = mediaStream;
      await videoEl.value.play();
    }
    scanFrame = requestAnimationFrame(scanFrameLoop);
  } catch (err) {
    stopCamera();
    error.value = err.message || "Camera is not available.";
  }
}

onMounted(loadBranches);
onUnmounted(stopCamera);
</script>

<template>
  <AppShell>
    <PageHeader eyebrow="Front desk" title="Check-in" lede="Search a member or scan a QR token. Eligibility is decided on the server." />
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="message" class="ok">{{ message }}</p>
    <form class="row" @submit.prevent="findMembers">
      <input v-model="search" placeholder="Name, phone, or member ID" />
      <button type="submit">Find</button>
    </form>
    <label>
      Member
      <select v-model="selectedMember">
        <option disabled value="">Select member</option>
        <option v-for="m in members" :key="m.id" :value="m.id">{{ m.full_name }} ({{ m.member_code }})</option>
      </select>
    </label>
    <label>
      Branch
      <select v-model="selectedBranch">
        <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </label>
    <button type="button" :disabled="!selectedMember || !selectedBranch" @click="checkIn">Check in</button>

    <h2>QR check-in</h2>
    <form class="row" @submit.prevent="checkInFromToken()">
      <input v-model="qrPayload" placeholder="gymportal:member:…" autocomplete="off" />
      <button type="submit" :disabled="!qrPayload.trim() || !selectedBranch">Check in from token</button>
    </form>
    <p v-if="!canScanQr" class="note">This browser cannot scan a QR code. Paste the check-in token from the member portal.</p>
    <div v-else class="row">
      <button type="button" :disabled="!selectedBranch || scanning" @click="startScan">Scan QR</button>
      <button v-if="scanning" type="button" @click="stopCamera">Stop camera</button>
    </div>
    <video ref="videoEl" class="preview" autoplay muted playsinline v-show="scanning"></video>
  </AppShell>
</template>

<style scoped>
.preview {
  display: block;
  width: 100%;
  max-width: 20rem;
  margin-bottom: 1rem;
  background: #111;
}
</style>
