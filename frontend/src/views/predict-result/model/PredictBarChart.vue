<template>
  <VChart :option="option" autoresize />
  <div
    :class="['flex', 'items-center', 'relative', 'bottom-[100px]', 'w-full']"
  >
    <span :class="['mr-3']"> bins </span>
    <ElSlider
      :show-tooltip="false"
      :class="['flex-1']"
      v-model="binsCount"
      :debounce="300"
      :min="1"
      :max="50"
      :step="1"
    />
  </div>
</template>

<script lang="ts" setup>
import { getDistributionInfo } from "@/service/api/model";
import { bin } from "d3-array";
import { BarChart, ScatterChart } from "echarts/charts";
import {
  DatasetComponent,
  GridComponent,
  TooltipComponent,
  TransformComponent,
} from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { ElSlider } from "element-plus";
import { ref, shallowRef, watchEffect } from "vue";
import VChart from "vue-echarts";
import { useRoute } from "vue-router";
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
const props = defineProps<{ data: any }>();
function getOption() {
  return {
    grid: {
      bottom: "30%",
    },
    tooltip: {},
    xAxis: {
      type: "value",
      scale: true,
      axisTick: { show: true },
      axisLabel: { show: true },
      axisLine: { show: true },
      // min: 0,
      // max: 1,
    },
    yAxis: {},
    series: [
      {
        name: "histogram",
        type: "bar",
        data: [],
        barWidth: "100%",
        label: {
          show: true,
          position: "top",
          formatter: function (params: any) {
            // params.value 是当前数据项的值
            // 如果值为 0，则不显示标签
            if (params.value[1] === 0) {
              return "";
            }
            // 否则，显示该值
            return params.value[1];
          },
        },

        encode: { x: 0, y: 1, itemName: 2 },
      },
    ],
  };
}

const route = useRoute();
use([
  DatasetComponent,
  TooltipComponent,
  GridComponent,
  TransformComponent,
  ScatterChart,
  BarChart,
  CanvasRenderer,
]);
const option = shallowRef(getOption());
const binsCount = ref(10);
watchEffect(() => {
  const curTargetDistribution = props.data.map((item: any) => item.name);
  if (curTargetDistribution && curTargetDistribution.length) {
    const data = curTargetDistribution;
    const minValue = Math.min(...data);
    const maxValue = Math.max(...data);
    const minRounded = Math.floor(minValue);
    const maxRounded = Math.ceil(maxValue) + 1;

    const histoGenerator = bin()
      .value((d: number) => +d) // 设置数据访问器
      .thresholds(binsCount.value); // 设置分箱的数量（或自定义阈值数组）
    const bins1 = histoGenerator(data).map((item: any) => [
      ((item.x0 + item.x1) / 2).toFixed(5),
      item.length,
      `[${item.x0},${item.x1})`,
      item.x0,
      item.x1,
    ]);
    // var bins = (ecStat as any).histogram(data);
    // bins.data.forEach((item: any) => {
    //   item[0] = ((item[2] + item[3]) / 2).toFixed(5);
    // });

    const newData: any = getOption();
    newData.xAxis.min = bins1[0][3];
    newData.xAxis.max = bins1[bins1.length - 1][4];
    newData.series[0].data = bins1;
    option.value = newData;
  }
});
</script>

<style lang="scss" scoped></style>
