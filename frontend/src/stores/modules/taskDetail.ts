import { MULTICLASS, taskOptions } from "@/constants/task";
import { defineStore } from "pinia";
import { ClassificationList } from "@/constants/task";
export type TaskDetailState = {
  currentSelfModel: string;
  taskType: string;
  currentTarget: string;
  distributionData: Record<string, any[]>;
  metricsData: Record<string, string>[];
  modelParamData: Record<string, Record<string, string>>;
  selfModelDetail: Record<string, any>;
  taskDetail: Record<string, any>;
  TsneInfo: any;
  taskLog: string;
};
export const useTaskDetailStore = defineStore("taskDetailStore", {
  state: (): TaskDetailState => {
    return {
      currentSelfModel: "Ensemble",
      taskType: "",
      currentTarget: "",
      distributionData: {},
      metricsData: [],
      modelParamData: {},
      selfModelDetail: {},
      taskDetail: {},
      TsneInfo: {},
      taskLog: "",
    };
  },
  getters: {
    isMultiClass(): boolean {
      return this.taskType === MULTICLASS;
    },
    isClassification(): boolean {
      return ClassificationList.includes(this.taskType as any);
    },
    targetList: (state) => {
      return Object.keys(state.distributionData) as string[];
    },
  },
  actions: {
    resetStore() {
      this.$reset();
    },
    updateStore(payload: any) {
      this.$patch(payload);
    },
  },
});
