import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../api/axios'

const wait = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds))

const MIN_SALES_POINT = 1000
const MAX_RECOMMENDATIONS = 5
const DISCOVER_CACHE_KEY = 'trendbook_discover_cache'

const getStorage = () => {
  if (typeof window === 'undefined' || !window.localStorage) return null
  return window.localStorage
}

const normalizeRecommendation = (item) => item && ({
  id: item.id,
  isbn: item.book?.isbn,
  title: item.book?.title,
  author: item.book?.author || '저자 미상',
  cover: item.book?.cover_img,
  salesPoint: Number(item.book?.sales_point || 0),
  reason: item.reason,
  relevanceScore: Number(item.relevance_score || 0),
  retrievalScore: Number(item.retrieval_score || 0),
  embeddingModel: item.embedding_model,
})

const filterRecommendations = (items) => {
  const seenIsbns = new Set()
  const sorted = [...items].sort(
    (left, right) => (right.relevanceScore || 0) - (left.relevanceScore || 0),
  )

  const filtered = []
  for (const item of sorted) {
    if (!item?.isbn || seenIsbns.has(item.isbn)) continue
    if ((item.salesPoint || 0) < MIN_SALES_POINT) continue
    seenIsbns.add(item.isbn)
    filtered.push(item)
    if (filtered.length >= MAX_RECOMMENDATIONS) break
  }
  return filtered
}

const normalizeWeather = (payload) => {
  if (!payload) return null
  const fixes = {
    튼구름: '구름 많음',
    '튼구름 많음': '구름 많음',
    온흐림: '흐림',
    흐린: '흐림',
    '맑은 하늘': '맑음',
    구름조금: '구름 조금',
  }
  const condition = fixes[payload.condition] || payload.condition
  return { ...payload, condition }
}

const createSummaryPreview = (summary = '') => {
  const text = String(summary || '').replace(/\s+/g, ' ').trim()
  if (!text) return ''
  const matches = text.match(/[^.!?。]+(?:[.!?。]+|다\.)/g)
  if (matches?.length) {
    return matches.slice(0, 2).join(' ').trim()
  }
  return text.length > 150 ? `${text.slice(0, 150).trim()}...` : text
}

const getBrowserPosition = () => new Promise((resolve, reject) => {
  if (typeof navigator === 'undefined' || !navigator.geolocation) {
    reject(new Error('Geolocation is not supported.'))
    return
  }
  navigator.geolocation.getCurrentPosition(resolve, reject, {
    enableHighAccuracy: false,
    timeout: 5000,
    maximumAge: 10 * 60 * 1000,
  })
})

const normalizeArticle = (article) => article && ({
  id: article.id,
  title: article.title,
  summary: article.summary,
  summaryPreview: createSummaryPreview(article.summary),
  category: article.category,
  source: article.source,
  url: article.source_url,
  pubDate: article.published_at,
  rank: article.rank,
  isPrimary: article.is_primary,
  recommendations: filterRecommendations(
    (article.recommendations || []).map(normalizeRecommendation).filter(Boolean),
  ),
})

const normalizeTopic = (topic) => ({
  ...topic,
  label: topic.label || topic.category,
  representativeNews: normalizeArticle(topic.representative_news),
  news: (topic.news || []).map(normalizeArticle).filter(Boolean),
})

const readCachedDiscover = () => {
  try {
    const raw = getStorage()?.getItem(DISCOVER_CACHE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const writeCachedDiscover = (payload = {}) => {
  try {
    const results = payload.results || []
    if (!results.length) return
    getStorage()?.setItem(DISCOVER_CACHE_KEY, JSON.stringify({
      results,
      weather: payload.weather || null,
      is_stale: Boolean(payload.is_stale),
      article_recommendation: payload.article_recommendation || null,
      cached_at: new Date().toISOString(),
    }))
  } catch {
    // Cache persistence should never break the Discover page.
  }
}

export const useDiscoverStore = defineStore('discover', () => {
  const trends = ref([])
  const currentTrend = ref(null)
  const weather = ref(null)
  const recommendations = ref([])
  const loading = ref(false)
  const recommendationLoading = ref(false)
  const recommendationStatus = ref('not_started')
  const articleRecommendation = ref(null)
  const error = ref(null)
  const isStale = ref(false)
  const hasLoaded = ref(false)
  const refreshing = ref(false)
  const refreshStatus = ref('idle')
  const refreshMessage = ref('')
  const refreshError = ref(null)

  const restoreCachedTrends = () => {
    const cached = readCachedDiscover()
    if (!cached?.results?.length) return false
    trends.value = cached.results.map(normalizeTopic)
    weather.value = normalizeWeather(cached.weather)
    isStale.value = Boolean(cached.is_stale)
    articleRecommendation.value = cached.article_recommendation || null
    hasLoaded.value = true
    return true
  }

  restoreCachedTrends()

  const hasTrends = computed(() => trends.value.length > 0)
  const hasError = computed(() => Boolean(error.value))

  const needsArticleRecommendations = (topics, recommendationMeta) => {
    const hasMissingBooks = (topics || []).some(
      (topic) => (topic.news || []).some((article) => !article.recommendations.length),
    )
    if (!hasMissingBooks) return false
    const status = recommendationMeta?.status
    return !status || ['failed', 'not_started'].includes(status)
  }

  const pollArticleRecommendationJob = async (jobId) => {
    for (let attempt = 0; attempt < 20; attempt += 1) {
      await wait(1500)
      const { data } = await api.get(`/ai/jobs/${jobId}`)
      articleRecommendation.value = {
        status: data.status,
        job_id: data.job_id,
        error: data.error || null,
      }
      if (data.status === 'completed') return
      if (data.status === 'failed') {
        throw new Error(data.error || '뉴스별 도서 추천 생성에 실패했습니다.')
      }
    }
    throw new Error('추천 생성 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.')
  }

  const ensureArticleRecommendations = async (recommendationMeta) => {
    if (!needsArticleRecommendations(trends.value, recommendationMeta)) {
      if (['pending', 'processing'].includes(recommendationMeta?.status) && recommendationMeta?.job_id) {
        await pollArticleRecommendationJob(recommendationMeta.job_id)
        return true
      }
      return false
    }

    recommendationLoading.value = true
    try {
      const response = await api.post('/trends/article-recommendations/generate')
      articleRecommendation.value = response.data
      if (response.data.status === 'completed') return true
      if (response.data.job_id) {
        await pollArticleRecommendationJob(response.data.job_id)
        return true
      }
      return false
    } finally {
      recommendationLoading.value = false
    }
  }

  const fetchCurrentWeather = async () => {
    try {
      const position = await getBrowserPosition()
      const latitude = position.coords?.latitude
      const longitude = position.coords?.longitude
      if (latitude == null || longitude == null) return
      const { data } = await api.get('/weather/current', {
        params: { lat: latitude, lon: longitude },
      })
      weather.value = normalizeWeather(data)
    } catch {
      // Keep the server-provided fallback weather when geolocation is unavailable.
    }
  }

  const applyRefreshStatus = (payload = {}) => {
    refreshStatus.value = payload.status || 'idle'
    refreshMessage.value = payload.message || ''
    refreshError.value = payload.error || null
  }

  const fetchRefreshStatus = async () => {
    const { data } = await api.get('/trends/refresh/status')
    applyRefreshStatus(data)
    return data
  }

  const fetchTrends = async ({ retryRecommendations = true, preserveCacheOnError = false } = {}) => {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/trends')
      trends.value = (data.results || []).map(normalizeTopic)
      weather.value = normalizeWeather(data.weather)
      void fetchCurrentWeather()
      isStale.value = Boolean(data.is_stale)
      articleRecommendation.value = data.article_recommendation || null
      writeCachedDiscover(data)

      if (retryRecommendations) {
        const shouldRefresh = await ensureArticleRecommendations(data.article_recommendation)
        if (shouldRefresh) {
          const refreshed = await api.get('/trends')
          trends.value = (refreshed.data.results || []).map(normalizeTopic)
          articleRecommendation.value = refreshed.data.article_recommendation || null
          writeCachedDiscover(refreshed.data)
        }
      }
    } catch (requestError) {
      if (!preserveCacheOnError) {
        trends.value = []
        weather.value = null
      }
      const message = requestError.response?.data?.detail || requestError.message || '트렌드를 불러오지 못했습니다.'
      if (preserveCacheOnError && trends.value.length) {
        refreshStatus.value = 'failed'
        refreshError.value = message
        refreshMessage.value = message
      } else {
        error.value = message
      }
    } finally {
      hasLoaded.value = true
      loading.value = false
    }
  }

  const pollRefreshUntilComplete = async () => {
    for (let attempt = 0; attempt < 180; attempt += 1) {
      await wait(2000)
      const data = await fetchRefreshStatus()
      if (data.status === 'completed') {
        refreshing.value = false
        await fetchTrends({ retryRecommendations: false, preserveCacheOnError: true })
        return
      }
      if (data.status === 'failed') {
        refreshing.value = false
        return
      }
    }
    refreshing.value = false
    refreshStatus.value = 'failed'
    refreshError.value = '트렌드 갱신 대기 시간이 초과되었습니다.'
    refreshMessage.value = refreshError.value
  }

  const resumeRefresh = async () => {
    if (refreshing.value) return
    try {
      refreshStatus.value = 'running'
      refreshing.value = true
      const data = await fetchRefreshStatus()
      if (['running', 'processing'].includes(data.status)) {
        await pollRefreshUntilComplete()
      } else {
        refreshing.value = false
        refreshStatus.value = 'idle'
        refreshMessage.value = ''
        refreshError.value = null
      }
    } catch {
      refreshing.value = false
      // Login state or network can be restored independently of cached trends.
    }
  }

  const startRefresh = async () => {
    if (refreshing.value) return
    refreshing.value = true
    refreshStatus.value = 'running'
    refreshMessage.value = '트렌드 갱신을 준비 중입니다.'
    refreshError.value = null
    try {
      const { data } = await api.post('/trends/refresh')
      applyRefreshStatus(data)
      if (data.status === 'completed') {
        refreshing.value = false
        await fetchTrends({ retryRecommendations: false, preserveCacheOnError: true })
        return
      }
      if (data.status === 'failed') {
        refreshing.value = false
        return
      }
      await pollRefreshUntilComplete()
    } catch (requestError) {
      refreshing.value = false
      refreshStatus.value = 'failed'
      refreshError.value = requestError.response?.data?.detail || requestError.message || '트렌드 갱신을 시작하지 못했습니다.'
      refreshMessage.value = refreshError.value
    }
  }

  const fetchTrendDetail = async (trendId) => {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get(`/trends/${trendId}`)
      const relatedArticles = (data.related_news || []).map(normalizeArticle).filter(Boolean)
      currentTrend.value = {
        ...data,
        label: data.label || data.category,
        relatedArticles,
      }
      const topicRecommendations = (data.recommendations || [])
        .map(normalizeRecommendation)
        .filter(Boolean)
      const articleRecommendations = relatedArticles.flatMap(
        (article) => article.recommendations,
      )
      recommendations.value = filterRecommendations(
        topicRecommendations.length ? topicRecommendations : articleRecommendations,
      )
      recommendationStatus.value = data.recommendation_status
      return data
    } catch (requestError) {
      currentTrend.value = null
      error.value = requestError.response?.data?.detail || '트렌드 상세를 불러오지 못했습니다.'
      throw requestError
    } finally {
      loading.value = false
    }
  }

  const pollRecommendationJob = async (jobId) => {
    for (let attempt = 0; attempt < 20; attempt += 1) {
      await wait(1500)
      const { data } = await api.get(`/ai/jobs/${jobId}`)
      recommendationStatus.value = data.status
      if (data.status === 'completed') {
        recommendations.value = filterRecommendations(
          (data.results || []).map(normalizeRecommendation).filter(Boolean),
        )
        return
      }
      if (data.status === 'failed') {
        throw new Error(data.error || 'AI 추천 생성에 실패했습니다.')
      }
    }
    throw new Error('추천 생성 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.')
  }

  const ensureRecommendations = async (trendId) => {
    if (recommendations.value.length) return
    recommendationLoading.value = true
    error.value = null
    try {
      const response = await api.post(`/trends/${trendId}/recommendations/generate`)
      recommendationStatus.value = response.data.status
      if (response.status === 200) {
        recommendations.value = filterRecommendations(
          (response.data.results || []).map(normalizeRecommendation).filter(Boolean),
        )
      } else {
        await pollRecommendationJob(response.data.job_id)
      }
    } catch (requestError) {
      recommendationStatus.value = 'failed'
      error.value = requestError.response?.data?.detail || requestError.message || '추천 생성에 실패했습니다.'
    } finally {
      recommendationLoading.value = false
    }
  }

  const resetTrendDetail = () => {
    currentTrend.value = null
    recommendations.value = []
    recommendationStatus.value = 'not_started'
    error.value = null
  }

  return {
    trends, currentTrend, weather, recommendations, loading,
    recommendationLoading, recommendationStatus, articleRecommendation, error, isStale, hasLoaded,
    refreshing, refreshStatus, refreshMessage, refreshError,
    hasTrends, hasError, fetchTrends, fetchTrendDetail, startRefresh, resumeRefresh,
    fetchRefreshStatus, restoreCachedTrends,
    ensureRecommendations, ensureArticleRecommendations, resetTrendDetail,
  }
})
