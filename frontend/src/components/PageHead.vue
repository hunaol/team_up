<script setup>
defineProps({
  crumbs: { type: Array, default: () => [] },
  title: { type: String, default: '' },
  desc: { type: String, default: '' }
})
</script>

<template>
  <div class="page-head">
    <div>
      <div v-if="crumbs.length" class="crumbs">
        <template v-for="(c, i) in crumbs" :key="i">
          <router-link v-if="c.to" :to="c.to">{{ c.label }}</router-link>
          <span v-else>{{ c.label }}</span>
          <span v-if="i < crumbs.length - 1" class="sep">/</span>
        </template>
      </div>
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="desc" class="page-desc">{{ desc }}</p>
    </div>
    <div v-if="$slots.actions" class="page-head-actions">
      <slot name="actions" />
    </div>
  </div>
</template>
