export const CLASSIFICATION = "classification";
export const REGRESSION = "regression";
export const MULTICLASS = "multiclass";
export const MULTILABEL_CLASSIFICATION = "multilabel_classification";
export const MULTILABEL_REGRESSION = "multilabel_regression";
export const taskOptions = [
  { label: "分类", value: CLASSIFICATION, i18nKey: "task.分类" },
  { label: "回归", value: REGRESSION, i18nKey: "task.回归" },
  { label: "多类别分类", value: MULTICLASS, i18nKey: "task.多类别分类" },
  {
    label: "多标签分类",
    value: MULTILABEL_CLASSIFICATION,
    i18nKey: "task.多标签分类",
  },
  {
    label: "多标签回归",
    value: MULTILABEL_REGRESSION,
    i18nKey: "task.多标签回归",
  },
];

export const ClassificationList = [
  CLASSIFICATION,
  MULTILABEL_CLASSIFICATION,
  MULTICLASS,
] as const;
export const RegressionList = [REGRESSION, MULTILABEL_REGRESSION] as const;

export const paramLabelMap: Record<string, string> = {
  LRModel: "Logistic Regression",
  GBDTModel: "GBDT",
  ETModel: "ExtraTrees",
  SVMModel: "ExtraTrees",
  UniMolModel: "UniMol",
  BERTModel: "BERT",
  FE_fringerprint: "Molecular Fingerprints",
  FE_handcrafts: "Molecular Descriptors",
  "3D_conformer_all_h": "3D Unimol Pre-trained Features (with Hydrogens)",
  "3D_conformer_no_h": "3D Unimol Pre-trained Features (without Hydrogens)",
  "1D_smiles": "1D SMILES Pre-trained Features",
  Meta_feature: "Meta Features",
  learning_rate: "Learning Rate",
  batch_size: "Batch Size",
  max_epochs: "Max Epochs",
  NN: "NN",
  model: "Model",
  feature: "Feature",
  hyperopt: "Hyperparameter",
  // params: "超参数",
  // feature: "特征",
  // model: "模型",
};

export const taskTypeOptions = [
  {
    label: "预测",
    value: "infer",
  },
  {
    label: "训练",
    value: "fit",
  },
];

export const taskRunStatusOptions = [
  {
    label: "排队中",
    value: "SCHEDULED",
    i18nKey: "task.排队中",
  },
  {
    label: "主动终止",
    value: "KILLED",
    i18nKey: "task.主动终止",
  },
  {
    label: "运行成功",
    value: "FINISHED",
    i18nKey: "task.运行成功",
  },
  {
    label: "运行失败",
    value: "FAILED",
    i18nKey: "task.运行失败",
  },
  {
    label: "运行中",
    value: "RUNNING",
    i18nKey: "task.运行中",
  },
];
export const transOptionToMap = (options: any[]) => {
  return options.reduce((acc, cur) => {
    acc[cur.value] = cur;
    return acc;
  }, {});
};
export const taskRunStatusMap = transOptionToMap(taskRunStatusOptions);
