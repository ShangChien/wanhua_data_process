<template>
  <div :class="['flex', 'items-center', props.vertical ? 'flex-col' : '']">
    <span :class="['text-label', 'mr-2']">
      {{ props.label }}
    </span>
    <span :class="['text-value']">
      <slot name="value">
        {{ props.value }}
      </slot>
    </span>
  </div>
</template>

<script lang="ts" setup>
const props = defineProps<{
  label: string;
  value: string | undefined;
  vertical?: boolean;
}>();
</script>

<style lang="scss" scoped></style>
