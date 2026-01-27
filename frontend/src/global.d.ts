import { type RDKitModule } from "@/types/rdkit/index";
import { AxiosRequestConfig } from "axios";

declare global {
  interface Window {
    RDKit: RDKitModule;
  }
}

declare module "@vue/shared" {}

declare module "axios" {
  export interface AxiosRequestConfig {
    ignoreDefaultErrorToast?: boolean;
  }
}
