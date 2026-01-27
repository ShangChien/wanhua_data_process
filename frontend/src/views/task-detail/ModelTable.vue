<template>
  <VxeTable
    ref="modelTableRef"
    :loading="loadingState"
    height="340"
    auto-resize
    round
    :radio-config="{ trigger: 'row', highlight: true }"
    :column-config="{ isCurrent: true, isHover: true }"
    :data="modelTableData"
    @radio-change="handleCurrentChange"
  >
    <VxeColumn fixed="left" type="radio"> </VxeColumn>
    <template v-for="item in columnList" :key="item.prop">
      <template v-if="isIndexCol(item.prop)">
        <VxeColumn
          fixed="left"
          minWidth="140"
          :title="item.label"
          :field="item.prop"
        >
          <template #default="scope">
            <div :title="scope.row[item.prop]">
              {{ IndexLabelMap[scope.row[item.prop]] }}
            </div>
          </template>
        </VxeColumn>
      </template>
      <template v-else>
        <VxeColumn
          show-header-overflow
          show-overflow="title"
          show-footer-overflow
          minWidth="110"
          :title="item.label"
          :field="item.prop"
          :prop="item.prop"
          sortable
        >
          <template #header="scope">
            <span v-html="formatParamLabel(scope.column.title)"></span>
          </template>
          <template #default="scope">
            <div :title="scope.row[item.prop]">
              {{ formatterScienceNumber(scope.row[item.prop]) }}
            </div>
          </template>
        </VxeColumn>
      </template>
    </template>
  </VxeTable>
  <!-- <ElTable
    ref="modelTableRef"
    :class="['w-full', 'overflow-auto']"
    fit
    highlight-current-row
    stripe
    v-loading="loadingState"
    :flexible="true"
    :data="modelTableData"
    height="380"
    table-layout="auto"
    @current-change="handleCurrentChange"
  >
    <ElTableColumn
      v-for="item in columnList"
      :key="item.prop"
      :label="item.label"
      :prop="item.prop"
    >
      <template #header="scope">
        <div v-html="formatParamLabel(scope.column.label)"></div>
      </template>
      <template #default="scope">
        <div :title="scope.row[item.prop]">
          {{ formatterScienceNumber(scope.row[item.prop]) }}
        </div>
      </template>
    </ElTableColumn>
  </ElTable> -->
</template>

<script lang="ts" setup>
import { getMetricsInfo } from "@/service/api/model";
import { getTaskDetail } from "@/service/api/task";
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { ElTable, ElTableColumn, vLoading } from "element-plus";
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { formatterScienceNumber, formatParamLabel } from "@/utils/formatter";
const loadingState = ref(true);
const modelTableData = ref([]);
const columnList = ref<any>([]);
const modelTableRef = ref<any>();
const route = useRoute();
const taskId = route.query.taskId as string;
const taskDetailStore = useTaskDetailStore();
const isIndexCol = (val: string) => {
  return val === "Index";
};
const IndexLabelMap: any = {
  Ensemble: "Ensemble",
  ML01: "LR-FP",
  ML02: "GBDT-MD",
  ML03: "ET-MD",
  ML04: "SVM-FP",
  NN01: "UniMol-All_H",
  NN02: "UniMol-No_H",
  NN03: "BERT-SMILES",
  // ML01: "Features",
  // ML04: "Model",
  // ML04: "Model",
  // ML04: "Model",
  // ML04: "Model",
};
getMetricsInfo({ run_id: taskId })
  .then((res) => {
    modelTableData.value = res.data.data;
    if (modelTableData.value.length > 0) {
      columnList.value = Object.keys(modelTableData.value[0])
        .map((item) => {
          return {
            label: item,
            prop: item,
          };
        })
        .filter((item) => {
          return !["Models", "Features"].includes(item.prop);
        });
    }
    if (modelTableRef.value)
      modelTableRef.value.setRadioRow(modelTableData.value[0]);
  })
  .finally(() => {
    loadingState.value = false;
  });
onMounted(() => {
  if (modelTableData.value.length)
    modelTableRef.value.setRadioRow(modelTableData.value[0]);
});
const handleCurrentChange = ({ row: currentRow }: any) => {
  taskDetailStore.updateStore({
    currentSelfModel: currentRow.Index,
  });
};
</script>

<style lang="scss" scoped>
:deep(.el-scrollbar__thumb) {
  position: absolute !important;
}
</style>
