<template>
  <div :class="['flex', 'justify-center', 'flex-col', 'items-center']">
    <div :class="['chart-wrapper']">
      <VChart :option="option" autoresize />
    </div>
    <div :class="['relative', 'bottom-[50px]', 'left-6']">
      <ElRadioGroup v-model="activeFold" size="small">
        <ElRadioButton :value="0">Fold 0</ElRadioButton>
        <ElRadioButton :value="1">Fold 1</ElRadioButton>
        <ElRadioButton :value="2">Fold 2</ElRadioButton>
        <ElRadioButton :value="3">Fold 3</ElRadioButton>
        <ElRadioButton :value="4">Fold 4</ElRadioButton>
      </ElRadioGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { ScatterChart } from "echarts/charts";
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
} from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { ElOption, ElSelect, ElRadioGroup, ElRadioButton } from "element-plus";
import { isEmpty } from "lodash";
import { ref, shallowRef, watchEffect } from "vue";
import VChart from "vue-echarts";
import { useRoute } from "vue-router";
use([
  ScatterChart,
  GridComponent,
  TitleComponent,
  LegendComponent,
  CanvasRenderer,
]);
const activeFold = ref(0);
const option = shallowRef(getData());
const route = useRoute();

function getData(): any {
  return {
    grid: {
      containLabel: true,
      // bottom: "30%",
    },
    tooltip: {
      formatter: function (data: any) {
        return `类别: Fold ${data.data[2]}<br>&nbsp;&nbsp;&nbsp;&nbsp;x: ${data.data[0]}<br>&nbsp;&nbsp;&nbsp;&nbsp;y: ${data.data[1]}`;
      },
      textStyle: {
        align: "left",
      },
    },
    legend: {
      // https://echarts.apache.org/zh/option.html#legend.top
      borderRadius: 2,
      type: "scroll", // 使用滚动类型的图例，适合图例项较多的情况
      // orient: "vertical", // 图例列表的布局朝向，默认为水平，此处设置为垂直
      top: 25,
      right: "10%",
      borderWidth: 1, // 设置边框宽度
      padding: 10, // 设置内边距
    },
    xAxis: {
      axisLine: {
        onZero: false,
      },
      splitLine: {
        show: false,

        lineStyle: {
          type: "dashed",
        },
      },

      name: "x",
    },
    yAxis: {
      name: "y",

      axisLine: {
        onZero: false,
      },
      splitLine: {
        show: false,
        lineStyle: {
          type: "dashed",
        },
      },
      scale: true,
    },
    series: [
      {
        type: "scatter",
        symbolSize(data: any) {
          return 5;
        },
        emphasis: {},
        itemStyle: {
          color: "blue",
        },
        z: 2,
      },
      {
        type: "scatter",
        symbolSize(data: any) {
          return 5;
        },
        tooltip: {},
        emphasis: {},
        itemStyle: {
          color: "orange",
        },
        z: 1,
      },
    ],
  };
}
const taskDetailStore = useTaskDetailStore();
watchEffect(() => {
  if (!isEmpty(taskDetailStore.TsneInfo)) {
    const newData = getData();
    const data1 = taskDetailStore.TsneInfo;
    if (data1) {
      let min = Infinity;
      let max = -Infinity;
      const data2 = data1.x.map((item: any, idx: any) => {
        min = Math.min(min, item, data1.y[idx]);
        max = Math.max(max, item, data1.y[idx]);
        return [item, data1.y[idx], data1.fold[idx]];
      });
      min = Math.floor(min) - 1;
      max = Math.ceil(max) + 1;
      function groupBy(data: any[]) {
        const result: any = {
          currentFold: [],
          otherFolds: [],
        };
        data.forEach((item) => {
          if (item[2] === activeFold.value) {
            result.currentFold.push(item);
          } else {
            result.otherFolds.push(item);
          }
        });
        return result;
      }
      const ret = groupBy(data2);
      newData.series[0].data = ret.currentFold;
      newData.series[0].name = "Validation";
      newData.series[1].data = ret.otherFolds;
      newData.series[1].name = "Train";
      newData.xAxis.min = min;
      newData.xAxis.max = max;
      newData.yAxis.min = min;
      newData.yAxis.max = max;
      // newData.legend.data.forEach((item: any, index: number) => {
      //   newData.series[index].name = item;
      //   newData.series[index].data = data3[index];
      // });
      option.value = newData;
    }
  }
});
</script>

<style lang="scss" scoped>
.chart-wrapper {
  height: 400px;
  width: 450px;
}
</style>
