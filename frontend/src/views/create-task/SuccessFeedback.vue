<template>
  <div :class="['h-full', 'w-full', 'flex', 'items-center']">
    <ElResult
      :class="['h-full', 'w-full', 'flex', 'items-center']"
      icon="success"
      title="任务进入训练"
    >
      <template #extra>
        <ElSpace>
          <ElButton type="primary" @click="handleNewTask">开启新任务</ElButton>
          <ElButton @click="gotoTaskManage">回到任务管理</ElButton>
        </ElSpace>
      </template>
    </ElResult>
  </div>
</template>

<script lang="ts" setup>
import { useFileStore } from "@/stores/modules/file";
import { ElButton, ElResult, ElSpace } from "element-plus";
import { useRouter } from "vue-router";
const router = useRouter();
const fileStore = useFileStore();

const handleNewTask = () => {
  fileStore.resetStore();
};
const gotoTaskManage = () => {
  fileStore.resetStore();
  router.push({
    name: "taskManage",
  });
};
</script>

<style lang="scss" scoped></style>
