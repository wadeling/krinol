// Sidepanel 控制脚本
class ScrapingController {
    constructor() {
        this.isRunning = false;
        this.scrapedCount = 0;
        this.maxCount = 100;
        this.scrapedData = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadStoredData();
    }
    
    initializeElements() {
        this.statusElement = document.getElementById('status');
        this.scrapedCountElement = document.getElementById('scraped-count');
        this.progressFillElement = document.getElementById('progress-fill');
        this.startBtn = document.getElementById('start-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.debugBtn = document.getElementById('debug-btn');
        this.exportBtn = document.getElementById('export-btn');
        this.logElement = document.getElementById('log');
    }
    
    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startScraping());
        this.stopBtn.addEventListener('click', () => this.stopScraping());
        this.debugBtn.addEventListener('click', () => this.debugPage());
        this.exportBtn.addEventListener('click', () => this.exportData());
        
        // 监听来自 content script 的消息
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
        });
    }
    
    async loadStoredData() {
        try {
            const result = await chrome.storage.local.get(['scrapedData', 'scrapedCount']);
            if (result.scrapedData) {
                this.scrapedData = result.scrapedData;
                this.scrapedCount = result.scrapedCount || 0;
                this.updateUI();
            }
        } catch (error) {
            this.log('加载存储数据失败: ' + error.message, 'error');
        }
    }
    
    async saveData() {
        try {
            await chrome.storage.local.set({
                scrapedData: this.scrapedData,
                scrapedCount: this.scrapedCount
            });
        } catch (error) {
            this.log('保存数据失败: ' + error.message, 'error');
        }
    }
    
    handleMessage(message, sender, sendResponse) {
        switch (message.type) {
            case 'SCRAPING_STARTED':
                this.isRunning = true;
                this.updateUI();
                this.log('开始抓取数据...', 'info');
                break;
                
            case 'SCRAPING_STOPPED':
                this.isRunning = false;
                this.updateUI();
                this.log('抓取已停止', 'warning');
                break;
                
            case 'DATA_SCRAPED':
                this.scrapedCount++;
                this.scrapedData.push(message.data);
                this.updateUI();
                this.saveData();
                this.log(`已抓取第 ${this.scrapedCount} 个数据`, 'success');
                break;
                
            case 'SCRAPING_COMPLETED':
                this.isRunning = false;
                this.updateUI();
                this.log(`抓取完成！共抓取 ${this.scrapedCount} 个数据`, 'success');
                break;
                
            case 'SCRAPING_ERROR':
                this.log('抓取错误: ' + message.error, 'error');
                break;
                
            case 'LOG_MESSAGE':
                this.log(message.message, message.level || 'info');
                break;
        }
    }
    
    async startScraping() {
        try {
            // 获取当前活动标签页
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab) {
                this.log('无法获取当前标签页', 'error');
                return;
            }
            
            // 检查 content script 是否已注入
            try {
                const response = await chrome.tabs.sendMessage(tab.id, { type: 'PING' });
                if (response && response.status === 'pong') {
                    this.log('Content script 已就绪', 'info');
                }
            } catch (error) {
                this.log('Content script 未注入，尝试注入...', 'warning');
                // 尝试注入 content script
                try {
                    await chrome.scripting.executeScript({
                        target: { tabId: tab.id },
                        files: ['content.js']
                    });
                    await this.sleep(1000);
                    this.log('Content script 注入成功', 'info');
                } catch (injectError) {
                    this.log('注入失败: ' + injectError.message, 'error');
                    return;
                }
            }
            
            // 向 content script 发送开始抓取的消息
            await chrome.tabs.sendMessage(tab.id, {
                type: 'START_SCRAPING',
                maxCount: this.maxCount
            });
            
            this.log('已发送开始抓取指令', 'info');
            
        } catch (error) {
            this.log('启动抓取失败: ' + error.message, 'error');
            // 尝试重新注入 content script
            try {
                const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['content.js']
                });
                this.log('已重新注入 content script', 'info');
            } catch (injectError) {
                this.log('重新注入失败: ' + injectError.message, 'error');
            }
        }
    }
    
    async stopScraping() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (tab) {
                await chrome.tabs.sendMessage(tab.id, {
                    type: 'STOP_SCRAPING'
                });
            }
            
            this.log('已发送停止抓取指令', 'warning');
            
        } catch (error) {
            this.log('停止抓取失败: ' + error.message, 'error');
        }
    }
    
    updateUI() {
        // 更新状态
        if (this.isRunning) {
            this.statusElement.textContent = '抓取中...';
            this.statusElement.className = 'status-value running';
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
        } else {
            this.statusElement.textContent = this.scrapedCount >= this.maxCount ? '已完成' : '就绪';
            this.statusElement.className = this.scrapedCount >= this.maxCount ? 'status-value completed' : 'status-value';
            this.startBtn.disabled = false;
            this.stopBtn.disabled = true;
        }
        
        // 更新计数
        this.scrapedCountElement.textContent = this.scrapedCount;
        
        // 更新进度条
        const progress = (this.scrapedCount / this.maxCount) * 100;
        this.progressFillElement.style.width = progress + '%';
        
        // 更新导出按钮
        this.exportBtn.disabled = this.scrapedData.length === 0;
    }
    
    log(message, level = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        
        this.logElement.appendChild(logEntry);
        this.logElement.scrollTop = this.logElement.scrollHeight;
        
        // 限制日志条数
        const entries = this.logElement.querySelectorAll('.log-entry');
        if (entries.length > 50) {
            entries[0].remove();
        }
    }
    
    exportData() {
        if (this.scrapedData.length === 0) {
            this.log('没有数据可导出', 'warning');
            return;
        }
        
        try {
            const dataStr = JSON.stringify(this.scrapedData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `resume_data_${new Date().toISOString().slice(0, 10)}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.log(`已导出 ${this.scrapedData.length} 条数据`, 'success');
            
        } catch (error) {
            this.log('导出数据失败: ' + error.message, 'error');
        }
    }
    
    async debugPage() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab) {
                this.log('无法获取当前标签页', 'error');
                return;
            }
            
            this.log('开始调试页面结构...', 'info');
            
            // 注入调试脚本
            await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['debug_iframe.js']
            });
            
            this.log('调试脚本已注入，请查看浏览器控制台获取详细信息', 'info');
            this.log('按F12打开开发者工具，查看Console标签页', 'info');
            
        } catch (error) {
            this.log('调试页面失败: ' + error.message, 'error');
        }
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 初始化控制器
document.addEventListener('DOMContentLoaded', () => {
    new ScrapingController();
});
