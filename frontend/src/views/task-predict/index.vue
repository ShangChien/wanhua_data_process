<template>
  <div :class="['general-wrapper']">
    <div :class="['card-style']">
      <div :class="['text-step']">
        {{ $t("task.步骤一：选择输入数据") }}
      </div>

      <div :class="['flex', 'gap-10']">
        <div :class="['w-[700px]', 'pt-6']">
          <ElForm
            label-width="auto"
            :model="formData"
            :rules="formRules"
            ref="formRef"
          >
            <ElFormItem label=" ">
              <ElSpace>
                <Icon
                  icon="ep:warning-filled"
                  width="16"
                  height="22"
                  style="color: #ffa956"
                ></Icon>
                <span :class="['text-tip', 'text-nowrap']">
                  {{ $t("task.经过检查的数据集才可以预测") }}
                </span>
                <ElButton link type="primary" @click="handleDownLoadTemplate">
                  <svg :class="['iconpark-icon', 'mr-[4px]']">
                    <use href="#down-cloud"></use>
                  </svg>
                  {{ $t("task.下载模板") }}
                </ElButton>
              </ElSpace>
            </ElFormItem>

            <ElFormItem :label="$t('task.任务名称')" prop="task_name">
              <ElInput
                clearable
                v-model.trim="formData.task_name"
                :placeholder="$t('task.请输入任务名称')"
              />
            </ElFormItem>
            <ElFormItem :label="$t('task.子结构可解释性')" prop="explain">
              <ElRadioGroup v-model="formData.explain">
                <ElRadio :value="true" :label="$t('task.是')"></ElRadio>
                <ElRadio :value="false" :label="$t('task.否')"></ElRadio>
              </ElRadioGroup>
            </ElFormItem>
            <ElFormItem :label="$t('task.输入方式')" prop="inputMethod">
              <ElRadioGroup
                v-model="inputMethod"
                @change="handleInputMethodChange"
              >
                <ElRadioButton
                  :label="$t('task.上传文件')"
                  :value="InputMethod.FILE"
                >
                </ElRadioButton>
                <ElRadioButton
                  :label="$t('task.输入SMILES')"
                  :value="InputMethod.SMILES"
                >
                </ElRadioButton>
                <ElRadioButton
                  :label="$t('task.绘制分子')"
                  :value="InputMethod.DRAW"
                >
                </ElRadioButton>
              </ElRadioGroup>
            </ElFormItem>
            <template v-if="inputMethod === InputMethod.FILE">
              <ElFormItem :label="$t('task.数据集')" prop="file">
                <div
                  :class="[
                    'flex',
                    'items-center',
                    'justify-between',
                    'hover:bg-gray-100',
                  ]"
                  v-if="formData.file"
                >
                  <ElLink :class="['cursor-text']">
                    <svg class="button-iconpark-icon">
                      <use href="#file"></use>
                    </svg>
                    {{ formData.file.name }}</ElLink
                  >
                  <ElButton link @click="handleDeleteFile">
                    <svg class="iconpark-icon">
                      <use href="#delete-icon"></use>
                    </svg>
                  </ElButton>
                </div>

                <ElUpload
                  v-else
                  :on-change="handleFileChange"
                  accept=".csv,.sdf"
                  :auto-upload="false"
                  :show-file-list="false"
                >
                  <ElButton :class="['round-btn']">
                    <svg class="button-iconpark-icon">
                      <use href="#upload"></use>
                    </svg>
                    {{ $t("task.请上传文件") }}</ElButton
                  >
                  <template #tip>
                    <div :class="['text-tip__upload', 'mt-2']">
                      {{ $t("task.文件类型大小tip") }}
                    </div>
                  </template>
                </ElUpload>
              </ElFormItem>
              <div v-loading="paseColLoading">
                <ElFormItem
                  v-if="!isSDFFile"
                  label="smiles_col"
                  prop="smiles_col"
                >
                  <ElSelect
                    clearable
                    v-model="formData.smiles_col"
                    :placeholder="$t('task.请选择 smiles 列字段')"
                    @change="handleSmilesChange"
                  >
                    <ElOption
                      v-model="formData.smiles_col"
                      v-for="item in headerList"
                      :key="item"
                      :label="item"
                      :value="item"
                      :disabled="formData.target_cols.includes(item)"
                    ></ElOption>
                  </ElSelect>
                </ElFormItem>
              </div>
            </template>
            <template v-if="inputMethod === InputMethod.SMILES">
              <ElFormItem label="SMILES" prop="SMILESStr">
                <div :class="['flex', 'gap-2']">
                  <ElInput
                    :autosize="{ minRows: 10, maxRows: 12 }"
                    type="textarea"
                    v-model="formData.SMILESStr"
                    @change="handleSmilesChange"
                    @input="handleSmilesChange"
                    :placeholder="$t('task.回车换行可添加多个 SMILES 表达式')"
                  ></ElInput>
                  <ElSpace alignment="start" direction="vertical">
                    <ElButton @click="handleInputExample" type="primary">
                      {{ $t("common.案例") }}
                    </ElButton>
                    <ElButton @click="handleSMILESReset">
                      {{ $t("common.重置") }}
                    </ElButton>
                  </ElSpace>
                </div>
              </ElFormItem>
            </template>
            <template v-if="inputMethod === InputMethod.DRAW">
              <ElFormItem label="SMILES" prop="SMILESStr">
                <KetcherEditor ref="editorRef" @change="handleEditorChange" />
              </ElFormItem>
            </template>

            <ElFormItem label=" " v-if="validateBtnVisible">
              <ElButton
                type="primary"
                v-bind:loading="checkState === '检查中'"
                @click="handleNext"
                >{{
                  checkState === "未检查"
                    ? $t("task.检查数据集")
                    : $t("task.提交")
                }}</ElButton
              >
            </ElFormItem>
            <template v-if="checkState !== '未检查'">
              <ElDivider />
              <ElFormItem :label="$t('task.数据集检查结果：')">
                <ElText
                  :type="
                    checkTagTypeMap[checkState as unknown as FileCheckState]
                  "
                >
                  {{ $t(`task.${checkState}`) }}
                </ElText>
                <div></div>
                <ElText v-if="checkState === '存在错误数据项'">
                  {{
                    $t(`common.共有1条可预测数据2条错误数据项`, {
                      checkedCount: inputFileList.length - errorList.length,
                      errorCount: errorList.length,
                    })
                  }}
                </ElText>
              </ElFormItem>
            </template>
          </ElForm>
        </div>
        <div :class="['list-wrapper']" v-if="inputFileList.length">
          <SMILESList :list="inputFileList" />
        </div>
      </div>
    </div>

    <div :class="['card-style', 'mt-4']">
      <div>
        <div :class="['text-step']">
          {{ $t("task.步骤二：选择训练模型") }}
        </div>
      </div>
      <div
        v-if="!isEmpty(selectedModel)"
        :class="[
          'flex',
          'items-center',
          'justify-between',
          'mt-4',
          'hover:bg-gray-100',
        ]"
      >
        <div>
          <div :class="['flex']">
            <ElSpace alignment="center" size="large">
              <Description
                :label="$t('task.模型名称:')"
                :value="selectedModel.name"
              />
              <Description
                :label="$t('task.模型类型：')"
                v-if="selectedModel.model_task"
                :value="$t(getTaskI18nKey(selectedModel.model_task))"
              />
              <Description
                :label="$t('task.使用训练数据集:')"
                :value="
                  getOriginDataSetFileName(selectedModel.data_path || '') || ''
                "
              />
              <ElSpace alignment="center" size="large">
                <ElButton link @click="handlePreviewDetail" type="primary">
                  {{ $t("task.查看模型具体参数") }}
                </ElButton>
                <ElButton link @click="handleRemoveModel">
                  <svg class="iconpark-icon">
                    <use href="#delete-icon"></use>
                  </svg>
                </ElButton>
              </ElSpace>
            </ElSpace>
          </div>
        </div>
      </div>
      <ElButton v-else type="primary" @click="handleChoose" :class="['mt-4']">
        <svg class="iconpark-icon" :class="['mr-2']">
          <use href="#select-model"></use>
        </svg>
        {{ $t("task.选择训练模型") }}
      </ElButton>
      <ElDivider :class="['my-10']" />
      <ElButton
        :loading="submitLoading"
        @click="handleSubmit"
        :type="submitBtnDisabled ? 'info' : 'primary'"
        :disabled="submitBtnDisabled"
      >
        {{ $t("task.提交") }}
      </ElButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Cookie from "js-cookie";
import { popup } from "@/components/modal/ModalContainer.vue";
import { newInferTask } from "@/service/api/predict";
import {
  confirmCheckFile,
  getFileCols,
  getTaskDetail,
  getTemplateDetail,
  type TaskDetail,
} from "@/service/api/task";
import Description from "@/components/description/index.vue";
import { getOriginDataSetFileName } from "@/utils/formatter";
import { getTaskI18nKey } from "@/utils/formatter";
import { getTaskType } from "@/utils/getInfo";
import { getUniqueName } from "@/utils/name";
import { Icon } from "@iconify/vue";
import {
  ElButton,
  ElDivider,
  ElForm,
  ElFormItem,
  ElInput,
  ElLink,
  ElMessage,
  ElOption,
  ElRadio,
  ElRadioButton,
  ElRadioGroup,
  ElSelect,
  ElSpace,
  ElText,
  ElUpload,
  vLoading,
  type FormInstance,
  type UploadFile,
  type UploadFiles,
  type UploadRawFile,
} from "element-plus";
import { isEmpty } from "lodash";
import { computed, ref, watchEffect } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { triggerDownload } from "../../utils/download";
import CheckFailedModal from "../create-task/modal/CheckFailedModal.vue";
import TaskListDrawer from "./modal/TaskListDrawer.vue";
import ViewModelParam from "../predict-result/model/ViewModelParam.vue";
import { get } from "lodash";
import { checkTagTypeMap, type FileCheckState } from "@/stores/modules/file";
import KetcherEditor from "@/components/ketcher-editor/index.vue";
import { generateSMILESFile } from "@/utils/csvFile";
import { parse } from "sdf-parser";
import SMILESList from "@/components/SMILES-list/index.vue";
import Papa from "papaparse";
import { isUniMolTask } from "@/utils/judge";
const editorRef = ref();
interface FormCheckData {
  smiles_col: string;
  target_cols: string[];
  file: null | UploadRawFile;
  uid: string;
  task_name: string;
  checkId: string;
  SMILESStr: string;
  explain: boolean;
}
enum InputMethod {
  FILE = "file",
  SMILES = "SMILES",
  DRAW = "draw",
}
const { t } = useI18n();
const modelId = ref<string>("");
const inputMethod = ref<InputMethod>(InputMethod.FILE);

const route = useRoute();
modelId.value = route.query.taskId as string;
const formRef = ref<FormInstance>();

const paseColLoading = ref<boolean>(false);
const checkState = ref<FileCheckState>("未检查");

const getDefaultFileInfo = () => ({
  smiles_col: "",
  target_cols: [],
  file: null,
  uid: "",
  task_name: getUniqueName("predict"),
  checkId: "",
  SMILESStr: "",
  explain: true,
});
const formData = ref<FormCheckData>(getDefaultFileInfo());
const handleInputMethodChange = () => {
  formData.value = getDefaultFileInfo();
  checkState.value = "未检查";
};
const isSDFFile = computed(() => {
  return formData.value.file?.name?.endsWith(".sdf");
});
const handlePreviewDetail = () => {
  popup(ViewModelParam, {
    paramData: get(selectedModel.value, "task_type.fit"),
  })
    .then(() => {})
    .catch(() => {});
};
const handleDownLoadTemplate = () => {
  getTemplateDetail({
    type: "predict",
  }).then((res) => {
    triggerDownload(
      res.data,
      {
        type: "text/csv",
      },
      "test.csv"
    ).then((res) => {});
  });
};

const formRules = {
  task_name: [
    {
      required: true,
      message: t("task.请输入任务名称"),
      trigger: ["change", "blur"],
    },
    {
      pattern: /^[\u4e00-\u9fa50-9a-zA-Z_-]{1,200}$/,
      message: t("task.任务名称必须是1到200位的汉字、数字、字母、下划线或横线"),
      trigger: ["change", "blur"],
    },
  ],
  explain: [
    {
      required: true,
      trigger: ["change", "blur"],
    },
  ],
  file: [
    {
      required: true,
      message: t("task.请上传数据集"),
      trigger: ["change", "blur"],
    },
  ],
  smiles_col: [
    {
      required: true,
      message: t("task.请选择 smiles_col"),
      trigger: ["change", "blur"],
    },
  ],
  // target_cols: [
  //   {
  //     required: true,
  //     message: "请选择 target_cols",
  //     trigger: ["change", "blur"],
  //   },
  // ],
};
const handleSmilesChange = () => {
  if (checkState.value !== "未检查") checkState.value = "未检查";
};
const handleDeleteFile = () => {
  formData.value.file = null;
  formData.value.uid = "";
  formData.value.smiles_col = "";
  formData.value.target_cols = [];
  headerList.value = [];
  checkState.value = "未检查";
};
const headerList = ref<string[]>();

const handleFileChange = (uploadFile: UploadFile, uploadFiles: UploadFiles) => {
  const limitFileCount = 1;
  // const judgeFileType = (file: UploadFile) => {}
  const onExceed = (count: number, fileList: UploadFiles) => {
    if (fileList.length > count) {
      fileList.splice(0, fileList.length - count);
    }
  };
  if (uploadFile.raw) formData.value.file = uploadFile.raw;

  const params = new FormData();
  params.set("file", uploadFile.raw!);
  paseColLoading.value = true;
  getFileCols(params)
    .then((res) => {
      headerList.value = res.data.data.columns;
      formData.value.uid = res.data.data.file_id;
    })
    .finally(() => {
      paseColLoading.value = false;
    });

  onExceed(limitFileCount, uploadFiles);
};
let errorList: any[] = [];
const handleHasErrorContinue = (list: any[], colHeaderList: string[]) => {
  popup(CheckFailedModal, {
    tableData: list,
    headList: colHeaderList,
  })
    .then((res) => {})
    .catch(() => {});
};
const checkInputData = (
  fileID: string,
  smiles_col: string,
  target_cols: string[],
  showColHeader: string[]
) => {
  return confirmCheckFile({
    file_id: fileID,
    smiles_col: smiles_col,
    target_cols: target_cols,
  })
    .then((res) => {
      if (res.data.data) {
        formData.value.checkId = res.data.data.file_id;
        ElMessage({
          type: "success",
          message: t("task.数据集检查完成"),
        });

        if (res.data.data.error_rows && res.data.data.error_rows.length) {
          checkState.value = "存在错误数据项";
          errorList = res.data.data.error_rows;
          handleHasErrorContinue(errorList, showColHeader);
        } else if (res.data.data.valid_length === 0) {
          checkState.value = "检查未能通过";
          ElMessage.closeAll();
          ElMessage({
            type: "error",
            message: t("task.数据集未通过检查，请输入有效数据集"),
          });
        } else {
          checkState.value = "检查通过";
        }
      } else {
        checkState.value = "检查未能通过";
      }
    })
    .catch(() => {
      checkState.value = "检查未能通过";
      ElMessage({
        type: "error",
        message: t("task.数据集未通过检查，请检查检查数据列"),
      });
    });
};

const handleNext = () => {
  if (!formRef.value) return;
  formRef.value.validate((valid) => {
    if (valid) {
      switch (checkState.value) {
        case "未检查": {
          if (inputMethod.value === InputMethod.SMILES) {
            const colKey = "SMILES";
            const list = formData.value.SMILESStr.split("\n").filter(
              (item) => item.trim().length > 0
            );
            if (list.length === 0) {
              ElMessage({
                type: "warning",
                message: t("task.请输入至少一个有效的SMILES表达式"),
              });
              return;
            }
            checkState.value = "检查中";
            const csvFile = generateSMILESFile(colKey, list);
            const params = new FormData();
            params.set("file", csvFile);

            getFileCols(params).then((res) => {
              formData.value.uid = res.data.data.file_id;
              checkInputData(formData.value.uid, colKey, [], [colKey]).then(
                () => {}
              );
            });
            return;
          } else if (inputMethod.value === InputMethod.DRAW) {
            if (editorRef.value) {
              const colKey = "SMILES";
              const list = formData.value.SMILESStr.split(".").filter(
                (item) => item.trim().length > 0
              );
              if (list.length === 0) {
                ElMessage({
                  type: "warning",
                  message: t("task.请绘制分子"),
                });
                return;
              }
              checkState.value = "检查中";
              const csvFile = generateSMILESFile(colKey, list);
              const params = new FormData();
              params.set("file", csvFile);
              getFileCols(params).then((res) => {
                formData.value.uid = res.data.data.file_id;
                checkInputData(formData.value.uid, colKey, [], [colKey]).then(
                  () => {}
                );
              });
              return;
            } else {
              ElMessage({
                type: "warning",
                message: t("task.请等待编辑器加载完成"),
              });
              return;
            }
            return;
          } else {
            checkInputData(
              formData.value.uid,
              formData.value.smiles_col,
              formData.value.target_cols,
              headerList.value || []
            ).then(() => {});
          }
          break;
        }
        case "检查中": {
          ElMessage({
            type: "warning",
            message: t("task.数据集检查中，请继续等待"),
          });
          break;
        }
        case "检查通过": {
          break;
        }
        case "存在错误数据项": {
          break;
        }
      }
    }
  });
};
const inputFileList = ref<any[]>([]);
const handleEditorChange = () => {
  handleSmilesChange();
  editorRef.value.getCurrentSmile().then((res: string) => {
    formData.value.SMILESStr = res;
  });
};

watchEffect(() => {
  if (inputMethod.value === InputMethod.FILE) {
    if (formData.value.file) {
      if (formData.value.file.type === "text/csv") {
        // formData.value.file.raw.text().then((res) => {
        //   formData.value.SMILESStr = res;
        Papa.parse(formData.value.file, {
          header: true, // 启用头部信息
          skipEmptyLines: true,
          complete: function (results) {
            inputFileList.value = results.data;
          },
          error: function (error) {
            console.error("Error parsing CSV:", error);
          },
        });
      } else {
        const reader = new FileReader();
        // var result = parse(formData.value.file);
        reader.onload = (e) => {
          const sdfContent = e.target?.result || "";
          const parsedSDF = parse(sdfContent);
          inputFileList.value = parsedSDF.molecules;
        };
        reader.onerror = (error) => {
          console.error("Error reading SDF file:", error);
        };
        reader.readAsText(formData.value.file);
      }
    } else {
      inputFileList.value = [];
    }
  } else if (inputMethod.value === InputMethod.SMILES) {
    inputFileList.value = formData.value.SMILESStr.split("\n")
      .filter((item) => item.trim().length > 0)
      .map((str) => ({
        SMILES: str,
      }));
  } else {
    inputFileList.value = formData.value.SMILESStr.split(".")
      .filter((item) => item.trim().length > 0)
      .map((str) => ({
        SMILES: str,
      }));
  }
});
const handleInputExample = () => {
  formData.value.SMILESStr = `CC1=CC(OCCCC(C)(C)C(O)=O)=C(C)C=C1
CC(C)N1N=CC=C1C1=C(COC2=CC=CC(O)=C2C=O)C=CC=N1
CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=C(OC1=O)C=CC=C2
CC(C)CC1=CC=C(C=C1)C(C)C(O)=O
COC1=CC2=C(C=C1)N=C(N2)S(=O)CC1=NC=C(C)C(OC)=C1C
COCCC1=CC=C(OCC(O)CNC(C)C)C=C1
CN\C(NCCSCC1=C(C)NC=N1)=N\C#N
COC1=C(C=C(Cl)C=C1)C(=O)NCCC1=CC=C(C=C1)S(=O)(=O)NC(=O)NC1CCCCC1
CN(CCOC1=CC=C(CC2SC(=O)NC2=O)C=C1)C1=CC=CC=N1
CN1CCN(CCCN2C3=CC=CC=C3SC3=C2C=C(C=C3)C(F)(F)F)CC1
`;
};
const handleSMILESReset = () => {
  formData.value.SMILESStr = "";
  handleSmilesChange();
};
const handleChoose = () => {
  popup(TaskListDrawer, {
    selectModelId: "",
  })
    .then((model: any) => {
      modelId.value = model.run_id;
    })
    .catch(() => {});
};
const router = useRouter();
const submitLoading = ref<boolean>(false);
const handleSubmit = () => {
  if (formRef.value)
    formRef.value.validate((valid) => {
      if (valid) {
        const restParams: any = {};
        const appAccessKey = Cookie.get("appAccessKey") || "";
        // Cookie.get("appAccessKey") || `sk-8eb6b738d4c140e3ab1d926389e1abd8`;
        const clientName = Cookie.get("clientName") || "";
        restParams["access_key"] = appAccessKey;
        restParams["app_key"] = clientName;
        submitLoading.value = true;

        if (formData.value.explain) {
          if (!isUniMolTask(selectedModel.value)) {
            ElMessage({
              type: "error",
              message: t("task.该训练模型未选择 UniMol 无法开启可解释性"),
            });
            submitLoading.value = false;
            return;
          }
        }
        newInferTask({
          task: {
            name: formData.value.task_name,
            file_id: formData.value.checkId,
            smiles_col: formData.value.smiles_col,
            model_trained_run_id: modelId.value as string,
            explain: formData.value.explain,
          },
          sku: {
            ...restParams,
          },
        })
          .then((res) => {
            ElMessage({
              type: "success",
              message: t("task.提交成功,预计扣费", {
                countNumber: +res.data.msg.match(/\d+/g)[0] / 100,
              }),
            });
            router.push({
              name: "taskManage",
            });
          })
          .finally(() => {
            submitLoading.value = false;
          });
      }
    });
};
const selectedModel = ref<TaskDetail>();

watchEffect(() => {
  if (modelId.value) {
    getTaskDetail({ run_id: modelId.value }).then((res) => {
      selectedModel.value = res.data.data;
    });
  }
});
const handleRemoveModel = () => {
  modelId.value = "";
  selectedModel.value = undefined;
};

const submitBtnDisabled = computed(() => {
  return (
    !selectedModel.value ||
    !["检查通过", "存在错误数据项"].includes(checkState.value)
  );
});
const validateBtnVisible = computed(() => {
  if (["检查数据集", "未检查"].includes(checkState.value)) {
    if (inputMethod.value === InputMethod.DRAW) {
      return true;
    }
    if (inputMethod.value === InputMethod.SMILES && formData.value.SMILESStr) {
      return true;
    }
    if (inputMethod.value === InputMethod.FILE) {
      return formData.value.smiles_col || (isSDFFile && formData.value.uid);
    }
  }
  return false;
});
</script>

<style lang="scss" scoped>
@import "@/assets/variables";
:deep() {
  .el-form-item__content {
    > div {
      width: 100%;
      .el-upload {
        // width: 100%;
      }
      .el-input {
        .el-input__wrapper {
          cursor: pointer !important;
          input {
            cursor: pointer !important;
          }
        }
      }
    }
  }
}
.list-wrapper {
  width: calc(100% - 700px - 40px);
  // box-shadow: 0px 4px 19px 0px rgba(222, 222, 222, 0.2);
  flex: 1;
}
</style>
