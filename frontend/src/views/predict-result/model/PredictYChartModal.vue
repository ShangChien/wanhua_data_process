<template>
  <ElDialog
    :lock-scroll="true"
    :title="props.title"
    v-model="dialogVisible"
    :before-close="props.handleOK"
  >
    <div :class="['flex', 'items-center', 'justify-center']">
      <div
        :class="[
          'h-[500px]',
          'w-[500px]',
          'flex',
          'flex-col',
          'items-center',
          'justify-center',
        ]"
      >
        <PredictPieChart
          v-if="props.chartType === 'pie'"
          :data="props.chartData"
        />
        <PredictBarChart :data="props.chartData" v-else />
      </div>
    </div>
  </ElDialog>
</template>

<script lang="ts" setup>
import { ElDialog } from "element-plus";
import PredictPieChart from "./PredictPieChart.vue";
import PredictBarChart from "./PredictBarChart.vue";
import { onMounted, ref } from "vue";
const dialogVisible = ref(false);
onMounted(() => {
  dialogVisible.value = true;
});
const props = defineProps<{
  chartData: any;
  handleOK: any;
  handleCancel: any;
  chartType: "pie" | "bar";
  title: string;
}>();
</script>

<style lang="scss" scoped></style>
