<template>
  <div v-html="svg" :class="['border-shadow']"></div>
</template>

<script lang="ts" setup>
import { type JSMol } from "@/types/rdkit/index";
import initRDKit from "@/utils/rdkit/init";
import { onMounted, reactive, ref } from "vue";
const props = defineProps({
  structure: {
    type: String,
    required: true,
  },
  subStructure: {
    type: String,
    default: "",
  },

  drawingDelay: {
    type: Number,
    default: undefined,
  },
});

// RDKit state reporting values
let rdkitLoaded = ref(false);
let rdkitError = ref(false);

// Molecule state values
let molDetails = reactive({
  width: 200,
  height: 200,
  bondLineWidth: 1,
  addStereoAnnotation: true,
});
let svg = ref("");

/**
 * Validate the molecule
 */
function isValid(m: JSMol | null) {
  return !!m;
}

/**
 * Get highlight details for molecule
 */
function getMolDetails(mol: JSMol | null, qmol: JSMol | null) {
  if (isValid(mol) && isValid(qmol)) {
    // get substructure highlight details
    const details = JSON.parse(mol?.get_substruct_matches(qmol as JSMol) || "");
    // reduce the list of objects to a single list object with all atoms and bonds
    const detailsMerged: { atoms: number[]; bonds: number[] } = details
      ? details.reduce(
          (
            acc: { atoms: number[]; bonds: number[] },
            { atoms, bonds }: { atoms: number[]; bonds: number[] }
          ) => ({
            atoms: [...acc.atoms, ...atoms],
            bonds: [...acc.bonds, ...bonds],
          }),
          { atoms: [], bonds: [] }
        )
      : details;

    return JSON.stringify({
      ...molDetails,
      ...detailsMerged,
    });
  } else {
    // if one of the molecules are not valid, return no highlight details
    return JSON.stringify({
      ...molDetails,
    });
  }
}

/**
 * Draw the molecule to the canvas, or return set the SVG variable
 */
function drawSVGorCanvas() {
  const mol = window.RDKit.get_mol(props.structure || "invalid");
  const qmol = window.RDKit.get_qmol(props.subStructure || "invalid");
  const isValidMol = isValid(mol);

  if (isValidMol) {
    const svgGenerated = (mol as JSMol).get_svg_with_highlights(
      getMolDetails(mol, qmol)
    );
    svg.value = svgGenerated;
  }

  /**
   * Delete C++ mol objects manually
   * https://emscripten.org/docs/porting/connecting_cpp_and_javascript/embind.html#memory-management
   */
  mol?.delete();
  qmol?.delete();
}

/**
 * Calls the main drawing logic, either with a delay or without
 */
function draw() {
  drawSVGorCanvas();
}

onMounted(() => {
  initRDKit()
    .then(() => {
      rdkitLoaded.value = true;
      try {
        draw();
      } catch (err) {}
    })
    .catch((err) => {
      rdkitError.value = true;
    });
});
</script>

<style lang="scss" scoped>
.border-shadow {
  box-shadow: 0px 4px 19px 0px rgba(222, 222, 222, 0.2);
}
</style>
