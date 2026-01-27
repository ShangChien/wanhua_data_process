<template>
  <div :class="['w-[1px]', 'flex-1', 'min-h-[600px]']">
    <Transition>
      <div
        :key="renderKey"
        :class="[
          'sticky',
          'top-[70px]',
          'overflow-auto',
          'rounded-xl',
          'bg-gradient-to-br',
          'px-4',
          'py-5',
          'ring-1',
          'ring-blue-100/70',
          'md:px-6',
          'md:py-8',
        ]"
      >
        <div v-for="item in props.descList">
          <template v-for="detail in item.desc">
            <div :class="['text-value']">{{ detail.label }}</div>
            <div :class="['text-label']" v-html="detail.value"></div>
          </template>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script lang="ts" setup>
import { uniqueId } from "lodash";
import { computed, ref, watchEffect } from "vue";

const props = defineProps<{
  title?: string;
  descList: {
    title: string;
    desc: {
      label: string;
      value: string;
    }[];
  }[];
}>();

const renderKey = computed(() => {
  const b = props.descList;
  return uniqueId();
});
</script>

<style lang="scss" scoped>
.v-enter-active,
.v-leave-active {
  transition: all 0.25s linear;
}

.v-enter-from {
  opacity: 0;
  transform: translateY(60px);
}
.v-leave-to {
  opacity: 0;
  transform: translateY(-60px);
}
</style>
