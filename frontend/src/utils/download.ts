export const triggerDownload = (
  binaryData: BlobPart,
  options: BlobPropertyBag,
  fileName: string
) => {
  return new Promise<void>((resolve, reject) => {
    try {
      const blob = new Blob([binaryData], options);
      const downloadUrl = URL.createObjectURL(blob);
      const downloadLink = document.createElement("a");
      downloadLink.href = downloadUrl;
      downloadLink.download = fileName; // 设置下载文件的名称

      // 触发下载
      document.body.appendChild(downloadLink);
      downloadLink.click();

      // 下载完成后释放Object URL
      URL.revokeObjectURL(downloadUrl);
      downloadLink.remove();

      resolve();
    } catch (error) {
      reject();
    }
  });
};
export const triggerBase64Download = (
  base64String: string,
  fileName: string
) => {
  return new Promise<void>((resolve, reject) => {
    try {
      const downloadUrl = base64String;
      const downloadLink = document.createElement("a");
      downloadLink.href = downloadUrl;
      downloadLink.download = fileName; // 设置下载文件的名称

      // 触发下载
      document.body.appendChild(downloadLink);
      downloadLink.click();

      // 下载完成后释放Object URL
      URL.revokeObjectURL(downloadUrl);
      downloadLink.remove();

      resolve();
    } catch (error) {
      reject();
    }
  });
};
