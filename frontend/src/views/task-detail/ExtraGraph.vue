<template>
  <div></div>
</template>

<script lang="ts" setup>
const data = {
  ML01: {
    TARGET: {
      total: {
        tp: [7, 0, 0, 7, 1, 0],
        fp: [18, 2, 1, 7, 7, 0],
        fn: [5, 8, 5, 7, 6, 4],
      },
    },
  },
  ML02: {
    TARGET: {
      total: {
        tp: [5, 0, 0, 9, 0, 0],
        fp: [9, 2, 0, 25, 0, 0],
        fn: [7, 8, 5, 5, 7, 4],
      },
    },
  },
  ML03: {
    TARGET: {
      total: {
        tp: [8, 1, 2, 11, 0, 0],
        fp: [12, 2, 1, 10, 3, 0],
        fn: [4, 7, 3, 3, 7, 4],
      },
    },
  },
  ML04: {
    TARGET: {
      total: {
        tp: [2, 0, 0, 9, 0, 0],
        fp: [10, 3, 0, 26, 0, 0],
        fn: [10, 8, 5, 5, 7, 4],
      },
    },
  },
  NN01: {
    TARGET: {
      total: {
        tp: [2, 3, 0, 10, 0, 0],
        fp: [1, 11, 0, 23, 0, 0],
        fn: [10, 5, 5, 4, 7, 4],
      },
    },
  },
  NN02: {
    TARGET: {
      total: {
        tp: [7, 2, 0, 4, 0, 0],
        fp: [15, 9, 0, 12, 1, 0],
        fn: [5, 6, 5, 10, 7, 4],
      },
    },
  },
  NN03: {
    TARGET: {
      total: {
        tp: [7, 1, 0, 8, 2, 0],
        fp: [3, 8, 7, 6, 6, 2],
        fn: [5, 7, 5, 6, 5, 4],
      },
    },
  },
  Ensemble: {
    TARGET: {
      total: {
        tp: [7, 0, 0, 14, 0, 0],
        fp: [10, 3, 0, 16, 0, 0],
        fn: [5, 8, 5, 0, 7, 4],
      },
    },
  },
};
</script>

<style lang="scss" scoped></style>
