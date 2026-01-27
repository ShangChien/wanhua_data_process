<template>
  <div :class="['flex', 'gap-8']">
    <div :class="['w-[600px]', 'pt-4']">
      <ElForm
        label-width="210"
        :model="formData"
        :rules="formRules"
        ref="formRef"
        scroll-to-error
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
              {{ $t("task.经过检查的数据集才可以训练") }}
            </span>
            <IconButton
              v-if="handleDownLoadTemplate"
              iconSVGHref="#down-cloud"
              @click="handleDownLoadTemplate"
              :tooltip-text="$t('task.下载模板')"
            ></IconButton>
          </ElSpace>
        </ElFormItem>

        <ElFormItem :label="$t('task.任务名称')" prop="task_name">
          <ElInput
            clearable
            v-model.trim="formData.task_name"
            :placeholder="$t('task.请输入任务名称')"
          />
        </ElFormItem>
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
          <ElFormItem v-if="!isSDFFile" label="smiles_col" prop="smiles_col">
            <ElSelect
              clearable
              v-model="formData.smiles_col"
              :placeholder="$t('task.请选择 smiles 列字段')"
              @change="handleSelectedColChange"
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
          <ElFormItem label="target_cols" prop="target_cols">
            <ElSelect
              clearable
              multiple
              tag-type="primary"
              v-model="formData.target_cols"
              :placeholder="$t('task.请选择 target 列字段')"
              @change="handleSelectedColChange"
            >
              <ElOption
                :key="item"
                v-for="item in headerList"
                :label="item"
                :value="item"
                :disabled="formData.smiles_col === item"
              ></ElOption>
            </ElSelect>
          </ElFormItem>
        </div>
        <ElFormItem
          label=" "
          v-if="
            (formData.smiles_col || isSDFFile) &&
            formData.target_cols.length &&
            ['检查数据集', '未检查'].includes(fileStore.checkState)
          "
        >
          <ElButton
            type="primary"
            :class="['mt-4']"
            v-bind:loading="fileStore.checkState === '检查中'"
            @click="handleNext"
            >{{ $t("task.检查数据集") }}</ElButton
          >
        </ElFormItem>

        <template v-if="fileStore.checkState !== '未检查'">
          <ElDivider />
          <ElFormItem :label="$t('task.数据集检查结果：')">
            <ElText
              :type="
                checkTagTypeMap[
                  fileStore.checkState as unknown as FileCheckState
                ]
              "
            >
              {{ $t(`task.${fileStore.checkState}`) }}
            </ElText>

            <ElText v-if="fileStore.checkState === '存在错误数据项'">
              {{
                $t(`common.共有1条可训练数据2条错误数据项`, {
                  checkedCount:
                    fileStore.fileTableData.length - errorList.length,
                  errorCount: errorList.length,
                })
              }}
            </ElText>
          </ElFormItem>
        </template>
      </ElForm>
    </div>
    <div :class="['list-wrapper']" v-if="fileStore.fileTableData.length">
      <SMILESList :list="fileStore.fileTableData" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import IconButton from "@/components/icon-button/index.vue";
import {
  checkTagTypeMap,
  type FileCheckState,
  useFileStore,
} from "@/stores/modules/file";
import { Icon } from "@iconify/vue";
import CheckFailedModal from "./modal/CheckFailedModal.vue";
import SMILESList from "@/components/SMILES-list/index.vue";

import {
  confirmCheckFile,
  getFileCols,
  getTemplateDetail,
} from "@/service/api/task";
import {
  ElButton,
  ElDivider,
  ElForm,
  ElFormItem,
  ElInput,
  ElLink,
  ElMessage,
  ElOption,
  ElProgress,
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
import { computed, ref, watchEffect } from "vue";
import { popup } from "@/components/modal/ModalContainer.vue";
import { triggerDownload } from "../../utils/download";
import { getUniqueName } from "@/utils/name";
import { useI18n } from "vue-i18n";
import Papa from "papaparse";
import { parse } from "sdf-parser";
const { t } = useI18n();
interface FormCheckData {
  smiles_col: string;
  target_cols: string[];
  file: null | UploadRawFile;
  uid: string;
  task_name: string;
}

const fileStore = useFileStore();
const formRef = ref<FormInstance>();

const checkBtnVisible = computed(() => {
  return true;
});
const getDefaultFileInfo = () => ({
  smiles_col: "",
  target_cols: [],
  file: null,
  uid: "",
  task_name: getUniqueName("train"),
});
const formData = ref<FormCheckData>(getDefaultFileInfo());

const handleDownLoadTemplate = () => {
  getTemplateDetail({
    type: "train",
  }).then((res) => {
    triggerDownload(
      res.data,
      {
        type: "text/csv",
      },
      "train.csv"
    ).then((res) => {});
  });
};
const validateTargetCols = (rule: any, value: any, callback: any) => {
  if (value === "") {
    callback(new Error(t("task.请选择 target_cols")));
  } else {
    for (const item of value) {
      if (item.includes("/")) {
        callback(
          new Error(
            t(
              "task.target_cols 所选列名不能包含/,请重新选择或者修改数据集 col 名称"
            )
          )
        );
      }
    }
    callback();
  }
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
  target_cols: [
    {
      required: true,
      validator: validateTargetCols,
      trigger: ["change", "blur"],
    },
  ],
};
const handleSelectedColChange = () => {
  fileStore.checkState = "未检查";
};
const handleDeleteFile = () => {
  formData.value.file = null;
  formData.value.uid = "";
  formData.value.smiles_col = "";
  formData.value.target_cols = [];
  headerList.value = [];
  fileStore.checkState = "未检查";
};
const headerList = ref<string[]>();
const isSDFFile = computed(() => {
  return formData.value.file?.name?.endsWith(".sdf");
});
const paseColLoading = ref<boolean>(false);
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
const handleHasErrorContinue = () => {
  popup(CheckFailedModal, {
    tableData: errorList,
    headList: headerList.value,
  })
    .then(() => {})
    .catch(() => {});
};
const handleNext = () => {
  if (!formRef.value) return;
  formRef.value.validate((valid) => {
    if (valid) {
      switch (fileStore.checkState) {
        case "未检查": {
          fileStore.checkState = "检查中";
          confirmCheckFile({
            file_id: formData.value.uid,
            smiles_col: formData.value.smiles_col,
            target_cols: formData.value.target_cols,
          })
            .then((res) => {
              ElMessage({
                type: "success",
                message: t("task.数据集检查完成"),
              });
              fileStore.updateStore({
                headerList: headerList.value,
                file_id: res.data.data.file_id,
                task_name: formData.value.task_name,
                smiles_col: formData.value.smiles_col,
                target_cols: formData.value.target_cols,
              });

              if (
                res.data.data.error_rows &&
                res.data.data.error_rows.length &&
                res.data.data.valid_length > 0
              ) {
                fileStore.checkState = "存在错误数据项";
                errorList = res.data.data.error_rows;
                fileStore.checkTaskType = res.data.data.guess_task_type;
                handleHasErrorContinue();
              } else if (res.data.data.valid_length === 0) {
                fileStore.checkState = "检查未能通过";
                ElMessage.closeAll();
                ElMessage({
                  type: "error",
                  message: t("task.数据集未通过检查，请输入有效数据集"),
                });
              } else {
                fileStore.checkTaskType = res.data.data.guess_task_type;
                fileStore.checkState = "检查通过";
              }
            })
            .catch(() => {
              fileStore.checkState = "检查未能通过";
              ElMessage({
                type: "error",
                message: t("task.数据集未通过检查，请检查检查数据列"),
              });
            });

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
          handleHasErrorContinue();
          break;
        }
      }
    }
  });
};

watchEffect(() => {
  if (formData.value.file) {
    if (formData.value.file.type === "text/csv") {
      // formData.value.file.raw.text().then((res) => {
      //   formData.value.SMILESStr = res;
      Papa.parse(formData.value.file, {
        header: true, // 启用头部信息
        skipEmptyLines: true,
        complete: function (results) {
          fileStore.updateStore({
            fileTableData: results.data,
          });
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
        fileStore.updateStore({
          fileTableData: parsedSDF.molecules,
        });
      };
      reader.onerror = (error) => {
        console.error("Error reading SDF file:", error);
      };
      reader.readAsText(formData.value.file);
    }
  } else {
    fileStore.updateStore({
      fileTableData: [],
    });
  }
});
</script>

<style lang="scss" scoped>
:deep() {
  .el-form-item__content {
    > div {
      width: 100%;

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
  width: calc(100% - 600px - 32px);
  // box-shadow: 0px 4px 19px 0px rgba(222, 222, 222, 0.2);
  flex: 1;
}
</style>
