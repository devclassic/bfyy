<template>
  <el-menu
    background-color="#545c64"
    text-color="#fff"
    active-text-color="#ffd04b"
    :default-active="route.path"
    :router="true">
    <el-menu-item index="/">管理首页</el-menu-item>
    <el-menu-item v-if="isroot" index="/user">用户管理</el-menu-item>
    <el-menu-item v-if="isroot" index="/app">应用管理</el-menu-item>
    <el-menu-item v-if="isroot" index="/account">账户管理</el-menu-item>
    <el-menu-item index="/data">数据管理</el-menu-item>
    <el-menu-item index="/knowledge">知识库管理</el-menu-item>
    <el-menu-item @click="logout">退出登录</el-menu-item>
  </el-menu>
</template>

<script setup>
  import { useRoute } from 'vue-router'
  const route = useRoute()
  const isroot = sessionStorage.getItem('user') === 'root'
  const logout = () => {
    sessionStorage.removeItem('token')
    window.location.reload()
  }
</script>
