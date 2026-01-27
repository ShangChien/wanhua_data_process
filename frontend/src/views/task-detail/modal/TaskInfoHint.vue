<template>
  <ElDialog
    :lock-scroll="true"
    :show-close="true"
    v-model="dialogVisible"
    title="参数说明"
    width="500"
    :before-close="props.handleOK"
  >
    <template #default>
      <ElScrollbar max-height="400px">
        <div :class="['pr-3']">
          <ElDescriptions
            v-if="props.isClassificationTask"
            :column="1"
            title="Classification (分类任务)"
          >
            <ElDescriptionsItem label="1. Log Loss (Logarithmic Loss):"
              >对数损失，用于评估分类模型的性能。值越小越好。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="2. AUC (Area Under the ROC Curve):"
              >接收者操作特征曲线下面积，衡量分类模型在所有分类阈值上的性能。值越接近1越好。</ElDescriptionsItem
            >
            <ElDescriptionsItem
              label="3. AUPRC (Area Under the Precision-Recall Curve): "
              >精确率-召回率曲线下面积，特别适用于不平衡数据集。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="4. F1 Score: "
              >F1
              分数，精确率和召回率的调和平均数，是模型精确度和完整性的平衡。</ElDescriptionsItem
            >
            <ElDescriptionsItem
              label="5. MCC (Matthews Correlation Coefficient): "
              >皮马修斯相关系数，一个介于-1和+1之间的值，用于衡量二分类模型的质量。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="6. Accuracy:">
              准确率，正确分类的样本数占总样本数的比例。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="7. Precision:">
              精确率，预测为正类别中实际为正类别的比例。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="8. Recall:">
              召回率，实际为正类别中被正确预测为正类别的比例。</ElDescriptionsItem
            >
          </ElDescriptions>
          <ElDescriptions v-else :column="1" title="Regression (回归任务)">
            <ElDescriptionsItem label="1. MSE (Mean Squared Error):"
              >均方误差，衡量实际值与预测值之差的平方的平均值。数值越小，模型性能越好。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="2. MAE (Mean Absolute Error):"
              >平均绝对误差，计算实际值与预测值之差的绝对值的平均值。与MSE类似，但对异常值的敏感度较低。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="3. R2 (Coefficient of Determination):"
              >决定系数，衡量模型解释的变异性的比例。值接近1表示模型拟合度好。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="4. Spearmanr:"
              >斯皮尔曼相关系数，一种非参数的秩相关系数，用于衡量两个变量之间的单调相关性。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="5. Pearsonr: "
              >皮尔逊相关系数，用于衡量两个连续变量之间的线性相关性。</ElDescriptionsItem
            >
            <ElDescriptionsItem label="6. RMSE (Root Mean Squared Error):"
              >均方根误差，MSE的平方根，与原始数据在同一量纲上，便于解释。</ElDescriptionsItem
            >
          </ElDescriptions>
        </div>
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
  isClassificationTask: boolean;
}>();
const dialogVisible = ref<boolean>(false);
onMounted(() => {
  dialogVisible.value = true;
});
</script>

<style lang="scss" scoped></style>
