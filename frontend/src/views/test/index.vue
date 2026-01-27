<template>
  <div :class="['w-full', 'h-96']">
    <VChart :option="option" theme="ovilia-green" autoresize />
  </div>
</template>
<script setup lang="ts">
import { use, registerTheme } from "echarts/core";
import { BarChart } from "echarts/charts";
import { GridComponent, DatasetComponent } from "echarts/components";
import { shallowRef, onBeforeUnmount } from "vue";
import VChart from "vue-echarts";
import { CanvasRenderer } from "echarts/renderers";
import { getDistributionInfo } from "@/service/api/model";
import { useRoute } from "vue-router";

use([BarChart, DatasetComponent, GridComponent, CanvasRenderer]);
function getData() {
  return {
    xAxis: {
      type: "value",
    },
    yAxis: { type: "value" },
    tooltip: {
      trigger: "axis",
    },
    // Declare several bar series, each will be mapped
    // to a column of dataset.source by default.
    series: [
      {
        type: "bar",
        encode: {
          x: [0, 1],
          y: [2],
        },
        tooltip: [0, 1, 2],
        data: [],
      },
    ],
  };
}
const route = useRoute();

const option = shallowRef(getData());
// getDistributionInfo({ run_id: route.query.taskId as string }).then((res) => {
//   const newData = getData();
//   const data = {
//     TARGET: {
//       x: [
//         "(0.00278, 0.101]",
//         "(0.101, 0.198]",
//         "(0.198, 0.295]",
//         "(0.295, 0.392]",
//         "(0.392, 0.489]",
//         "(0.489, 0.586]",
//         "(0.586, 0.683]",
//         "(0.683, 0.78]",
//         "(0.78, 0.877]",
//         "(0.877, 0.974]",
//       ],
//       y: [6, 5, 7, 8, 6, 4, 1, 7, 2, 4],
//     },
//   };

//   newData.series[0].data = data.TARGET.x.map((item, index) => [
//     +item.split(",")[0].slice(1),
//     +item.split(",")[1].slice(0, -1),
//     data.TARGET.y[index],
//   ]) as any;
//   option.value = newData;
//   // option.value.series[0].data = res.data.data.TARGET;
//   // console.log(res.data.data.TARGET, option.value.series[0]);
// });
const newData = getData();
const data = {
  TARGET: {
    x: [
      "(0.00278, 0.101]",
      "(0.101, 0.198]",
      "(0.198, 0.295]",
      "(0.295, 0.392]",
      "(0.392, 0.489]",
      "(0.489, 0.586]",
      "(0.586, 0.683]",
      "(0.683, 0.78]",
      "(0.78, 0.877]",
      "(0.877, 0.974]",
    ],
    y: [6, 5, 7, 8, 6, 4, 1, 7, 2, 4],
  },
};

newData.series[0].data = data.TARGET.x.map((item, index) => [
  +item.split(",")[0].slice(1),
  +item.split(",")[1].slice(0, -1),
  data.TARGET.y[index],
]) as any;
option.value = newData;
</script>
