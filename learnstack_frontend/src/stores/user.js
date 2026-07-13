import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,  // 用户状态
  }),
  actions: {
    // 设置用户信息
    setCurrentUser(user) {
      this.currentUser = user;
    },
  },
});