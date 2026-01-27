<template>
  <div class="general-wrapper">
    <!-- <ElSteps
        simple
        :active="fileStore.activeStep"
        align-center
        process-status="wait"
      >
        <ElStep v-for="item in stepList" :key="item.title" class="step-item">
          <template #title>
            {{ item.title }}
          </template>
          <template #icon>
            <Icon :icon="item.icon" width="100" height="100" />
          </template>
        </ElStep>
      </ElSteps> -->
    <div :class="['card-style']">
      <div :class="['text-step']">
        {{ $t("task.步骤一：选择输入数据") }}
      </div>
      <AdjustFile></AdjustFile>
    </div>
    <div :class="['card-style', 'mt-4']">
      <div :class="['text-step']">
        {{ $t("task.步骤二：配置训练参数") }}
      </div>
      <ParamAdjust></ParamAdjust>
    </div>
    <!-- <SuccessFeedback></SuccessFeedback> -->
  </div>
</template>

<script lang="tsx" setup>
import { useFileStore } from "@/stores/modules/file";
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import AdjustFile from "./AdjustFile.vue";
import ParamAdjust from "./ParamAdjust.vue";

const router = useRouter();
const fileStore = useFileStore();

onMounted(() => {});
const stepList = [
  {
    title: "上传数据集",
    icon: "iwwa:upload",
  },
  {
    title: "配置训练参数",
    icon: "mynaui:config",
  },
  {
    title: "提交成功",
    icon: "mdi:success-circle",
  },
];
const handleBack = () => {
  fileStore.resetStore();
  router.push({
    name: "taskManage",
  });
};
onUnmounted(() => {
  fileStore.resetStore();
});
</script>

<style lang="scss" scoped>
:deep() {
  .el-step.is-simple .el-step__head {
    display: flex;
    align-items: center;
    .el-step__icon {
      width: 22px;
      // color: red;
    }
  }
}
</style>
