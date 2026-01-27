<template>
  <ElDrawer
    size="70%"
    :before-close="props.handleCancel"
    v-model="drawerVisible"
    :title="$t('task.选择训练模型')"
  >
    <template #default>
      <div :class="['h-full']">
        <div :class="['mb-4']">
          <ElSpace>
            <ElInput
              :class="['w-[150px]']"
              clearable
              size="small"
              :placeholder="$t('task.模糊搜索任务名称/ID')"
              v-model="searchParams.fussy_re"
              @input="debounceSearch"
            >
            </ElInput>
            <ElButton @click="searchTaskList" link>
              <Icon icon="mdi:refresh" width="22" height="22"></Icon>
            </ElButton>
          </ElSpace>
        </div>
        <div :class="['table-container']">
          <VxeTable
            border="none"
            ref="tableRef"
            :loading="dataLoading"
            height="auto"
            :column-config="{ isCurrent: true, isHover: true }"
            :data="tableData"
            :radio-config="{ highlight: true }"
            @radio-change="
              ({ row }: any) => {
                selectRow = row;
              }
            "
            @filter-change="handleFilterChange"
          >
            <template #empty>
              <div :class="['flex', 'items-center', 'flex-col']">
                <img src="@/assets/img/empty-data.png" />
                <p :class="['text-tip']">
                  {{ $t("common.暂无内容") }}
                </p>
              </div>
            </template>
            <VxeColumn type="radio" width="70">
              <template #header>
                <ElButton
                  type="primary"
                  link
                  @click="handleRadioCancel"
                  :disabled="!selectRow"
                  >{{ $t("common.取消") }}</ElButton
                >
              </template>
            </VxeColumn>
            <VxeColumn :title="$t('task.任务名称')" width="200">
              <template #default="scope">
                <ElSpace direction="vertical" alignment="start">
                  <ElButton type="primary" link>
                    {{ scope.row.name }}
                  </ElButton>
                  <LongTextComponent
                    width="130px"
                    :line-number="1"
                    :text="scope.row.run_id"
                  >
                  </LongTextComponent>
                </ElSpace>
              </template>
            </VxeColumn>
            <VxeColumn field="ctime" :title="$t('task.创建时间')" sortable />
            <VxeColumn
              field="model_task"
              :title="$t('task.任务类型')"
              :filters="taskOptions"
            >
              <template #default="scope">
                <span>{{ $t(getTaskI18nKey(scope.row.model_task)) }}</span>
              </template>
            </VxeColumn>
            <!-- <VxeColumn
              title="运行状态"
              :filters="taskRunStatusOptions"
              :filter-method="filterRunStateMethod"
            >
              <template #default="scope">
                <span>{{ $t(getStatusI18nKey(scope.row.state)) }}</span>
              </template>
            </VxeColumn> -->
            <!-- <VxeColumn
              title="训练 / 预测"
              field="task_type"
              :filters="taskTypeOptions"
              :filter-method="filterTaskTypeMethod"
            >
              <template #default="scope">
                <span>{{
                  scope.row.task_type === "fit" ? "训练" : "预测"
                }}</span>
              </template>
            </VxeColumn> -->

            <VxeColumn :title="$t('task.数据集')" field="data_path">
            </VxeColumn>

            <!-- <ElTableColumn type="selection" width="55" />
     
      
       
     -->
          </VxeTable>
        </div>
        <ElPagination
          :class="['pager']"
          v-model:currentPage="pageVO.currentPage"
          v-model:pageSize="pageVO.pageSize"
          :total="pageVO.total"
          v-bind="paginationProp"
          @change="handlePaginationChange"
        />
      </div>
    </template>
    <template #footer>
      <ElButton @click="props.handleCancel">
        {{ $t("common.取消") }}
      </ElButton>
      <ElButton type="primary" @click="handleConfirm">
        {{ $t("common.确认") }}
      </ElButton>
    </template>
  </ElDrawer>
</template>

<script lang="ts" setup>
import LongTextComponent from "@/components/long-text-component/index.vue";
import useConstants from "@/hooks/useConstants";
import usePageVO from "@/hooks/usePageVO";
import { getTaskList } from "@/service/api/task";
import { getOriginDataSetFileName, getTaskI18nKey } from "@/utils/formatter";
import { Icon } from "@iconify/vue/dist/iconify.js";
import {
  dayjs,
  ElButton,
  ElDrawer,
  ElInput,
  ElMessage,
  ElPagination,
  ElSpace,
} from "element-plus";
import { debounce, isEmpty } from "lodash";
import { onMounted, ref } from "vue";
const { pageVO, paginationProp } = usePageVO();
const { taskOptions } = useConstants();
const drawerVisible = ref<boolean>(false);
const searchParams = ref<any>({
  fussy_re: "",
  filter: {
    task_type: ["fit"],
    model_task: [],
    state: ["FINISHED"],
    is_favorite: [],
  },
});
const tableRef = ref();
const searchKeyword = ref<string>("");
const props = defineProps<{
  selectModelId: any;
  handleOK: any;
  handleCancel: any;
}>();
onMounted(() => {
  drawerVisible.value = true;
  searchTaskList();
});
const handleFilterChange = (tableInstance: any) => {
  if (
    tableInstance.property &&
    tableInstance.property in searchParams.value.filter
  ) {
    searchParams.value.filter[tableInstance.property] = tableInstance.values;
    searchTaskList();
  }
};
const selectRow = ref<any>(null);
const handleRadioCancel = () => {
  if (tableRef.value) {
    selectRow.value = null;
    tableRef.value.clearRadioRow();
  }
};
const searchTaskList = () => {
  dataLoading.value = true;
  getTaskList({
    length: pageVO.value.pageSize,
    page: pageVO.value.currentPage,
    ...searchParams.value,
  })
    .then((res) => {
      pageVO.value.total = res.data.data.total_count;
      tableData.value = res.data.data.data
        // .filter((item: any) => {
        //   return item.state === "FINISHED" && item.task_type === "fit";
        // })
        .map((item: any) => {
          const taskTypeLabel = taskOptions.value.find(
            (option) => item.model_task === option.value
          )?.label;
          return {
            ...item,
            ctime: dayjs.unix(item.ctime).format("YYYY-MM-DD HH:mm"),
            data_path: getOriginDataSetFileName(item.data_path),
            taskTypeLabel,
          };
        });
    })
    .finally(() => {
      dataLoading.value = false;
    });
};
const debounceSearch = debounce(searchTaskList, 500);
const dataLoading = ref(false);
const handleConfirm = () => {
  if (isEmpty(selectRow.value)) {
    ElMessage({
      message: "请选择一个模型",
      type: "error",
    });
    return;
  }
  props.handleOK(selectRow.value);
};

const tableData = ref<any[]>([]);

const multipleSelection = ref<string[]>([]);
// if (props.selectModelId) {
//   multipleSelection.value = [props.selectModelId];
// }
const handleSelectionChange = (val: any) => {
  multipleSelection.value = val;
};
const handlePaginationChange = () => {
  searchTaskList();
};
</script>

<style lang="scss" scoped>
.table-container {
  height: calc(100% - 62px - 44px);
}
</style>
