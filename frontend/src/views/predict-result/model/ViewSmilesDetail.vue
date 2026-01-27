<template>
  <ElDialog
    v-model="dialogVisible"
    width="1200"
    :before-close="props.handleOK"
    :title="$t('task.子结构可解释性')"
    :lock-scroll="true"
  >
    <div :class="['h-[60vh]', 'flex', 'flex-col', 'gap-4']">
      <ElRadioGroup v-model="currentTarget">
        <ElRadioButton
          :value="target"
          :label="target"
          v-for="target in props.kindOfKeys.targetList"
        ></ElRadioButton>
      </ElRadioGroup>
      <div
        :class="[
          'color-bar',
          'bg-gradient-to-r',
          'from-red-600',
          'via-white',
          'to-blue-700',
          'rounded-md',
          'h-4',
          'relative',
          'mb-4',
        ]"
      >
        <span :class="['color-label', 'text-tip', 'left-0']">
          {{ $t("task.正向") }}
        </span>
        <span :class="['color-label', 'text-tip', 'right-0']">
          {{ $t("task.负向") }}
        </span>
      </div>
      <div :class="['image-container', 'flex-1']">
        <div :class="['w-full', 'h-full', 'flex']">
          <template v-if="imageList.length === 1">
            <CustomImg :src="imageList[0]" :class="['image-only']" />
            <!-- <img :src="imageList[0]" :class="['image-only']" /> -->
          </template>
          <template v-else>
            <CustomImg
              :class="['image-only']"
              v-for="src in imageList"
              :src="src"
              :key="src"
            />

            <!-- <img
              v-for="src in imageList"
              :src="src"
              :key="src"
              :class="['image-item']"
            /> -->
          </template>
        </div>
        <!-- <Viewer :options="{}" :images="imageList" :class="['w-full', 'h-full']">
          <template #default="scope">
            <img
              v-for="src in scope.images"
              :src="src"
              :key="src"
              :class="['image-item']"
            />
          </template>
        </Viewer> -->
      </div>
    </div>
    <template #footer>
      <ElSpace wrap>
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
          <Description
            :titleValue="props.data['predict_' + currentTarget]"
            :label="'predict_' + currentTarget"
            :value="
              formatterScienceNumber(props.data['predict_' + currentTarget]) +
              ''
            "
          />
          <Description
            :titleValue="props.data['predict_std_' + currentTarget]"
            :label="'predict_std_' + currentTarget"
            :value="
              formatterScienceNumber(
                props.data['predict_std_' + currentTarget]
              ) + ''
            "
          />
        </template>
        <template v-else>
          <Description
            :titleValue="props.data['predict_' + currentTarget]"
            :label="'predict_' + currentTarget"
            :value="
              formatterScienceNumber(props.data['predict_' + currentTarget]) +
              ''
            "
          />
          <Description
            :titleValue="props.data['prob_' + currentTarget]"
            :label="'prob_' + currentTarget"
            :value="
              formatterScienceNumber(props.data['prob_' + currentTarget]) + ''
            "
          />
        </template>
      </ElSpace>
    </template>
  </ElDialog>
</template>

<script lang="ts" setup>
import Description from "@/components/description/index.vue";
import LongTextComponent from "@/components/long-text-component/index.vue";
import { formatterScienceNumber } from "@/utils/formatter";
import {
  ElCol,
  ElDialog,
  ElRadioButton,
  ElRadioGroup,
  ElRow,
  ElSpace,
} from "element-plus";
import CustomImg from "@/components/custom-img/index.vue";
import { onMounted, ref, watchEffect } from "vue";
import { MULTICLASS, RegressionList } from "@/constants/task";
import { component as Viewer } from "v-viewer";
const dialogVisible = ref(false);
const props = defineProps<{
  handleOK: any;
  handleCancel: any;
  imgSrc: string;
  data: Record<string, any>;
  taskType: string;
  kindOfKeys: {
    probNumberList: string[];
    targetList: string[];
  };
}>();

const imgSrc = () => {
  if (currentTarget.value)
    return (
      `${import.meta.env.VITE_REQUEST_BASE_URL}model/chart/predict_image/` +
      props.data["2D_Graph_Explanation_" + currentTarget.value]
    );
  return "";
};
const originalImgSrc = () => {
  return (
    `${import.meta.env.VITE_REQUEST_BASE_URL}model/chart/predict_image/` +
    props.data["2D_Graph"]
  );
};

const currentTarget = ref();
const imageList = ref<string[]>([originalImgSrc()]);
watchEffect(() => {
  if (props.data["2D_Graph_Explanation_" + currentTarget.value])
    imageList.value[1] = imgSrc();
});
watchEffect(() => {
  if (props.kindOfKeys.targetList.length) {
    currentTarget.value = props.kindOfKeys.targetList[0];
  }
});
onMounted(() => {
  dialogVisible.value = true;
});
// const images = [
//   "https://picsum.photos/200/200",
//   "https://picsum.photos/300/200",
//   "https://picsum.photos/250/200",
// ];
</script>

<style lang="scss" scoped>
@import "@/assets/variables.scss";
.image-container {
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid $gray5-color;
  height: 1px;
}
.image-item {
  width: 50%;
  height: 100%;
  object-fit: contain;
}
.image-only {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
:deep() {
  .el-dialog__footer {
    text-align: center;
  }
}
.color-label {
  position: absolute;
  bottom: -22px;
}
</style>
