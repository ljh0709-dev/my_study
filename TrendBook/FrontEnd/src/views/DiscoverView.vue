<template>
  <section class="discover-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <!-- CSS Aurora Background Effects -->
      <div class="hero-bg-effects">
        <div class="glow-sphere glow-1"></div>
        <div class="glow-sphere glow-2"></div>
        <div class="glow-sphere glow-3"></div>
      </div>

      <div class="hero-content">
        <p class="kicker">TREND BOOK DISCOVER</p>
        <h1 class="hero-title">오늘의 <span class="gradient-text-serif">흐름</span>과 함께 읽을 책</h1>
        <p class="intro">테크·비즈니스·예술&amp;문화 세 가지 흐름을 따라, 각 뉴스와 맞닿은 도서를 연결합니다.</p>
        
        <div class="hero-actions">
          <div v-if="weather" class="weather-pill">
            <span class="material-symbols-outlined text-[16px]">{{ weatherIcon(weather.condition) }}</span>
            <strong>{{ weather.location || '현재 위치' }}</strong>
            <span>{{ weather.condition }} · {{ weather.temperature_c }}℃</span>
          </div>
          <div v-if="isStale" class="stale-pill">최신 갱신 대기 중</div>
          <div v-if="refreshMessage" class="refresh-status-pill" :class="{ error: refreshError }">{{ refreshMessage }}</div>
          <button v-if="isAuthenticated" class="refresh-btn" :disabled="refreshing || loading || recommendationLoading" @click="startRefresh">
            <span class="material-symbols-outlined" :class="{ spinning: refreshing }">refresh</span>
            {{ refreshing ? '갱신 중' : '새로고침' }}
          </button>
        </div>
      </div>
    </div>

    <!-- State Cards -->
    <div v-if="!hasLoaded || (loading && !hasTrends)" class="state-card">
      <div class="loader"></div>
      <p>새로운 흐름을 읽고 있습니다.</p>
    </div>
    <div v-else-if="error" class="state-card error">
      <p>{{ error }}</p>
      <button class="primary" @click="fetchTrends">다시 시도</button>
    </div>
    <div v-else-if="!hasTrends" class="state-card">
      <p>공개된 트렌드 캐시가 아직 없습니다.</p>
    </div>

    <!-- Trend list section -->
    <div v-else class="section-list">
      <article v-for="topic in trends" :key="topic.id" class="trend-section">
        <!-- Topic Category Row -->
        <div class="topic-category-row">
          <span class="topic-rank">0{{ topic.rank }}</span>
          <h2 class="topic-label">{{ topic.label }}</h2>
        </div>

        <!-- Topic Header Row -->
        <div class="topic-header-row">
          <!-- Left Column -->
          <div class="topic-title-col">
            <h3 class="topic-subtitle">{{ topic.title }}</h3>
          </div>
          
          <!-- Middle Column -->
          <div class="topic-desc-col">
            <p class="topic-summary-text">{{ topic.summary }}</p>
          </div>
          
          <!-- Right Column -->
          <div class="topic-actions-col">
            <router-link :to="`/discover/${topic.id}`" class="detail-btn">
              <span class="material-symbols-outlined text-[16px]">add</span>
              자세히 보기
            </router-link>
            <div class="topic-tags">
              <span v-for="keyword in topic.keywords" :key="keyword" class="keyword-tag">{{ keyword }}</span>
            </div>
          </div>
        </div>

        <!-- News Grid Section -->
        <div class="news-container">
          <div class="news-grid">
            <article v-for="article in topic.news" :key="article.id" class="news-card">
              <div class="news-meta">
                <span class="news-source">{{ article.source }}</span>
                <span class="news-date">{{ formatDate(article.pubDate) }}</span>

              </div>
              
              <h4 class="news-headline">{{ article.title }}</h4>
              <p class="news-summary">{{ article.summaryPreview }}</p>
              
              <a :href="article.url" target="_blank" rel="noopener noreferrer" class="read-original-link">
                원문 보기
                <span class="material-symbols-outlined">chevron_right</span>
              </a>
              
              <!-- Recommended Book matching design -->
              <div class="news-book-recommendation">
                <template v-if="article.recommendations && article.recommendations.length">
                  <router-link :to="`/books/${article.recommendations[0].isbn}`" class="recommend-book-card">
                    <img 
                      :src="article.recommendations[0].cover || placeholder" 
                      :alt="article.recommendations[0].title" 
                      class="recommend-book-cover"
                      @error="(e) => (e.target.src = placeholder)"
                    />
                    <div class="recommend-book-info">
                      <strong class="recommend-book-title">{{ article.recommendations[0].title }}</strong>
                      <span class="recommend-book-author">{{ article.recommendations[0].author }}</span>
                      
                      <div class="matching-container">
                        <div class="matching-label-row">
                          <span class="matching-label">매칭도</span>
                          <span class="matching-percent">{{ Math.round(article.recommendations[0].relevanceScore * 100) }}%</span>
                        </div>
                        <div class="matching-progress-bar">
                          <div 
                            class="matching-progress-fill" 
                            :style="{ width: Math.round(article.recommendations[0].relevanceScore * 100) + '%' }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </router-link>
                </template>
                <div v-else class="recommend-pending">
                  {{ pendingLabel(topic.recommendation_status) }}
                </div>
              </div>
            </article>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useDiscoverStore } from '../stores/discover'
import { useAuthStore } from '../stores/auth'

const store = useDiscoverStore()
const authStore = useAuthStore()
const {
  trends, weather, loading, recommendationLoading, error, isStale, hasTrends, hasLoaded,
  refreshing, refreshMessage, refreshError,
} = storeToRefs(store)
const { isAuthenticated } = storeToRefs(authStore)
const { fetchTrends, startRefresh, resumeRefresh } = store
const placeholder = 'https://via.placeholder.com/96x140?text=No+Cover'

const formatDate = (value) => (
  value
    ? new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
    : '-'
)

const pendingLabel = (status) => {
  if (status === 'failed') return '추천 생성 실패'
  if (status === 'processing' || status === 'pending') return '추천 생성 중'
  return '추천 대기 중'
}

const weatherIcon = (condition) => {
  if (!condition) return 'wb_sunny'
  const cond = condition.toLowerCase()
  if (cond.includes('cloud') || cond.includes('구름') || cond.includes('흐림') || cond.includes('온흐림')) return 'cloud'
  if (cond.includes('rain') || cond.includes('비')) return 'rainy'
  if (cond.includes('snow') || cond.includes('눈')) return 'ac_unit'
  return 'wb_sunny'
}

onMounted(() => {
  if (isAuthenticated.value) void resumeRefresh()
  void fetchTrends({ preserveCacheOnError: hasTrends.value })
})
</script>

<style scoped>
.discover-page {
  max-width: 1240px;
  margin: auto;
  padding: 24px var(--space-margin-mobile) 80px;
}

@media (min-width: 768px) {
  .discover-page { padding-left: var(--space-margin-desktop); padding-right: var(--space-margin-desktop); }
}

/* Hero Section */
.hero-section {
  display: flex;
  align-items: center;
  background: var(--color-surface-container-lowest);
  border-radius: var(--radius-xl);
  padding: 56px 64px;
  margin-bottom: 56px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(196, 198, 204, 0.15);
  box-shadow: var(--shadow-sm);
}

.hero-content {
  flex: 1;
  max-width: 680px;
  position: relative;
  z-index: 2;
}

.kicker {
  margin: 0 0 12px;
  font: var(--text-label-sm);
  letter-spacing: var(--ls-label);
  color: var(--color-primary);
  text-transform: uppercase;
}

.hero-title {
  max-width: 780px;
  margin: 0 0 16px;
  font-family: var(--font-serif);
  font-size: clamp(2rem, 4.8vw, 3.2rem);
  font-weight: 400;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: var(--color-on-background);
}

.gradient-text-serif {
  color: var(--color-primary);
  font-weight: 700;
  font-style: italic;
}

.intro {
  max-width: 620px;
  margin: 0 0 28px;
  font: 300 16px/1.7 var(--font-body);
  color: var(--color-on-surface-variant);
}

.hero-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.weather-pill,
.stale-pill,
.refresh-status-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: var(--radius-full);
  padding: 8px 16px;
  background: var(--color-surface-container-low);
  color: var(--color-primary);
  font-size: 0.82rem;
  font-weight: 300;
  border: 1px solid rgba(196, 198, 204, 0.3);
}

.stale-pill { background: var(--color-warning-bg); color: var(--color-warning); }
.refresh-status-pill { background: var(--color-surface-container-low); color: var(--color-on-surface-variant); }
.refresh-status-pill.error { background: var(--color-error-container); color: var(--color-error); }

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  border: 1px solid var(--color-outline-variant);
  background: var(--color-surface-container-lowest);
  padding: 8px 16px;
  border-radius: var(--radius-full);
  color: var(--color-on-surface-variant);
  font-weight: 300;
  font-size: 0.82rem;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.refresh-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.refresh-btn:disabled { opacity: .55; }
.spinning { animation: spin .8s linear infinite; }

/* CSS Aurora Background Effects */
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
  filter: blur(50px);
  opacity: 0.85;
  mix-blend-mode: normal;
}

.glow-1 {
  width: 450px;
  height: 450px;
  background: radial-gradient(circle, rgba(120, 155, 185, 0.85) 0%, rgba(120, 155, 185, 0) 75%);
  top: -150px;
  right: -50px;
}

.glow-2 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(220, 180, 140, 0.8) 0%, rgba(220, 180, 140, 0) 75%);
  bottom: -100px;
  right: 120px;
}

.glow-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(140, 190, 155, 0.75) 0%, rgba(140, 190, 155, 0) 75%);
  top: 80px;
  right: 280px;
}

/* Trend sections */
.section-list { display: grid; gap: 56px; }

.trend-section {
  padding: 0 0 32px;
  border-bottom: 1px solid rgba(196, 198, 204, 0.15);
}

.trend-section:last-child {
  border-bottom: none;
}

/* Topic Header Row style */
.topic-header-row {
  display: grid;
  grid-template-columns: 340px 1fr auto;
  gap: 24px;
  align-items: center;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(196, 198, 204, 0.1);
}

.topic-title-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.topic-category-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 14px;
}

.topic-rank {
  font: 400 48px/1 var(--font-headline);
  color: var(--color-primary-fixed-dim);
}

.topic-label {
  font: 600 32px/1 var(--font-headline);
  color: var(--color-primary);
  margin: 0;
  letter-spacing: var(--ls-headline);
  white-space: nowrap;
}

.topic-subtitle {
  font-family: var(--font-serif);
  font-size: 1.22rem;
  font-weight: 700;
  color: var(--color-on-background);
  margin: 0;
  display: inline-block;
  position: relative;
  z-index: 1;
  word-break: keep-all;
}

.topic-subtitle::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 1px;
  width: 100%;
  height: 6px;
  background: rgba(183, 200, 221, 0.45);
  z-index: -1;
  transform: skewX(-12deg);
}

.topic-desc-col {
  font: 300 14px/1.65 var(--font-body);
  color: var(--color-on-surface-variant);
}

.topic-summary-text {
  margin: 0;
}

.topic-actions-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
}

.detail-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--color-primary);
  background: var(--color-primary);
  padding: 8px 16px;
  border-radius: var(--radius-full);
  color: var(--color-on-primary);
  font-size: 0.82rem;
  font-weight: 500;
  text-decoration: none;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.detail-btn:hover {
  background: var(--color-primary-container);
  border-color: var(--color-primary-container);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
  color: var(--color-on-primary);
}

.topic-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.keyword-tag {
  background: var(--color-surface-container-low);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-full);
  padding: 4px 10px;
  font-size: 0.72rem;
  color: var(--color-on-surface-variant);
}

/* News Grid Section */
.news-container {
  margin-top: 24px;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

/* News Card */
.news-card {
  display: flex;
  flex-direction: column;
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.15);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  box-shadow: var(--shadow-sm);
  min-width: 0;
  width: 100%;
}

.news-card:hover {
  border-color: var(--color-outline-variant);
  box-shadow: var(--shadow-md);
}

.news-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  color: var(--color-outline);
  margin-bottom: 12px;
}

.news-source {
  color: var(--color-primary);
  font-weight: 600;
}

.bookmark-btn {
  background: none;
  border: none;
  padding: 0;
  color: var(--color-outline-variant);
  cursor: pointer;
  transition: color var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.bookmark-btn:hover { color: var(--color-primary); }

.bookmark-icon {
  font-size: 16px;
}

.news-headline {
  margin: 0 0 8px;
  font: 600 15px/1.4 var(--font-body);
  color: var(--color-on-background);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 42px;
  word-break: break-all;
  overflow-wrap: anywhere;
}

.news-summary {
  margin: 0 0 14px;
  font: 300 13px/1.6 var(--font-body);
  color: var(--color-on-surface-variant);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 42px;
  word-break: break-all;
  overflow-wrap: anywhere;
}

.read-original-link {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: var(--color-primary);
  font-size: 0.76rem;
  font-weight: 500;
  text-decoration: none;
  margin-bottom: 18px;
  width: fit-content;
  transition: gap var(--transition-fast);
}

.read-original-link:hover {
  gap: 4px;
  text-decoration: underline;
}

.read-original-link .material-symbols-outlined {
  font-size: 14px;
}

/* Recommended book style */
.news-book-recommendation {
  margin-top: auto;
  border-top: 1px solid rgba(196, 198, 204, 0.1);
  padding-top: 16px;
}

.recommend-book-card {
  display: flex;
  gap: 12px;
  background: var(--color-surface-container-low);
  border: 1px solid rgba(196, 198, 204, 0.15);
  border-radius: var(--radius-md);
  padding: 10px;
  text-decoration: none;
  color: inherit;
  transition: border-color var(--transition-fast);
  min-width: 0;
}

.recommend-book-card:hover {
  border-color: var(--color-primary);
}

.recommend-book-cover {
  width: 48px;
  height: 70px;
  object-fit: cover;
  border-radius: var(--radius-xs);
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
}

.recommend-book-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.recommend-book-title {
  font: 600 13px/1.3 var(--font-body);
  color: var(--color-on-surface);
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 2px;
  word-break: break-all;
  overflow-wrap: anywhere;
}

.recommend-book-author {
  font: 300 11px/1.2 var(--font-body);
  color: var(--color-outline);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
  word-break: break-all;
  overflow-wrap: anywhere;
}

.matching-container {
  margin-top: auto;
}

.matching-label-row {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  margin-bottom: 2px;
}

.matching-label {
  color: var(--color-on-surface-variant);
  font-weight: 300;
}

.matching-percent {
  color: var(--color-primary);
  font-weight: 600;
}

.matching-progress-bar {
  height: 4px;
  background: var(--color-surface-container-high);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.matching-progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-full);
}

.recommend-pending {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 92px;
  border: 1px dashed var(--color-outline-variant);
  border-radius: var(--radius-md);
  color: var(--color-outline);
  font-size: 0.82rem;
  font-weight: 300;
}

/* State cards */
.state-card {
  display: grid;
  place-items: center;
  gap: 12px;
  min-height: 330px;
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-lg);
  color: var(--color-on-surface-variant);
  font-weight: 300;
}

.state-card.error { color: var(--color-error); }

.loader {
  width: 34px;
  height: 34px;
  border: 3px solid var(--color-surface-container-high);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 980px) {
  .hero-section {
    padding: 40px 32px;
  }
  
  .glow-1 {
    width: 300px;
    height: 300px;
  }

  .glow-2 {
    width: 250px;
    height: 250px;
  }

  .glow-3 {
    width: 200px;
    height: 200px;
  }

  .topic-header-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .topic-actions-col {
    align-items: flex-start;
  }
  
  .topic-tags {
    justify-content: flex-start;
  }

  .news-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .news-grid {
    grid-template-columns: 1fr;
  }

  .news-card {
    padding: 16px;
  }
}
</style>
