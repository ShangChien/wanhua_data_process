import Papa from "papaparse";

export const generateSMILESFile = (smileHeaderName: string, list: string[]) => {
  const colKey = smileHeaderName;
  const JSONdata = list.map((item) => {
    return {
      [colKey]: item,
    };
  });
  const csvData = Papa.unparse(JSONdata);
  const csvFile = new File([csvData], "data.csv", {
    type: "text/csv;charset=utf-8;",
  });
  return csvFile;
};
