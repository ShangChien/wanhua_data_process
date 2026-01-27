import AppAxios from "../request";

export type InferTaskPayload = {
  name: string;
  model_trained_run_id: string;
  file_id: string;
  smiles_col: string;
  explain: boolean;
};
export const newInferTask = (payload: {
  task: InferTaskPayload;
  sku: {
    access_key: string;
    app_key: string;
  };
}) => {
  return AppAxios.post("/task/new_infer", payload);
};
export const getPredictTableData = (payload: {
  run_id: string;
  page: number;
  page_size: number;
  keyword: string;
}) => {
  return AppAxios.post("/model/chart/predict_table_data", payload);
};

export const getPredictTableXLSX = (payload: { run_id: string }) => {
  return AppAxios.get("/model/chart/export_predict_result_xlsx", {
    params: payload,
    responseType: "arraybuffer",
  });
};

export const getPredictTableCSV = (payload: { run_id: string }) => {
  return AppAxios.get("/model/chart/export_predict_result_csv", {
    params: payload,
    responseType: "arraybuffer",
  });
};

export const getPredictTableZIP = (payload: {
  run_id: string;
  with_explain: boolean;
}) => {
  return AppAxios.get("/model/chart/export_predict_result_xlsx_zip", {
    params: payload,
    responseType: "arraybuffer",
  });
};
