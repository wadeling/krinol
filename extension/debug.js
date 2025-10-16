// 调试脚本 - 用于测试消息传递
console.log('Debug script loaded');

// 监听来自 sidepanel 的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Debug received message:', message);
    
    switch (message.type) {
        case 'PING':
            console.log('Pong!');
            sendResponse({ status: 'pong', timestamp: Date.now() });
            break;
        case 'TEST':
            console.log('Test message received');
            sendResponse({ status: 'test_ok' });
            break;
        default:
            console.log('Unknown message type:', message.type);
    }
    
    return true; // 保持消息通道开放
});

// 发送初始化消息
chrome.runtime.sendMessage({
    type: 'DEBUG_READY',
    message: 'Debug script is ready'
}).catch(error => {
    console.log('Failed to send ready message:', error);
});
