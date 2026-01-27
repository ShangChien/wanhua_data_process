import AppAxios, { type ResponseWrapper } from "../request";

// axiosInstance
enum ResCode {
  success = 0,
  error = -1,
}

export type TaskDetail = {
  metrics: Metrics;
  params: Params;
  task_type: string;
  model_task: string;
  data_path: string;
  name: string;
  status: string;
  start_time: number;
  end_time: number;
  model_trained_run_id: any;
};

export type Metrics = {
  mcc: number;
  cohen_kappa: number;
  acc: number;
  log_loss: number;
  auc: number;
  recall: number;
  f1_score: number;
  auprc: number;
  precision: number;
};

export type Params = {
  Featurehub3D_conformer: string;
  Datahub: string;
  Featurehub: string;
  Trainer: string;
  Ensembler: string;
  Base: string;
  status: string;
  Modelhub: string;
};

export const getFileCols = (payload: any) => {
  return AppAxios.post("/file/upload", payload);
};

export const confirmCheckFile = (
  payload: any,
  ignoreDefaultErrorToast: boolean = true
) => {
  return AppAxios.post("/file/check", payload, {
    ignoreDefaultErrorToast,
  });
};
export interface TaskListResponse {
  data: TaskData[];
  total_count: number;
}

export interface TaskData {
  run_id: string;
  name: string;
  ctime: number;
  model_task: string;
  data_path: string;
  task_type: string;
  is_favorite: boolean;
  state: string;
  model_trained_run_id: string;
}
export const getTaskList = (payload: {
  length: number;
  page: number;
  fussy_re: string;
  filter: {
    task_type: string[];
    model_task: string[];
    state: string[];
    is_favorite: string[];
  };
}) => {
  return AppAxios.post<ResponseWrapper<TaskListResponse>>(
    "/task/list",
    payload
  );
};

export const submitTaskFormData = (payload: any) => {
  return AppAxios.post("/task/new_train", payload);
};

export const getTaskDetail = (payload: { run_id: string }) => {
  // return AppAxios.get(`/task/${payload.taskId}`);
  return AppAxios.post<ResponseWrapper<TaskDetail>>(
    `/task/get_by_run_id`,
    payload
  );
};

export const getTemplateDetail = (payload: { type: "predict" | "train" }) => {
  return AppAxios.get("/file/download_template", {
    params: payload,
  });
};

export const deleteTask = (payload: { run_id: string }) => {
  return AppAxios.post<ResponseWrapper<boolean>>(`/task/remove`, payload);
};

export const stopTask = (payload: { run_id: string }) => {
  return AppAxios.post<ResponseWrapper<boolean>>(`/task/stop`, payload);
};

export const getTaskLog = (
  payload: { run_id: string },
  ignoreDefaultErrorToast: boolean = true
) => {
  return AppAxios.post("/task/log", payload, {
    ignoreDefaultErrorToast,
  });
};

export const updateTaskCollectedStatus = (payload: {
  run_id: string;
  is_favorite: boolean;
}) => {
  return AppAxios.post("/model/set_model_favorite_status", payload);
};

export const restartTask = (payload: {
  data: { run_id: string };
  sku: {
    access_key: string;
    app_key: string;
  };
}) => {
  return AppAxios.post("/task/re_run", payload);
};

export const getTaskRunProgress = (
  payload: { run_id: string },
  ignoreDefaultErrorToast: boolean = true
) => {
  return AppAxios.post("/task/log_progress", payload, {
    ignoreDefaultErrorToast,
  });
};

export const getPDFReportImg = (payload: { run_id: string }) => {
  return AppAxios.post<
    ResponseWrapper<
      {
        file_name: string;
        content: string;
      }[]
    >
  >("/model/chart/pdf_content_img", payload);
};

export const downloadDataFile = (payload: { file_id: string }) => {
  return AppAxios.get("/file/download_data_file", { params: payload });
};
