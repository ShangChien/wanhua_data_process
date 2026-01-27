<template>
  <div :class="['flex', 'flex-row', 'gap-4']">
    <div v-for="item in props.list" :class="['flex-1']">
      <div :class="['text-xl']" :title="item.label">
        {{ formatterScienceNumber(item.label) }}
      </div>
      <ElDivider :class="['m-0']" />
      <div
        :class="['text-lg', 'text-[#0009]']"
        v-html="formatParamLabel(item.value)"
      ></div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ElDivider } from "element-plus";
import { ref } from "vue";
import { formatParamLabel, formatterScienceNumber } from "@/utils/formatter";

const props = defineProps<{
  list: {
    label: string;
    value: string;
  }[];
}>();
const list = ref<any>([]);

// watchEffect(() => {
//   if (taskDetailStore.metricsData.length) {
//     list.value = Object.entries(taskDetailStore.metricsData[0]).filter(
//       (item) => {
//         return !["Index", "Models", "Features"].includes(item[0]);
//       }
//     );
//   }
// });
</script>

<style lang="scss" scoped></style>
