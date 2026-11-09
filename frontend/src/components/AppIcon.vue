<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 18 },
  stroke: { type: [Number, String], default: 1.7 }
})

/* 统一 24×24 线性图标，风格与设计稿一致 */
const ICONS = {
  home: '<path d="M4 10.5 12 4l8 6.5"/><path d="M6 9.8V19a1 1 0 0 0 1 1h3.5v-5h3V20H17a1 1 0 0 0 1-1V9.8"/>',
  compass:
    '<circle cx="12" cy="12" r="8.2"/><path d="m15.4 8.6-1.9 4.9-4.9 1.9 1.9-4.9 4.9-1.9Z"/>',
  megaphone:
    '<path d="M4 10v4a1 1 0 0 0 1 1h2.2l5.6 3.6a1 1 0 0 0 1.5-.9V6.3a1 1 0 0 0-1.5-.9L7.2 9H5a1 1 0 0 0-1 1Z"/><path d="M18 9.4a3.4 3.4 0 0 1 0 5.2"/>',
  file: '<path d="M13.5 3.5H7a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9l-5.5-5.5Z"/><path d="M13.5 3.5V9H19"/><path d="M9 13h6M9 16.5h4"/>',
  bookmark: '<path d="M6.5 4.5h11a1 1 0 0 1 1 1V20l-6.5-4-6.5 4V5.5a1 1 0 0 1 1-1Z"/>',
  chart: '<path d="M4 19V5"/><path d="M4 19h16"/><path d="m7.5 15 3.2-3.8 3 2.6L19 8.5"/><circle cx="19" cy="8.5" r="1.4"/>',
  users:
    '<circle cx="9.5" cy="8.5" r="3.2"/><path d="M3.8 19.2a5.7 5.7 0 0 1 11.4 0"/><path d="M16.4 5.6a3 3 0 0 1 0 5.8"/><path d="M17.6 14.2a5.4 5.4 0 0 1 3.1 4.6"/>',
  list: '<path d="M8 6.5h12M8 12h12M8 17.5h12"/><circle cx="4.3" cy="6.5" r="1.1"/><circle cx="4.3" cy="12" r="1.1"/><circle cx="4.3" cy="17.5" r="1.1"/>',
  search: '<circle cx="10.8" cy="10.8" r="6.3"/><path d="m15.6 15.6 4.1 4.1"/>',
  bell: '<path d="M18 9a6 6 0 1 0-12 0c0 5-2 6.5-2 6.5h16S18 14 18 9Z"/><path d="M10.3 19a2 2 0 0 0 3.4 0"/>',
  logout: '<path d="M15 5.5h3a1.5 1.5 0 0 1 1.5 1.5v10a1.5 1.5 0 0 1-1.5 1.5h-3"/><path d="M10.5 8.5 7 12l3.5 3.5"/><path d="M7 12h9"/>',
  plus: '<path d="M12 5.5v13M5.5 12h13"/>',
  edit: '<path d="M16.3 4.6a2 2 0 0 1 2.8 2.8L8.4 18.1l-4 .9.9-4L16.3 4.6Z"/>',
  trash: '<path d="M4.8 6.8h14.4"/><path d="M9.4 6.8V5.2a1 1 0 0 1 1-1h3.2a1 1 0 0 1 1 1v1.6"/><path d="M6.6 6.8 7.5 19a1 1 0 0 0 1 .9h7a1 1 0 0 0 1-.9l.9-12.2"/>',
  chevronLeft: '<path d="m14.5 6-6 6 6 6"/>',
  chevronRight: '<path d="m9.5 6 6 6-6 6"/>',
  chevronDown: '<path d="m6 9.5 6 6 6-6"/>',
  close: '<path d="m6.5 6.5 11 11M17.5 6.5l-11 11"/>',
  check: '<path d="m5.5 12.5 4.2 4.2L18.5 8"/>',
  image:
    '<rect x="3.6" y="5" width="16.8" height="14" rx="2.4"/><circle cx="8.6" cy="10" r="1.5"/><path d="m4.5 16.8 4.3-4.2a1.4 1.4 0 0 1 2 0l3 2.9 1.5-1.4a1.4 1.4 0 0 1 1.9 0l2.3 2.2"/>',
  bold: '<path d="M7.5 4.8h5.2a3.6 3.6 0 0 1 0 7.2H7.5Z"/><path d="M7.5 12h5.9a3.6 3.6 0 0 1 0 7.2H7.5Z"/>',
  italic: '<path d="M10.5 4.8h7M6.5 19.2h7M14.2 4.8 9.8 19.2"/>',
  underline: '<path d="M7 4.8v6.4a5 5 0 0 0 10 0V4.8"/><path d="M5.8 19.4h12.4"/>',
  more: '<circle cx="12" cy="5.4" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="18.6" r="1.5"/>',
  eye: '<path d="M2.8 12S6.2 6.2 12 6.2 21.2 12 21.2 12 17.8 17.8 12 17.8 2.8 12 2.8 12Z"/><circle cx="12" cy="12" r="2.8"/>',
  heart: '<path d="M12 19.3s-7.4-4.5-7.4-9.4a4.2 4.2 0 0 1 7.4-2.7 4.2 4.2 0 0 1 7.4 2.7c0 4.9-7.4 9.4-7.4 9.4Z"/>',
  calendar:
    '<rect x="3.8" y="5.5" width="16.4" height="15" rx="2.4"/><path d="M8 3.5v4M16 3.5v4M3.8 10.4h16.4"/>',
  user: '<circle cx="12" cy="8.2" r="3.7"/><path d="M4.8 20.2a7.4 7.4 0 0 1 14.4 0"/>',
  filter: '<path d="M4.5 6h15l-5.8 7v5.4l-3.4 1.6V13L4.5 6Z"/>',
  arrowRight: '<path d="M4.8 12h14M13.5 6.8l5.3 5.2-5.3 5.2"/>',
  refresh: '<path d="M19.4 12a7.4 7.4 0 1 1-2.2-5.2"/><path d="M19.6 4.6v4.2h-4.2"/>',
  alert: '<circle cx="12" cy="12" r="8.4"/><path d="M12 7.8v4.8"/><circle cx="12" cy="16.2" r="1"/>',
  lock: '<rect x="4.8" y="10.2" width="14.4" height="9.6" rx="2.2"/><path d="M8.4 10.2V7.8a3.6 3.6 0 0 1 7.2 0v2.4"/>',
  building:
    '<path d="M3.8 20.2V6.4a1 1 0 0 1 1-1h6.4a1 1 0 0 1 1 1v13.8"/><path d="M12.2 20.2V10h6a1 1 0 0 1 1 1v9.2"/><path d="M3 20.2h18"/><path d="M6.4 9h2.6M6.4 12.6h2.6M6.4 16.2h2.6M15 13.4h1.8M15 16.6h1.8"/>',
  trend: '<path d="M4 16.5 9.2 11l3.4 3.2L20 7.4"/><path d="M15.4 7.4H20v4.6"/>',
  sparkles:
    '<path d="m12 4 1.7 4.4L18 10l-4.3 1.6L12 16l-1.7-4.4L6 10l4.3-1.6L12 4Z"/><path d="M18.2 15.4 19 17.4l2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2Z"/>',
  link: '<path d="M10.2 13.8a3.6 3.6 0 0 0 5.1 0l2.6-2.6a3.6 3.6 0 0 0-5.1-5.1l-1.4 1.4"/><path d="M13.8 10.2a3.6 3.6 0 0 0-5.1 0l-2.6 2.6a3.6 3.6 0 0 0 5.1 5.1l1.4-1.4"/>',
  clock: '<circle cx="12" cy="12" r="8.4"/><path d="M12 7.6V12l3 1.8"/>',
  send: '<path d="M20.2 3.8 10.6 13.4"/><path d="M20.2 3.8 14 20.2l-3.4-6.8-6.8-3.4L20.2 3.8Z"/>',
  shield: '<path d="M12 3.6 5 6.4v5.4c0 4.2 2.9 7.4 7 8.6 4.1-1.2 7-4.4 7-8.6V6.4L12 3.6Z"/><path d="m9.2 12 2 2 3.6-3.8"/>',
  grid: '<rect x="4" y="4" width="6.6" height="6.6" rx="1.6"/><rect x="13.4" y="4" width="6.6" height="6.6" rx="1.6"/><rect x="4" y="13.4" width="6.6" height="6.6" rx="1.6"/><rect x="13.4" y="13.4" width="6.6" height="6.6" rx="1.6"/>',
  flag: '<path d="M6 20.4V4.6"/><path d="M6 5.4h9.6l-1.6 3.4 1.6 3.4H6"/>',
  download: '<path d="M12 4.6v10.8"/><path d="m7.8 11.4 4.2 4.2 4.2-4.2"/><path d="M5 19.4h14"/>',
  phone: '<path d="M7.4 4.6h2.2l1.4 3.6-1.8 1.4a10.4 10.4 0 0 0 5.2 5.2l1.4-1.8 3.6 1.4v2.2a2 2 0 0 1-2.2 2A15.4 15.4 0 0 1 5.4 6.8a2 2 0 0 1 2-2.2Z"/>',
  chat: '<path d="M20.2 11.4a7.6 7.6 0 0 1-8.2 7.6 8.8 8.8 0 0 1-2.6-.5L4.6 20l1.4-4.2a7.4 7.4 0 0 1-1-3.8 7.6 7.6 0 0 1 7.6-7.4 7.6 7.6 0 0 1 7.6 6.8Z"/>',
  at: '<circle cx="12" cy="12" r="7.6"/><circle cx="12" cy="12" r="2.8"/><path d="M15 9.2v3.6a2.4 2.4 0 0 0 4.4 1.3"/>'
}

const inner = computed(() => ICONS[props.name] || ICONS.grid)
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="stroke"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    v-html="inner"
  />
</template>
