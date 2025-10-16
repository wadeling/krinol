// iframe 调试脚本
console.log('=== iframe 调试脚本开始 ===');
console.log('当前页面URL:', window.location.href);
console.log('当前页面标题:', document.title);

// 查找所有 iframe
const iframes = document.querySelectorAll('iframe');
console.log(`主页面找到 ${iframes.length} 个iframe`);

iframes.forEach((iframe, index) => {
    console.log(`iframe[${index}]: name="${iframe.name}", src="${iframe.src}"`);
    
    // 尝试访问 iframe 内容
    try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        if (iframeDoc) {
            console.log(`iframe[${index}] 内容可访问`);
            
            // 分析 iframe 内的结构
            const iframeLis = iframeDoc.querySelectorAll('li');
            console.log(`iframe[${index}] 包含 ${iframeLis.length} 个li元素`);
            
            if (iframeLis.length > 0) {
                console.log('iframe[${index}] 中的li元素:');
                iframeLis.forEach((li, liIndex) => {
                    if (liIndex < 5) {
                        console.log(`  li[${liIndex}]: class="${li.className}", data-v="${li.getAttribute('data-v-b753c1ac') || 'none'}"`);
                    }
                });
            }
            
            // 查找包含"card"的元素
            const cardElements = iframeDoc.querySelectorAll('[class*="card"]');
            console.log(`iframe[${index}] 包含 ${cardElements.length} 个"card"元素`);
            
            // 查找包含"打招呼"的元素
            const allElements = iframeDoc.querySelectorAll('*');
            let foundElements = [];
            allElements.forEach(el => {
                if (el.textContent && el.textContent.includes('打招呼')) {
                    foundElements.push(el);
                }
            });
            console.log(`iframe[${index}] 包含 ${foundElements.length} 个"打招呼"元素`);
            
        } else {
            console.log(`iframe[${index}] 内容无法访问（可能是跨域限制）`);
        }
    } catch (error) {
        console.log(`iframe[${index}] 访问出错: ${error.message}`);
    }
});

// 如果当前页面就是目标页面，直接分析
if (window.location.href.includes('recommend')) {
    console.log('当前页面是推荐页面，分析主文档结构:');
    
    const allLis = document.querySelectorAll('li');
    console.log(`主文档包含 ${allLis.length} 个li元素`);
    
    allLis.forEach((li, index) => {
        if (index < 10) {
            console.log(`li[${index}]: class="${li.className}", data-v="${li.getAttribute('data-v-b753c1ac') || 'none'}"`);
        }
    });
    
    const cardElements = document.querySelectorAll('[class*="card"]');
    console.log(`主文档包含 ${cardElements.length} 个"card"元素`);
    
    const allElements = document.querySelectorAll('*');
    let foundElements = [];
    allElements.forEach(el => {
        if (el.textContent && el.textContent.includes('打招呼')) {
            foundElements.push(el);
        }
    });
    console.log(`主文档包含 ${foundElements.length} 个"打招呼"元素`);
}

console.log('=== iframe 调试脚本结束 ===');
