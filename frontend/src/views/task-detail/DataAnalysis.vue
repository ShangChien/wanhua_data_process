<template>
  <div :class="['flex', 'flex-col', 'items-center']">
    <div class="wrapper">
      <VChart :option="option" autoresize />
    </div>
    <div :class="['relative', 'bottom-[50px]']">
      <ElRadioGroup v-model="selectFold" size="small">
        <ElRadioButton :value="0">Fold 0</ElRadioButton>
        <ElRadioButton :value="1">Fold 1</ElRadioButton>
        <ElRadioButton :value="2">Fold 2</ElRadioButton>
        <ElRadioButton :value="3">Fold 3</ElRadioButton>
        <ElRadioButton :value="4">Fold 4</ElRadioButton>

        <ElRadioButton value="total">Total</ElRadioButton>
      </ElRadioGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getSelfModelAllDetail } from "@/service/api/model";
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { LineChart, ScatterChart } from "echarts/charts";
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  DataZoomComponent,
} from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { ElOption, ElRadioButton, ElRadioGroup, ElSelect } from "element-plus";
import { isEmpty } from "lodash";
import { computed, ref, shallowRef, watchEffect } from "vue";
import VChart from "vue-echarts";
import { useRoute } from "vue-router";
const taskDetailStore = useTaskDetailStore();

const allSelfModelDetail = ref<any>({});
use([
  ScatterChart,
  GridComponent,
  TitleComponent,
  LegendComponent,
  CanvasRenderer,
  DataZoomComponent,
  LineChart,
]);

const option = shallowRef(getData());

const route = useRoute();

function getData(): any {
  return {
    grid: {
      // show: true,
      right: "23%",
      bottom: "23%",
    },
    tooltip: {
      formatter: function (data: any) {
        return `x: ${data.data[0]}<br>y: ${data.data[1]}`;
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
      formatter: function (name: any) {
        return name;
      },
      top: 25,
      right: "10%",

      borderWidth: 1, // 设置边框宽度
      padding: 10, // 设置内边距
    },
    xAxis: {
      // axisLine: {
      //   onZero: false,
      // },
      splitLine: { show: false },
      axisLine: {
        show: true,
        onZero: false,
      },
      name: "True Values",
    },
    yAxis: {
      // axisLine: {
      //   onZero: false,
      // },
      // splitLine: {},
      name: "Predict Values",
      axisLine: {
        show: true,
        onZero: false,
      },
      splitLine: { show: false },
    },
    series: [],
    dataZoom: [],
  };
}
const selectFold = ref<string>("0");

const foldOptions = ref<{ label: string; value: string }[]>([]);
const formatFoldKey = (key: string) => {
  if (/\d/.test(key)) {
    return "Fold " + key;
  }
  return "Total";
};
watchEffect(() => {
  if (
    taskDetailStore.currentTarget &&
    taskDetailStore.currentSelfModel &&
    !isEmpty(taskDetailStore.selfModelDetail)
  ) {
    const currentModelDetail =
      taskDetailStore.selfModelDetail[taskDetailStore.currentSelfModel][
        taskDetailStore.currentTarget
      ];

    const keyList = Reflect.ownKeys(currentModelDetail);
    foldOptions.value = keyList.map((item: any) => ({
      label: formatFoldKey(item as string),
      value: item,
    }));
    const ret1: any = {};
    let ret: any = currentModelDetail;
    for (let i = 0; i < keyList.length; i++) {
      const curKey = keyList[i];
      ret1[curKey] = {};
      if (
        curKey === "total" ||
        taskDetailStore.currentSelfModel === "Ensemble"
      ) {
        const Validation = ret[curKey].pred.map((item: any, index: number) => {
          return [ret[curKey].true[index], item].flat(2);
        });
        ret1[curKey].Validation = Validation;
      } else {
        const Train = ret[curKey].train.pred.map((item: any, index: number) => {
          return [ret[curKey].train.true[index], item].flat(2);
        });
        const Validation = ret[curKey].test.pred.map(
          (item: any, index: number) => {
            return [ret[curKey].test.true[index], item].flat(2);
          }
        );
        ret1[curKey].Train = Train;
        ret1[curKey].Validation = Validation;
      }
    }
    const data1 = ret1[selectFold.value];
    let min = Infinity;
    let max = -Infinity;
    Reflect.ownKeys(data1).forEach((item: any) => {
      for (let i = 0; i < data1[item].length; i++) {
        min = Math.min(min, data1[item][i][0], data1[item][i][1]);
        max = Math.max(max, data1[item][i][0], data1[item][i][1]);
      }
    });

    min = Math.floor(min);
    max = Math.ceil(max);
    const lineData = [];
    for (let i = min; i <= max; i++) {
      lineData.push([i, i]);
    }

    const legend = Object.keys(data1);
    const newData = getData();
    newData.xAxis.min = min;
    newData.xAxis.max = max;
    newData.yAxis.min = min;
    newData.yAxis.max = max;
    legend.forEach((item, index) => {
      newData.series.push({
        type: "scatter",
        symbolSize() {
          return 5;
        },
        name: item,
        data: data1[legend[index]],
        emphasis: {},
        itemStyle: {},
      });
    });

    newData.series.push({
      type: "line",
      data: lineData,
      smooth: true,
      symbol: "none",

      lineStyle: {
        // 添加 lineStyle 配置
        type: "dashed", // 设置线条类型为虚线
      },
    });
    // debugger;
    option.value = newData;
  }
});
</script>
<style lang="scss" scoped>
.wrapper {
  height: 400px;
  width: 400px;
}
</style>
