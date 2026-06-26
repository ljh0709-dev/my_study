<template>
  <section class="detail-page">
    <router-link to="/discover" class="back">← Discover</router-link>
    <div v-if="loading" class="state">트렌드를 불러오는 중입니다…</div>
    <div v-else-if="!currentTrend" class="state error-text">{{ error || '트렌드를 찾을 수 없습니다.' }}</div>
    <template v-else>
      <header class="topic-hero">
        <!-- CSS Aurora Background Effects -->
        <div class="hero-bg-effects">
          <div class="glow-sphere glow-1"></div>
          <div class="glow-sphere glow-2"></div>
          <div class="glow-sphere glow-3"></div>
        </div>

        <div class="hero-content">
          <div class="topic-meta"><span>0{{ currentTrend.rank }}</span><b>{{ categoryLabel(currentTrend.category) }}</b></div>
          <h1>{{ currentTrend.title }}</h1>
          <p>{{ currentTrend.summary }}</p>
          <div class="keywords"><span v-for="keyword in currentTrend.keywords" :key="keyword">#{{ keyword }}</span></div>
        </div>
      </header>

      <div class="copyright-note">
        <strong>뉴스 이용 안내</strong>
        <span>네이버 뉴스 검색 API가 제공한 제목·요약·출처만 표시합니다. 기사 전문은 각 언론사의 원문에서 확인하세요.</span>
      </div>

      <div class="content-layout">
        <main class="news-column">
          <div class="section-title"><div><small>NEWS CONTEXT</small><h2>이 흐름을 만든 뉴스</h2></div><span>{{ currentTrend.relatedArticles.length }} articles</span></div>
          <article v-for="(article,index) in currentTrend.relatedArticles" :key="article.id" :class="['news-card',{lead:index===0}]">
            <div class="news-index">0{{ index + 1 }}</div>
            <div>
              <div class="news-meta"><b>{{ article.source }}</b><time>{{ formatDate(article.pubDate) }}</time></div>
              <h3>{{ article.title }}</h3>
              <p>{{ article.summary }}</p>
              <a :href="article.url" target="_blank" rel="noopener noreferrer">언론사 원문 읽기 <span>↗</span></a>
            </div>
          </article>
        </main>

        <aside class="book-column">
          <div class="section-title"><div><small>VECTOR RAG + GPT</small><h2>더 깊이 읽을 책</h2></div></div>
          <div v-if="recommendationLoading" class="recommend-state"><div class="loader"></div><p>뉴스 문맥과 도서 임베딩을 비교하고 있습니다.</p></div>
          <div v-if="error && recommendationStatus === 'failed'" class="recommend-state error-text"><p>{{ error }}</p><button @click="ensureRecommendations(currentTrend.id)">재시도</button></div>
          <router-link v-for="(book,index) in recommendations" :key="book.id" :to="`/books/${book.isbn}`" class="book-card">
            <div class="book-rank">{{ index + 1 }}</div>
            <img :src="book.cover || placeholder" :alt="book.title">
            <div class="book-copy">
              <strong>{{ book.title }}</strong><small>{{ book.author }}</small>
              <div class="scores"><span>AI {{ Math.round(book.relevanceScore * 100) }}%</span><span>Vector {{ Math.round(book.retrievalScore * 100) }}%</span></div>
              <p>{{ book.reason }}</p>
            </div>
          </router-link>
        </aside>
      </div>
    </template>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useDiscoverStore } from '../stores/discover'

const route=useRoute()
const store=useDiscoverStore()
const {currentTrend,recommendations,loading,recommendationLoading,recommendationStatus,error}=storeToRefs(store)
const {fetchTrendDetail,ensureRecommendations,resetTrendDetail}=store
const placeholder='https://via.placeholder.com/96x140?text=No+Cover'
const labels={TECH_SCIENCE:'테크 & 과학',BUSINESS:'비즈니스',ARTS_CULTURE:'예술 & 문화'}
const categoryLabel=(value)=>labels[value]||value
const formatDate=(value)=>value?new Intl.DateTimeFormat('ko-KR',{dateStyle:'medium',timeStyle:'short'}).format(new Date(value)):'-'
onMounted(async()=>{try{await fetchTrendDetail(route.params.trendId);await ensureRecommendations(route.params.trendId)}catch{/* store state */}})
onBeforeUnmount(resetTrendDetail)
</script>

<style scoped>
.detail-page { max-width: 1180px; margin: auto; padding: 18px var(--space-margin-mobile) 70px; }
@media (min-width: 768px) { .detail-page { padding-left: var(--space-margin-desktop); padding-right: var(--space-margin-desktop); } }

.back { display: inline-block; margin: 12px 0 24px; color: var(--color-on-surface-variant); text-decoration: none; font-weight: 300; }
.back:hover { color: var(--color-primary); }

/* Hero */
.topic-hero {
  background: var(--color-primary);
  border-radius: var(--radius-xl);
  padding: 54px;
  color: var(--color-on-primary);
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.hero-content {
  position: relative;
  z-index: 2;
}

.topic-meta { display: flex; gap: 14px; align-items: center; color: var(--color-primary-fixed-dim); margin-bottom: 24px; }
.topic-meta span { font: 300 2.2rem/1 var(--font-serif); color: var(--color-primary-fixed-dim); }
.topic-meta b {
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: var(--radius-full);
  padding: 6px 14px;
  font-size: .72rem;
  font-weight: 500;
  color: var(--color-primary-fixed-dim);
}

.topic-hero h1 {
  max-width: 900px;
  margin: 20px 0 16px;
  font-family: var(--font-serif);
  font-size: clamp(2rem, 5.2vw, 3.4rem);
  font-weight: 400;
  line-height: 1.25;
  letter-spacing: -0.02em;
}

.topic-hero p { max-width: 820px; color: var(--color-primary-fixed-dim); line-height: 1.8; font-weight: 300; }

.keywords { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 22px; }
.keywords span { font-size: .76rem; color: var(--color-primary-fixed-dim); font-weight: 300; }

/* CSS Aurora Background Effects (Dark Mode Adaption) */
.hero-bg-effects {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}

.glow-sphere {
  position: absolute;
  border-radius: 50%;
  filter: blur(55px);
  opacity: 0.85;
  mix-blend-mode: screen;
}

.glow-1 {
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, rgba(80, 180, 210, 0.75) 0%, rgba(80, 180, 210, 0) 70%);
  top: -120px;
  right: -60px;
}

.glow-2 {
  width: 360px;
  height: 360px;
  background: radial-gradient(circle, rgba(235, 150, 100, 0.65) 0%, rgba(235, 150, 100, 0) 70%);
  bottom: -80px;
  right: 180px;
}

.glow-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(210, 120, 230, 0.6) 0%, rgba(210, 120, 230, 0) 70%);
  top: 40px;
  right: 320px;
}

/* Copyright Note */
.copyright-note {
  display: flex;
  gap: 15px;
  margin: 18px 0 45px;
  padding: 14px 18px;
  background: var(--color-surface-container-low);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-lg);
  color: var(--color-on-surface-variant);
  font-size: .78rem;
  font-weight: 300;
}

.copyright-note strong { font-weight: 400; color: var(--color-on-surface); }

/* Layout */
.content-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(360px, .88fr);
  gap: 34px;
}

.section-title { display: flex; justify-content: space-between; align-items: end; margin-bottom: 17px; }
.section-title small { font: var(--text-label-sm); letter-spacing: var(--ls-label); color: var(--color-primary); text-transform: uppercase; }
.section-title h2 { margin: 5px 0 0; font: 300 1.3rem/1.3 var(--font-headline); color: var(--color-on-surface); }
.section-title > span { color: var(--color-outline); font-size: .72rem; font-weight: 300; }

/* News */
.news-card {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 14px;
  padding: 22px 0;
  border-top: 1px solid rgba(196, 198, 204, 0.2);
}

.news-card.lead {
  padding: 24px;
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-xl);
  margin-bottom: 12px;
}

.news-index { color: var(--color-primary-fixed-dim); font: 300 1.2rem/1 var(--font-headline); }
.news-meta { display: flex; justify-content: space-between; gap: 15px; font-size: .7rem; }
.news-meta b { color: var(--color-primary); font-weight: 600; }
.news-meta time { color: var(--color-outline); }
.news-card h3 { margin: 12px 0 9px; font: 300 1.1rem/1.4 var(--font-body); color: var(--color-on-surface); }
.news-card p { color: var(--color-on-surface-variant); font-size: .88rem; line-height: 1.68; font-weight: 300; }
.news-card a { color: var(--color-primary); font-size: .78rem; font-weight: 400; text-decoration: underline; text-underline-offset: 3px; }

/* Book cards */
.book-column { position: sticky; top: 20px; align-self: start; }

.book-card {
  position: relative;
  display: grid;
  grid-template-columns: 64px 78px 1fr;
  gap: 12px;
  padding: 16px;
  margin-bottom: 10px;
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-xl);
  color: inherit;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.book-card:hover { border-color: var(--color-outline-variant); box-shadow: var(--shadow-card); }
.book-rank { color: var(--color-primary-fixed-dim); font: 300 1.5rem/1 var(--font-headline); }
.book-card img { width: 78px; height: 112px; object-fit: cover; border-radius: var(--radius-md); }

.book-copy { min-width: 0; overflow: hidden; }
.book-copy strong, .book-copy small { display: block; }
.book-copy strong { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; font-size: .92rem; font-weight: 400; line-height: 1.35; }
.book-copy small { margin-top: 5px; color: var(--color-outline); font-size: .7rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.scores { display: flex; gap: 6px; margin-top: 10px; }
.scores span { padding: 4px 7px; background: var(--color-surface-container); border-radius: var(--radius-full); color: var(--color-primary); font-size: .62rem; font-weight: 600; }

.book-copy p { margin: 10px 0 0; color: var(--color-on-surface-variant); font-size: .75rem; line-height: 1.55; font-weight: 300; }

/* States */
.recommend-state {
  display: grid;
  place-items: center;
  min-height: 190px;
  padding: 24px;
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-xl);
  color: var(--color-on-surface-variant);
  text-align: center;
  font-weight: 300;
}

.recommend-state.error-text { color: var(--color-error); }
.recommend-state button { border: 0; border-radius: var(--radius-full); background: var(--color-primary); color: var(--color-on-primary); padding: 9px 16px; font-weight: 400; }

.loader { width: 30px; height: 30px; border: 3px solid var(--color-surface-container-high); border-top-color: var(--color-primary); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.state { padding: 40px; text-align: center; background: var(--color-surface-container-lowest); border: 1px solid rgba(196, 198, 204, 0.2); border-radius: var(--radius-xl); font-weight: 300; color: var(--color-on-surface-variant); }
.error-text { color: var(--color-error); }

@media (max-width: 880px) {
  .content-layout { grid-template-columns: 1fr; }
  .book-column { position: static; }
  .topic-hero { padding: 30px; }
  .copyright-note { align-items: flex-start; flex-direction: column; }
  .book-card { grid-template-columns: 35px 70px 1fr; }
  .book-card img { width: 70px; height: 102px; }
}
</style>
