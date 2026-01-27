<template>
  <ElDialog :lock-scroll="true" v-model="modalVisible">
    <div :class="['mb-3']">
      {{ $t("common.数据集存在问题，继续创建，该任务会忽略如下数据") }}
    </div>
    <ElTable
      ref="tableRef"
      max-height="1000"
      height="300"
      border
      highlight-current-row
      :data="tableData"
    >
      <ElTableColumn prop="index" label="index" />
      <ElTableColumn v-for="item in headList" :prop="item" :label="item" />
      <!-- <ElTableColumn :prop="fileStore.baseOptions.smiles_col" label="smiles" />
      <ElTableColumn
        v-for="(item, index) in fileStore.baseOptions.target_cols"
        :prop="item"
        :label="`target ${index + 1}`"
        :key="item"
      /> -->
    </ElTable>
    <template #footer>
      <ElButton @click="props.handleCancel">
        {{ $t("common.取消") }}
      </ElButton>
      <ElButton @click="props.handleOK" type="primary">
        {{ $t("common.继续创建") }}
      </ElButton>
    </template>
  </ElDialog>
</template>

<script lang="ts" setup>
import {
  ElButton,
  ElDialog,
  ElMessageBox,
  ElTable,
  ElTableColumn,
  type TableInstance,
} from "element-plus";
import { onMounted, onUnmounted, ref } from "vue";
const props = defineProps<{
  handleOK: any;
  handleCancel: any;
  tableData: any[];
  headList: any[];
}>();

const tableData = ref<any[]>([]);
tableData.value = props.tableData;
const tableRef = ref<TableInstance>();
const currentData = ref<any>();
const selectedRows = ref<unknown[]>([]);

const modalVisible = ref(true);
const handleSearch = () => {
  //   const curList = fileStore.fileInfo.list.slice(startIdx, endIdx)
  const curList: any[] = [];
  // tableData.value = [
  //   {
  //     smiles: 'OCOOCOCOC',
  //     target: 1,
  //     name: '121'
  //   },
  //   {
  //     smiles: 'OCOOCOC',
  //     target: 2
  //   }
  // ]
  if (curList.length > 0) {
    tableRef.value?.setCurrentRow(curList[0]);
  }
};
onMounted(() => {
  handleSearch();
});
onUnmounted(() => {
  console.log("unmounted");
});
const handlePaginationChange = () => {
  handleSearch();
};
const handleCurrentChange = (curData: any) => {
  // console.log(tableData.value)

  currentData.value = curData;
};
const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows;
};
// const handleEdit = (curRol: any) => {
//   rowModalVisible.value = true
// }
const handleDelete = () => {
  // const targetIndex = current
  ElMessageBox.confirm("确认要删除勾选行数据么？", "提示", {
    confirmButtonText: "确认",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      try {
        // fileStore.deleteItems(selectedRows.value.map((item: any) => item.id))
        // ElMessage({
        //   type: 'success',
        //   message: '删除成功'
        // })
        handleSearch();
      } catch (error) {}
    })
    .catch(() => {});
};
</script>

<style lang="scss" scoped></style>
