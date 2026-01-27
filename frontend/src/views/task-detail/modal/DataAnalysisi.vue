wagn1
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
            >分类任务： 使用AUC（Area Under the
            Curve）曲线衡量模型的性能，其能够展示模型在不同阈值下的表现，从而评估模型区分正负类的能力。AUC值越高，表示模型的分类性能越好。AUC值为0.5时，模型的性能等同于随机猜测；AUC值为1时，模型具有完美的分类能力。
            回归任务：
            使用散点图将实际值与预测值进行对比，可以直观地看出模型预测的准确性。如果散点图上的点集中在一条直线附近，这表明模型的预测偏差较小；如果点远离这条直线，则可能存在较大的偏差。散点图可以帮助识别数据中的模式或趋势以及揭示数据中的异常值或离群点</ElDescriptionsItem
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
