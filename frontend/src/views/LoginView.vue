<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const email = ref("");
const password = ref("");
const error = ref("");
const submitting = ref(false);

async function onSubmit() {
  error.value = "";
  submitting.value = true;
  try {
    await auth.login(email.value, password.value);
    const next = typeof route.query.next === "string" ? route.query.next : "/";
    await router.replace(next);
  } catch (err) {
    error.value = err.message || "Invalid email or password.";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <main class="auth-screen">
    <section class="auth-hero" aria-hidden="true"></section>
    <section class="auth-panel">
      <div class="auth-card">
        <p class="label-caps">Apex Pulse</p>
        <h1>Sign in</h1>
        <p class="lede">Staff and member access to gym operations.</p>
        <form @submit.prevent="onSubmit">
          <label>
            Email
            <input v-model="email" type="email" autocomplete="username" required />
          </label>
          <label>
            Password
            <input v-model="password" type="password" autocomplete="current-password" required />
          </label>
          <p v-if="error" class="error" role="alert">{{ error }}</p>
          <button type="submit" :disabled="submitting">
            {{ submitting ? "Signing in…" : "Sign in" }}
          </button>
        </form>
      </div>
    </section>
  </main>
</template>
