<template>
  <div :class="['general-wrapper']" :id="TaskDetailDOMId">
    <div
      :class="['card-style', 'sticky', 'border-bottom-shadow']"
      :style="{
        position: 'sticky',
        zIndex: 20,
        top: tabPageStore.hasNav ? '56px' : '0px',
      }"
    >
      <div :class="['flex', 'justify-between', 'gap-3']">
        <ElSpace alignment="center" size="large" :class="['text-nowrap']">
          <div>
            <span :class="['text-label', 'mr-2']">
              {{ $t("task.任务名称:") }}
            </span>
            <span :class="['text-value']">
              {{ taskInfo.name }}
            </span>
          </div>

          <div>
            <span :class="['text-label', 'mr-2']">
              {{ $t("task.任务类型:") }}
            </span>
            <span :class="['text-value']" v-if="taskDetailStore.taskType">
              {{ $t(getTaskI18nKey(taskDetailStore.taskType)) }}
            </span>
          </div>
          <div>
            <span :class="['text-label', 'mr-2']">
              {{ $t("task.任务状态：") }}
            </span>
            <span
              :class="['text-value']"
              v-if="taskDetailStore.taskDetail.status"
            >
              {{
                $t(
                  taskRunStatusMap[taskDetailStore.taskDetail.status || ""]
                    ?.i18nKey || ""
                )
              }}
            </span>
          </div>
        </ElSpace>
        <ElSpace alignment="center" size="large">
          <ElRadioGroup v-model="taskDetailStore.currentTarget">
            <ElRadio v-for="item in taskDetailStore.targetList" :value="item">{{
              item
            }}</ElRadio>
          </ElRadioGroup>

          <ElButton link @click="handlePreviewDetail" type="primary">
            {{ $t("task.查看模型具体参数") }}
          </ElButton>
          <!-- <div :class="['flex', 'items-center']">
          <span :class="['mr-3']"> &nbsp;</span>
          <ElSelect size="small" :class="['!w-40']">
            <ElOption :key="item" :label="item"></ElOption>
          </ElSelect>
        </div> -->
        </ElSpace>
      </div>
      <div v-if="processVisible" :class="['flex', 'items-center', 'mt-4']">
        <span :class="['text-label', 'mr-2']">
          {{ $t("task.训练进度：") }}
        </span>
        <ElProgress
          :stroke-width="10"
          :class="['w-[200px]']"
          :percentage="runPercentage"
        />
      </div>
      <ElDivider :class="['my-[20px]']" v-if="isSuccessTask" />
      <ElRow v-if="isSuccessTask">
        <ElCol :span="16">
          <StatisticData />
        </ElCol>
        <ElCol :span="8" :class="['flex', 'flex-row-reverse']">
          <ElSpace>
            <ElButton type="primary" @click="handlePredict">
              <svg :class="['iconpark-icon', 'mr-1']">
                <use href="#predict"></use>
              </svg>
              {{ $t("task.预测") }}
            </ElButton>
            <ElButton @click="handleUpdateCollectStatus">
              <svg :class="['iconpark-icon', 'mr-1']">
                <use
                  :href="
                    taskDetailStore?.taskDetail?.is_favorite
                      ? '#collected'
                      : '#collect'
                  "
                ></use>
              </svg>
              {{
                taskDetailStore?.taskDetail?.is_favorite
                  ? $t("task.取消收藏")
                  : $t("task.收藏")
              }}
            </ElButton>
            <ElDropdown @command="handleExport">
              <ElButton class="!outline-none">
                <svg :class="['iconpark-icon', 'mr-1']">
                  <use href="#export"></use>
                </svg>
                {{ $t("task.导出") }}
              </ElButton>
              <template #dropdown>
                <ElDropdownItem :command="CommandKey.REPORT">{{
                  $t("common.模型报告")
                }}</ElDropdownItem>
                <ElDropdownItem :command="CommandKey.DATA">{{
                  $t("common.数据文件")
                }}</ElDropdownItem>
              </template>
            </ElDropdown>
          </ElSpace></ElCol
        >
      </ElRow>
    </div>
    <template v-if="isSuccessTask">
      <div :class="['card-style', 'mt-5']">
        <div :class="['text-h6']">
          {{ $t("task.模型指标") }}
          <ElTooltip :content="$t('task.更多信息')" placement="bottom">
            <ElButton @click="handleOpenInfoModal" link type="primary">
              <svg class="iconpark-icon"><use href="#hint"></use></svg>
            </ElButton>
          </ElTooltip>
        </div>
        <MainModel />
      </div>

      <ElRow :class="['mt-5']" :gutter="colGutterNum" v-if="isSuccessTask">
        <ElCol :span="9" align="start">
          <div :class="['card-style', 'h-[450px]']">
            <div :class="['text-h6', 'flex', 'items-center']">
              {{ $t("task.模型细节") }}

              <ElTooltip :content="$t('task.更多信息')" placement="bottom">
                <ElButton @click="handleOpenInfoModal" link type="primary">
                  <svg class="iconpark-icon"><use href="#hint"></use></svg>
                </ElButton>
              </ElTooltip>
            </div>

            <ModelTable />
          </div>
        </ElCol>
        <ElCol :span="6" align="start">
          <div :class="['card-style', 'h-[450px]']">
            <div :class="['text-h6', 'flex', 'items-center']">
              {{ $t("task.超参数列表") }}
              <ElTooltip :content="$t('task.更多信息')" placement="bottom">
                <ElButton @click="openParamListHint" link type="primary">
                  <svg class="iconpark-icon"><use href="#hint"></use></svg>
                </ElButton>
              </ElTooltip>
            </div>
            <ParamList />
          </div>
        </ElCol>
        <ElCol :span="9" align="start">
          <div :class="['card-style', 'h-[450px]']" v-loading="detailLoading">
            <div :class="['text-h6', 'flex', 'items-center']">
              {{ $t("task.数据分析") }}
              <ElTooltip :content="$t('task.更多信息')" placement="bottom">
                <ElButton @click="handleHintAnalysis" link type="primary">
                  <svg class="iconpark-icon">
                    <use href="#hint"></use>
                  </svg>
                </ElButton>
              </ElTooltip>
            </div>
            <template v-if="taskDetailStore.taskType">
              <StackedBar v-if="taskDetailStore.isMultiClass" />
              <MetricGraph v-else-if="taskDetailStore.isClassification" />
              <DataAnalysis v-else />
            </template>
          </div>
        </ElCol>
      </ElRow>
      <ElRow :class="['mt-5']" :gutter="colGutterNum">
        <ElCol :span="12" align="start">
          <div :class="['card-style', 'h-[500px]']">
            <div :class="['text-h6', 'flex', 'items-center']">
              {{ $t("task.数据分布") }}
              <ElTooltip :content="$t('task.更多信息')" placement="bottom">
                <ElButton @click="handleHintDistribution" link type="primary">
                  <svg class="iconpark-icon">
                    <use href="#hint"></use>
                  </svg>
                </ElButton>
              </ElTooltip>
            </div>
            <DataDistributionGraph />
          </div>
        </ElCol>
        <ElCol :span="12" align="start">
          <div :class="['card-style', 'h-[500px]']">
            <div :class="['text-h6', 'flex', 'items-center']">
              {{ $t("task.分子相似度") }}
              <ElTooltip :content="$t('task.更多信息')" placement="bottom">
                <ElButton @click="handleHintSimilarity" link type="primary">
                  <svg class="iconpark-icon">
                    <use href="#hint"></use>
                  </svg>
                </ElButton>
              </ElTooltip>
            </div>
            <SimilarityGraph />
          </div>
        </ElCol>
      </ElRow>
    </template>
    <ElRow :class="['mt-5']" v-if="logModelVisible">
      <TaskLogViewer :logFileName="taskInfo.name + '-log'" />
    </ElRow>
  </div>
</template>

<script lang="ts" setup>
import HintModal from "@/components/modal/HintModal.vue";
import { popup } from "@/components/modal/ModalContainer.vue";
import {
  CLASSIFICATION,
  MULTICLASS,
  MULTILABEL_CLASSIFICATION,
  MULTILABEL_REGRESSION,
  REGRESSION,
  taskRunStatusMap,
} from "@/constants/task";
import {
  getDistributionInfo,
  getMetricsInfo,
  getModelParamInfo,
  getSelfModelAllDetail,
  getTsneInfo,
} from "@/service/api/model";
import {
  getTaskDetail,
  getTaskRunProgress,
  updateTaskCollectedStatus,
} from "@/service/api/task";
import { useTabPageStore } from "@/stores/modules/page";
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { triggerBase64Download } from "@/utils/download";
import { getTaskI18nKey } from "@/utils/formatter";
import { Icon } from "@iconify/vue/dist/iconify.js";
import domtoimage from "dom-to-image-more";
import Papa from "papaparse";
import {
  ElButton,
  ElCol,
  ElDivider,
  ElDropdown,
  ElMessage,
  ElProgress,
  ElRadio,
  ElDropdownItem,
  ElRadioGroup,
  ElRow,
  ElSpace,
  ElTooltip,
  vLoading,
} from "element-plus";
import { computed, ref, watchEffect } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import ViewModelParam from "../predict-result/model/ViewModelParam.vue";
import DataAnalysis from "./DataAnalysis.vue";
import DataDistributionGraph from "./DataDistributionGraph.vue";
import MainModel from "./MainModel.vue";
import MetricGraph from "./MetricGraph.vue";
import ModelTable from "./ModelTable.vue";
import ParamList from "./ParamList.vue";
import SimilarityGraph from "./SimilarityGraph.vue";
import StackedBar from "./StackedBar.vue";
import StatisticData from "./StatisticalData.vue";
import TaskLogViewer from "./TaskLogViewer.vue";
import ExportReportView from "./modal/ExportReportView.vue";

import { saveAs } from "file-saver";
import { get } from "lodash";
import JSZip from "jszip";

const tabPageStore = useTabPageStore();
const { t } = useI18n();
const colGutterNum = 20;

const route = useRoute();
const taskId = route.query.taskId as string;
const taskDetailStore = useTaskDetailStore();
taskDetailStore.resetStore();
const isSuccessTask = computed(
  () => taskDetailStore.taskDetail.status === "FINISHED"
);

const logModelVisible = computed(() => {
  const value = get(taskDetailStore, "taskDetail.status");
  return value && value !== "SCHEDULED";
});
const processVisible = computed(() => {
  return (
    taskDetailStore.taskDetail.status === "RUNNING" &&
    get(taskDetailStore, "taskDetail.task_type.fit.hpo_enable") === false
  );
});
const openParamListHint = () => {
  popup(HintModal, {
    title: t("task.提示"),
    descList: [
      {
        title: t("task.超参数列表"),
        desc: [
          {
            label: "",
            value: t("task.超参数列表hint"),
          },
        ],
      },
    ],
  })
    .then((res) => {})
    .catch(() => {});
};
const runPercentage = ref(0);
const updateRunTaskProgress = () => {
  if (processVisible.value) {
    getTaskRunProgress({ run_id: taskId }).then((res) => {
      // 1->100
      runPercentage.value = res.data.data * 100;
    });
  }
};
watchEffect(() => {
  updateRunTaskProgress();
});
const handleUpdateCollectStatus = () => {
  updateTaskCollectedStatus({
    run_id: taskId,
    is_favorite: !taskDetailStore.taskDetail.is_favorite,
  }).then((res) => {
    ElMessage.success({
      type: "success",
      message: taskDetailStore.taskDetail.is_favorite
        ? t("task.取消收藏成功")
        : t("task.收藏成功"),
    });
    getTaskDetail({ run_id: taskId }).then((res) => {
      taskInfo.value = res.data.data;
      const taskType = res.data.data.model_task;
      taskDetailStore.updateStore({
        taskType,
        taskDetail: res.data.data,
      });
    });
  });
};
const handleOpenInfoModal = () => {
  const list = [];
  switch (taskDetailStore.taskType) {
    case MULTICLASS:
      list.push(
        {
          label: "ACC (Accuracy)",
          value: t("task.ACC"),
        },
        {
          label: "Macro_F1 (Macro-averaging F1 Score)",
          value: t("task.Macro_F1"),
        },
        {
          label: "Micro_F1 (Micro-averaging F1 Score)",
          value: t("task.Micro_F1"),
        },
        {
          label: "Log_Loss (Logarithmic Loss)",
          value: t("task.Log_Loss"),
        }
      );
      break;
    case MULTILABEL_CLASSIFICATION:
    case CLASSIFICATION:
      list.push(
        {
          label: "AUC (Area Under the ROC Curve)",
          value: t("task.AUC"),
        },
        {
          label: "AUPRC (Area Under the Precision-Recall Curve)",
          value: t("task.AUPRC"),
        },
        {
          label: "F1_Score",
          value: t("task.F1_Score"),
        },
        {
          label: "MCC(Matthews Correlation Coefficient)",
          value: t("task.MCC"),
        },
        {
          label: "ACC(Accuracy)",
          value: t("task.ACC"),
        },
        {
          label: "Precision",
          value: t("task.Precision"),
        },
        {
          label: "Recall",
          value: t("task.Recall"),
        },
        {
          label: "Cohen_kappa (Cohen’s Kappa Coefficient)",
          value: t("task.Cohen_kappa"),
        },
        {
          label: "Log_Loss (Logarithmic Loss)",
          value: t("task.Log_Loss"),
        }
      );
      break;
    case REGRESSION:
    case MULTILABEL_REGRESSION:
      list.push(
        {
          label: "R2(Coefficient of Determination)",
          value: t("task.R2"),
        },
        {
          label: "Spearmanr",
          value: t("task.Spearmanr"),
        },
        {
          label: "Pearsonr",
          value: t("task.Pearsonr"),
        },
        {
          label: "MSE (Mean Squared Error)",
          value: t("task.MSE"),
        },
        {
          label: "MAE (Mean Absolute Error)",
          value: t("task.MAE"),
        },
        {
          label: "RMSE(Root Mean Squared Error):",
          value: t("task.RMSE"),
        }
      );
      break;
    default:
      break;
  }
  popup(HintModal, {
    title: t("task.提示"),
    descList: [
      {
        title: t("task.模型细节"),
        desc: list,
      },
    ],
  })
    .then((res) => {})
    .catch(() => {});
};
const handlePreviewDetail = () => {
  popup(ViewModelParam, {
    paramData: get(taskDetailStore.taskDetail, "task_type.fit"),
  })
    .then(() => {})
    .catch(() => {});
};
const detailLoading = ref<boolean>(true);

watchEffect(() => {
  if (get(taskDetailStore, "taskDetail.status") === "FINISHED") {
    getMetricsInfo({ run_id: taskId }).then((res) => {
      taskDetailStore.updateStore({
        metricsData: res.data.data,
      });
    });
    getDistributionInfo({ run_id: taskId }).then((res) => {
      taskDetailStore.updateStore({
        distributionData: res.data.data,
        currentTarget: Reflect.ownKeys(res.data.data)[0],
      });
    });
    getModelParamInfo({ run_id: taskId }).then((res) => {
      taskDetailStore.updateStore({
        modelParamData: res.data.data,
      });
    });
    getSelfModelAllDetail({ run_id: route.query.taskId as string })
      .then((res) => {
        taskDetailStore.updateStore({
          selfModelDetail: res.data.data,
        });
        detailLoading.value = false;
      })
      .finally(() => {
        detailLoading.value = false;
      });

    getTsneInfo({ run_id: route.query.taskId as string }).then((res) => {
      taskDetailStore.updateStore({
        TsneInfo: res.data.data,
      });
    });
  }
});

// getTaskAllInfo({ run_id: taskId }).then((res) => {
//   debugger;
//   taskDetailStore.updateStore({
//     allTaskInfo: res.data.data,
//   });
// });

const taskInfo = ref({ name: "" });
getTaskDetail({ run_id: taskId }).then((res) => {
  taskInfo.value = res.data.data;
  // const regex = /'task':\s*'([^']+)'/;
  // const match = res.data.data.params.Base.match(regex);
  // const taskType = match ? match[1] : "";
  const taskType = res.data.data.model_task;
  taskDetailStore.updateStore({
    taskType,
    taskDetail: res.data.data,
  });
});

const router = useRouter();
const handlePredict = () => {
  router.push({
    name: "taskPredict",
    query: {
      taskId,
    },
  });
};
const TaskDetailDOMId = "task-detail-dom";
const exportLoading = ref<boolean>(false);
enum CommandKey {
  DATA = "data",
  REPORT = "report",
}
const handleExport = (command: CommandKey) => {
  switch (command) {
    case CommandKey.DATA: {
      exportLoading.value = true;
      const zip = new JSZip();

      zip.file(
        `${t("task.模型细节")}.csv`,
        Papa.unparse(taskDetailStore.metricsData)
      );

      zip.file(
        `${t("task.数据分析")}.json`,
        JSON.stringify(taskDetailStore.selfModelDetail)
      );
      zip.file(
        `${t("task.分子相似度")}.json`,
        JSON.stringify(taskDetailStore.TsneInfo)
      );

      zip
        .generateAsync({ type: "blob" })
        .then((content) => {
          exportLoading.value = false;
          saveAs(content, `${taskDetailStore.taskDetail.name}-data.zip`);
          ElMessage.success({
            type: "success",
            message: t("task.导出成功"),
          });
        })
        .finally(() => {
          exportLoading.value = false;
        });

      break;
    }
    case CommandKey.REPORT: {
      popup(ExportReportView, {
        taskId: taskId,
      })
        .then((res) => {})
        .catch(() => {});
      break;
    }
    default:
      break;
  }
};

const handleHintSimilarity = () => {
  popup(HintModal, {
    title: t("task.提示"),
    descList: [
      {
        title: t("task.分子相似度"),
        desc: [
          {
            label: "",
            value: t("task.骨架hint"),
          },
        ],
      },
    ],
  })
    .then((res) => {})
    .catch(() => {});
};
const handleHintDistribution = () => {
  popup(HintModal, {
    title: t("task.提示"),
    descList: [
      {
        title: t("task.数据分布"),
        desc: [
          {
            label: "",
            value: t("task.数据分布hint"),
          },
        ],
      },
    ],
  })
    .then((res) => {})
    .catch(() => {});
};
const handleHintAnalysis = () => {
  const list = [];
  switch (taskDetailStore.taskType) {
    case MULTICLASS:
      list.push({
        label: "",
        value: t("task.数据分析多分类hint"),
      });
      break;
    case MULTILABEL_CLASSIFICATION:
    case CLASSIFICATION:
      list.push({
        label: "",
        value: t("task.数据分析分类hint"),
      });
      break;
    case REGRESSION:
    case MULTILABEL_REGRESSION:
      list.push({
        label: "",
        value: t("task.数据分析回归hint"),
      });
      break;
    default:
      break;
  }
  popup(HintModal, {
    title: t("task.提示"),
    descList: [
      {
        title: t("task.分子相似度"),
        desc: list,
      },
    ],
  })
    .then((res) => {})
    .catch(() => {});
};
</script>

<style lang="scss" scoped>
.border-bottom-shadow {
  box-shadow: #00000014 0px 2px 6px 0px;
}
:deep() {
  .el-progress__text {
    font-size: 14px !important;
  }
}
</style>
