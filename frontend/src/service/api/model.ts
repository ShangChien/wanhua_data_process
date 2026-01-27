import AppAxios from "../request";

export const getTaskAllInfo = (payload: { run_id: string }) => {
  return AppAxios.post("/model/chart/all_info", payload);
};

export const getMetricsInfo = (payload: { run_id: string }) => {
  return AppAxios.post("/model/chart/metrics", payload);
};
export const getPredictMetric = (payload: { run_id: string }) => {
  return AppAxios.post("/model/chart/predict_metrics", payload);
};
export const getTsneInfo = (payload: { run_id: string }) => {
  return AppAxios.post("/model/chart/tsne", payload);
};

export const getPredictInfo = (payload: { run_id: string }) => {
  return AppAxios.post("/model/chart/predict", payload);
};

export const getDistributionInfo = (payload: { run_id: string }) => {
  return AppAxios.post("/model/chart/distribution", payload);
};

export const getSelfModelAllDetail = (payload: { run_id: string }) => {
  return AppAxios.post("/model/chart/all_model_details", payload);
};

export const getModelParamInfo = (payload: { run_id: string }) => {
  return AppAxios.post("/model/chart/params", payload);
};
