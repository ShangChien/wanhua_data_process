import {
  MULTILABEL_REGRESSION,
  MULTILABEL_CLASSIFICATION,
  CLASSIFICATION,
  REGRESSION,
  MULTICLASS,
} from "@/constants/task";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const useConstants = () => {
  const { t } = useI18n();
  const taskOptions = computed(() => {
    return [
      { label: t("task.分类"), value: CLASSIFICATION, i18nKey: "task.分类" },
      { label: t("task.回归"), value: REGRESSION, i18nKey: "task.回归" },
      {
        label: t("task.多类别分类"),
        value: MULTICLASS,
        i18nKey: "task.多类别分类",
      },
      {
        label: t("task.多标签分类"),
        value: MULTILABEL_CLASSIFICATION,
        i18nKey: "task.多标签分类",
      },
      {
        label: t("task.多标签回归"),
        value: MULTILABEL_REGRESSION,
        i18nKey: "task.多标签回归",
      },
    ];
  });
  const isFavoriteOptions = computed(() => [
    {
      label: t("task.是"),
      value: true,
      i18nKey: "task.是",
    },
    {
      label: t("task.否"),
      value: false,
      i18nKey: "task.否",
    },
  ]);
  const taskTypeOptions = computed(() => [
    {
      label: t("task.名词预测"),
      value: "infer",
    },
    {
      label: t("task.训练"),
      value: "fit",
    },
  ]);
  const taskRunStatusOptions = computed(() => [
    {
      label: t("task.排队中"),
      value: "SCHEDULED",
      i18nKey: "task.排队中",
    },
    {
      label: t("task.主动终止"),
      value: "KILLED",
      i18nKey: "task.主动终止",
    },
    {
      label: t("task.运行成功"),
      value: "FINISHED",
      i18nKey: "task.运行成功",
    },
    {
      label: t("task.运行失败"),
      value: "FAILED",
      i18nKey: "task.运行失败",
    },
    {
      label: t("task.运行中"),
      value: "RUNNING",
      i18nKey: "task.运行中",
    },
  ]);
  return {
    taskOptions,
    taskTypeOptions,
    taskRunStatusOptions,
    isFavoriteOptions,
  };
};

export default useConstants;
