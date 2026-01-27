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
        <ElDescriptions :column="1" title="骨架相似图">
          <ElDescriptionsItem label="1. MSE (Mean Squared Error):"
            >分子指纹降维后的散点图，是一种将复杂分子数据简化为二维视图的方法，便于我们直观地观察和分析。在这个图中，每个点代表一个分子，而点的颜色则表示它们属于当前数据集的验证集（Validation）或训练集（Train)。如果不同颜色的点聚集在一起，说明这些分子在结构或性质上具有相似性；如果点分散，则表示它们之间存在较大差异。简而言之，这张图就像是一张分子的“地图”，通过颜色区分不同数据集，通过点的分布和距离，揭示分子间的相似性和差异性。</ElDescriptionsItem
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
