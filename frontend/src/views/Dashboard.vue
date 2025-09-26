<template>
  <div class="min-h-screen bg-slate-50 text-slate-700">
    <!-- Top Nav -->
    <header class="bg-white border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 lg:px-6">
        <div class="flex items-center h-16 gap-4">
          <!-- Brand -->
          <div class="flex items-center gap-3">
            <div class="text-2xl font-black text-slate-800">Krinol</div>
          </div>

          <!-- Right side -->
          <div class="ml-auto flex items-center gap-3">
            <!-- Language + user -->
            <div class="flex items-center gap-2 text-xs">
              <span class="px-2 py-1 rounded bg-slate-100">EN</span>
              <span class="px-2 py-1 rounded bg-slate-100">Hello,</span>
              <span class="font-medium">{{ userStore.user?.email || 'user@example.com' }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main -->
    <main class="max-w-7xl mx-auto px-4 lg:px-6 py-6">
      <!-- Quick actions -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <!-- Resume attachment -->
        <div class="card action-card p-5 flex items-center gap-4" @click="$router.push('/resumes')">
          <div class="h-12 w-12 rounded-2xl bg-sky-100 grid place-items-center text-sky-500 text-xl">▣</div>
          <div>
            <div class="font-semibold">Resume attachment</div>
            <div class="text-xs text-slate-500">Import attachments from email</div>
          </div>
        </div>
        
        <!-- Batch analysis -->
        <div class="card action-card p-5 flex items-center gap-4" @click="$router.push('/analysis')">
          <div class="h-12 w-12 rounded-2xl bg-emerald-100 grid place-items-center text-emerald-500 text-xl">▥</div>
          <div>
            <div class="font-semibold">Batch analysis</div>
            <div class="text-xs text-slate-500">Parse multiple CVs</div>
          </div>
        </div>
      </section>

      <!-- Content grid: table left, charts right -->
      <section class="mt-6 grid grid-cols-12 gap-6">
        <!-- Left: table -->
        <div class="col-span-12 lg:col-span-8">
          <div class="card overflow-hidden">
            <!-- Table header -->
            <div class="bg-slate-100/70 px-4 py-2 text-xs font-semibold text-slate-600">
              Candidates
            </div>
            <div class="overflow-auto scrollbar-thin">
              <table class="w-full text-sm candidates-table">
                <thead>
                  <tr class="bg-slate-50 text-slate-500">
                    <th class="text-left font-medium px-4 py-3">Name</th>
                    <th class="text-left font-medium px-4 py-3">Phone</th>
                    <th class="text-left font-medium px-4 py-3">Company</th>
                    <th class="text-left font-medium px-4 py-3">Position</th>
                    <th class="text-left font-medium px-4 py-3">Location</th>
                    <th class="text-left font-medium px-4 py-3">Working time</th>
                    <th class="text-left font-medium px-4 py-3">CV Score</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <!-- Sample data -->
                  <tr class="hover:bg-slate-50" v-for="candidate in candidates" :key="candidate.id">
                    <td class="px-4 py-3 text-sky-600">{{ candidate.name }}</td>
                    <td class="px-4 py-3">{{ candidate.phone }}</td>
                    <td class="px-4 py-3 truncate">{{ candidate.company }}</td>
                    <td class="px-4 py-3">{{ candidate.position }}</td>
                    <td class="px-4 py-3">{{ candidate.location }}</td>
                    <td class="px-4 py-3">{{ candidate.workingTime }}</td>
                    <td class="px-4 py-3">
                      <span class="score-badge" :class="getScoreClass(candidate.cvScore)">
                        {{ candidate.cvScore }}/100
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Right: charts and side panel -->
        <aside class="col-span-12 lg:col-span-4 space-y-4">
          <!-- Chart 1 -->
          <div class="card p-4">
            <div class="text-sm font-semibold mb-3">Candidate Status Analysis</div>
            <div class="flex items-center gap-4">
              <!-- Donut -->
              <div class="relative h-28 w-28">
                <svg viewBox="0 0 36 36" class="h-28 w-28">
                  <!-- base track -->
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#E5E7EB" stroke-width="7"></circle>
                  <!-- arcs (fake data proportions) -->
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#22c55e" stroke-width="7" stroke-dasharray="22 90" stroke-dashoffset="0"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#f97316" stroke-width="7" stroke-dasharray="15 97" stroke-dashoffset="-22"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#38bdf8" stroke-width="7" stroke-dasharray="18 94" stroke-dashoffset="-37"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#a78bfa" stroke-width="7" stroke-dasharray="10 102" stroke-dashoffset="-55"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#ef4444" stroke-width="7" stroke-dasharray="12 100" stroke-dashoffset="-65"></circle>
                </svg>
                <div class="absolute inset-0 m-auto h-14 w-14 rounded-full bg-white ring-soft"></div>
              </div>
              <!-- Legend -->
              <ul class="text-xs space-y-1">
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> 初步沟通</li>
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-orange-500"></span> 面试安排</li>
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-sky-400"></span> 简历推荐</li>
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-violet-400"></span> Offer</li>
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-red-500"></span> 入职</li>
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-blue-600"></span> 淘汰</li>
              </ul>
            </div>
          </div>

          <!-- Chart 2 -->
          <div class="card p-4">
            <div class="text-sm font-semibold mb-3">Position Status Analysis</div>
            <div class="flex items-center gap-4">
              <div class="relative h-28 w-28">
                <svg viewBox="0 0 36 36" class="h-28 w-28">
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#E5E7EB" stroke-width="7"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#10b981" stroke-width="7" stroke-dasharray="40 72" stroke-dashoffset="0"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#f59e0b" stroke-width="7" stroke-dasharray="25 87" stroke-dashoffset="-40"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#ef4444" stroke-width="7" stroke-dasharray="15 97" stroke-dashoffset="-65"></circle>
                </svg>
                <div class="absolute inset-0 m-auto h-14 w-14 rounded-full bg-white ring-soft"></div>
              </div>
              <ul class="text-xs space-y-1">
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> 已开始</li>
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-amber-500"></span> 进行中</li>
                <li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-rose-500"></span> 已完成</li>
              </ul>
            </div>
          </div>
        </aside>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 示例候选人数据
const candidates = ref([
  {
    id: 1,
    name: 'Rick',
    phone: '156662781098',
    company: '用友软件股份有限公司苏州分公司',
    position: '销售工程师',
    location: '江苏-苏州',
    workingTime: '7',
    cvScore: 85,
    status: 'Deprecated'
  },
  {
    id: 2,
    name: 'Sarah',
    phone: '13812345678',
    company: '腾讯科技（深圳）有限公司',
    position: '前端开发工程师',
    location: '广东-深圳',
    workingTime: '5',
    cvScore: 92,
    status: 'Active'
  },
  {
    id: 3,
    name: 'Mike',
    phone: '13987654321',
    company: '阿里巴巴（中国）有限公司',
    position: '产品经理',
    location: '浙江-杭州',
    workingTime: '8',
    cvScore: 78,
    status: 'Pending'
  },
  {
    id: 4,
    name: 'Lisa',
    phone: '13765432109',
    company: '字节跳动科技有限公司',
    position: 'UI设计师',
    location: '北京-朝阳',
    workingTime: '3',
    cvScore: 88,
    status: 'Active'
  }
])

// 根据分数返回对应的样式类
const getScoreClass = (score) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  return 'score-poor'
}

onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
/* 页面特定样式 - 使用全局组件样式 */

/* 表格特定样式 */
.candidates-table {
  .score-badge {
    @apply px-2 py-1 rounded text-xs font-medium;
    
    &.score-excellent {
      @apply bg-green-100 text-green-800;
    }
    
    &.score-good {
      @apply bg-blue-100 text-blue-800;
    }
    
    &.score-average {
      @apply bg-yellow-100 text-yellow-800;
    }
    
    &.score-poor {
      @apply bg-red-100 text-red-800;
    }
  }
}

/* 图表容器样式 */
.chart-container {
  @apply relative;
  
  .chart-legend {
    @apply text-xs space-y-1;
    
    li {
      @apply flex items-center gap-2;
      
      .legend-dot {
        @apply h-2 w-2 rounded-full;
      }
    }
  }
}

/* 快速操作区域样式 */
.quick-actions {
  .action-card {
    @apply cursor-pointer hover:shadow-lg transition-shadow;
    
    &:hover {
      transform: translateY(-2px);
    }
  }
}
</style>
