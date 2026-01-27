<template>
  <ElDialog
    :title="$t('task.导出预览')"
    :show-close="true"
    v-model="dialogVisible"
    width="80%"
    :before-close="props.handleOK"
    :close-on-press-escape="false"
  >
    <div :class="['report-wrapper']">
      <div :class="['report-container']" id="report">
        <div :class="['flex', 'gap-6', 'flex-col']">
          <div :class="['card-style']">
            <div :class="['flex', 'justify-between', 'mb-8']">
              <ElSpace alignment="center" size="large">
                <Description
                  :label="$t('task.任务名称:')"
                  :value="taskDetailStore.taskDetail.name"
                />
                <Description
                  :label="$t('task.任务类型:')"
                  :value="$t(getTaskI18nKey(taskDetailStore.taskType))"
                />
              </ElSpace>
            </div>
            <StatisticData />
          </div>
          <div :class="['card-style']">
            <div :class="['text-h6', 'flex', 'items-center']">
              {{ $t("task.模型对比") }}
            </div>
            <VxeTable
              border="none"
              ref="modelTableRef"
              height="440"
              auto-resize
              round
              :data="taskDetailStore.metricsData"
            >
              <template v-for="item in columnList" :key="item.prop">
                <VxeColumn
                  show-header-overflow
                  show-overflow="title"
                  show-footer-overflow
                  minWidth="110"
                  :title="item.label"
                  :field="item.prop"
                  :prop="item.prop"
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
            </VxeTable>
          </div>
          <ElRow v-for="item in taskDetailStore.targetList" :gutter="24">
            <ElCol :span="12">
              <div :class="['card-style']">
                <div :class="['text-h6', 'flex', 'items-center']">
                  {{ item + " " + $t("task.数据分析") }}
                </div>
                <div :class="['flex', 'items-center', 'justify-center']">
                  <CustomImg
                    v-if="pdfContentImgDict"
                    @handle-img-load="handleImgLoaded"
                    :src="pdfContentImgDict[validImageName(item)]"
                  />
                </div>
              </div>
            </ElCol>
            <ElCol :span="12">
              <div :class="['card-style', 'flex', 'flex-col', 'h-full']">
                <div :class="['text-h6', 'flex', 'items-center']">
                  {{ item + " " + $t("task.数据分布") }}
                </div>
                <div
                  :class="['flex', 'items-center', 'justify-center', 'flex-1']"
                >
                  <div :class="['w-full', 'h-full']">
                    <PieChartGraph
                      v-if="taskDetailStore.isClassification"
                      :data="getTargetGraphData(item)"
                    />

                    <DistributionChart
                      v-else
                      :data="getTargetGraphData(item)"
                    />
                  </div>
                </div>
              </div>
            </ElCol>
          </ElRow>

          <ElRow :gutter="24">
            <ElCol :span="12">
              <div :class="['card-style']">
                <div :class="['text-h6', 'flex', 'items-center']">
                  {{ $t("task.分子指纹 T-SNE降维绘图") }}
                </div>
                <div :class="['flex', 'items-center', 'justify-center']">
                  <CustomImg
                    v-if="pdfContentImgDict"
                    @handle-img-load="handleImgLoaded"
                    :src="pdfContentImgDict['fp_pca.png']"
                  />
                </div>
              </div>
            </ElCol>
            <ElCol :span="12">
              <div :class="['card-style']">
                <div :class="['text-h6', 'flex', 'items-center']">
                  {{ $t("task.分子指纹 PCA主成分分析绘图") }}
                </div>
                <div :class="['flex', 'items-center', 'justify-center']">
                  <CustomImg
                    v-if="pdfContentImgDict"
                    @handle-img-load="handleImgLoaded"
                    :src="pdfContentImgDict['fp_tsne.png']"
                  />
                </div>
              </div>
            </ElCol>
          </ElRow>
        </div>
      </div>
    </div>
    <template #footer>
      <ElButton @click="props.handleCancel">{{ $t("common.取消") }}</ElButton>
      <ElButton
        :disabled="exportBtnDisabled"
        :loading="exportLoading"
        type="primary"
        @click="handleExport"
        >{{ $t("common.导出") }}</ElButton
      >
    </template>
  </ElDialog>
</template>

<script lang="ts" setup>
import CustomImg from "@/components/custom-img/index.vue";
import Description from "@/components/description/index.vue";
import DistributionChart from "@/components/graph/DistributionChart.vue";
import PieChartGraph from "@/components/graph/PieChartGraph.vue";
import { getPDFReportImg } from "@/service/api/task";
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import {
  formatParamLabel,
  formatterScienceNumber,
  getTaskI18nKey,
} from "@/utils/formatter";
import {
  ElButton,
  ElCol,
  ElDialog,
  ElMessage,
  ElRow,
  ElSpace,
  vLoading,
} from "element-plus";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { countBy } from "lodash";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import StatisticData from "../StatisticalData.vue";

const { t } = useI18n();
const exportLoading = ref<boolean>(false);
const loadedImgCount = ref(0);
const exportBtnDisabled = computed(() => {
  return loadedImgCount.value < 3;
});
const taskDetailStore = useTaskDetailStore();
const props = defineProps<{
  handleOK: any;
  handleCancel: any;
  taskId: string;
}>();
const formData = ref({
  exportType: "pdf",
  exportName: taskDetailStore.taskDetail.name + `-${t("common.训练任务报告")}`,
});
const dialogVisible = ref<boolean>(false);
const pdfContentImgDict = ref<any>();
const handleImgLoaded = () => {
  loadedImgCount.value++;
};
getPDFReportImg({
  run_id: props.taskId,
}).then((res) => {
  const ret: Record<string, string> = {};
  res.data.data.forEach((item) => {
    ret[item.file_name] = item.content;
  });
  pdfContentImgDict.value = ret;
});

onMounted(() => {
  dialogVisible.value = true;
});
const columnList = computed(() => {
  if (taskDetailStore.metricsData && taskDetailStore.metricsData.length)
    return Object.keys(taskDetailStore.metricsData[0])
      .filter((item) => item !== "_X_ROW_KEY")
      .map((item) => {
        return {
          label: item,
          prop: item,
        };
      });
  return [];
});
const validImageName = (target: string) => {
  return `valid_${target}_result.png`;
};
const getTargetGraphData = (target: string) => {
  const curTargetDistribution =
    taskDetailStore.distributionData[taskDetailStore.currentTarget];

  if (taskDetailStore.isClassification) {
    return Object.entries(countBy(curTargetDistribution)).map((item) => {
      return {
        name: item[0],
        value: item[1],
      };
    });
  } else {
    return curTargetDistribution;
  }
};
const handleExport = () => {
  exportLoading.value = true;
  let node = document.getElementById("report")!;
  html2canvas(node, {
    allowTaint: true,
    scale: 2, // 提高分辨率
    useCORS: true, // 处理跨域问题
  }).then((canvas) => {
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "pt",
      format: [canvas.width, canvas.height],
    });
    pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height);
    pdf.save(taskDetailStore.taskDetail.name + `-${t("common.训练任务报告")}`);
    exportLoading.value = false;
    ElMessage.success(t("common.导出成功"));
    // const pageWidth = 841.89;
    // const pageHeight = 592.28;
    // // 设置内容的宽高
    // const contentWidth = canvas.width;
    // const contentHeight = canvas.height;
    // // 默认的偏移量
    // let position = 0;
    // // 设置生成图片的宽高
    // const imgCanvasWidth = pageWidth;
    // const imgCanvasHeight = (592.28 / contentWidth) * contentHeight;
    // let imageHeight = imgCanvasHeight;
    // // 生成canvas截图，1表示生成的截图质量（0-1）
    // let pageData = canvas.toDataURL("image/jpeg", 1);
    // // new JsPDF接收三个参数，landscape表示横向，（默认不填是纵向），打印单位和纸张尺寸
    // let PDF = new jsPDF("landscape", "pt", "a4");
    // // 当内容不超过a4纸一页的情况下
    // if (imageHeight < pageHeight) {
    //   PDF.addImage(pageData, "JPEG", 20, 20, imgCanvasWidth, imgCanvasHeight);
    // } else {
    //   // 当内容超过a4纸一页的情况下，需要增加一页
    //   while (imageHeight > 0) {
    //     PDF.addImage(
    //       pageData,
    //       "JPEG",
    //       20,
    //       position,
    //       imgCanvasWidth,
    //       imgCanvasHeight
    //     );
    //     imageHeight -= pageHeight;
    //     position -= pageHeight;
    //     // 避免添加空白页
    //     if (imageHeight > 0) {
    //       PDF.addPage();
    //     }
    //   }
    // }
    // // 调用save方法生成pdf文件
    // PDF.save("导出pdf" + ".pdf");
  });
};
</script>

<style lang="scss" scoped>
@import "@/assets/variables";
.report-container {
  background: $gray1-color;
  padding: 24px;
  min-width: 2000px;
}
.report-wrapper {
  overflow: auto;
  max-height: 50vh;
}
.abc {
  display: none;
}
:deep() {
  #modal-container {
    display: none;
  }
  .vxe-table--body-wrapper {
    .vxe-body--row:first-child {
      font-weight: bold;
    }
  }
}
</style>
