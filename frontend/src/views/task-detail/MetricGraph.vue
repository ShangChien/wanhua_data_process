<template>
  <div :class="['flex', 'flex-col', 'items-center']">
    <div :class="['chart-wrapper']">
      <VChart :option="option" autoresize />
    </div>
    <div :class="['relative', 'bottom-[80px]']">
      <ElRadioGroup v-model="selectFold" size="small">
        <ElRadioButton :value="'0'">Fold 0</ElRadioButton>
        <ElRadioButton :value="'1'">Fold 1</ElRadioButton>
        <ElRadioButton :value="'2'">Fold 2</ElRadioButton>
        <ElRadioButton :value="'3'">Fold 3</ElRadioButton>
        <ElRadioButton :value="'4'">Fold 4</ElRadioButton>
        <ElRadioButton value="total">Total</ElRadioButton>
      </ElRadioGroup>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import type { LineSeriesOption } from "echarts/charts";
import { LineChart } from "echarts/charts";
import type {
  GridComponentOption,
  TitleComponentOption,
  TooltipComponentOption,
} from "echarts/components";
import {
  GridComponent,
  TitleComponent,
  TooltipComponent,
  DataZoomComponent,
} from "echarts/components";
import type { ComposeOption } from "echarts/core";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { ElOption, ElRadioButton, ElRadioGroup, ElSelect } from "element-plus";
import { isEmpty } from "lodash";
import { ref, shallowRef, watchEffect } from "vue";
import VChart from "vue-echarts";
import { useRoute } from "vue-router";
const taskDetailStore = useTaskDetailStore();
const route = useRoute();

use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DataZoomComponent,
  LineChart,
  CanvasRenderer,
]);

type EChartsOption = ComposeOption<
  | TitleComponentOption
  | TooltipComponentOption
  | GridComponentOption
  | LineSeriesOption
>;

interface DataItem {
  l: number;
  u: number;
  date: string;
  value: number;
}
// const
const selectFold = ref("total");

watchEffect(() => {
  if (
    taskDetailStore.currentSelfModel &&
    !isEmpty(taskDetailStore.selfModelDetail) &&
    taskDetailStore.currentTarget
  ) {
    const data =
      taskDetailStore.selfModelDetail[taskDetailStore.currentSelfModel];
    const list = [];
    const keysList = Object.keys(data[taskDetailStore.currentTarget]);

    for (let i = 0; i < keysList.length; i++) {
      const foldKey = keysList[i];
      const curData = (data[taskDetailStore.currentTarget] as any)[foldKey];
      if (foldKey === selectFold.value) {
        if (
          foldKey === "total" ||
          taskDetailStore.currentSelfModel === "Ensemble"
        ) {
          if (!Array.isArray(curData)) {
            list.push({
              name: `${foldKey}`,
              symbol: "none",
              data: curData.x.map((item: any, idx: string | number) => [
                item,
                curData.y[idx],
              ]),
              type: "line",
              itemStyle: {},
            });
          } else {
            list.push({
              name: `${foldKey}`,
              symbol: "none",
              data: curData[0].x.map((item: any, idx: string | number) => [
                item,
                curData[0].y[idx],
              ]),
              type: "line",
              itemStyle: {},
            });
          }
        } else {
          list.push({
            name: `${foldKey} train`,
            symbol: "none",
            data: curData.train.x.map((item: any, idx: string | number) => [
              item,
              curData.train.y[idx],
            ]),
            type: "line",
            itemStyle: {},
          });
          list.push({
            name: `${foldKey} test`,
            symbol: "none",
            data: curData.test.x.map((item: any, idx: string | number) => [
              item,
              curData.test.y[idx],
            ]),
            type: "line",
            itemStyle: {},
          });
        }
      }
    }
    option.value = {
      ...option.value,
      series: [...list],
    };
  }
});

const list: any[] = [];
const option = shallowRef({
  // ... 其他配置 ...
  grid: {
    show: false,
    right: "32%",
    bottom: "32%",
    containLabel: true,
  },
  xAxis: {
    type: "value",
    min: 0,
    max: 1,
    name: "False Positive Rate",
    splitLine: { show: false },
    axisLine: {
      show: true,
      onZero: false,
    },
  },
  tooltip: {},
  yAxis: {
    type: "value",
    min: 0,
    max: 1,
    name: "True  Positive Rate",
    splitLine: { show: false },
    axisLine: {
      show: true,
      onZero: false,
    },
  },
  dataZoom: [],
  series: [...list],
  legend: {
    // https://echarts.apache.org/zh/option.html#legend.top
    borderRadius: 2,
    type: "scroll", // 使用滚动类型的图例，适合图例项较多的情况
    // orient: "vertical", // 图例列表的布局朝向，默认为水平，此处设置为垂直
    formatter: function (name: any) {
      return name;
    },
    show: true,
    // bottom: "17.5%",
    top: "8%",
    right: "31%",
    borderWidth: 1, // 设置边框宽度
    // padding: 10, // 设置内边距
  },
});
</script>

<style lang="scss" scoped>
.chart-wrapper {
  height: 400px;
  width: 400px;
}
</style>
