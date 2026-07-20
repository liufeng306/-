/* ============================================
   考研学习网站 - main.js
   ============================================ */

// ========== 词汇点击变色逻辑 ==========

// 词汇等级颜色切换
// 状态机: 未掌握 -> Lv1绿 -> Lv2黄 -> Lv3橙 -> Lv4红 -> 已掌握(灰色)
const VOCAB_STATES = {
  0: { level: 1, color: '#22c55e', label: 'Lv1-认识' },
  1: { level: 2, color: '#eab308', label: 'Lv2-熟悉' },
  2: { level: 3, color: '#f97316', label: 'Lv3-掌握' },
  3: { level: 4, color: '#ef4444', label: 'Lv4-精通' },
  4: { level: 0, color: '#6b7280', label: '已掌握' }
};

function initVocabCards() {
  const vocabCards = document.querySelectorAll('.vocab-card');
  
  vocabCards.forEach(card => {
    card.addEventListener('click', function() {
      const currentState = parseInt(this.dataset.state || '0');
      const nextState = (currentState + 1) % 5;
      
      this.dataset.state = nextState;
      
      // 更新样式
      const stateInfo = VOCAB_STATES[nextState];
      this.style.borderLeftColor = stateInfo.color;
      
      // 更新标签显示
      let labelEl = this.querySelector('.level-badge');
      if (!labelEl) {
        labelEl = document.createElement('span');
        labelEl.className = 'level-badge';
        labelEl.style.cssText = 'position:absolute;top:8px;right:8px;font-size:0.7rem;padding:2px 6px;border-radius:4px;background:rgba(0,0,0,0.3);';
        this.style.position = 'relative';
        this.appendChild(labelEl);
      }
      labelEl.textContent = stateInfo.label;
      labelEl.style.color = stateInfo.color;
      
      // 已掌握状态
      if (nextState === 4) {
        this.classList.add('mastered');
      } else {
        this.classList.remove('mastered');
      }
    });
  });
}

// ========== 词汇搜索功能 ==========
function initVocabSearch() {
  const searchInput = document.getElementById('vocab-search');
  const vocabGrid = document.querySelector('.vocab-grid');
  
  if (!searchInput || !vocabGrid) return;
  
  searchInput.addEventListener('input', function() {
    const query = this.value.toLowerCase().trim();
    const cards = vocabGrid.querySelectorAll('.vocab-card');
    let visibleCount = 0;
    
    cards.forEach(card => {
      const word = card.querySelector('.word').textContent.toLowerCase();
      const meaning = card.querySelector('.meaning').textContent.toLowerCase();
      
      if (word.includes(query) || meaning.includes(query) || query === '') {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });
    
    // 更新计数
    const countEl = document.getElementById('vocab-count');
    if (countEl) {
      countEl.textContent = visibleCount;
    }
  });
}

// ========== 词汇等级筛选 ==========
function initVocabFilter() {
  const filterBtns = document.querySelectorAll('.vocab-filter-btn');
  const vocabGrid = document.querySelector('.vocab-grid');
  
  if (!filterBtns.length || !vocabGrid) return;
  
  filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      // 更新按钮状态
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      const level = this.dataset.level; // '1','2','3','4' 或 'all'
      const cards = vocabGrid.querySelectorAll('.vocab-card');
      
      cards.forEach(card => {
        if (level === 'all') {
          card.style.display = '';
        } else {
          const cardLevel = card.querySelector('.level-badge');
          const cardLevelNum = parseInt(card.dataset.state || '0') + 1;
          card.style.display = cardLevelNum === parseInt(level) ? '' : 'none';
        }
      });
    });
  });
}

// ========== PDF导出（词汇页） ==========
function initVocabExport() {
  const exportBtn = document.getElementById('export-pdf');
  if (!exportBtn) return;
  
  exportBtn.addEventListener('click', function() {
    const vocabGrid = document.querySelector('.vocab-grid');
    if (!vocabGrid) return;
    
    const cards = vocabGrid.querySelectorAll('.vocab-card');
    let content = '考研英语词汇表\n================\n\n';
    let currentLevel = 0;
    
    cards.forEach(card => {
      const word = card.querySelector('.word').textContent;
      const phonetic = card.querySelector('.phonetic').textContent;
      const meaning = card.querySelector('.meaning').textContent;
      const state = parseInt(card.dataset.state || '0');
      const level = VOCAB_STATES[state].label;
      
      if (state !== 4) { // 跳过已掌握的
        content += `[${level}] ${word} ${phonetic}\n  ${meaning}\n\n`;
      }
    });
    
    // 创建下载
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '考研词汇表_' + new Date().toLocaleDateString('zh-CN') + '.txt';
    a.click();
    URL.revokeObjectURL(url);
    
    alert('词汇表已导出！');
  });
}

// ========== 考研计划标签页 ==========
function initPlanTabs() {
  const tabs = document.querySelectorAll('.plan-tab');
  const tables = document.querySelectorAll('.plan-table-wrapper');
  
  if (!tabs.length) return;
  
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      const phase = this.dataset.phase;
      tables.forEach(table => {
        table.style.display = table.dataset.phase === phase ? '' : 'none';
      });
    });
  });
}

// ========== AI聊天功能 ==========
function initAIChat() {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.querySelector('.chat-messages');
  
  if (!chatForm || !chatMessages) return;
  
  chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // 添加用户消息
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    // 添加loading状态
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message ai loading';
    loadingDiv.innerHTML = `
      <div class="sender">AI 助手</div>
      <div class="content">思考中...</div>
    `;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // 调用真正的AI API
    fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
      chatMessages.removeChild(loadingDiv);
      if (data.error) {
        addChatMessage('抱歉，AI暂时无法回答: ' + data.error, 'ai');
      } else {
        addChatMessage(data.response || '...', 'ai');
      }
    })
    .catch(err => {
      chatMessages.removeChild(loadingDiv);
      addChatMessage('网络错误，请稍后重试。', 'ai');
      console.error('Chat error:', err);
    });
  });
  
  function addChatMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}`;
    if (sender === 'ai') {
      const senderDiv = document.createElement('div');
      senderDiv.className = 'sender';
      senderDiv.textContent = 'AI 助手';
      msgDiv.appendChild(senderDiv);
    }
    const contentDiv = document.createElement('div');
    contentDiv.className = 'content';
    contentDiv.textContent = text;
    contentDiv.style.whiteSpace = 'pre-wrap';
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

// ========== 初始化 ==========
document.addEventListener('DOMContentLoaded', function() {
  initVocabCards();
  initVocabSearch();
  initVocabFilter();
  initVocabExport();
  initPlanTabs();
  initAIChat();
});
