<template>
  <div
    ref="viewerContainer"
    :class="['w-[200px]', 'h-[200px]', 'relative', 'border-shadow']"
  ></div>
</template>

<script lang="ts" setup>
import axios from "axios";
import { defineProps, onMounted, ref, watchEffect } from "vue";
import initRDKit from "@/utils/rdkit/init";
const props = defineProps({
  SMILES: String,
});

const viewerContainer = ref(null);

const loadMolecule = (smiles: string) => {
  try {
    // Convert SMILES to PDB using Open Babel API
    initRDKit().then((res) => {
      const mol = res.get_mol(smiles);

      if (mol) {
        mol.set_new_coords(true);
        const molblock = mol.get_molblock();

        // Initialize 3Dmol viewer
        const viewer = (window as any).$3Dmol.createViewer(
          viewerContainer.value,
          {
            backgroundColor: "white",
          }
        );
        // Add PDB data to viewer
        viewer.addModel(molblock, "mol");
        viewer.setStyle({}, { stick: {} });
        viewer.zoomTo();
        viewer.render();
      }
    });
  } catch (error) {
    console.error("Error converting SMILES to PDB:", error);
  }
};

watchEffect(() => {
  if (props.SMILES && viewerContainer.value) {
    loadMolecule(props.SMILES);
  }
});
</script>

<style lang="scss" scoped>
/* Add any custom styles here */
.border-shadow {
  box-shadow: 0px 4px 19px 0px rgba(222, 222, 222, 0.2);
}
</style>
