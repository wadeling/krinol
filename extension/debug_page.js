// 页面结构调试脚本
console.log('=== 页面结构调试开始 ===');
console.log('当前页面URL:', window.location.href);
console.log('当前页面标题:', document.title);

// 分析页面结构
function analyzePageStructure() {
    console.log('1. 分析所有li元素:');
    const allLis = document.querySelectorAll('li');
    console.log(`总共找到 ${allLis.length} 个li元素`);
    
    allLis.forEach((li, index) => {
        if (index < 10) { // 只显示前10个
            console.log(`li[${index}]: class="${li.className}", data-v="${li.getAttribute('data-v-b753c1ac') || 'none'}"`);
        }
    });
    
    console.log('\n2. 分析所有包含"card"的元素:');
    const cardElements = document.querySelectorAll('[class*="card"]');
    console.log(`找到 ${cardElements.length} 个包含"card"的元素`);
    
    cardElements.forEach((el, index) => {
        if (index < 5) {
            console.log(`card[${index}]: ${el.tagName}.${el.className}`);
        }
    });
    
    console.log('\n3. 分析所有包含"recommend"的元素:');
    const recommendElements = document.querySelectorAll('[id*="recommend"], [class*="recommend"]');
    console.log(`找到 ${recommendElements.length} 个包含"recommend"的元素`);
    
    recommendElements.forEach((el, index) => {
        console.log(`recommend[${index}]: ${el.tagName}#${el.id}.${el.className}`);
    });
    
    console.log('\n4. 分析所有ul元素:');
    const allUls = document.querySelectorAll('ul');
    console.log(`找到 ${allUls.length} 个ul元素`);
    
    allUls.forEach((ul, index) => {
        const lis = ul.querySelectorAll('li');
        console.log(`ul[${index}]: 包含 ${lis.length} 个li元素, class="${ul.className}"`);
    });
    
    console.log('\n5. 查找包含"打招呼"的元素:');
    const allElements = document.querySelectorAll('*');
    let foundElements = [];
    
    allElements.forEach(el => {
        if (el.textContent && el.textContent.includes('打招呼')) {
            foundElements.push(el);
        }
    });
    
    console.log(`找到 ${foundElements.length} 个包含"打招呼"的元素`);
    foundElements.forEach((el, index) => {
        if (index < 5) {
            console.log(`打招呼[${index}]: ${el.tagName}.${el.className} - "${el.textContent.trim()}"`);
        }
    });
    
    console.log('\n=== 页面结构调试结束 ===');
}

// 执行分析
analyzePageStructure();

// 发送分析结果到插件
try {
    chrome.runtime.sendMessage({
        type: 'DEBUG_ANALYSIS',
        message: '页面结构分析完成，请查看控制台'
    });
} catch (error) {
    console.log('无法发送消息到插件:', error);
}
