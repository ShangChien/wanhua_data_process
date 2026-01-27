export const getUniqueName = (prefixName: string): string => {
  function generateShortId() {
    // 获取当前时间戳的36进制表示
    const timestamp = Date.now().toString(36);
    // 生成一个随机数的36进制表示
    const randomPart = Math.random().toString(36).substring(2, 8);
    // 组合两部分得到一个较短的唯一标识符
    return `${timestamp}-${randomPart}`;
  }
  return `${prefixName}-${generateShortId()}`;
};
