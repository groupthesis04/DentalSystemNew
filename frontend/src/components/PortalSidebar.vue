<script setup>
import { LogOut } from "lucide-vue-next";

import AvatarBadge from "./AvatarBadge.vue";

defineProps({
  user: { type: Object, required: true },
  roleLabel: { type: String, required: true },
  items: { type: Array, required: true },
  active: { type: String, required: true },
});
const emit = defineEmits(["select", "logout"]);
</script>

<template>
  <aside class="profile-sidebar" :aria-label="`${roleLabel} navigation`">
    <button
      class="sidebar-brand"
      type="button"
      title="Dashboard"
      aria-label="Open dashboard"
      @click="emit('select', items[0]?.id)"
    >
      <img src="/assets/logo.png" alt="" />
      <span>BORJA</span>
    </button>
    <nav class="side-nav">
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        :class="{ active: active === item.id }"
        :title="item.label"
        :aria-current="active === item.id ? 'page' : undefined"
        @click="emit('select', item.id)"
      >
        <span class="sidebar-icon-wrap">
          <component :is="item.icon" class="nav-icon" :size="21" aria-hidden="true" />
        </span>
        <span>{{ item.shortLabel || item.label }}</span>
      </button>
    </nav>
    <div class="sidebar-account" :title="`${user.name} - ${roleLabel}`">
      <AvatarBadge :name="user.name" :image="user.profile_image" />
      <span class="sr-only">{{ user.name }}, {{ roleLabel }}</span>
    </div>
    <button
      class="sidebar-logout"
      type="button"
      title="Log out"
      aria-label="Log out"
      @click="emit('logout')"
    >
      <LogOut :size="20" aria-hidden="true" />
      <span>Logout</span>
    </button>
  </aside>
</template>
