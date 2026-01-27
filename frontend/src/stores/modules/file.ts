import { defineStore } from "pinia";
export type FileCheckState =
  | "检查通过"
  | "存在错误数据项"
  | "检查中"
  | "未检查"
  | "检查未能通过";

export const checkTagTypeMap: Record<
  FileCheckState,
  "success" | "warning" | "info" | "primary" | "danger"
> = {
  检查通过: "success",
  存在错误数据项: "warning",
  检查中: "primary",
  未检查: "warning",
  检查未能通过: "danger",
} as const;
export interface TrainTaskFormState {
  headerList: string[];
  task_name: string;
  target_cols: string[];
  smiles_col: string;
  file_id: string;
  checkState: FileCheckState;
  checkTaskType: string;
  fileTableData: any[];
}
export const useFileStore = defineStore("fileStore", {
  state(): TrainTaskFormState {
    return {
      headerList: [],
      target_cols: [],
      smiles_col: "",
      task_name: "",
      file_id: "",
      checkState: "未检查",
      checkTaskType: "",
      fileTableData: [],
    };
  },
  actions: {
    updateStore(payload: Partial<TrainTaskFormState>) {
      // @ts-ignore-next-line
      this.$patch(payload);
    },
    resetStore() {
      this.$reset();
    },
  },
});
