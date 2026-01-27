<template>
  <ElDrawer
    size="50%"
    :before-close="props.handleCancel"
    v-model="drawerVisible"
    :lock-scroll="true"
  >
    <div :class="['h-[800px]']">
      <div v-html="htmlStr"></div>
    </div>
  </ElDrawer>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount, watchEffect, h } from "vue";
import { codeToHtml } from "shiki";
import { ElDrawer } from "element-plus";
import { formatYAMLToJSON } from "@/utils/formatter";
const drawerVisible = ref<boolean>(false);

const props = defineProps<{
  handleOK: any;
  handleCancel: any;
  paramData: Record<string, any>;
}>();
onMounted(() => {
  drawerVisible.value = true;
});
const paramsObj = ref<any>({
  Featurehub3D_conformer: "{'active': True}",
  Datahub:
    "{'parsing': 'auto', 'smiles_col': 'SMILES', 'target_cols': 'TARGET,TARGET_1,TARGET_2', 'target_col_prefix': 'TARGET', 'target_normalize': 'auto', 'anomaly_clean': False, 'split_method': 'scaffold', 'group_col': 'GROUP', 'split_n': 5, 'split_seed': 42}",
  Featurehub:
    "{'1D_smiles': {'active': True, 'max_len': 200}, '2D_graph_1': {'active': False}, '3D_conformer': {'active': True, 'size': 1, 'mode': 'heavy'}, 'FE_fringerprint': {'active': True, 'neighbor': 5, 'dim': 2048}, 'FE_handcrafts': {'active': True, 'base_featureset': True}}",
  Trainer:
    "{'hyperopt': {'nn_trials': 10, 'nn_hpo_range': {'max_epochs': [50, 150], 'learning_rate': [2e-05, 0.001], 'batch_size': [8, 64]}, 'ml_trials': 30}, 'Common': {'seed': 0, 'mode': 'fast', 'logger_level': 1, 'report': True}, 'NNtrainer': {'patience': 10, 'max_epochs': 100, 'learning_rate': '1e-4', 'warmup_ratio': 0.03, 'batch_size': 16, 'max_norm': 5.0, 'cuda': True, 'amp': True}, 'MLtrainer': {'cpu': -1}}",
  Ensembler:
    "{'method': 'stacking', 'filter_size': 1, 'model': 'LRModel', 'feature': 'Meta_feature', 'params': {'C': 1.0}}",
  Base: "{'loss_func': 'auto', 'seed': 42, 'confidence': False, 'task': 'multilabel_regression'}",
  status: "running",
  Modelhub:
    "{'NNModel': {'NN01': {'active': True, 'model': 'UniMolModel', 'feature': '3D_conformer_all_h', 'params': {'pretrain': 'mol_pre_all_h_220816.pt'}}, 'NN02': {'active': True, 'model': 'UniMolModel', 'feature': '3D_conformer_no_h', 'params': {'pretrain': 'mol_pre_no_h_220816.pt'}}, 'NN03': {'active': True, 'model': 'BERTModel', 'feature': '1D_smiles'}, 'NN04': {'active': False, 'model': 'HIGNNModel', 'feature': '2D_graph_1'}}, 'MLModel': {'ML01': {'active': True, 'model': 'LRModel', 'feature': 'FE_fringerprint', 'params': {'C': 1.0}}, 'ML02': {'active': True, 'model': 'GBDTModel', 'feature': 'FE_handcrafts', 'params': {'n_estimators': 1000, 'num_leaves': 31, 'learning_rate': 0.03}}, 'ML03': {'active': True, 'model': 'ETModel', 'feature': 'FE_handcrafts', 'params': {'n_estimators': 100, 'max_depth': 40}}, 'ML04': {'active': True, 'model': 'SVMModel', 'feature': 'FE_fringerprint', 'params': {'C': 10, 'epsilon': 0.1}}}}",
});
const htmlStr = ref<string>("");
watchEffect(() => {
  codeToHtml(JSON.stringify(formatYAMLToJSON(props.paramData), null, 2), {
    lang: "javascript",
    theme: "material-theme-lighter",
  }).then((res) => {
    htmlStr.value = res;
  });
});
</script>

<style lang="scss" scoped></style>
