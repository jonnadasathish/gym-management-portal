<script setup>
defineProps({
  eyebrow: { type: String, default: "Operations" },
  title: { type: String, required: true },
  lede: { type: String, default: "" },
});
</script>

<template>
  <header class="page-head">
    <p class="label-caps">{{ eyebrow }}</p>
    <h1>{{ title }}</h1>
    <p v-if="lede" class="lede">{{ lede }}</p>
  </header>
</template>
