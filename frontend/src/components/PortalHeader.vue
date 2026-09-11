<script setup>
import { Moon, Sun } from "lucide-vue-next";

import { dashboardTheme, toggleDashboardTheme } from "../services/theme";
import NotificationMenu from "./NotificationMenu.vue";

defineProps({
  mode: { type: String, required: true },
  title: { type: String, default: "" },
  subtitle: { type: String, default: "" },
});
const emit = defineEmits(["open-notification"]);
</script>

<template>
  <header class="site-header portal-header">
    <div class="portal-context">
      <strong>{{ mode === "doctor" ? "Clinic Operations" : title }}</strong>
      <span>{{ mode === "doctor" ? "Dental management workspace" : subtitle }}</span>
    </div>
    <div class="portal-header-spacer" aria-hidden="true"></div>
    <div class="auth-actions">
      <NotificationMenu @open-target="emit('open-notification', $event)" />
      <button
        class="theme-toggle-button"
        type="button"
        :aria-label="dashboardTheme === 'dark' ? 'Use light theme' : 'Use dark theme'"
        :aria-pressed="dashboardTheme === 'dark'"
        :title="dashboardTheme === 'dark' ? 'Use light theme' : 'Use dark theme'"
        @click="toggleDashboardTheme"
      >
        <Sun v-if="dashboardTheme === 'dark'" :size="20" aria-hidden="true" />
        <Moon v-else :size="20" aria-hidden="true" />
      </button>
    </div>
  </header>
</template>
