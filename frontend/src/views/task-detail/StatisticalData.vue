<template>
  <div :class="['static-container']">
    <ElSpace alignment="center" :size="64">
      <StatisticItem
        bg-color="#F5E8FF"
        line-color="#722ED1"
        icon="#used-time"
        :title="$t('task.任务用时')"
        >{{ customTime }}</StatisticItem
      >
      <StatisticItem
        bg-color="#FFE4BA"
        line-color="#F77234"
        icon="#dataset"
        :title="$t('task.数据总数')"
        >{{ statisticData.total }}</StatisticItem
      >
      <template v-if="taskDetailStore.taskType === 'regression'">
        <StatisticItem
          bg-color="#E8FFFB"
          line-color="#33D1C9"
          icon="#mean"
          height="24"
          width="24"
          :title="$t('task.均值')"
          >{{ formatterScienceNumber(statisticData.meanVal) }}</StatisticItem
        >
        <StatisticItem
          bg-color="#E8F3FF"
          line-color="#165DFF"
          height="24"
          width="24"
          icon="#variance"
          :title="$t('task.方差')"
          >{{
            formatterScienceNumber(statisticData.standardDeviationVal)
          }}</StatisticItem
        ></template
      >
      <template v-if="taskDetailStore.taskType === 'multiclass'">
        <StatisticItem
          v-for="item in statisticData.classList"
          :key="item.label"
          bg-color="#E8FFFB"
          line-color="#33D1C9"
          icon="#kind"
          :title="`${$t('task.类别')} ${item.label}`"
          >{{ item.count }}</StatisticItem
        >
      </template>
      <template v-if="taskDetailStore.taskType === 'multilabel_classification'">
        <StatisticItem
          bg-color="#E8FFFB"
          line-color="#33D1C9"
          icon="#one-kind"
          :title="$t('task.正样本数')"
          >{{ statisticData.count1 }}</StatisticItem
        >
        <StatisticItem
          bg-color="#E8F3FF"
          line-color="#165DFF"
          icon="#zero-kind"
          :title="$t('task.负样本数')"
          >{{ statisticData.count0 }}</StatisticItem
        >
      </template>
      <template v-if="taskDetailStore.taskType === 'classification'">
        <StatisticItem
          bg-color="#E8FFFB"
          line-color="#33D1C9"
          icon="#one-kind"
          :title="$t('task.正样本数')"
          >{{ statisticData.count1 }}</StatisticItem
        >
        <StatisticItem
          bg-color="#E8F3FF"
          line-color="#165DFF"
          icon="#zero-kind"
          :title="$t('task.负样本数')"
          >{{ statisticData.count0 }}</StatisticItem
        >
      </template>
      <template v-if="taskDetailStore.taskType === 'multilabel_regression'">
        <StatisticItem
          bg-color="#F5E8FF"
          line-color="#722ED1"
          icon="#mean"
          :title="$t('task.均值')"
          >{{ formatterScienceNumber(statisticData.meanVal) }}</StatisticItem
        >

        <StatisticItem
          bg-color="#F5E8FF"
          line-color="#722ED1"
          icon="#variance"
          :title="$t('task.方差')"
          >{{
            formatterScienceNumber(statisticData.standardDeviationVal)
          }}</StatisticItem
        >
      </template>
    </ElSpace>
  </div>
</template>

<script lang="ts" setup>
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { formatDuration, formatterScienceNumber } from "@/utils/formatter";
import { mean, variance } from "d3-array";
import { ElScrollbar, ElSpace } from "element-plus";
import { ref, watchEffect } from "vue";
import StatisticItem from "./StatisticItem.vue";
import { isEmpty } from "lodash";

const taskDetailStore = useTaskDetailStore();

const statisticData = ref<{
  total: string;
  consumeTime: string;
  count0: string;
  count1: string;
  meanVal: string;
  standardDeviationVal: string;
  classList: { label: string; count: number }[];
}>({
  total: "",
  consumeTime: "",
  count0: "",
  count1: "",
  meanVal: "",
  standardDeviationVal: "",
  classList: [],
});
const customTime = ref("");
watchEffect(() => {
  const curTargetDistribution =
    taskDetailStore.distributionData[taskDetailStore.currentTarget];
  if (curTargetDistribution && curTargetDistribution.length) {
    statisticData.value.total = curTargetDistribution.length + "";
    switch (taskDetailStore.taskType) {
      case "multilabel_regression":
      case "regression": {
        statisticData.value.meanVal = mean(curTargetDistribution) + "";
        statisticData.value.standardDeviationVal =
          variance(curTargetDistribution) + "";
        break;
      }
      case "multilabel_classification":
      case "classification": {
        const countObj: Record<string, number> = {};
        for (let i = 0; i < curTargetDistribution.length; i++) {
          const label = curTargetDistribution[i];
          countObj[label] = countObj[label] ? countObj[label] + 1 : 1;
        }
        statisticData.value.count1 = (countObj["1"] || 0) + "";
        statisticData.value.count0 = (countObj["0"] || 0) + "";
        break;
      }
      case "multiclass": {
        const countObj: Record<string, number> = {};
        for (let i = 0; i < curTargetDistribution.length; i++) {
          const label = curTargetDistribution[i];
          countObj[label] = countObj[label] ? countObj[label] + 1 : 1;
        }
        statisticData.value.classList = Object.keys(countObj)
          .sort((a, b) => +a - +b)
          .map((item) => {
            return { label: item, count: countObj[item] };
          });
        break;
      }
    }
  }
});
watchEffect(() => {
  if (!isEmpty(taskDetailStore.taskDetail)) {
    customTime.value = formatDuration(
      taskDetailStore.taskDetail.start_time,
      taskDetailStore.taskDetail.end_time
    );
  }
});
</script>

<style lang="scss" scoped>
@import "@/assets/variables.scss";
.static-container {
  overflow-x: auto;
  overflow-y: auto;
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: #fff;
  }
  &:hover {
    &::-webkit-scrollbar-thumb {
      background-color: $gray6-color;
    }
  }
}
</style>
