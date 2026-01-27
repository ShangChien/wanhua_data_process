import { createI18n } from "vue-i18n";
import { get } from "lodash";
import { LocalStorageKeys, LocaleOptions } from "@/constants/storage";

const defaultLocale =
  localStorage.getItem(LocalStorageKeys.localeKey) || LocaleOptions.en;

// "./zh-CN/task.json" -> "task"
const formatFilename = (filename: string) => {
  return filename.match(/(?<=\/)[^\/]+(?=\.json)/)?.[0] || "";
};
const getMessageFromModules = (_moduleMap: Record<string, unknown>) => {
  const ret: Record<string, any> = {};
  for (const key in _moduleMap) {
    const exportContent = get(_moduleMap[key], "default");
    if (exportContent) {
      ret[formatFilename(key)] = exportContent;
    }
  }
  return ret;
};
const cnMessages = getMessageFromModules(
  import.meta.glob("./zh-CN/*.json", { eager: true })
);
const enMessages = getMessageFromModules(
  import.meta.glob("./en-US/*.json", { eager: true })
);
const i18n = createI18n({
  locale: defaultLocale,
  fallbackLocale: LocaleOptions.cn,
  legacy: false,
  allowComposition: true,
  messages: {
    [LocaleOptions.en]: enMessages,
    [LocaleOptions.cn]: cnMessages,
  },
});

export default i18n;
