<template>
  <div :class="['flex', 'pt-8', 'gap-8']">
    <ElForm
      :id="formId"
      @mousemove="handleMouseMove"
      ref="formRef"
      :class="['w-[600px]']"
      :model="formData"
      :rules="formRules"
      label-width="210"
      status-icon
      inline
    >
      <ElCollapse v-model="activeCollapseItem">
        <ElCollapseItem title="Base Option" name="base">
          <ElFormItem
            :data-prop="HintFormProp.task"
            :label="$t('task.任务类型')"
            prop="task"
            :class="['w-full']"
          >
            <ElSelect v-model="formData.task">
              <ElOption
                v-for="item in [
                  { label: $t('task.自动识别'), value: autoDetect },
                  {
                    label: $t('task.分类'),
                    value: 'multilabel_classification',
                  },
                  { label: $t('task.回归'), value: 'multilabel_regression' },
                  { label: $t('task.多分类'), value: 'multiclass' },
                  // {
                  //   label: $t('task.多标签分类'),
                  //   value: 'multilabel_classification',
                  // },
                  // {
                  //   label: $t('task.多标签回归'),
                  //   value: 'multilabel_regression',
                  // },
                ]"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              ></ElOption>
            </ElSelect>
          </ElFormItem>

          <ElFormItem
            :data-prop="HintFormProp.modelPick"
            :label="$t('task.模型选择')"
            prop="modelPick"
            :class="['w-full']"
          >
            <ElSelect tag-type="primary" v-model="formData.modelPick" multiple>
              <ElOption
                v-for="item in [
                  { value: 'Uni-Mol(all_h)', label: 'UniMol-All_H' },
                  { value: 'Uni-Mol(no_h)', label: 'UniMol-No_H' },
                  { value: 'BERT', label: 'BERT-SMILES' },
                  { value: 'LR', label: 'LR-FP' },
                  { value: 'GBDT', label: 'GBDT-MD' },
                  { value: 'ET', label: 'ET-MD' },
                  { value: 'SVM', label: 'SVM-FP' },
                ]"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              ></ElOption>
            </ElSelect>
          </ElFormItem>

          <ElFormItem
            :data-prop="HintFormProp.autoOptimize"
            :label="$t('task.超参数优化')"
            prop="autoOptimize"
            :class="['w-full']"
          >
            <ElRadioGroup
              size="small"
              v-model="formData.autoOptimize"
              @change="handleOptimize"
            >
              <ElRadio :value="true">
                {{ $t("task.是") }}
              </ElRadio>
              <ElRadio :value="false">
                {{ $t("task.否") }}
              </ElRadio>
            </ElRadioGroup>
            <hr />
            <div v-if="formData.autoOptimize" :class="['text-[11px]']">
              {{ $t("task.开启此选项会大幅增加耗时！") }}
            </div>
          </ElFormItem>
        </ElCollapseItem>

        <ElCollapseItem title="Advanced Option" name="advance">
          <template #title>
            <div :class="['flex', 'gap-2', 'items-center']">
              Advanced Option
              <ElTooltip :content="$t('task.更多信息')" placement="bottom">
                <ElButton @click.stop="handleOpenHintModal" link type="primary">
                  <svg class="iconpark-icon"><use href="#hint"></use></svg>
                </ElButton>
              </ElTooltip>
            </div>
          </template>
          <template v-if="formData.autoOptimize">
            <ElFormItem
              :data-prop="HintFormProp.split_method"
              :label="$t('task.划分方式')"
              prop="split_method"
              :class="['w-full']"
            >
              <ElSelect
                @change="handleSplitMethodChange"
                v-model="formData.split_method"
              >
                <ElOption
                  v-for="item in ['random', 'scaffold', 'group', 'stratified']"
                  :key="item"
                  :label="item"
                  :value="item"
                ></ElOption>
              </ElSelect>
            </ElFormItem>
            <ElFormItem
              :data-prop="HintFormProp.group_col"
              v-if="hasGroupCol"
              label="group_col"
              prop="group_col"
              :class="['w-full']"
            >
              <ElSelect
                clearable
                v-model="formData.group_col"
                :placeholder="$t('task.请选择 group 列字段')"
              >
                <ElOption
                  v-for="(item, index) in fileStore.headerList"
                  :key="item"
                  :label="item"
                  :value="item"
                ></ElOption>
              </ElSelect>
            </ElFormItem>
            <ElFormItem
              :data-prop="HintFormProp.autoOptimizeParamPick"
              :label="$t('task.参数选择')"
              prop="autoOptimizeParamPick"
            >
              <ElRadioGroup
                v-model="formData.autoOptimizeParamPick"
                @change="handleAutoOptimizeParamPick"
                size="small"
              >
                <ElRadio :value="true">
                  {{ $t("task.推荐") }}
                </ElRadio>
                <ElRadio :value="false">
                  {{ $t("task.自定义") }}
                </ElRadio>
              </ElRadioGroup>
            </ElFormItem>

            <ElFormItem
              :data-prop="HintFormProp.recommend"
              v-if="formData.autoOptimizeParamPick"
              :label="$t('task.推荐配置')"
              prop="recommend"
              :class="['w-full']"
            >
              <ElRadioGroup
                @change="handleConfigChange"
                v-model="formData.recommend"
                size="small"
              >
                <ElRadio
                  v-for="item in configList"
                  :key="item.label"
                  :label="$t(`task.${item.label}`)"
                  :value="item.label"
                ></ElRadio>
              </ElRadioGroup>
            </ElFormItem>

            <ElFormItem
              :data-prop="HintFormProp.ml_trials"
              label="ml_trials"
              prop="ml_trials"
              :class="['w-full']"
            >
              <ElInput
                min="0"
                type="number"
                :disabled="optimizeParamDisabled"
                v-model="formData.ml_trials"
              />
            </ElFormItem>

            <ElFormItem
              :data-prop="HintFormProp.nn_trials"
              label="nn_trials"
              prop="nn_trials"
              :class="['w-full']"
            >
              <ElInput
                min="0"
                type="number"
                :disabled="optimizeParamDisabled"
                v-model="formData.nn_trials"
              />
            </ElFormItem>

            <ElFormItem
              :data-prop="HintFormProp.epochRange"
              label="Epoch Range"
              prop="EpochList"
              :class="['w-full']"
            >
              <VueSlider
                tooltip="active"
                marks
                :disabled="optimizeParamDisabled"
                :class="['!w-full', '!px-4']"
                :data="epochRangeEnum"
                :enable-cross="false"
                v-model="formData.epochRange"
              />
            </ElFormItem>

            <ElFormItem
              :data-prop="HintFormProp.batchRange"
              label="Batch Size Range"
              prop="EpochList"
              :class="['w-full']"
            >
              <VueSlider
                tooltip="active"
                marks
                :disabled="optimizeParamDisabled"
                :class="['!w-full', '!px-4']"
                :data="batchRangeEnum"
                :enable-cross="false"
                v-model="formData.batchRange"
              />
            </ElFormItem>

            <ElFormItem
              label="Learning Rate Range"
              prop="EpochList"
              :class="['!w-full']"
              :data-prop="HintFormProp.leaningRateRange"
            >
              <VueSlider
                tooltip="active"
                marks
                :disabled="optimizeParamDisabled"
                :class="['!w-full', '!px-4']"
                :data="leaningRateRangeEnum"
                :enable-cross="false"
                v-model="formData.leaningRateRange"
              />
            </ElFormItem>
          </template>
          <template v-else>
            <ElFormItem
              :label="$t('task.划分方式')"
              prop="split_method"
              :class="['w-full']"
              :data-prop="HintFormProp.split_method"
            >
              <ElSelect
                @change="handleSplitMethodChange"
                v-model="formData.split_method"
              >
                <ElOption
                  v-for="item in ['random', 'scaffold', 'group', 'stratified']"
                  :key="item"
                  :label="item"
                  :value="item"
                ></ElOption>
              </ElSelect>
            </ElFormItem>
            <ElFormItem
              v-if="hasGroupCol"
              label="group_col"
              prop="group_col"
              :data-prop="HintFormProp.group_col"
              :class="['w-full']"
            >
              <ElSelect
                clearable
                v-model="formData.group_col"
                :placeholder="$t('task.请选择 group 列字段')"
              >
                <ElOption
                  v-for="(item, index) in fileStore.headerList"
                  :key="item"
                  :label="item"
                  :value="item"
                ></ElOption>
              </ElSelect>
            </ElFormItem>
            <ElFormItem
              :data-prop="HintFormProp.paramPick"
              :label="$t('task.参数选择')"
              prop="param_pick"
              :class="['w-full']"
            >
              <ElRadioGroup
                size="small"
                v-model="formData.paramPick"
                @change="handlePickParams"
              >
                <ElRadio :value="true">
                  {{ $t("task.推荐") }}
                </ElRadio>
                <ElRadio :value="false">
                  {{ $t("task.自定义") }}
                </ElRadio>
              </ElRadioGroup>
            </ElFormItem>

            <ElFormItem
              :data-prop="HintFormProp.epoch"
              label="Epoch"
              prop="epoch"
              :class="['w-full']"
            >
              <ElSlider
                :disabled="advancedParamDisabled"
                :min="10"
                :max="200"
                size="small"
                show-input
                v-model="formData.epoch"
                :step="1"
              />
              <span> {{ formData.epoch }}</span>
            </ElFormItem>
            <ElFormItem
              :data-prop="HintFormProp.batchsize"
              label="Batch Size"
              prop="batchsize"
              :class="['w-full']"
            >
              <ElSlider
                :disabled="advancedParamDisabled"
                :min="8"
                :max="256"
                size="small"
                show-input
                v-model="formData.batchsize"
                :step="1"
              />
              <span> {{ formData.batchsize }}</span>
            </ElFormItem>

            <ElFormItem
              :data-prop="HintFormProp.Learningrate"
              label="Learning Rate"
              prop="Learningrate"
              :class="['w-full']"
            >
              <ElSlider
                :disabled="advancedParamDisabled"
                size="small"
                v-model="formData.Learningrate"
                show-input
                :max="0.1"
                :min="1e-5"
                :step="1e-5"
              />
              <span> {{ formData.Learningrate }}</span>
            </ElFormItem>
          </template>
        </ElCollapseItem>
      </ElCollapse>

      <ElFormItem label=" " :class="['mt-5']">
        <ElTooltip
          :disabled="!submitBtnDisabled"
          effect="dark"
          placement="top"
          :content="$t('task.请先检查文件')"
        >
          <ElButton
            :loading="submitLoading"
            :type="submitBtnDisabled ? 'info' : 'primary'"
            :disabled="submitBtnDisabled"
            @click="handleSubmit"
          >
            {{ $t("task.提交任务") }}
          </ElButton>
        </ElTooltip>
      </ElFormItem>
    </ElForm>
    <FormFieldHint
      v-if="hintList?.length && activeCollapseItem.length"
      :descList="hintList"
    />
  </div>
</template>

<script lang="ts" setup>
import { submitTaskFormData } from "@/service/api/task";
import { useFileStore } from "@/stores/modules/file";
import {
  ElButton,
  ElCol,
  ElCollapse,
  ElCollapseItem,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElMessage,
  ElOption,
  ElRadio,
  ElRadioGroup,
  ElRow,
  ElSelect,
  ElSlider,
  ElTooltip,
  type FormInstance,
} from "element-plus";
import { cloneDeep, get, isString, set } from "lodash";
import { computed, reactive, ref, watchEffect } from "vue";
import { popup } from "@/components/modal/ModalContainer.vue";
import VueSlider from "vue-slider-component";
import "vue-slider-component/theme/antd.css";
import HintModal from "@/components/modal/HintModal.vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import FormFieldHint from "./FormFieldHint.vue";
import Cookie from "js-cookie";
const autoDetect = "auto_detect";
let detectedValue: string = "";
const epochRangeEnum = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200];
const batchRangeEnum = [4, 8, 16, 32, 64, 128, 256];
const leaningRateRangeEnum = [
  "1e-5",
  "2e-5",
  "5e-5",
  "1e-4",
  "2e-4",
  "5e-4",
  "1e-3",
  "2e-3",
  "5e-3",
  "1e-2",
];
const { t } = useI18n();
const router = useRouter();
const fileStore = useFileStore();
const submitBtnDisabled = computed(() => {
  return !["检查通过", "存在错误数据项"].includes(fileStore.checkState);
});
enum HintFormProp {
  task = "task",
  modelPick = "modelPick",
  split_method = "split_method",
  group_col = "group_col",
  autoOptimize = "autoOptimize",
  paramPick = "paramPick",
  autoOptimizeParamPick = "autoOptimizeParamPick",
  recommend = "recommend",
  nn_trials = "nn_trials",
  ml_trials = "ml_trials",
  epochRange = "epochRange",
  batchRange = "batchRange",
  leaningRateRange = "leaningRateRange",
  epoch = "epoch",
  batchsize = "batchsize",
  Learningrate = "Learningrate",
}
const focusFormItemHint = ref(HintFormProp.task);
let hintList = computed(() => {
  let ret: any[] = [];
  switch (focusFormItemHint.value) {
    case HintFormProp.task: {
      ret = [
        {
          title: "Task Type",
          desc: [
            {
              label: t("task.自动识别"),
              value: t("task.TaskTypeHint"),
            },
            {
              label: t("task.分类"),
              value: t("task.分类Hint"),
            },
            {
              label: t("task.回归"),
              value: t("task.回归Hint"),
            },
            {
              label: t("task.多分类"),
              value: t("task.多分类Hint"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.modelPick: {
      ret = [
        {
          title: t("task.模型选择"),
          desc: [
            {
              label: t("task.Uni-Mol (all_h)"),
              value: t("task.Uni-Mol (all_h)Hint"),
            },
            {
              label: t("task.Uni-Mol (no_h)"),
              value: t("task.Uni-Mol (no_h)Hint"),
            },
            {
              label: t("task.BERT"),
              value: t("task.BERTHint"),
            },
            {
              label: t("task.LR"),
              value: t("task.LRHint"),
            },
            {
              label: t("task.GBDT (梯度提升决策树)"),
              value: t("task.GBDTHint"),
            },
            {
              label: t("task.ET (极端随机树)"),
              value: t("task.ETHint"),
            },
            {
              label: t("task.SVM (支持向量机)"),
              value: t("task.SVMHint"),
            },
            {
              label: t("task.MD"),
              value: t("task.MDHint"),
            },
            {
              label: t("task.FP"),
              value: t("task.FPHint"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.split_method: {
      ret = [
        {
          title: t("task.划分方式"),
          desc: [
            {
              label: t("task.五折验证"),
              value: t("task.五者hint"),
            },
            {
              label: t("task.随机划分（Random）"),
              value: t("task.随机划分hint"),
            },
            {
              label: t("task.骨架划分（Scaffold）"),
              value: t("task.骨架划分hint"),
            },
            {
              label: t("task.分组划分（Group）"),
              value: t("task.分组划分hint"),
            },
            {
              label: t("task.分层划分（Stratified）"),
              value: t("task.分层划分hint"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.group_col: {
      break;
    }
    case HintFormProp.autoOptimize: {
      ret = [
        {
          title: "autoOptimize",
          desc: [
            {
              label: t("task.超参数优化"),
              value: t("task.超参数优化Hint"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.paramPick:
      break;
    case HintFormProp.autoOptimizeParamPick:
      break;
    case HintFormProp.recommend: {
      ret = [
        {
          title: "recommend",
          desc: [
            {
              label: t("task.推荐配置"),
              value: t("task.推荐配置Hint"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.nn_trials: {
      ret = [
        {
          title: "nn_trials",
          desc: [
            {
              label: "nn_trials",
              value: t("task.nn_trialsHint"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.ml_trials: {
      ret = [
        {
          title: "ml_trials",
          desc: [
            {
              label: "ml_trials",
              value: t("task.ml_trialsHint"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.epochRange:
    case HintFormProp.epoch: {
      ret = [
        {
          title: "Epoch",
          desc: [
            {
              label: "Epoch",
              value: t("task.epochHint"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.batchRange:
    case HintFormProp.batchsize: {
      ret = [
        {
          title: "Batch Size",
          desc: [
            {
              label: "Batch Size",
              value: t("task.batchHint1"),
            },
          ],
        },
      ];
      break;
    }
    case HintFormProp.leaningRateRange:
    case HintFormProp.Learningrate: {
      ret = [
        {
          title: "Learning Rate",
          desc: [
            {
              label: "Learning Rate",
              value: t("task.学习率hint1"),
            },
          ],
        },
      ];
      break;
    }
  }
  return ret;
});

// const handleFormFieldValidate = (a, b, c) => {
//   debugger;
// };
const handleMouseEnter = (e: MouseEvent) => {};
const formId = "task-form";
const handleMouseMove = (e: MouseEvent) => {
  let target = e.target as HTMLElement;
  while (target) {
    if (target.id === formId) {
      break;
    }
    const propName = get(target, "dataset.prop");
    if (propName && propName in HintFormProp) {
      // console.log(propName);
      focusFormItemHint.value = propName as HintFormProp;
    }
    if (target.parentNode) target = target.parentNode as HTMLElement;
    else break;
  }
};
// const
const handleMouseLeave = (e: MouseEvent) => {};

const handleOpenHintModal = () => {
  popup(HintModal, {
    title: t("task.提示"),
    descList: [
      {
        title: t("task.划分方式"),
        desc: [
          {
            label: t("task.五折验证"),
            value: t("task.五者hint"),
          },
          {
            label: t("task.随机划分（Random）"),
            value: t("task.随机划分hint"),
          },
          {
            label: t("task.骨架划分（Scaffold）"),
            value: t("task.骨架划分hint"),
          },
          {
            label: t("task.分组划分（Group）"),
            value: t("task.分组划分hint"),
          },
          {
            label: t("task.分层划分（Stratified）"),
            value: t("task.分层划分hint"),
          },
        ],
      },
      {
        title: "Epoch",
        desc: [
          {
            label: "",
            value: t("task.epochHint"),
          },
        ],
      },
      {
        title: "Batch Size",
        desc: [
          {
            label: "",
            value: t("task.batchHint1"),
          },
        ],
      },
      {
        title: "Learning Rate",
        desc: [
          {
            label: "",
            value: t("task.学习率hint1"),
          },
        ],
      },
    ],
  })
    .then((res) => {})
    .catch(() => {});
};

const activeCollapseItem = ref<string[]>([]);
const configList = [
  {
    label: "基础搜索",
    EpochMin: 100,
    EpochMax: 100,
    BatchSizeMin: 8,
    BatchSizeMax: 32,
    LearningRateMin: 2e-5,
    LearningRateMax: 1e-3,
    epochRange: [100, 100],
    batchRange: [8, 32],
    leaningRateRange: ["2e-5", "1e-3"],
    nn_trials: 10,
    ml_trials: 30,
  },
  {
    label: "扩展搜索",
    EpochMin: 40,
    EpochMax: 160,
    BatchSizeMin: 8,
    BatchSizeMax: 64,
    LearningRateMin: 2e-5,
    LearningRateMax: 1e-3,
    epochRange: [40, 160],
    batchRange: [8, 64],
    leaningRateRange: ["2e-5", "1e-3"],
    nn_trials: 20,
    ml_trials: 40,
  },
  {
    label: "穷举搜索",
    EpochMin: 20,
    EpochMax: 200,
    BatchSizeMin: 8,
    BatchSizeMax: 256,
    LearningRateMin: 1e-5,
    LearningRateMax: 1e-3,
    epochRange: [20, 200],
    batchRange: [8, 256],
    leaningRateRange: ["1e-5", "1e-3"],
    nn_trials: 30,
    ml_trials: 50,
  },
];
const handleOptimize = (val: any) => {
  if (val) {
    if (activeCollapseItem.value.every((item) => item !== "advance"))
      activeCollapseItem.value.push("advance");
  }
};

const handleAutoOptimizeParamPick = (val: unknown) => {
  // handleConfigChange("基础搜索");
  if (val) formData.value.recommend = "基础搜索";
  handleConfigChange("基础搜索");
};
const handleConfigChange = (val: unknown) => {
  if (isString(val)) {
    const targetConfig = configList.find((item) => item.label === val);
    const setFormDataConfig = (config: any) => {
      formData.value.epochMin = config.EpochMin;
      formData.value.epochMax = config.EpochMax;
      formData.value.batchSizeMin = config.BatchSizeMin;
      formData.value.batchSizeMax = config.BatchSizeMax;
      formData.value.learningRateMin = config.LearningRateMin;
      formData.value.learningRateMax = config.LearningRateMax;
      formData.value.nn_trials = config.nn_trials;
      formData.value.ml_trials = config.ml_trials;
      formData.value.epochRange = [...config.epochRange];
      formData.value.batchRange = [...config.batchRange];
      formData.value.leaningRateRange = [...config.leaningRateRange];
    };
    setFormDataConfig(targetConfig);
  }
};
const formRef = ref<FormInstance>();
const formData = ref<any>({
  task_name: "",
  task: autoDetect,
  group_col: "",
  split_method: "random",
  paramPick: true,

  autoOptimizeParamPick: true,
  epoch: 100,
  batchsize: 16,
  modelPick: [
    "Uni-Mol(all_h)",
    "Uni-Mol(no_h)",
    "BERT",
    "LR",
    "GBDT",
    "ET",
    "SVM",
  ],
  autoOptimize: false,
  WarmupRatio: 0.06,
  Learningrate: 1e-4,
  EarlyStop: 12,

  EpochList: [12, 19],

  epochMin: 100,
  epochMax: 100,
  batchSizeMin: 16,
  batchSizeMax: 16,
  learningRateMin: 1e-4,
  learningRateMax: 1e-4,

  recommend: "基础搜索",
  epochRange: [100, 100],
  batchRange: [8, 32],
  leaningRateRange: ["2e-5", "1e-3"],
  nn_trials: 10,
  ml_trials: 30,
});
watchEffect(() => {
  if (fileStore.checkTaskType) {
    // formData.value.task = fileStore.checkTaskType;
    detectedValue = fileStore.checkTaskType;
  }
});

const handlePickParams = (val: any) => {
  if (val) {
    formData.value.epoch = 100;
    formData.value.batchsize = 16;
    formData.value.Learningrate = 1e-4;
  }
};

const advancedParamDisabled = computed(() => formData.value.paramPick);
const optimizeParamDisabled = computed(
  () => formData.value.autoOptimizeParamPick
);
const hasGroupCol = computed(() =>
  ["group", "stratified"].includes(formData.value.split_method)
);
const handleSplitMethodChange = () => {
  if (!hasGroupCol.value && formData.value.group_col) {
    formData.value.group_col = "";
  }
};

const formRules = computed(() => {
  const commonRules = {
    task: [
      {
        required: true,
        message: t("task.请选择 task"),
        trigger: ["change", "blur"],
      },
    ],
    split_method: [
      {
        required: true,
        message: t("task.请选择 split_method"),
        trigger: ["change", "blur"],
      },
    ],
    modelPick: [
      {
        required: true,
        message: t("task.请选择 modelPick"),
        trigger: ["change", "blur"],
      },
    ],
  };

  if (!hasGroupCol.value)
    return {
      ...commonRules,
    };

  return {
    ...commonRules,
    group_col: [
      {
        required: true,
        message: t("task.请选择 group_col"),
        trigger: ["change", "blur"],
      },
    ],
  };
});
const submitLoading = ref(false);
const handleSubmit = () => {
  if (!formRef.value) return;
  formRef.value.validate((valid) => {
    if (valid) {
      let taskVal = formData.value.task;
      if (taskVal === "multiclass" && fileStore.target_cols.length > 1) {
        ElMessage({
          type: "error",
          message: t("task.多分类任务只支持单列 target_cols"),
        });
        return;
      }
      if (
        taskVal === "multilabel_regression" &&
        formData.value.split_method === "stratified"
      ) {
        ElMessage({
          type: "error",
          message: t("task.回归任务不支持分层划分，请修改划分方式"),
        });
        return;
      }
      if (
        formData.value.task === "auto_detect" &&
        ["multilabel_regression", "regression"].includes(detectedValue) &&
        formData.value.split_method === "stratified"
      ) {
        ElMessage({
          type: "error",
          message: t(
            "task.该任务被识别为回归任务，回归任务不支持分层划分，请修改划分方式"
          ),
        });
        return;
      }
      if (formData.value.split_method === "group") {
        const groupColDataLabelSet = new Set(
          fileStore.fileTableData.map((item) => item[formData.value.group_col])
        );
        if (groupColDataLabelSet.size < 5) {
          ElMessage({
            type: "error",
            message: t("task.分组划分至少需要5个不同的group_col"),
          });
          return;
        }
      }
      if (
        taskVal === "multilabel_classification" &&
        fileStore.target_cols.length === 1
      ) {
        taskVal = "classification";
      } else if (
        taskVal === "multilabel_regression" &&
        fileStore.target_cols.length === 1
      ) {
        taskVal = "regression";
      }

      let ret = {
        Base: {
          task:
            formData.value.task === "auto_detect"
              ? detectedValue || "multilabel_regression"
              : taskVal,
        },
        Datahub: {
          smiles_col: fileStore.smiles_col,
          target_cols: fileStore.target_cols,
          split_method: formData.value.split_method,
        },
      } as any;
      if (formData.value.group_col) {
        set(ret, "Datahub.group_col", formData.value.group_col);
      }
      if (formData.value.autoOptimize) {
        const epochList = [];
        const batchSizeList = [];
        const learningRateList = [];
        const getCheckList = (
          boundary: [string | number, string | number],
          list: (string | number)[]
        ) => {
          if (boundary[0] == boundary[1]) {
            return [+boundary[0]];
          } else {
            const start = list.indexOf(boundary[0]);
            const end = list.indexOf(boundary[1]);
            return list.slice(start, end + 1);
          }
        };
        set(ret, "Trainer.hyperopt.nn_trials", formData.value.nn_trials);
        set(ret, "Trainer.hyperopt.ml_trials", formData.value.ml_trials);
        set(
          ret,
          "Trainer.hyperopt.nn_hpo_range.max_epochs",
          getCheckList(formData.value.epochRange, epochRangeEnum)
        );
        set(
          ret,
          "Trainer.hyperopt.nn_hpo_range.learning_rate",
          getCheckList(formData.value.leaningRateRange, leaningRateRangeEnum)
        );
        set(
          ret,
          "Trainer.hyperopt.nn_hpo_range.batch_size",
          getCheckList(formData.value.batchRange, batchRangeEnum)
        );
      } else {
        set(ret, "Trainer.NNtrainer.max_epochs", formData.value.epoch);
        set(
          ret,
          "Trainer.NNtrainer.learning_rate",
          formData.value.Learningrate
        );
        set(ret, "Trainer.NNtrainer.batch_size", formData.value.batchsize);
      }
      if (
        !formData.value.modelPick.includes("Uni-Mol(all_h)") &&
        !formData.value.modelPick.includes("Uni-Mol(no_h)")
      ) {
        set(ret, "Featurehub.3D_conformer.active", false);
      }
      if (!formData.value.modelPick.includes("Uni-Mol(all_h)")) {
        set(ret, "Modelhub.NNModel.NN01.active", false);
      }
      if (!formData.value.modelPick.includes("Uni-Mol(no_h)")) {
        set(ret, "Modelhub.NNModel.NN02.active", false);
      }
      if (!formData.value.modelPick.includes("BERT")) {
        set(ret, "Featurehub.1D_smiles.active", false);
        set(ret, "Modelhub.NNModel.NN03.active", false);
      }
      if (!formData.value.modelPick.includes("LR")) {
        set(ret, "Modelhub.MLModel.ML01.active", false);
      }
      if (!formData.value.modelPick.includes("GBDT")) {
        set(ret, "Modelhub.MLModel.ML02.active", false);
      }
      if (!formData.value.modelPick.includes("ET")) {
        set(ret, "Modelhub.MLModel.ML03.active", false);
      }
      if (!formData.value.modelPick.includes("SVM")) {
        set(ret, "Modelhub.MLModel.ML04.active", false);
      }
      const restParams: any = {};
      const appAccessKey = Cookie.get("appAccessKey") || "";
      // Cookie.get("appAccessKey") || `sk-8eb6b738d4c140e3ab1d926389e1abd8`;
      const clientName = Cookie.get("clientName") || "";
      restParams["access_key"] = appAccessKey;
      restParams["app_key"] = clientName;
      submitLoading.value = true;
      submitTaskFormData({
        task: {
          name: fileStore.task_name,
          task: formData.value.task,
          file_id: fileStore.file_id,
          hpo_enable: formData.value.autoOptimize,
          config_dict: ret,
        },
        sku: restParams,
      })
        .then((res) => {
          ElMessage({
            type: "success",
            message: t("task.提交成功,预计扣费", {
              countNumber: +res.data.msg.match(/\d+/g)[0] / 100,
            }),
          });
          router.push({ name: "taskManage" });
        })
        .catch((e) => {})
        .finally(() => {
          submitLoading.value = false;
        });
    }
  });
};
</script>

<style lang="scss" scoped>
:deep() {
  .el-slider {
    margin-left: 10px;
  }
  .el-collapse {
    :last-child.el-collapse-item {
      .el-collapse-item__content {
        // padding-bottom: 0;
      }
    }
  }
}
</style>
