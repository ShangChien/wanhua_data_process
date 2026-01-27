<template>
  <div>
    <div :class="['general-wrapper']">
      <div :class="['card-style', 'mb-5']">
        <div :class="['flex', 'items-center', 'mb-3']">
          <svg :class="['mr-2']" width="20" height="20">
            <use href="#prediction"></use>
          </svg>
          <span :class="['text-h6', 'mb-0']">
            {{ $t("task.预测任务") }}
          </span>
        </div>
        <ElSpace size="large">
          <Description :label="$t('task.任务名称:')" :value="taskDetail.name" />

          <Description
            :label="$t('task.使用数据集:')"
            :value="getOriginDataSetFileName(taskDetail.data_path || '') || ''"
          />
          <Description
            v-if="trainTaskDetail.status"
            :label="$t('task.任务状态：')"
            :value="$t(getStatusI18nKey(taskDetail.status))"
          >
            <template #value>
              <div>
                {{ $t(getStatusI18nKey(taskDetail.status)) }}
              </div>
              <ElProgress
                v-if="processVisible"
                size="small"
                :stroke-width="10"
                :class="['w-[200px]']"
                :percentage="runPercentage"
              />
            </template>
          </Description>
          <Description
            :label="$t('task.使用模型：')"
            :value="trainTaskDetail.name"
          />
          <Description
            v-if="trainTaskDetail.model_task"
            :label="$t('task.模型类型：')"
            :value="$t(getTaskI18nKey(trainTaskDetail.model_task))"
          />
          <Description
            v-if="taskDetail.explain_state"
            :label="$t('task.可解释性运行状态：')"
            :value="taskDetail.explain_state"
          />
        </ElSpace>
        <ElDivider :class="['my-[20px]']" />
        <ElRow>
          <ElCol :span="16">
            <ElSpace alignment="center" :size="64">
              <StatisticItem
                bg-color="#F5E8FF"
                line-color="#722ED1"
                icon="#used-time"
                :title="$t('task.任务用时')"
                >{{ customTime }}</StatisticItem
              >
              <StatisticItem
                bg-color="#FFE4BA"
                line-color="#F77234"
                icon="#dataset"
                :title="$t('task.数据总数')"
                >{{ totalNumber }}</StatisticItem
              >
            </ElSpace>
          </ElCol>
          <ElCol :span="8" :class="['flex', 'flex-row-reverse']">
            <ElSpace>
              <ElButton type="primary" @click="viewModelDetail">
                {{ $t("task.查看模型") }}
              </ElButton>
              <ElButton type="primary" @click="handleViewModelParam">
                {{ $t("task.查看模型参数") }}
              </ElButton>
            </ElSpace></ElCol
          >
        </ElRow>
      </div>
      <template v-if="metricsList.length">
        <div :class="['card-style', 'mt-5', 'mb-6']">
          <div :class="['text-h6']">
            {{ $t("task.模型指标") }}
          </div>
          <MetricsEnum :list="metricsList" />
        </div>
      </template>

      <div :class="['card-style', 'mb-6']" v-if="isSuccessTask">
        <div
          :class="['mb-4', 'flex', 'gap-3', 'items-center', 'justify-between']"
        >
          <ElSpace>
            <ElRadioGroup v-model="currentShowMethod">
              <ElRadioButton :label="$t('task.卡片')" :value="'CARD'" />
              <ElRadioButton :label="$t('task.表格')" :value="'TABLE'" />
            </ElRadioGroup>
            <ElTooltip :content="$t('task.更多信息')" placement="bottom">
              <ElButton @click="handleHintPredictInfo" link type="primary">
                <svg class="iconpark-icon">
                  <use href="#hint"></use>
                </svg>
              </ElButton>
            </ElTooltip>
          </ElSpace>
          <ElSpace>
            <ElDropdown @command="handleExport">
              <ElButton type="primary" :loading="downLoading">
                {{ $t("task.导出") }}
              </ElButton>
              <template #dropdown>
                <ElDropdownMenu>
                  <ElDropdownItem command="csv">
                    <!-- {{ $t("task.导出csv") }} -->
                    csv
                  </ElDropdownItem>
                  <ElDropdownItem command="xlsx">
                    <!-- {{ $t("task.导出xlsx") }} -->
                    xlsx
                  </ElDropdownItem>
                </ElDropdownMenu>
              </template>
            </ElDropdown>

            <ElInput
              clearable
              :class="['w-[240px]']"
              :placeholder="$t('task.模糊搜索SMILES')"
              v-model.trim="searchKeyword"
              @input="debouncedSearchTaskList"
            />
            <ElButton @click="getData" link>
              <Icon icon="mdi:refresh" width="22" height="22"></Icon>
            </ElButton>
          </ElSpace>
        </div>

        <template v-if="currentShowMethod === 'TABLE'">
          <div :class="['mb-4']">
            <ElButton @click="handleConfigColumn" type="primary">
              {{ $t("task.显示/隐藏 理化性质表格列") }}
            </ElButton>
          </div>
          <VxeTable
            v-loading="tableLoading"
            height="500"
            show-overflow
            :scroll-y="{ enabled: true, gt: 0 }"
            :data="data"
            :row-config="{
              height: 97,
            }"
          >
            <VxeColumn
              min-width="100"
              title="ID"
              fixed="left"
              field="ID"
              sortable
            />
            <VxeColumn min-width="100" title="SMILES" fixed="left">
              <template #default="scope">
                <LongTextComponent
                  :text="scope.row[scope.column.title]"
                  :lineNumber="1"
                />
              </template>
            </VxeColumn>
            <VxeColumn title="2D_Graph" min-width="100" :field="'2D_Graph'">
              <template #default="scope">
                <div>
                  <CustomImg
                    :key="getImageUrl(scope.row, scope.column.property)"
                    :src="getImageUrl(scope.row, scope.column.property)"
                    width="80"
                    height="80"
                  />
                </div>
              </template>
            </VxeColumn>

            <template v-if="taskDetail.model_task === MULTICLASS">
              <template v-for="targetKey in kindOfKeys.targetList">
                <VxeColgroup :title="targetKey">
                  <VxeColumn
                    v-if="hasExplainGraph"
                    min-width="100"
                    title="2D_Graph_Explanation"
                    :field="'2D_Graph_Explanation_' + targetKey"
                  >
                    <template #default="scope">
                      <div>
                        <CustomImg
                          :src="getImageUrl(scope.row, scope.column.property)"
                          width="80"
                          height="80"
                          :key="getImageUrl(scope.row, scope.column.property)"
                        />
                      </div>
                    </template>
                  </VxeColumn>
                  <VxeColumn
                    min-width="100"
                    title="predict"
                    sortable
                    field="predict_TARGET"
                  >
                    <template #header="scope">
                      <ElSpace>
                        <div>{{ scope.column.title }}</div>
                        <ElTooltip
                          :content="
                            $t('task.查看分布图', { field: scope.column.title })
                          "
                          placement="top"
                        >
                          <ElButton
                            link
                            @click="handlePreviewChart(scope.column)"
                          >
                            <Icon
                              icon="solar:chart-2-bold-duotone"
                              width="18"
                              height="18"
                              style="color: #2e3db2"
                            ></Icon>
                          </ElButton>
                        </ElTooltip>
                      </ElSpace>
                    </template>
                    <template #default="scope">
                      <div :title="scope.row[scope.column.property]">
                        {{
                          formatterScienceNumber(
                            scope.row[scope.column.property]
                          )
                        }}
                      </div>
                    </template>
                  </VxeColumn>
                  <VxeColumn
                    sortable
                    min-width="100"
                    v-for="item in kindOfKeys.probNumberList"
                    :key="item"
                    :title="item"
                    :field="item"
                  >
                    <template #default="scope">
                      <div :title="scope.row[scope.column.property]">
                        {{
                          formatterScienceNumber(
                            scope.row[scope.column.property]
                          )
                        }}
                      </div>
                    </template>
                  </VxeColumn>
                </VxeColgroup>
              </template>
            </template>
            <template
              v-else-if="RegressionList.includes(taskDetail.model_task)"
            >
              <template v-for="targetKey in kindOfKeys.targetList">
                <VxeColgroup :title="targetKey">
                  <VxeColumn
                    min-width="100"
                    v-if="hasExplainGraph"
                    title="2D_Graph_Explanation"
                    :field="'2D_Graph_Explanation_' + targetKey"
                  >
                    <template #default="scope">
                      <div>
                        <CustomImg
                          :key="getImageUrl(scope.row, scope.column.property)"
                          :src="getImageUrl(scope.row, scope.column.property)"
                          width="80"
                          height="80"
                        />
                      </div>
                    </template>
                  </VxeColumn>
                  <VxeColumn
                    sortable
                    min-width="100"
                    title="predict"
                    :field="'predict_' + targetKey"
                  >
                    <template #header="scope">
                      <ElSpace>
                        <div>{{ scope.column.title }}</div>
                        <ElTooltip
                          :content="
                            $t('task.查看分布图', { field: scope.column.title })
                          "
                          placement="top"
                        >
                          <ElButton
                            link
                            @click="handlePreviewChart(scope.column)"
                          >
                            <Icon
                              icon="solar:chart-2-bold-duotone"
                              width="18"
                              height="18"
                              style="color: #2e3db2"
                            ></Icon>
                          </ElButton>
                        </ElTooltip>
                      </ElSpace>
                    </template>
                    <template #default="scope">
                      <div :title="scope.row[scope.column.property]">
                        {{
                          formatterScienceNumber(
                            scope.row[scope.column.property]
                          )
                        }}
                      </div>
                    </template>
                  </VxeColumn>
                  <VxeColumn
                    sortable
                    min-width="100"
                    title="predict_std"
                    :field="'predict_std_' + targetKey"
                  >
                    <template #default="scope">
                      <div :title="scope.row[scope.column.property]">
                        {{
                          formatterScienceNumber(
                            scope.row[scope.column.property]
                          )
                        }}
                      </div>
                    </template>
                  </VxeColumn>
                </VxeColgroup>
              </template>
            </template>
            <template v-else>
              <template v-for="targetKey in kindOfKeys.targetList">
                <VxeColgroup :title="targetKey">
                  <VxeColumn
                    min-width="100"
                    v-if="hasExplainGraph"
                    title="2D_Graph_Explanation"
                    :field="'2D_Graph_Explanation_' + targetKey"
                  >
                    <template #default="scope">
                      <div>
                        <CustomImg
                          :key="getImageUrl(scope.row, scope.column.property)"
                          :src="getImageUrl(scope.row, scope.column.property)"
                          width="80"
                          height="80"
                        />
                      </div>
                    </template>
                  </VxeColumn>
                  <VxeColumn
                    min-width="100"
                    title="predict"
                    sortable
                    :field="'predict_' + targetKey"
                  >
                    <template #header="scope">
                      <ElSpace>
                        <div>{{ scope.column.title }}</div>
                        <ElTooltip
                          :content="
                            $t('task.查看分布图', { field: scope.column.title })
                          "
                          placement="top"
                        >
                          <ElButton
                            link
                            @click="handlePreviewChart(scope.column)"
                          >
                            <Icon
                              icon="solar:chart-2-bold-duotone"
                              width="18"
                              height="18"
                              style="color: #2e3db2"
                            ></Icon>
                          </ElButton>
                        </ElTooltip>
                      </ElSpace>
                    </template>
                    <template #default="scope">
                      <div :title="scope.row[scope.column.property]">
                        {{
                          formatterScienceNumber(
                            scope.row[scope.column.property]
                          )
                        }}
                      </div>
                    </template>
                  </VxeColumn>
                  <VxeColumn
                    min-width="100"
                    title="prob"
                    sortable
                    :field="'prob_' + targetKey"
                  >
                    <template #default="scope">
                      <div :title="scope.row[scope.column.property]">
                        {{
                          formatterScienceNumber(
                            scope.row[scope.column.property]
                          )
                        }}
                      </div>
                    </template>
                  </VxeColumn>
                </VxeColgroup>
              </template>
            </template>

            <VxeColumn
              min-width="100"
              v-for="item in configColumnList"
              :key="item"
              :title="item"
              :field="item"
              sortable
            >
              <template #header="scope">
                <ElTooltip
                  :content="$t(`task.${scope.column.title}`)"
                  placement="top"
                >
                  <span>{{ scope.column.title }}</span>
                </ElTooltip>
              </template>
              <template #default="scope">
                <div :title="scope.row[scope.column.title]">
                  {{ formatterScienceNumber(scope.row[scope.column.title]) }}
                </div>
              </template>
            </VxeColumn>
          </VxeTable>
        </template>
        <template v-else>
          <div
            ref="cardWrapper"
            v-loading="tableLoading"
            :class="['max-h-[600px]', 'min-h-52', 'overflow-auto']"
          >
            <RecycleScroller
              key-field="id"
              :items="data"
              :item-size="162"
              :buffer="1000"
              :grid-items="cardNumberPreRow"
              :item-secondary-size="cardItemWidth"
              :page-mode="true"
              @resize="handleVirtualListResize"
            >
              <template #default="{ item, index }">
                <!-- <ElCol
                  :span="8"
                  :xl="{
                    span: 4,
                  }"
                  v-for="(item, index) in data"
                  :key="index"
                > -->
                <div :class="['p-[10px]']">
                  <SmilesCard
                    :data="item"
                    :kindOfKeys="kindOfKeys"
                    :taskType="taskDetail.model_task"
                  />
                </div>
              </template>
              <!-- </ElCol> -->
            </RecycleScroller>
          </div>
        </template>
        <ElPagination
          :class="['pager']"
          v-model:currentPage="pageVO.currentPage"
          v-model:pageSize="pageVO.pageSize"
          :total="pageVO.total"
          @change="handlePaginationChange"
          v-bind="paginationProp"
        />
      </div>
      <div :class="['card-style', 'mt-6']" v-if="logModelVisible">
        <ElRow>
          <TaskLogViewer :logFileName="taskDetail.name + '-log'" />
        </ElRow>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Description from "@/components/description/index.vue";
import ImageViewer from "@/components/img-viewer/index.vue";
import LongTextComponent from "@/components/long-text-component/index.vue";
import HintModal from "@/components/modal/HintModal.vue";
import { popup } from "@/components/modal/ModalContainer.vue";
import { physicochemicalPropertyList } from "@/constants/predict";
import {
  CLASSIFICATION,
  MULTICLASS,
  MULTILABEL_CLASSIFICATION,
  MULTILABEL_REGRESSION,
  REGRESSION,
  RegressionList,
} from "@/constants/task";
import {
  getPredictTableCSV,
  getPredictTableData,
  getPredictTableXLSX,
  getPredictTableZIP,
} from "@/service/api/predict";
import { getTaskDetail, getTaskRunProgress } from "@/service/api/task";
import {
  formatDuration,
  formatterScienceNumber,
  getOriginDataSetFileName,
  getStatusI18nKey,
  getTaskI18nKey,
} from "@/utils/formatter";
import { isClassificationTask } from "@/utils/judge";
import { useNavigation } from "@/utils/navigation";
import { Icon } from "@iconify/vue/dist/iconify.js";
import {
  ElButton,
  ElCol,
  ElDivider,
  ElDropdownMenu,
  ElDropdownItem,
  ElDropdown,
  ElInput,
  ElMessage,
  ElPagination,
  ElProgress,
  ElRadioButton,
  ElRadioGroup,
  ElRow,
  ElSpace,
  ElTable,
  ElTableColumn,
  ElTooltip,
  vLoading,
} from "element-plus";
import { debounce, get, isEmpty, uniqueId } from "lodash";
import { computed, onMounted, ref, watchEffect } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import StatisticItem from "../task-detail/StatisticItem.vue";
import TaskLogViewer from "../task-detail/TaskLogViewer.vue";
import SmilesCard from "./components/SmilesCard.vue";
import ColumnConfig from "./model/ColumnConfig.vue";
import PredictYChartModal from "./model/PredictYChartModal.vue";
import ViewModelParam from "./model/ViewModelParam.vue";
import { triggerDownload } from "@/utils/download";
import { Parser } from "@json2csv/plainjs";
import CustomImg from "@/components/custom-img/index.vue";
import { getMetricsInfo, getPredictMetric } from "@/service/api/model";
import MetricsEnum from "@/components/metrics-enum/index.vue";
import { useElementBounding } from "@vueuse/core";
import usePageVO from "@/hooks/usePageVO";
import { saveAs } from "file-saver";
const { pageVO, paginationProp } = usePageVO();
const metricsList = ref<any[]>([]);
const tableLoading = ref(false);
const navigation = useNavigation();
const selectedURL = ref<string>("");
const route = useRoute();
const taskLog = ref("");
type PredictShowMethod = "TABLE" | "CARD";
const currentShowMethod = ref<PredictShowMethod>("CARD");
const taskDetail = ref<Record<string, any>>({});
const trainTaskDetail = ref<Record<string, any>>({});
const customTime = ref("");
const searchKeyword = ref<string>("");
const totalNumber = ref<number>(0);
getTaskDetail({
  run_id: route.query.taskId as string,
}).then((res) => {
  taskDetail.value = res.data.data;
});
const isSuccessTask = computed(() =>
  ["FINISHED", "FAILED"].includes(taskDetail.value.status)
);
const logModelVisible = computed(() => {
  const value = get(taskDetail.value, "status");
  return value && value !== "SCHEDULED";
});
const kindOfKeys = ref<{
  probNumberList: string[];
  targetList: string[];
}>({
  probNumberList: [],
  targetList: [],
});

const runPercentage = ref(0);
const processVisible = computed(() => {
  return taskDetail.value.status === "RUNNING";
});
const updateRunTaskProgress = () => {
  if (processVisible.value) {
    getTaskRunProgress({ run_id: route.query.taskId as string }).then((res) => {
      // 1->100
      runPercentage.value = res.data.data * 100;
    });
  }
};
watchEffect(() => {
  updateRunTaskProgress();
});
const { t } = useI18n();
const handleHintPredictInfo = () => {
  const list = [
    {
      label: "2D_Graph_Explanation_*:",
      value: t("task.解释2DGraph"),
    },
  ];

  switch (taskDetail.value.model_task) {
    case MULTICLASS:
      list.push({
        label: "predict_std_*:",
        value: t("task.解释多类别std"),
      });
      break;
    case MULTILABEL_CLASSIFICATION:
    case CLASSIFICATION:
      list.push({
        label: "prob_*:",
        value: t("task.解释prob"),
      });
      break;
    case REGRESSION:
    case MULTILABEL_REGRESSION:
      list.push({
        label: "predict_std_*:",
        value: t("task.解释std"),
      });
      break;
    default:
      break;
  }
  popup(HintModal, {
    title: t("task.提示"),
    descList: [
      {
        title: t("task.预测参数"),
        desc: list,
      },
    ],
  })
    .then((res) => {})
    .catch(() => {});
};
const handlePreview = (src: string) => {
  popup(ImageViewer, {
    imgSrc: src,
  })
    .then((res) => {})
    .catch(() => {});
};
const getData = () => {
  if (taskDetail.value.model_trained_run_id) {
    getTaskDetail({
      run_id: taskDetail.value.model_trained_run_id,
    })
      .then((res) => {
        trainTaskDetail.value = res.data.data;
      })
      .finally(() => {});
  }
};
watchEffect(() => {
  getData();
});
onMounted(() => {
  getPredictMetric({
    run_id: route.query.taskId as string,
    // run_id: "66a8567f8c079a472a9779af",
  }).then((res) => {
    if (!isEmpty(res.data.data)) {
      metricsList.value = Object.entries(res.data.data[0])
        .filter((item) => {
          return !["Index", "Models", "Features"].includes(item[0]);
        })
        .map((item) => ({ label: item[1], value: item[0] }));
    }
  });
});
const viewModelDetail = () => {
  if (taskDetail.value.model_trained_run_id)
    navigation.jumpToTaskDetailPage(taskDetail.value.model_trained_run_id);
};

const judgeIsChartCol = (data: any) => {
  return (data.column.label + "").startsWith("predict_TARGET");
};
const is2DSMILESCol = (data: any) => {
  return (data.column.label + "").startsWith("2D_Graph_Explanation_TARGET");
};
const isSMIlESCol = (label: string) => {
  return label === "SMILES";
};
const getImageUrl = (rowData: any, prop: string) => {
  return (
    `${import.meta.env.VITE_REQUEST_BASE_URL}model/chart/predict_image/` +
    rowData[prop]
  );
};
const fixedList = ref<string[]>([]);
const data = ref<any[]>([]);
let originalData: any[] = [];
const hasExplainGraph = computed(() => {
  if (data.value.length > 0) {
    const exampleData = data.value[0];
    return Reflect.ownKeys(exampleData).some((key: any) => {
      return key.startsWith("2D_Graph_Explanation");
    });
  }
  return false;
});
const SMILESGraphExplanationList = ref<string[]>([]);
watchEffect(() => {
  if (data.value.length) {
    const totalKeys = Reflect.ownKeys(data.value[0]);
    SMILESGraphExplanationList.value = totalKeys.filter((item: any) =>
      item.startsWith("2D_Graph_Explanation_TARGET")
    ) as string[];
    fixedList.value = totalKeys.filter(
      (item: any) => !physicochemicalPropertyList.includes(item)
    ) as string[];
    kindOfKeys.value.probNumberList = totalKeys.filter((item: any) =>
      /^prob_\d+$/.test(item)
    ) as string[];
    if (RegressionList.includes(taskDetail.value.model_task))
      kindOfKeys.value.targetList = (
        totalKeys.filter((item: any) => {
          return /predict_std(_\d+)?/.test(item);
        }) as string[]
      ).map((item: string) => item.replace("predict_std_", "")) as string[];
    else {
      kindOfKeys.value.targetList = (
        totalKeys.filter((item: any) => {
          return /predict(_\d+)?/.test(item);
        }) as string[]
      ).map((item: string) => item.replace("predict_", "")) as string[];
    }
  }
});

const handleConfigColumn = () => {
  popup(ColumnConfig, {
    currentSelectKeys: [...configColumnList.value],
  })
    .then((res: any) => {
      configColumnList.value = [...res];
    })
    .catch((err) => {});
};
const searchPredictTable = () => {
  tableLoading.value = true;
  getPredictTableData({
    run_id: route.query.taskId as string,
    page: pageVO.value.currentPage,
    page_size: pageVO.value.pageSize,
    keyword: searchKeyword.value,
  })
    .then((res) => {
      data.value = res.data.data.items.map((item: any) => ({
        id: uniqueId(),
        ...item,
      }));
      pageVO.value.total = res.data.data.total_count;
      originalData = data.value;
      totalNumber.value = res.data.data.total_count;
    })
    .finally(() => {
      tableLoading.value = false;
    });
};
const debouncedSearchTaskList = debounce(searchPredictTable, 500);
watchEffect(() => {
  if (isSuccessTask.value) {
    searchPredictTable();
  }
});
const handlePaginationChange = () => {
  searchPredictTable();
};
const configColumnList = ref<any>([]);
const handlePreviewChart = (colData: any) => {
  const list = data.value.map((item: any) => item[colData.property]);
  const ret: Record<string, number> = {};
  for (let i = 0; i < list.length; i++) {
    const key = list[i];
    if (key in ret) {
      ret[key] += 1;
    } else {
      ret[key] = 1;
    }
  }
  const ret1 = Reflect.ownKeys(ret).map((item: any) => {
    return {
      name: item,
      value: ret[item],
    };
  });
  popup(PredictYChartModal, {
    chartData: ret1,
    chartType: isClassificationTask(taskDetail.value?.model_task || "")
      ? "pie"
      : "bar",
    title: t("task.分布图", { field: colData.label }),
  })
    .then((res) => {})
    .catch();
};
const downLoading = ref<boolean>(false);
const handleExport = (command: string) => {
  downLoading.value = true;
  if (command === "csv") {
    getPredictTableCSV({
      run_id: route.query.taskId as string,
    })
      .then((res) => {
        saveAs(
          new Blob([res.data], {
            type: "text/csv;charset=utf-8",
          }),
          taskDetail.value.name + "-predict-result.csv"
        );
      })
      .catch(() => {
        ElMessage.error(t("task.导出失败"));
      })
      .finally(() => {
        downLoading.value = false;
      });
  } else {
    getPredictTableZIP({
      run_id: route.query.taskId as string,
      with_explain: taskDetail.value.explain_state == "FINISHED",
    })
      .then((res) => {
        // debugger;
        saveAs(
          new Blob([res.data], {
            type: "application/zip",
          }),
          taskDetail.value.name + "-predict-result.zip"
        );
      })
      .catch(() => {
        ElMessage.error(t("task.导出失败"));
      })
      .finally(() => {
        downLoading.value = false;
      });
  }
};

const handleRefreshLog = () => {};
const handleCopyLog = () => {};

const handleViewModelParam = () => {
  popup(ViewModelParam, {
    paramData: get(trainTaskDetail.value, "task_type.fit"),
  })
    .then((res) => {})
    .catch(() => {});
};
watchEffect(() => {
  if (!isEmpty(taskDetail.value)) {
    customTime.value = formatDuration(
      taskDetail.value.start_time,
      taskDetail.value.end_time
    );
  }
});
const handleSearch = () => {
  if (searchKeyword.value !== "") {
    const searchList = originalData.filter((item: any) => {
      return (
        item.SMILES.includes(searchKeyword.value) ||
        (item?.ID + "" || "").includes(searchKeyword.value)
      );
    });
    data.value = searchList;
  } else {
    data.value = originalData;
  }
};
const cardWrapper = ref();
const cardNumberPreRow = ref(4);
const cardItemWidth = ref(400);
const adjustCardNumberPreRow = () => {
  if (cardWrapper.value) {
    const { width } = useElementBounding(cardWrapper);
    if (width.value > 1900) {
      //xl
      cardNumberPreRow.value = 8;
    } else {
      cardNumberPreRow.value = 4;
    }
    cardItemWidth.value = width.value / cardNumberPreRow.value;
  }
};
onMounted(() => {
  adjustCardNumberPreRow();
});
const handleVirtualListResize = () => {
  adjustCardNumberPreRow();
};
</script>

<style lang="scss" scoped>
.card-text {
  color: #0009;
}
</style>
