import { ClassificationList } from "@/constants/task";
import { get } from "lodash";
export const isClassificationTask = (taskType: any) => {
  return ClassificationList.includes(taskType);
};

export const isUniMolTask = (data: any) => {
  console.log(data);
  const condition1 =
    get(data, "task_type.fit.config_dict.Modelhub.NNModel.NN01.active") ==
    undefined;
  const condition2 =
    get(data, "task_type.fit.config_dict.Modelhub.NNModel.NN02.active") ==
    undefined;
  return condition1 && condition2;
};
