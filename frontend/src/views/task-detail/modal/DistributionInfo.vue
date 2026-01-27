<template>
  <ElDialog
    :show-close="true"
    v-model="dialogVisible"
    title="参数说明"
    width="500"
    :before-close="props.handleOK"
  >
    <template #default>
      <ElScrollbar max-height="400px">
        <ElDescriptions :column="1" title="数据分布图">
          <ElDescriptionsItem label="1. MSE (Mean Squared Error):"
            >通过不同高度的柱子展示数据的分布情况，便于比较不同类别的数值大小，识别数据模式和异常值，从而辅助分析和决策过程</ElDescriptionsItem
          >
        </ElDescriptions>
      </ElScrollbar>
    </template>
  </ElDialog>
</template>

<script lang="ts" setup>
import {
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElScrollbar,
} from "element-plus";
import { onMounted, ref } from "vue";
const props = defineProps<{
  handleOK: any;
  handleCancel: any;
}>();
const dialogVisible = ref<boolean>(false);
onMounted(() => {
  dialogVisible.value = true;
});
</script>

<style lang="scss" scoped></style>
