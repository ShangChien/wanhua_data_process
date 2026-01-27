<template>
  <div :class="['general-wrapper']">
    <div>
      <ElRow :class="['mb-6']">
        <ElCol :span="12">
          <ElSpace :size="12">
            <span :class="['text-h6', '!mb-0']">
              {{ $t("task.任务管理") }}
            </span>
            <ElButton @click="searchTaskList" link>
              <Icon icon="mdi:refresh" width="22" height="22"></Icon>
            </ElButton>
          </ElSpace>
        </ElCol>
        <ElCol :span="12" :class="['flex-row-reverse', 'flex']">
          <ElSpace size="large">
            <ElInput
              clearable
              :class="['w-[280px]']"
              :placeholder="$t('task.模糊搜索任务名称/ID')"
              v-model="searchParams.fussy_re"
              @input="debouncedSearchTaskList"
            >
            </ElInput>
            <ElButton @click="handleNewTask" type="primary">
              <Icon
                icon="fluent:add-16-regular"
                width="16"
                height="16"
                :class="['mr-1']"
              ></Icon>
              {{ $t("task.新增训练任务") }}
            </ElButton>
            <ElButton @click="handleNewPredictTask" type="primary">
              <Icon
                icon="fluent:add-16-regular"
                width="16"
                height="16"
                :class="['mr-1']"
              ></Icon>
              {{ $t("task.新增预测任务") }}
            </ElButton>
          </ElSpace>
        </ElCol>
      </ElRow>
      <div :class="['table-container']" :style="tableContainerStyle">
        <VxeTable
          border="none"
          :loading="dataLoading"
          height="auto"
          :column-config="{ isCurrent: true, isHover: true }"
          :data="tableData"
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
          <VxeColumn fixed="left" :title="$t('task.任务名称')" min-width="300">
            <template #default="scope">
              <ElSpace direction="vertical" alignment="start">
                <ElButton
                  type="primary"
                  link
                  @click="handleViewDetail(scope.row)"
                >
                  {{ scope.row.name }}
                </ElButton>
                <LongTextComponent
                  width="210px"
                  :line-number="1"
                  :text="scope.row.run_id"
                >
                </LongTextComponent>
              </ElSpace>
            </template>
          </VxeColumn>
          <VxeColumn
            field="ctime"
            width="175"
            :title="$t('task.创建时间')"
            sortable
          />
          <VxeColumn
            field="sku_num"
            width="195"
            :title="$t('task.消耗光子')"
            sortable
          />
          <VxeColumn
            :title="$t('task.任务类型')"
            :filters="taskOptions"
            field="model_task"
            width="230"
          >
            <template #default="scope">
              <span>{{ $t(getTaskI18nKey(scope.row.model_task)) }}</span>
            </template>
          </VxeColumn>
          <VxeColumn
            width="176"
            show-header-overflow
            show-overflow
            :title="$t('task.运行状态')"
            field="state"
            :filters="taskRunStatusOptions"
          >
            <template #default="scope">
              <ElPopover
                trigger="hover"
                v-if="scope.row.state == 'FAILED'"
                placement="top"
                width="500"
              >
                <template #reference>
                  <div :class="['flex', 'items-center']">
                    <StatusComponent :type="scope.row.state" />
                    <!-- <svg class="icon-16"><use href="#TimeFilled"></use></svg> -->
                    <span>{{ $t(getStatusI18nKey(scope.row.state)) }}</span>
                  </div></template
                >
                <div class="flex flex-col justify-center items-center gap-3">
                  <div>
                    {{
                      $t(
                        "task.错误原因可添加微信或点击屏幕右上角我要反馈联系开发者进行排查"
                      )
                    }}
                  </div>
                  <img src="/qsar.jpg" width="100" height="100" alt="" />
                </div>
              </ElPopover>
              <div :class="['flex', 'items-center']" v-else>
                <StatusComponent :type="scope.row.state" />
                <!-- <svg class="icon-16"><use href="#TimeFilled"></use></svg> -->
                <span>{{ $t(getStatusI18nKey(scope.row.state)) }}</span>
              </div>
            </template>
          </VxeColumn>
          <VxeColumn
            show-header-overflow
            show-overflow
            :title="$t('task.训练 / 预测')"
            field="task_type"
            :filters="taskTypeOptions"
            width="300"
          >
            <template #default="scope">
              <span>{{
                scope.row.task_type === "fit"
                  ? $t("task.训练")
                  : $t("task.名词预测")
              }}</span>
            </template>
          </VxeColumn>
          <VxeColumn
            show-header-overflow
            show-overflow
            :title="$t('task.我的收藏')"
            field="is_favorite"
            :filters="isFavoriteOptions"
            width="200"
          >
            <template #default="scope">
              <span>{{
                scope.row.is_favorite ? $t("task.是") : $t("task.否")
              }}</span>
            </template>
          </VxeColumn>
          <VxeColumn
            v-if="ownerColVisible"
            :title="$t('task.用户')"
            show-overflow
            width="200"
            show-footer-overflow
            field="owner"
          />
          <VxeColumn
            width="300"
            :title="$t('task.数据集')"
            show-overflow
            show-footer-overflow
            field="formatDataPath"
          >
            <template #default="scope">
              <!-- <ElLink @click="handleDownloadData(scope.row)"> -->
              <span
                @click="handleDownloadData(scope.row)"
                :class="['cursor-pointer']"
              >
                {{ scope.row.formatDataPath }}
              </span>
              <!-- </ElLink> -->
            </template>
          </VxeColumn>
          <!-- <VxeColumn :title="$t('task.备注')" field="desc"> </VxeColumn> -->
          <VxeColumn fixed="right" :title="$t('task.操作')" min-width="250">
            <template #default="scope">
              <ElSpace :size="18">
                <IconButton
                  v-if="getPredictBtnVisible(scope.row)"
                  iconSVGHref="#predict"
                  @click="handlePredict(scope.row)"
                  :tooltip-text="$t('task.预测')"
                />

                <IconButton
                  iconSVGHref="#detail"
                  :tooltip-text="$t('task.详情')"
                  @click="handleViewDetail(scope.row)"
                />
                <IconButton
                  :iconSVGHref="
                    judgeDataIsCollected(scope.row) ? '#collected' : '#collect'
                  "
                  :tooltip-text="
                    judgeDataIsCollected(scope.row)
                      ? $t('task.取消收藏')
                      : $t('task.收藏')
                  "
                  @click="handleCollectTask(scope.row)"
                />
                <IconButton
                  v-if="restartBtnVisible(scope.row)"
                  width="24"
                  height="24"
                  iconSVGHref="#restart"
                  :tooltip-text="$t('task.重新运行')"
                  @click="handleRestart(scope.row)"
                />
                <IconButton
                  v-if="getPauseBtnVisible(scope.row)"
                  @click="handlePause(scope.row)"
                  iconSVGHref="#terminate"
                  :tooltip-text="$t('task.停止')"
                />
                <IconButton
                  v-if="getDeleteBtnVisible(scope.row)"
                  @click="handleDelete(scope.row)"
                  iconSVGHref="#delete"
                  :tooltip-text="$t('task.删除')"
                />
              </ElSpace>
            </template>
          </VxeColumn>
        </VxeTable>
      </div>
      <ElPagination
        :class="['pager']"
        v-model:currentPage="pageVO.currentPage"
        v-model:pageSize="pageVO.pageSize"
        :total="pageVO.total"
        @change="handlePaginationChange"
        v-bind="paginationProp"
      />
    </div>
    <RemindUser
      v-model:visible="remindUserVisible"
      @resolve="remindUserVisible = false"
    />
  </div>
</template>

<script lang="ts" setup>
import LongTextComponent from "@/components/long-text-component/index.vue";
import { popup } from "@/components/modal/ModalContainer.vue";
import RemindUser from "@/components/modal/RemindUser.vue";
import {
  downloadDataFile,
  getTaskList,
  restartTask,
  updateTaskCollectedStatus,
} from "@/service/api/task";
import {
  classifyTaskState,
  getFileId,
  getOriginDataSetFileName,
  getStatusI18nKey,
  getTaskI18nKey,
} from "@/utils/formatter";

import { Icon } from "@iconify/vue";
import {
  ElButton,
  ElCol,
  ElInput,
  ElLink,
  ElMessage,
  ElPagination,
  ElRow,
  ElSpace,
  ElPopover,
  dayjs,
} from "element-plus";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import MessageModal from "./modal/MessageModal.vue";
import StopMessageModal from "./modal/StopMessageModal.vue";
import StatusComponent from "@/components/status-component/index.vue";
import useConstants from "@/hooks/useConstants";
import { useTabPageStore } from "@/stores/modules/page";
import Cookie from "js-cookie";
import { getQSARTokenByApp } from "@/service/api/user";
import { useUserStore } from "@/stores/modules/user";
import IconButton from "@/components/icon-button/index.vue";
import usePageVO from "@/hooks/usePageVO";
import { debounce } from "lodash";
import { triggerDownload } from "@/utils/download";

const { pageVO, paginationProp } = usePageVO();
const userStore = useUserStore();
const {
  taskOptions,
  taskTypeOptions,
  taskRunStatusOptions,
  isFavoriteOptions,
} = useConstants();
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dataLoading = ref(false);
const searchParams = ref<any>({
  fussy_re: "",
  filter: {
    task_type: [],
    model_task: [],
    state: [],
    is_favorite: [],
  },
});
const remindUserVisible = ref(false);
const ownerColVisible = computed(() => {
  if (userStore.userInfo) {
    return userStore.userInfo.sub === "admin";
  }
  return false;
});

const bohriumAppAutoAddToken = () => {
  const appAccessKey = Cookie.get("appAccessKey");
  // Cookie.get("appAccessKey") || `sk-8eb6b738d4c140e3ab1d926389e1abd8`;
  const clientName = Cookie.get("clientName");
  // const clientName = Cookie.get("clientName") || `hash-qsar-uuid1721273438`;
  console.warn("appAccessKey", appAccessKey, "clientName", clientName);

  if (clientName && appAccessKey) {
    getQSARTokenByApp({
      appAccessKey,
      clientName,
    }).then((res) => {
      userStore.setToken(res.data.data);
      // router.push({ name: "dashboard" });

      searchTaskList();
    });
  } else {
    router.push({ name: "401" });
  }
};

const showChargingNotification = () => {
  const VISIT_COUNT_KEY = "app_visit_count";
  const MAX_NOTIFICATION_COUNT = 2;

  const visitCount = parseInt(localStorage.getItem(VISIT_COUNT_KEY) || "0");
  localStorage.setItem(VISIT_COUNT_KEY, (visitCount + 1).toString());
  // 如果访问次数小于最大提醒次数，则显示弹窗
  if (visitCount < MAX_NOTIFICATION_COUNT) {
    remindUserVisible.value = true;
  }
};

// 在页面初始化时调用
onMounted(() => {
  showChargingNotification();
});
const getPredictBtnVisible = (rowData: any) => {
  return rowData.state === "FINISHED" && rowData.task_type === "fit";
};
const restartBtnVisible = (rowData: any) => {
  return !["RUNNING"].includes(rowData.state);
};
const getDeleteBtnVisible = (rowData: any) => {
  return !["RUNNING", "SCHEDULED"].includes(rowData.state);
};
const judgeDataIsCollected = (rowData: any) => {
  return rowData.is_favorite;
};
const handlePause = (rowData: any) => {
  popup(StopMessageModal, {
    taskData: rowData,
  })
    .then(() => {
      ElMessage.success({
        type: "success",
        message: t("task.停止成功"),
      });
      searchTaskList();
    })
    .catch((e) => {});
};
const getPauseBtnVisible = (rowData: any) => {
  return ["RUNNING", "HOLDING", "SCHEDULED"].includes(rowData.state);
};

// onMounted(() => {
//   searchTaskList();
// });
const handleDownloadData = (rowData: any) => {
  downloadDataFile({
    file_id: rowData.fileId,
  }).then((res) => {
    // debugger;
    triggerDownload(
      res.data,
      {
        // type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      },
      rowData.formatDataPath
    )
      .then(() => {
        ElMessage.success(t("task.导出成功"));
      })
      .catch(() => {
        ElMessage.error(t("task.导出失败"));
      })
      .finally(() => {
        // downLoading.value = false;
      });
  });
};
const getDownloadLink = (id: string) => {
  return (
    import.meta.env.VITE_REQUEST_BASE_URL +
    "/file/download_data_file?file_id=" +
    id
  );
};
const handleViewDetail = async (rowData: any) => {
  if (rowData.task_type === "fit") {
    router.push({
      name: "taskDetail",
      query: {
        taskId: rowData.run_id,
      },
    });
  } else
    router.push({
      name: "predictResult",
      query: {
        taskId: rowData.run_id,
      },
    });
};
const handleFilterChange = (tableInstance: any) => {
  if (
    tableInstance.property &&
    tableInstance.property in searchParams.value.filter
  ) {
    searchParams.value.filter[tableInstance.property] = tableInstance.values;
    searchTaskList();
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
      tableData.value = res.data.data.data.map((item: any) => {
        const taskTypeLabel = taskOptions.value.find(
          (option) => item.model_task === option.value
        )?.label;
        return {
          ...item,
          formatDataPath: getOriginDataSetFileName(item.data_path),
          ctime: dayjs.unix(item.ctime).format("YYYY-MM-DD HH:mm"),
          taskTypeLabel,
          fileId: getFileId(item.data_path),
          state: classifyTaskState(item.state),
        };
      });
    })
    .finally(() => {
      dataLoading.value = false;
    });
};
const debouncedSearchTaskList = debounce(searchTaskList, 500);

if (import.meta.env.VITE_IS_BOHRIUM && userStore.token == null) {
  bohriumAppAutoAddToken();
} else {
  searchTaskList();
}

const tableData = ref<unknown[]>([]);

const handleDelete = (rowData: unknown) => {
  popup(MessageModal, {
    taskData: rowData,
  })
    .then(() => {
      ElMessage.success({
        type: "success",
        message: t("task.删除成功"),
      });
      searchTaskList();
    })
    .catch((e) => {});
};
const handlePaginationChange = () => {
  searchTaskList();
};

const handleNewTask = () => {
  router.push({
    name: "createTask",
  });
};
const handleNewPredictTask = () => {
  router.push({
    name: "taskPredict",
  });
};
const handlePredict = (rowData: any) => {
  router.push({
    name: "taskPredict",
    query: {
      taskId: rowData.run_id,
    },
  });
};
const handleCollectTask = (rowData: any) => {
  updateTaskCollectedStatus({
    run_id: rowData.run_id,
    is_favorite: !rowData.is_favorite,
  }).then(() => {
    ElMessage.success({
      type: "success",
      message: rowData.is_favorite
        ? t("task.取消收藏成功")
        : t("task.收藏成功"),
    });
    searchTaskList();
  });
};
const handleRestart = (rowData: any) => {
  const restParams: any = {};
  const appAccessKey = Cookie.get("appAccessKey") || "";
  const clientName = Cookie.get("clientName") || "";
  restParams["access_key"] = appAccessKey;
  restParams["app_key"] = clientName;
  restartTask({
    data: {
      run_id: rowData.run_id,
    },
    sku: restParams,
  }).then((res) => {
    ElMessage.success({
      type: "success",
      // message: t("task.重新运行成功"),
      message: t("task.提交成功,预计扣费", {
        countNumber: +res.data.msg.match(/\d+/g)[0] / 100,
      }),
    });
    searchTaskList();
  });
};
const tabPageStore = useTabPageStore();
const tableContainerStyle = computed(() => {
  const navHeight = tabPageStore.hasNav ? "56px" : "0px";
  return {
    height: `calc(100vh - ${navHeight} - 106px - 62px)`,
  };
});
</script>

<style lang="scss" scoped>
@import "@/assets/variables";
.id-text {
  color: #666e77;
}
.table-container {
  overflow: hidden;
  border-top-left-radius: $card-border-radius;
  border-top-right-radius: $card-border-radius;
  box-shadow: 0px 4px 19px 0px rgba(222, 222, 222, 0.2);
}
</style>
