<template>
  <section class="form-page">
    <h1>도서 리뷰 쓰기</h1>
    <form class="panel" @submit.prevent="submit">
      <label>도서 ISBN<input v-model="form.book_isbn" required :disabled="Boolean(route.query.book)"></label>
      <label>제목<input v-model="form.title" maxlength="200" required></label>
      <label>내용<textarea v-model="form.content" rows="12" required></textarea></label>
      <p v-if="error" class="error">{{error}}</p>
      <button class="primary" :disabled="saving">{{saving?'저장 중…':'등록하기'}}</button>
    </form>
  </section>
</template>

<script setup>
import {ref} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import api from '../api/axios'

const route=useRoute()
const router=useRouter()
const form=ref({book_isbn:route.query.book||'',title:'',content:''})
const saving=ref(false)
const error=ref('')

const submit=async()=>{
  saving.value=true
  try{
    const {data}=await api.post('/threads',form.value)
    router.push(`/threads/${data.id}`)
  }catch(e){
    error.value=e.response?.data?.detail||'도서 리뷰를 등록하지 못했습니다.'
  }finally{
    saving.value=false
  }
}
</script>

<style scoped>
.form-page {
  max-width: 720px;
  margin: auto;
  padding: 24px var(--space-margin-mobile);
}

@media (min-width: 768px) {
  .form-page { padding-left: var(--space-margin-desktop); padding-right: var(--space-margin-desktop); }
}

.form-page h1 {
  font: 300 clamp(1.8rem, 4vw, 2.4rem)/1.2 var(--font-headline);
  letter-spacing: var(--ls-headline);
  color: var(--color-primary);
  margin: 0 0 20px;
}

.panel {
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  padding: 26px;
  border-radius: var(--radius-xl);
}

.panel label {
  display: grid;
  gap: 8px;
  margin-bottom: 18px;
  color: var(--color-on-surface-variant);
  font-weight: 300;
  font-size: 0.88rem;
}

.error { color: var(--color-error); font-size: 0.88rem; }
</style>
