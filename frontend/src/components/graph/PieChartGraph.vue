<template>
  <VChart :option="option" autoresize />
</template>

<script lang="ts" setup>
import type { PieSeriesOption } from "echarts/charts";
import { PieChart } from "echarts/charts";
import type {
  LegendComponentOption,
  TitleComponentOption,
  TooltipComponentOption,
} from "echarts/components";
import {
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from "echarts/components";
import type { ComposeOption } from "echarts/core";
import { use } from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import { shallowRef, watchEffect } from "vue";
import VChart from "vue-echarts";

const props = defineProps<{ data: any }>();

use([TitleComponent, TooltipComponent, LegendComponent, PieChart, SVGRenderer]);

type EChartsOption = ComposeOption<
  | TitleComponentOption
  | TooltipComponentOption
  | LegendComponentOption
  | PieSeriesOption
>;
const option = shallowRef({
  title: {
    left: "center",
  },
  tooltip: {},
  legend: {
    orient: "vertical",
    left: "left",
  },
  series: [
    {
      name: "predict",
      type: "pie",
      radius: "50%",
      data: props.data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          //   shadowColor: "rgba(0, 0, 0, 0.5)",
        },
      },
    },
  ],
});
watchEffect(() => {
  option.value.series[0].data = props.data;
  option.value = { ...option.value };
});
</script>

<style lang="scss" scoped></style>
