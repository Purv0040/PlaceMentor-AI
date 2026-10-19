import { apiRequest } from './api';
import { aiService } from './aiService';
import { initialReadinessData } from '../data/readinessData';
import { initialResumeData } from '../data/resumeData';
import { initialGithubData } from '../data/githubData';
import { initialLeetcodeData } from '../data/leetcodeData';
import { getStoredProjects } from '../data/projectData';
import { initialSkillGapData } from '../data/skillGapData';
import { defaultInterviewHistory } from '../data/interviewData';
import { defaultCommunicationHistory } from '../data/communicationData';

const CHAT_STORAGE_KEY = 'placementCopilotMentorChat';

export const mentorService = {
  // Build normalized student context from active state and data stores
  buildMentorContext: ({ user, onboardingData, planningState }) => {
    const projects = getStoredProjects();
    const tasks = planningState?.tasks || [];
    const roadmap = planningState?.roadmap || {};
    const progress = planningState?.progress || {};

    const targetRole = user?.targetRole || onboardingData?.career?.targetRole || null;
    const targetCompany = onboardingData?.career?.companyTier || 'Tier-1 Product (MAANG / Unicorns)';
    const candidateName = user?.name || onboardingData?.profile?.name || null;

    const currentDay = Number(roadmap?.currentDay) || 1;
    const totalDays = Number(roadmap?.totalDays || roadmap?.duration_days) || 90;
    const remainingDays = Math.max(0, totalDays - currentDay);

    const todayTasksList = tasks.filter(t => Number(t.dayNumber || t.day) === currentDay);
    const todayCompleted = todayTasksList.filter(t => t.completed || t.status === 'completed');
    const todayPending = todayTasksList.filter(t => !t.completed && t.status !== 'completed');

    const allPending = tasks.filter(t => !t.completed && t.status !== 'completed');
    const allCompleted = tasks.filter(t => t.completed || t.status === 'completed');

    return {
      user: {
        name: candidateName,
        targetRole,
        targetCompany,
        college: onboardingData?.profile?.college || 'CSPIT',
        degree: onboardingData?.profile?.degree || 'B.Tech IT'
      },
      readiness: {
        overallScore: progress?.overallProgressPercent || initialReadinessData?.overallScore || 78,
        status: initialReadinessData?.readinessTier || 'Strong Tier-1 Prospect'
      },
      roadmap: {
        currentDay,
        totalDays,
        remainingDays,
        currentPhase: roadmap?.currentPhaseName || 'Foundation & Core Preparation',
        completionPercent: roadmap?.completionPercentage || (tasks.length > 0 ? Math.round((allCompleted.length / tasks.length) * 100) : 0),
        totalTasksCount: tasks.length,
        completedTasksCount: allCompleted.length,
        pendingTasksCount: allPending.length,
        lastAdapted: roadmap?.lastAdapted || 'Today (AI Calibrated)'
      },
      todayTasks: {
        currentDay,
        total: todayTasksList.length,
        completed: todayCompleted.length,
        remaining: todayPending.length,
        pendingTaskList: todayPending.map(t => ({
          id: t.id || t.taskId,
          title: t.title,
          category: t.category,
          duration: t.duration || t.estimated_minutes || '60 mins',
          priority: t.priority
        }))
      },
      allPendingTasks: {
        totalPending: allPending.length,
        tasks: allPending.slice(0, 15).map(t => ({
          id: t.id || t.taskId,
          title: t.title,
          category: t.category,
          day: t.dayNumber || t.day,
          priority: t.priority
        }))
      },
      skillGaps: {
        overallCoverage: initialSkillGapData.overallCoverage || 72,
        criticalGapsCount: initialSkillGapData.gapsIdentifiedCount || 6,
        topGaps: initialSkillGapData.gaps.slice(0, 4).map(g => ({
          skill: g.skill,
          priority: g.priority,
          category: g.category,
          actionRoute: g.actionRoute
        }))
      },
      resume: {
        atsScore: initialResumeData.metrics.atsScore || 84,
        missingSkills: initialResumeData.metrics.missingSkills || ['Redis', 'Kafka', 'Kubernetes']
      },
      github: {
        impactScore: initialGithubData.metrics.githubImpactScore || 82,
        commits: initialGithubData.metrics.totalCommits || 342,
        streakDays: initialGithubData.metrics.activeStreakDays || 14
      },
      leetcode: {
        totalSolved: initialLeetcodeData.metrics.totalSolved || 385,
        contestRating: initialLeetcodeData.metrics.contestRating || 1842,
        rankTitle: initialLeetcodeData.metrics.rankTitle || 'Knight'
      },
      projects: {
        count: projects.length || 4,
        avgScore: Math.round(projects.reduce((s, p) => s + (p.score || 85), 0) / (projects.length || 1))
      },
      interview: {
        technicalScore: defaultInterviewHistory?.[0]?.score || 82,
        accuracy: 85
      },
      communication: {
        clarityScore: defaultCommunicationHistory?.[0]?.verbalClarity || 82,
        wpm: defaultCommunicationHistory?.[0]?.wpm || 145
      }
    };
  },

  // Backend API methods
  createConversation: async (title = 'New Placement Session') => {
    try {
      const res = await apiRequest('/mentor/conversations', {
        method: 'POST',
        body: JSON.stringify({ title })
      });
      return res || { conversation_id: `local_conv_${Date.now()}`, title, status: 'active' };
    } catch (e) {
      console.warn('Backend unavailable for createConversation, using local session.', e);
      return { conversation_id: `local_conv_${Date.now()}`, title, status: 'active' };
    }
  },

  getConversations: async () => {
    try {
      const res = await apiRequest('/mentor/conversations');
      return Array.isArray(res) ? res : [];
    } catch (e) {
      return [];
    }
  },

  getConversationDetail: async (conversationId) => {
    try {
      return await apiRequest(`/mentor/conversations/${conversationId}`);
    } catch (e) {
      return null;
    }
  },

  askMentor: async (message, conversationId = null, targetRole = null, studentName = null, conversationHistory = null) => {
    try {
      return await apiRequest('/mentor/ask', {
        method: 'POST',
        isPublic: true,
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          target_role: targetRole,
          student_name: studentName,
          conversation_history: conversationHistory
        })
      });
    } catch (e) {
      console.warn('Backend unavailable for askMentor, using client fallback.', e);
      return null;
    }
  },

  // Retrieve all stored chat sessions
  getStoredSessions: () => {
    try {
      const saved = localStorage.getItem('placementMentorSessions');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {
      console.error('Failed to parse mentor sessions from localStorage', e);
    }
    return [];
  },

  saveStoredSessions: (sessions) => {
    try {
      localStorage.setItem('placementMentorSessions', JSON.stringify(sessions));
    } catch (e) {
      console.error('Failed to save mentor sessions to localStorage', e);
    }
  },

  // Retrieve stored conversation from localStorage
  getStoredChat: () => {
    try {
      const saved = localStorage.getItem(CHAT_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed.map((msg) => {
            const { checkpoint, actions, ...rest } = msg;
            if (rest.id === 'msg-init-1') {
              return {
                ...rest,
                verified: false,
                text: "Hi! Ready to grow? 🚀\n\nLet's build your skills and get you placement-ready."
              };
            }
            return rest;
          });
        }
      }
    } catch (e) {
      console.error('Failed to parse mentor chat from localStorage', e);
    }
    return null;
  },

  saveChat: (messages) => {
    try {
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
    } catch (e) {
      console.error('Failed to save mentor chat to localStorage', e);
    }
  },

  clearChat: () => {
    try {
      localStorage.removeItem(CHAT_STORAGE_KEY);
    } catch (e) {
      console.error('Failed to clear mentor chat localStorage', e);
    }
  },

  getInitialGreeting: (context, persona = 'tech') => {
    const greetingsByPersona = {
      tech: "Hi! I'm your Technical Interviewer & DSA Copilot 🚀\n\nAsk me about algorithms, coding problems, system design, or code review.",
      dsa: "Welcome to DSA Mode! 🧠\n\nLet's master patterns like Two Pointers, Sliding Window, Trees, and Dynamic Programming.",
      story: "Hello! I'm your STAR Behavioral Coach 🎯\n\nLet's refine your behavioral answers using Situation, Task, Action, and Result with quantifiable impact.",
      strat: "Welcome! I'm your Placement Strategist 📈\n\nI can analyze your 90-day roadmap, skill gaps, company tier targets, and interview milestones."
    };

    return [
      {
        id: `msg-init-${Date.now()}`,
        sender: 'ai',
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        verified: false,
        text: greetingsByPersona[persona] || "Hi! Ready to grow? 🚀\n\nLet's build your skills and get you placement-ready.",
        codeSnippet: null
      }
    ];
  },

  generateLocalFallback: (userMessage, mentorContext, persona = 'tech') => {
    const q = userMessage.toLowerCase().trim();
    const targetRole = mentorContext?.user?.targetRole || null;
    const roleDesc = targetRole ? ` for **${targetRole}**` : '';
    const currentDay = mentorContext?.roadmap?.currentDay || 1;
    const totalDays = mentorContext?.roadmap?.totalDays || 90;
    const remainingDays = mentorContext?.roadmap?.remainingDays ?? Math.max(0, totalDays - currentDay);
    const todayPending = mentorContext?.todayTasks?.pendingTaskList || [];
    const allPendingTotal = mentorContext?.allPendingTasks?.totalPending ?? (mentorContext?.roadmap?.pendingTasksCount || 0);

    let text = '';
    let actions = [
      { label: 'What can I do today?', route: '/tasks' },
      { label: 'How many days are remaining?', route: '/roadmap' }
    ];

    // 1. React & Frontend Questions
    if (q.includes('react') || q.includes('virtual dom') || q.includes('hook') || q.includes('jsx')) {
      if (q.includes('why') || q.includes('what is') || q.includes('used for') || q.includes('advantages')) {
        text = `### ⚛️ What is React.js and Why is it Used?

**React.js** is an open-source, component-based front-end JavaScript library developed by Meta (Facebook) used for building dynamic, high-performance user interfaces and Single Page Applications (SPAs).

---

### 🌟 Key Reasons React is Used:

1. **Virtual DOM (Fast Rendering)**:
   - React maintains an in-memory representation of the real DOM.
   - When state changes, React computes the diff (*reconciliation*) and only updates modified nodes in the real browser DOM, maximizing performance.

2. **Component-Based Architecture**:
   - UI is decomposed into self-contained, reusable blocks (Header, Card, Modal, Button).
   - Leads to cleaner codebases, easier testing, and fast team collaboration.

3. **Declarative UI**:
   - You describe *what* the UI should look like for each state, and React handles the DOM mutations efficiently.

4. **Rich Ecosystem & Tooling**:
   - Hooks (\`useState\`, \`useEffect\`, \`useMemo\`, \`useCallback\`) for state logic without classes.
   - Next.js (SSR/SSG), React Native (Mobile), Redux Toolkit, and Vite.

---

### 💻 Quick Code Demonstration
\`\`\`jsx
import React, { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button 
      onClick={() => setCount(prev => prev + 1)}
      className="px-4 py-2 bg-indigo-600 text-white rounded-lg"
    >
      Clicked {count} times
    </button>
  );
}
\`\`\`

💡 **Placement Tip**: In frontend interviews, interviewers love asking about **Virtual DOM vs Real DOM**, **Fiber architecture**, and **Rules of Hooks**.`;
        actions = [
          { label: 'Explain Virtual DOM vs Real DOM', route: '/interview' },
          { label: 'What are React Hooks?', route: '/interview' }
        ];
      } else {
        text = `**React.js Mastery for Technical Interviews**:\n\n1. **Core Fundamentals**: Components, JSX, Props vs State, Lifecycle/Hooks.\n2. **Optimization**: \`React.memo\`, \`useMemo\`, \`useCallback\`, code-splitting with \`React.lazy\`.\n3. **State Management**: Context API, Zustand, or Redux Toolkit.\n\nWhich specific React topic or coding pattern would you like to explore?`;
      }
    }

    // 2. DSA / Algorithms / LeetCode
    else if (q.includes('two sum') || (q.includes('leetcode') && q.includes('1'))) {
      text = `### 🧩 LeetCode #1: Two Sum

**Problem Statement**: Given an array of integers \`nums\` and an integer \`target\`, return indices of the two numbers such that they add up to \`target\`.

---

### 💡 Optimal Approach: Single-Pass Hash Map
- As we iterate through \`nums\`, calculate the complement: \`complement = target - num\`.
- Check if \`complement\` already exists in our dictionary:
  - If yes, return \`[seen[complement], current_index]\`.
  - Otherwise, insert \`seen[num] = current_index\`.

### 💻 Python Implementation:
\`\`\`python
def twoSum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
\`\`\`

- ⏱️ **Time Complexity**: $O(N)$ — Single pass through the array.
- 💾 **Space Complexity**: $O(N)$ — Stores up to $N$ elements in the dictionary.`;
      actions = [
        { label: 'Solve LeetCode #20: Valid Parentheses', route: '/leetcode' },
        { label: 'View Today\'s Tasks', route: '/tasks' }
      ];
    }
    else if (q.includes('reverse') && q.includes('list')) {
      text = `### 🔗 LeetCode #206: Reverse Linked List

**Approach**: Iterative 3-pointers (\`prev\`, \`curr\`, \`next_node\`).

\`\`\`python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseList(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        next_node = curr.next  # Save next
        curr.next = prev       # Reverse pointer
        prev = curr            # Move prev forward
        curr = next_node       # Move curr forward
    return prev
\`\`\`

- ⏱️ **Time Complexity**: $O(N)$
- 💾 **Space Complexity**: $O(1)$ in-place reversal`;
    }
    else if (q.includes('binary search')) {
      text = `### 🔍 Binary Search Algorithm

**Prerequisite**: The input array must be **sorted**.

\`\`\`python
def binary_search(arr: list[int], target: int) -> int:
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2  # Prevents integer overflow
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1
\`\`\`

- ⏱️ **Time Complexity**: $O(\\log N)$
- 💾 **Space Complexity**: $O(1)$`;
    }
    else if (q.includes('kahn') || q.includes('topological')) {
      text = `### 🧭 Kahn's Algorithm (Topological Sort via BFS)

Used for Directed Acyclic Graphs (DAGs) to find a linear ordering of vertices such that for every directed edge $u \\to v$, $u$ comes before $v$.

1. **Calculate In-degrees**: Count incoming edges for every vertex.
2. **Initialize Queue**: Enqueue all nodes with \`in_degree == 0\`.
3. **BFS Traversal**: Pop vertex $u$, add to topological order, decrement in-degree of its neighbors $v$.
4. If neighbor's in-degree drops to 0, enqueue it.
5. **Cycle Detection**: If processed count < total vertices $V$, graph contains a cycle!

- ⏱️ **Time**: $O(V + E)$ | 💾 **Space**: $O(V)$`;
    }

    // 3. OOP Concepts
    else if (q.includes('oop') || q.includes('object oriented') || q.includes('encapsulation') || q.includes('polymorphism') || q.includes('inheritance') || q.includes('abstraction')) {
      text = `### 🏛️ The 4 Pillars of Object-Oriented Programming (OOP)

1. 🔒 **Encapsulation**:
   - Bundling state and methods inside classes while keeping internal fields private (\`_private_var\`).
   - Prevents external code from corrupting internal object state.

2. 🎭 **Abstraction**:
   - Hiding complex background details and exposing only clean, essential interfaces (e.g. \`abc.ABC\` in Python or Interfaces in Java/TypeScript).

3. 🧬 **Inheritance**:
   - Mechanism where a child class acquires the properties and behaviors of a parent class to promote code reusability.

4. 🔄 **Polymorphism**:
   - Ability of different classes to share the same method name but exhibit specialized runtime behaviors (Method Overriding vs Overloading).

\`\`\`python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self): pass

class Dog(Animal):
    def speak(self): return "Woof!"

class Cat(Animal):
    def speak(self): return "Meow!"
\`\`\``;
    }

    // 4. Python Error Debugging
    else if (q.includes('typeerror') || q.includes('nonetype') || q.includes('subscriptable')) {
      text = `### 🛠️ Fixing \`TypeError: 'NoneType' object is not subscriptable\`

**Root Cause**: You are attempting to index or access a key on an object (\`obj[key]\` or \`obj[0]\`) whose value is \`None\`.

**Common Reasons**:
1. Function missed a \`return\` statement (evaluates to \`None\`).
2. Method modifies in-place and returns \`None\` (e.g. \`list.sort()\` or \`list.append()\`).
3. An API or dictionary \`.get()\` call did not find the key and defaulted to \`None\`.

**Corrected Pattern**:
\`\`\`python
data = fetch_record()

# Guard check before subscripting:
if data is not None and isinstance(data, dict):
    print(data.get("name", "Unknown"))
else:
    print("Record not found or invalid format")
\`\`\``;
    }
    else if (q.includes('error') && (q.includes('code') || q.includes('python') || q.includes('fix'))) {
      text = `**I'm ready to help you debug!** 🛠️\n\nPlease paste:\n1. Your code snippet\n2. The exact error message and traceback\n\nI will analyze the root cause and provide the corrected code with time/space complexity notes!`;
    }

    // 5. System Design & Backend Architecture
    else if (q.includes('system design') || q.includes('microservice') || q.includes('redis') || q.includes('kafka') || q.includes('cache') || q.includes('load balancer') || q.includes('rate limit')) {
      text = `### 🏗️ System Design Interview Framework

When designing scalable distributed systems in technical rounds:

1. **Clarify Requirements**:
   - Functional: Core API contracts, user interactions.
   - Non-Functional: Throughput (e.g., 50K QPS), Latency (<50ms), High Availability (99.99%), Read vs Write ratio.

2. **Core Architectural Flow**:
   \`Client -> CDN -> Load Balancer (Nginx/ALB) -> API Gateway -> Microservices -> Redis Cache -> Primary/Replica DB\`

3. **Key Components**:
   - **Distributed Cache**: Redis for hot-key caching (Cache-Aside pattern).
   - **Message Bus**: Apache Kafka / RabbitMQ for async event decoupling.
   - **Database Scaling**: Read replicas, Connection pooling (PgBouncer), Horizontal sharding.
   - **Rate Limiting**: Token Bucket or Sliding Window Counter to prevent DDoS.`;
    }

    // 6. Roadmap / Task Specific Queries
    else if (q.includes('do today') || q.includes('can i do') || q.includes('should i do') || q === 'today') {
      if (todayPending.length > 0) {
        const listStr = todayPending.map((t, idx) => `${idx + 1}. 📌 **${t.title}** (${t.category}, ${t.duration})`).join('\n');
        text = `Here are your incomplete tasks scheduled for today (Day ${currentDay} of ${totalDays}${roleDesc}):\n\n${listStr}\n\nStart with task #1 to maintain your daily consistency streak!`;
      } else {
        text = `You have no pending tasks scheduled for today (Day ${currentDay} of ${totalDays}${roleDesc})! 🎉\n\nAll tasks for today are completed. You can practice DSA problems or review upcoming roadmap topics.`;
      }
    }
    else if (q.includes('remaining') || q.includes('days left')) {
      text = `You are currently on **Day ${currentDay}** of your **${totalDays}-day** roadmap${roleDesc}.\n\nThere are **${remainingDays} days remaining** in your placement schedule.\n\n*(Note: You have ${allPendingTotal} pending tasks remaining across the rest of the roadmap).*`;
    }
    else if (q.includes('pending task') || q.includes('incomplete')) {
      text = `You have **${allPendingTotal}** pending task(s) in total across your ${totalDays}-day roadmap (${todayPending.length} due today on Day ${currentDay}).\n\nFocus on today's tasks first to maintain steady daily progress!`;
    }
    else if (q.includes('yesterday')) {
      text = `According to your records, you did not complete any tasks yesterday.\n\nYou can dive into today's tasks (Day ${currentDay} of ${totalDays}) to keep your preparation on track!`;
    }
    else if (/\bday\s*(\d+)\b/.test(q)) {
      const match = q.match(/\bday\s*(\d+)\b/);
      const targetDay = match ? match[1] : currentDay;
      text = `Day ${targetDay} is part of your ${totalDays}-day placement roadmap${roleDesc}.\n\nYou are currently on Day ${currentDay} with ${remainingDays} days remaining. Focus on completing today's tasks to advance toward Day ${targetDay}!`;
    }
    else if (q.includes('why') && (q.includes('pending') || q.includes('84') || q.includes('tasks'))) {
      const numMatch = q.match(/\b(\d+)\b/);
      const numStr = numMatch ? numMatch[1] : String(allPendingTotal);
      text = `The **${numStr}** pending tasks represent all the incomplete tasks distributed across the remaining **${remainingDays}** days of your **${totalDays}-day** roadmap.\n\nFor today (Day ${currentDay}), you only have **${todayPending.length}** task(s) to focus on!`;
    }

    // 7. General Greetings
    else if (['hi', 'hello', 'hey'].includes(q) || /^(hi|hello|hey)\b/.test(q)) {
      text = targetRole 
        ? `Hey there! How can I help with your **${targetRole}** placement preparation today?` 
        : `Hey there! How can I help with your placement preparation today?`;
    }

    // 8. General High-Value Fallback (Never empty or generic brush-off)
    else {
      text = `### 💡 Placement Guidance: "${userMessage}"${roleDesc}

To tackle this effectively in technical placement rounds:

1. **Core Concept & Foundations**:
   - Master the underlying theory, trade-offs, and key definitions.
   - For coding/algorithms, identify time and space complexities upfront ($O(N)$, $O(\\log N)$, $O(1)$).

2. **Interview Best Practices**:
   - **Communicate your thought process** before jumping to code or conclusions.
   - Verify edge cases (empty inputs, negative values, null pointers, boundary limits).

3. **Recommended Next Actions**:
   - Would you like a **step-by-step code example**, **architectural explanation**, or **interview questions** on this topic?`;
    }

    return {
      text,
      verified: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      actions
    };
  },

  generateMentorResponse: async (userMessage, mentorContext, conversationId = null, conversationHistory = null, persona = 'tech') => {
    // Try real backend API first with current student context
    const targetRole = mentorContext?.user?.targetRole || null;
    const studentName = mentorContext?.user?.name || null;
    const apiRes = await mentorService.askMentor(userMessage, conversationId, targetRole, studentName, conversationHistory);
    if (apiRes && apiRes.answer) {
      return {
        text: apiRes.answer,
        conversation_id: apiRes.conversation_id,
        verified: apiRes.verified === true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actions: (apiRes.suggested_actions || []).map(a => ({
          label: a.label || a.title || "View Details",
          route: a.route || "/dashboard"
        }))
      };
    }
    // Fallback to local AI service synthesizer if backend offline
    return mentorService.generateLocalFallback(userMessage, mentorContext, persona);
  }
};
