import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { authApi, clearAccessToken, setAccessToken } from "../api/client";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const bootstrapped = ref(false);

  const isAuthenticated = computed(() => Boolean(user.value));
  const role = computed(() => user.value?.role || null);

  async function login(email, password) {
    const data = await authApi.login(email, password);
    setAccessToken(data.access);
    user.value = data.user;
    return data.user;
  }

  async function logout() {
    try {
      await authApi.logout();
    } finally {
      clearAccessToken();
      user.value = null;
    }
  }

  async function bootstrap() {
    if (bootstrapped.value) return;
    try {
      await authApi.refresh();
      user.value = await authApi.me();
    } catch {
      clearAccessToken();
      user.value = null;
    } finally {
      bootstrapped.value = true;
    }
  }

  function canSeeStaffNav() {
    return ["OWNER", "STAFF_ADMIN", "TRAINER"].includes(role.value);
  }

  function canSeeFrontDeskNav() {
    return ["OWNER", "STAFF_ADMIN"].includes(role.value);
  }

  return {
    user,
    bootstrapped,
    isAuthenticated,
    role,
    login,
    logout,
    bootstrap,
    canSeeStaffNav,
    canSeeFrontDeskNav,
  };
});
