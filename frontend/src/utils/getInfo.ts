export const getTaskType = (str: string) => {
  const regex = /'task':\s*'([^']+)'/;
  const match = str.match(regex);
  const taskType = match ? match[1] : "";
  return taskType;
};
