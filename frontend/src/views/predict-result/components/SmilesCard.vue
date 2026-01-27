<template>
  <ElCard :class="['card-container']">
    <!-- <ElRadioGroup
      :class="['mb-4']"
      v-model="currentTarget"
      v-if="kindOfKeys.targetList.length > 1"
    >
      <ElRadioButton
        v-for="target in kindOfKeys.targetList"
        :label="target"
        :value="target"
      />
    </ElRadioGroup> -->
    <div :class="['content-container']">
      <ElScrollbar height="80">
        <ElSpace
          direction="vertical"
          alignment="start"
          size="small"
          :class="['pr-2']"
        >
          <Description label="SMILES" :value="props.data.SMILES"
            ><template #value>
              <LongTextComponent :line-number="1" :text="props.data.SMILES" />
            </template>
          </Description>
          <template v-if="props.taskType === MULTICLASS">
            <Description
              :titleValue="props.data.predict_TARGET"
              label="predict_TARGET"
              :value="formatterScienceNumber(props.data.predict_TARGET) + ''"
            />
            <template
              v-for="item in props.kindOfKeys.probNumberList"
              :key="item"
              :label="item"
            >
              <Description
                :titleValue="props.data[item]"
                :label="item"
                :value="formatterScienceNumber(props.data[item]) + ''"
              />
            </template>
          </template>
          <template v-else-if="RegressionList.includes(props.taskType as any)">
            <template v-for="item in props.kindOfKeys.targetList">
              <Description
                :titleValue="props.data['predict_' + item]"
                :label="'predict_' + item"
                :value="
                  formatterScienceNumber(props.data['predict_' + item]) + ''
                "
              />
              <Description
                :titleValue="props.data['predict_std_' + item]"
                :label="'predict_std_' + item"
                :value="
                  formatterScienceNumber(props.data['predict_std_' + item]) + ''
                "
              />
            </template>
          </template>
          <template v-else>
            <template v-for="item in props.kindOfKeys.targetList">
              <Description
                :titleValue="props.data['predict_' + item]"
                :label="'predict_' + item"
                :value="
                  formatterScienceNumber(props.data['predict_' + item]) + ''
                "
              />
              <Description
                :titleValue="props.data['prob_' + item]"
                :label="'prob_' + item"
                :value="formatterScienceNumber(props.data['prob_' + item]) + ''"
              />
            </template>
          </template>
        </ElSpace>
      </ElScrollbar>
      <img
        loading="lazy"
        :src="originalImgSrc"
        @click="() => handlePreview(originalImgSrc)"
        :class="['w-20', 'h-20', 'cursor-pointer']"
      />
    </div>
  </ElCard>
</template>

<script lang="ts" setup>
import Description from "@/components/description/index.vue";
import LongTextComponent from "@/components/long-text-component/index.vue";
import { formatterScienceNumber } from "@/utils/formatter";
import { ElCard, ElScrollbar, ElSpace } from "element-plus";
import { computed, ref, watchEffect } from "vue";

import { popup } from "@/components/modal/ModalContainer.vue";
import { MULTICLASS, RegressionList } from "@/constants/task";
import ViewSmilesDetail from "../model/ViewSmilesDetail.vue";
const props = defineProps<{
  data: Record<string, any>;
  taskType: string;
  kindOfKeys: {
    probNumberList: string[];
    targetList: string[];
  };
}>();
const currentTarget = ref<string>();
watchEffect(() => {
  if (props.kindOfKeys.targetList.length) {
    currentTarget.value = props.kindOfKeys.targetList[0];
  }
});
const handlePreview = (src: string) => {
  popup(ViewSmilesDetail, {
    imgSrc: src,
    data: props.data,
    taskType: props.taskType,
    kindOfKeys: props.kindOfKeys,
  })
    .then((res) => {})
    .catch(() => {});
};
const imgSrc = computed(() => {
  return (
    `${import.meta.env.VITE_REQUEST_BASE_URL}model/chart/predict_image/` +
    props.data["2D_Graph_Explanation_" + currentTarget.value]
  );
});
const originalImgSrc = computed(() => {
  return (
    `${import.meta.env.VITE_REQUEST_BASE_URL}model/chart/predict_image/` +
    props.data["2D_Graph"]
  );
});

const handleCopy = () => {};
</script>

<style lang="scss" scoped>
@import "@/assets/variables.scss";

.card-container {
  height: 122px;
  margin-bottom: 20px;
  border: 1px solid $gray5-color;
  border-radius: 12px;
  box-shadow: none;
}
.content-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
