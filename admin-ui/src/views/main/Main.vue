<template>
  <el-container>
    <el-aside class="left">
      <LeftMenu />
    </el-aside>
    <el-container>
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
  import { RouterView } from 'vue-router'
  import LeftMenu from './LeftMenu.vue'
</script>

<style scoped>
  .left {
    width: 200px;
    min-height: 100vh;
    background-color: #545c64;
  }
</style>
