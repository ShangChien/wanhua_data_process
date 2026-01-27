import { taskOptions, taskRunStatusOptions } from "@/constants/task";
import { dayjs } from "element-plus";
import { format, round } from "mathjs";
export const formatterScienceNumber = (data: string) => {
  if (isNaN(data as unknown as number) || isNaN(parseFloat(data))) return data;
  else {
    const num = +data;
    const isLargeNumber = Math.abs(num) >= 1e6;
    const isSmallNumber = num !== 0 && Math.abs(num) <= 1e-6;

    if (isLargeNumber || isSmallNumber) {
      return (+data).toExponential(3);
    } else {
      return round(+data, 4);
    }
  }
};

export const formatTaskList = (list: any[]) => {
  return list.map((item) => {
    const taskTypeLabel = taskOptions.find(
      (option) => item.model_task === option.value
    )?.label;
    return {
      ...item,
      ctime: dayjs.unix(item.ctime).format("YYYY-MM-DD HH:mm"),
      taskTypeLabel,
    };
  });
};

export const getTaskI18nKey = (type: string) => {
  const ret =
    taskOptions.find((option) => type === option.value)?.i18nKey || "";
  return ret;
};
export const getStatusI18nKey = (type: string) => {
  const ret =
    taskRunStatusOptions.find((option) => type === option.value)?.i18nKey || "";
  return ret;
};
function tryParseStr(str: string) {
  try {
    const parsedJson = JSON.parse(str);
    return parsedJson;
  } catch (error) {
    return str;
  }
}
export const formatYAMLToJSON = (yamlObj: Record<string, string>) => {
  const ret: Record<string, any> = {};
  const keyList = Reflect.ownKeys(yamlObj);
  for (let i = 0; i < keyList.length; i++) {
    const curKey = keyList[i] as string;
    const curYAMLStr = JSON.stringify(yamlObj[curKey as string]);
    const boolReplacedString = curYAMLStr
      .replace(/True/g, "true")
      .replace(/False/g, "false");
    const quoteReplacedString = boolReplacedString.replace(/'/g, '"');
    const jsonObject = tryParseStr(quoteReplacedString);
    ret[curKey] = jsonObject;
  }

  return ret;
};

export const formatParamLabel = (str: string) => {
  if (["r2", "R2"].includes(str)) return "R<sup>2</sup>";
  return str;
};

export const getOriginDataSetFileName = (name: string) => {
  if (name.includes("_valid_")) {
    return name.match(/(.+?)_valid_(.+)/)?.[2];
  }
};
export const getFileId = (name: string) => {
  if (name.includes("_valid_")) {
    return name.match(/(.+?)_valid_(.+)/)?.[1];
  }
};

export function formatDuration(startTime: number, endTime: number) {
  const duration = endTime - startTime;
  // 将毫秒转换为分钟
  const minutesTotal = Math.ceil(duration / 60);

  // 计算小时数和剩余分钟数
  const hours = Math.floor(minutesTotal / 60);
  const minutes = minutesTotal % 60;

  // 格式化输出
  return `${hours}h ${minutes}min`;
}

export const classifyTaskState = (str: string) => {
  switch (str) {
    case "CANCELED":
      return "KILLED";
    case "STAGING":
      return "SCHEDULED";
    default:
      return str;
  }
};
