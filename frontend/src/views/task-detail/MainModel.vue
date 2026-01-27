<template>
  <div :class="['flex', 'flex-row', 'gap-4']">
    <div v-for="item in list" :class="['flex-1']">
      <div :class="['text-xl']" :title="item[1]">
        {{ formatterScienceNumber(item[1]) }}
      </div>
      <ElDivider :class="['m-0']" />
      <div
        :class="['text-lg', 'text-[#0009]']"
        v-html="formatParamLabel(item[0])"
      ></div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { ElDivider } from "element-plus";
import { ref, watchEffect } from "vue";
import { formatParamLabel, formatterScienceNumber } from "@/utils/formatter";
const taskDetailStore = useTaskDetailStore();

const list = ref<any>([]);

watchEffect(() => {
  if (taskDetailStore.metricsData.length) {
    list.value = Object.entries(taskDetailStore.metricsData[0]).filter(
      (item) => {
        return !["Index", "Models", "Features"].includes(item[0]);
      }
    );
  }
});
</script>

<style lang="scss" scoped></style>
