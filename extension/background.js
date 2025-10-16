// Background Script - 处理插件的后台逻辑
chrome.runtime.onInstalled.addListener(() => {
    console.log('简历抓取插件已安装');
});

// 处理 sidepanel 的打开
chrome.action.onClicked.addListener(async (tab) => {
    try {
        await chrome.sidePanel.open({ tabId: tab.id });
    } catch (error) {
        console.error('打开 sidepanel 失败:', error);
    }
});

// 处理来自 content script 和 sidepanel 的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Background 收到消息:', message);
    
    switch (message.type) {
        case 'SCRAPING_STARTED':
        case 'SCRAPING_STOPPED':
        case 'SCRAPING_COMPLETED':
        case 'DATA_SCRAPED':
        case 'SCRAPING_ERROR':
        case 'LOG_MESSAGE':
            // 转发消息到 sidepanel
            chrome.runtime.sendMessage(message).catch(error => {
                console.error('转发消息失败:', error);
            });
            break;
            
        default:
            console.log('未知消息类型:', message.type);
    }
    
    return true;
});

// 处理标签页更新
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        console.log('标签页加载完成:', tab.url);
    }
});
