import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNavStore = defineStore('nav', () => {
  const currentPage = ref('home')

  function setPage(page: string) {
    currentPage.value = page
  }

  function resetToHome() {
    currentPage.value = 'home'
  }

  return {
    currentPage,
    setPage,
    resetToHome
  }
})
