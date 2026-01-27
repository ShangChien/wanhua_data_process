<template>
  <div :class="['flex', 'justify-center', 'items-center']">
    <div :class="['w-[400px]', 'h-[400px]']">
      <VChart :option="option" autoresize />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, shallowRef, watchEffect } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { BarChart } from "echarts/charts";
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { ComposeOption } from "echarts/core";
import type { BarSeriesOption } from "echarts/charts";
import type {
  TooltipComponentOption,
  LegendComponentOption,
  GridComponentOption,
} from "echarts/components";
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { isEmpty } from "lodash";

use([
  TooltipComponent,
  LegendComponent,
  GridComponent,
  BarChart,
  CanvasRenderer,
]);

type EChartsOption = ComposeOption<
  | TooltipComponentOption
  | LegendComponentOption
  | GridComponentOption
  | BarSeriesOption
>;
const getData = () => {
  return {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        // Use axis to trigger tooltip
        type: "shadow", // 'shadow' as default; can also be 'line' or 'shadow'
      },
    },
    legend: {},
    grid: {
      // left: "3%",
      right: "20%",
      // left: "20%",
      bottom: "20%",
      containLabel: true,
    },
    xAxis: {
      type: "value",
      splitLine: { show: false },
      axisLine: {
        show: true,
        onZero: false,
      },
      name: "Count",
    },
    yAxis: {
      type: "category",
      data: ["0", "1", "2", "3", "4", "5"],
      splitLine: { show: false },
      axisLine: {
        show: true,
        onZero: false,
      },
      name: "Categories",
    },
    series: [],
  };
};
const option = shallowRef(getData());
const taskDetailStore = useTaskDetailStore();
watchEffect(() => {
  // const data = {
  //   ML01: {
  //     TARGET: {
  //       total: {
  //         tp: [7, 0, 0, 7, 1, 0],
  //         fp: [18, 2, 1, 7, 7, 0],
  //         fn: [5, 8, 5, 7, 6, 4],
  //       },
  //     },
  //   },
  //   ML02: {
  //     TARGET: {
  //       total: {
  //         tp: [5, 0, 0, 9, 0, 0],
  //         fp: [9, 2, 0, 25, 0, 0],
  //         fn: [7, 8, 5, 5, 7, 4],
  //       },
  //     },
  //   },
  //   ML03: {
  //     TARGET: {
  //       total: {
  //         tp: [8, 1, 2, 11, 0, 0],
  //         fp: [12, 2, 1, 10, 3, 0],
  //         fn: [4, 7, 3, 3, 7, 4],
  //       },
  //     },
  //   },
  //   ML04: {
  //     TARGET: {
  //       total: {
  //         tp: [2, 0, 0, 9, 0, 0],
  //         fp: [10, 3, 0, 26, 0, 0],
  //         fn: [10, 8, 5, 5, 7, 4],
  //       },
  //     },
  //   },
  //   NN01: {
  //     TARGET: {
  //       total: {
  //         tp: [2, 3, 0, 10, 0, 0],
  //         fp: [1, 11, 0, 23, 0, 0],
  //         fn: [10, 5, 5, 4, 7, 4],
  //       },
  //     },
  //   },
  //   NN02: {
  //     TARGET: {
  //       total: {
  //         tp: [7, 2, 0, 4, 0, 0],
  //         fp: [15, 9, 0, 12, 1, 0],
  //         fn: [5, 6, 5, 10, 7, 4],
  //       },
  //     },
  //   },
  //   NN03: {
  //     TARGET: {
  //       total: {
  //         tp: [7, 1, 0, 8, 2, 0],
  //         fp: [3, 8, 7, 6, 6, 2],
  //         fn: [5, 7, 5, 6, 5, 4],
  //       },
  //     },
  //   },
  //   Ensemble: {
  //     TARGET: {
  //       total: {
  //         tp: [7, 0, 0, 14, 0, 0],
  //         fp: [10, 3, 0, 16, 0, 0],
  //         fn: [5, 8, 5, 0, 7, 4],
  //       },
  //     },
  //   },
  // } as any;
  if (
    taskDetailStore.currentTarget &&
    taskDetailStore.currentSelfModel &&
    !isEmpty(taskDetailStore.selfModelDetail)
  ) {
    const currentModelDetail =
      taskDetailStore.selfModelDetail[taskDetailStore.currentSelfModel][
        taskDetailStore.currentTarget
      ];
    option.value = {
      ...option.value,
      series: Object.keys(currentModelDetail.total).map((item: any) => {
        return {
          name: item.toUpperCase(),
          type: "bar",
          stack: "total",
          label: {
            show: true,
            formatter: function (params: any) {
              // params.value 是当前数据项的值
              // 如果值为 0，则不显示标签
              if (params.value == 0) {
                return "";
              }
              // 否则，显示该值
              return params.value;
            },
          },
          emphasis: {
            focus: "series",
          },
          data: currentModelDetail.total[item],
        };
      }) as any,
    };
  }
});
</script>

<style lang="scss" scoped></style>
