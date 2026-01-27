<template>
  <svg v-if="['RUNNING'].includes(props.type)" class="button-iconpark-icon">
    <use href="#running-status"></use>
  </svg>
  <svg v-else-if="props.type === 'FINISHED'" class="button-iconpark-icon">
    <use href="#success-status"></use>
  </svg>
  <svg v-else-if="props.type === 'FAILED'" class="button-iconpark-icon">
    <use href="#error-status"></use>
  </svg>
  <svg v-else-if="props.type === 'SCHEDULED'" class="button-iconpark-icon">
    <use href="#pending-status"></use>
  </svg>
  <Icon
    width="16"
    height="16"
    class="button-iconpark-icon"
    v-else
    icon="emojione:pause-button"
  />
</template>

<script lang="ts" setup>
import { Icon } from "@iconify/vue";
const props = defineProps<{
  type: "SCHEDULED" | "KILLED" | "FINISHED" | "FAILED" | "RUNNING";
}>();
</script>

<style lang="scss" scoped></style>
