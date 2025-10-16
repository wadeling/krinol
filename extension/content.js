// Content Script - 处理页面抓取逻辑
class ResumeScraper {
    constructor() {
        this.isRunning = false;
        this.scrapedCount = 0;
        this.maxCount = 100;
        this.scrapedData = [];
        this.currentIndex = 0;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.processedItems = new Set(); // 跟踪已处理的简历项
        
        this.initializeMessageListener();
    }
    
    initializeMessageListener() {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
        });
    }
    
    handleMessage(message, sender, sendResponse) {
        switch (message.type) {
            case 'PING':
                sendResponse({ status: 'pong' });
                break;
            case 'START_SCRAPING':
                this.startScraping(message.maxCount);
                break;
            case 'STOP_SCRAPING':
                this.stopScraping();
                break;
        }
    }
    
    async startScraping(maxCount = 100) {
        if (this.isRunning) {
            this.log('抓取已在进行中', 'warning');
            return;
        }
        
        this.isRunning = true;
        this.maxCount = maxCount;
        this.scrapedCount = 0;
        this.scrapedData = [];
        this.currentIndex = 0;
        this.retryCount = 0;
        
        this.log('开始抓取简历数据...', 'info');
        this.notifySidepanel('SCRAPING_STARTED');
        
        try {
            await this.waitForPageLoad();
            await this.findAndProcessItems();
        } catch (error) {
            this.log('抓取过程中发生错误: ' + error.message, 'error');
            this.notifySidepanel('SCRAPING_ERROR', { error: error.message });
        }
    }
    
    stopScraping() {
        this.isRunning = false;
        this.log('抓取已停止', 'warning');
        this.notifySidepanel('SCRAPING_STOPPED');
    }
    
    async waitForPageLoad() {
        return new Promise((resolve) => {
            if (document.readyState === 'complete') {
                resolve();
            } else {
                window.addEventListener('load', resolve);
            }
        });
    }
    
    async findAndProcessItems() {
        while (this.isRunning && this.scrapedCount < this.maxCount) {
            try {
                // 查找目标 iframe
                const iframe = await this.findTargetIframe();
                if (!iframe) {
                    this.log('未找到目标 iframe，等待页面加载...', 'warning');
                    await this.sleep(2000);
                    continue;
                }
                
                // 获取 iframe 内的文档
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (!iframeDoc) {
                    this.log('无法访问 iframe 内容，可能是跨域限制', 'error');
                    break;
                }
                
                // 查找简历列表
                const resumeList = await this.findResumeList(iframeDoc);
                if (!resumeList) {
                    this.log('未找到简历列表，等待页面加载...', 'warning');
                    await this.sleep(2000);
                    continue;
                }
                
                // 处理当前批次的简历项
                const hasScrolled = await this.processResumeItems(iframeDoc, resumeList, iframe);
                
                // 检查是否还需要继续
                if (!this.isRunning || this.scrapedCount >= this.maxCount) {
                    break;
                }
                
                // 如果发生了滚动，立即继续下一轮处理（不需要等待）
                if (hasScrolled) {
                    this.log('滚动完成，立即继续处理新内容...', 'info');
                    continue; // 立即开始下一轮循环
                }
                
                // 如果没有滚动，等待一下再继续下一轮
                this.log('等待3秒后继续下一轮处理...', 'info');
                await this.sleep(3000);
                
            } catch (error) {
                this.log('处理简历项时发生错误: ' + error.message, 'error');
                this.retryCount++;
                
                if (this.retryCount >= this.maxRetries) {
                    this.log('重试次数过多，停止抓取', 'error');
                    break;
                }
                
                await this.sleep(3000);
            }
        }
        
        if (this.isRunning) {
            this.isRunning = false;
            this.log(`抓取完成！共抓取 ${this.scrapedCount} 个数据`, 'success');
            this.notifySidepanel('SCRAPING_COMPLETED');
        }
    }
    
    async findTargetIframe() {
        // 查找包含 recommendFrame 的 iframe
        const iframes = document.querySelectorAll('iframe');
        this.log(`找到 ${iframes.length} 个iframe`, 'info');
        
        for (const iframe of iframes) {
            this.log(`检查iframe: name="${iframe.name}", src="${iframe.src}"`, 'info');
            
            if (iframe.name === 'recommendFrame' || 
                iframe.src.includes('/web/frame/recommend/') ||
                iframe.src.includes('zhipin.com/web/chat/recommend') ||
                iframe.src.includes('recommend')) {
                this.log(`找到目标iframe: ${iframe.src}`, 'info');
                return iframe;
            }
        }
        
        // 如果没有找到 iframe，可能页面直接加载在主页面上
        // 检查当前页面是否是目标页面
        if (window.location.href.includes('zhipin.com/web/chat/recommend')) {
            this.log('当前页面是目标页面，使用主文档', 'info');
            return { contentDocument: document, contentWindow: window };
        }
        
        this.log('未找到目标iframe', 'error');
        return null;
    }
    
    async findResumeList(iframeDoc) {
        // 根据图片中的实际DOM结构查找简历列表
        const selectors = [
            'ul.card-list',                    // 从图片看到的结构
            'ul[class*="card-list"]',          // 包含card-list的ul
            'ul[data-v-b753c1ac]',            // 有特定data-v属性的ul
            '#recommend-list .list-body ul',   // 原始选择器
            '#recommend-list ul',
            '.recommend-list-wrap ul',
            '.card-list-wrap ul',
            '[id="recommend-list"] ul',
            '#recommend-list',
            '.recommend-list-wrap',
            '.card-list-wrap',
            '[id*="recommend"]',
            'ul'
        ];
        
        for (const selector of selectors) {
            const element = iframeDoc.querySelector(selector);
            if (element) {
                this.log(`找到简历列表: ${selector}`, 'info');
                
                // 检查这个元素是否包含简历项
                const testItems = element.querySelectorAll('li.card-item, li[class*="card-item"]');
                if (testItems.length > 0) {
                    this.log(`该容器包含 ${testItems.length} 个card-item元素`, 'info');
                    return element;
                }
                
                // 也检查普通的li元素
                const allLis = element.querySelectorAll('li');
                if (allLis.length > 0) {
                    this.log(`该容器包含 ${allLis.length} 个li元素`, 'info');
                    return element;
                }
            }
        }
        
        // 如果没找到，尝试查找包含 card-item 的容器
        const cardItems = iframeDoc.querySelectorAll('li.card-item, li[class*="card-item"], li[data-v-b753c1ac]');
        if (cardItems.length > 0) {
            this.log(`找到 ${cardItems.length} 个简历卡片`, 'info');
            return cardItems[0].parentElement;
        }
        
        // 最后尝试：查找任何包含多个li元素的容器
        const allContainers = iframeDoc.querySelectorAll('div, ul, section');
        for (const container of allContainers) {
            const lis = container.querySelectorAll('li');
            if (lis.length >= 3) { // 假设至少有3个简历项
                this.log(`找到包含 ${lis.length} 个li元素的容器: ${container.tagName}`, 'info');
                return container;
            }
        }
        
        this.log('未找到简历列表容器', 'error');
        return null;
    }
    
    async processResumeItems(iframeDoc, resumeList, iframe) {
        // 根据图片中的实际DOM结构查找简历项
        const selectors = [
            'li.card-item',                    // 从图片看到的结构
            'li[class*="card-item"]',          // 包含card-item的li
            'li[data-v-b753c1ac]',            // 有特定data-v属性的li
            'li',                              // 所有li元素
            '.card-item',                      // 类名为card-item的元素
            '[class*="card-item"]'             // 包含card-item的元素
        ];
        
        let items = [];
        let usedSelector = '';
        
        for (const selector of selectors) {
            items = resumeList.querySelectorAll(selector);
            if (items.length > 0) {
                usedSelector = selector;
                break;
            }
        }
        
        this.log(`使用选择器 "${usedSelector}" 找到 ${items.length} 个简历项`, 'info');
        
        // 如果还是没找到，尝试在整个文档中查找
        if (items.length === 0) {
            this.log('在简历列表中未找到项目，尝试在整个文档中查找...', 'warning');
            for (const selector of selectors) {
                items = iframeDoc.querySelectorAll(selector);
                if (items.length > 0) {
                    usedSelector = selector;
                    this.log(`在整个文档中使用选择器 "${usedSelector}" 找到 ${items.length} 个项目`, 'info');
                    break;
                }
            }
        }
        
        // 如果还是没找到，输出调试信息
        if (items.length === 0) {
            this.log('未找到任何简历项，输出调试信息...', 'error');
            this.log(`简历列表HTML: ${resumeList.outerHTML.substring(0, 500)}...`, 'info');
            
            // 查找所有可能的li元素
            const allLis = iframeDoc.querySelectorAll('li');
            this.log(`文档中总共有 ${allLis.length} 个li元素`, 'info');
            
            if (allLis.length > 0) {
                this.log(`第一个li元素的类名: ${allLis[0].className}`, 'info');
                this.log(`第一个li元素的HTML: ${allLis[0].outerHTML.substring(0, 200)}...`, 'info');
            }
            return false; // 没有找到元素，停止处理
        }
        
        let hasScrolled = false;
        
        // 处理所有可见的简历项
        let processedCount = 0;
        for (let i = 0; i < items.length && this.isRunning && this.scrapedCount < this.maxCount; i++) {
            const item = items[i];
            
            // 获取简历项的唯一标识符
            const itemId = item.getAttribute('data-geek') || item.getAttribute('data-geekid') || `item-${i}`;
            
            // 检查是否已经处理过这个简历项
            if (this.processedItems.has(itemId)) {
                this.log(`简历项 ${itemId} 已经处理过，跳过`, 'info');
                continue;
            }
            
            try {
                await this.processSingleResume(iframeDoc, item, i);
                this.currentIndex++;
                processedCount++;
                
                // 标记为已处理
                this.processedItems.add(itemId);
                
                // 每处理3个简历项就检查是否需要滚动
                if (processedCount % 3 === 0 && this.isRunning && this.scrapedCount < this.maxCount) {
                    this.log(`已处理 ${processedCount} 个简历项，检查是否需要滚动`, 'info');
                    const needsScroll = await this.checkIfNeedsScroll(iframeDoc, items, i);
                    if (needsScroll) {
                        this.log(`处理完第 ${processedCount} 个简历项，需要滚动加载更多内容`, 'info');
                        await this.scrollToLoadMore(iframe);
                        hasScrolled = true;
                        break; // 滚动后跳出循环，让主循环重新处理
                    }
                }
                
                // 添加延迟避免被检测，每个简历项之间等待2-4秒
                if (this.isRunning) {
                    const delay = 2000 + Math.random() * 2000;
                    this.log(`等待 ${Math.round(delay/1000)} 秒后处理下一个简历项...`, 'info');
                    await this.sleep(delay);
                }
                
            } catch (error) {
                this.log(`处理第 ${i + 1} 个简历项时发生错误: ${error.message}`, 'error');
                continue;
            }
        }
        
        this.log(`本轮处理了 ${processedCount} 个新的简历项`, 'info');
        
        // 如果已经滚动了，直接返回
        if (hasScrolled) {
            this.log(`已滚动，返回主循环重新处理`, 'info');
            return hasScrolled;
        }
        
        // 处理完所有可见的简历项后，最后检查是否需要滚动
        if (this.isRunning && this.scrapedCount < this.maxCount && processedCount > 0) {
            this.log(`处理完所有可见简历项，最后检查是否需要滚动`, 'info');
            if (items.length > 0) {
                const needsScroll = await this.checkIfNeedsScroll(iframeDoc, items, items.length - 1);
                if (needsScroll) {
                    this.log(`最后检查发现需要滚动`, 'info');
                    await this.scrollToLoadMore(iframe);
                    hasScrolled = true;
                } else {
                    this.log(`最后检查发现无需滚动`, 'info');
                }
            }
        }
        
        // 返回是否发生了滚动（如果滚动了，需要重新开始处理）
        return hasScrolled;
    }
    
    async processSingleResume(iframeDoc, item, index) {
        this.log(`开始处理第 ${index + 1} 个简历项`, 'info');
        
        try {
            // 输出详细的元素信息
            this.logElementInfo(item, '原始li元素');
            
            // 查找并点击简历卡片
            const clickTarget = this.findDetailButton(item);
            if (!clickTarget) {
                this.log(`第 ${index + 1} 个简历项未找到可点击元素`, 'warning');
                return;
            }
            
            // 输出点击目标的详细信息
            this.logElementInfo(clickTarget, '点击目标元素');
            
            // 点击简历卡片
            this.log(`准备点击元素...`, 'info');
            
            // 记录点击前的页面状态
            const beforeClick = {
                modalCount: iframeDoc.querySelectorAll('[id*="boss-dynamic-dialog"]').length,
                bodyClass: iframeDoc.body.className,
                bodyStyle: iframeDoc.body.style.overflow
            };
            this.log(`点击前状态: 弹窗数量=${beforeClick.modalCount}, body类名="${beforeClick.bodyClass}"`, 'info');
            
            clickTarget.click();
            this.log(`已点击第 ${index + 1} 个简历卡片`, 'info');
            
            // 等待弹窗出现
            this.log(`等待1.5秒让弹窗出现...`, 'info');
            await this.sleep(1500);
            
            // 记录点击后的页面状态
            const afterClick = {
                modalCount: iframeDoc.querySelectorAll('[id*="boss-dynamic-dialog"]').length,
                bodyClass: iframeDoc.body.className,
                bodyStyle: iframeDoc.body.style.overflow
            };
            this.log(`点击后状态: 弹窗数量=${afterClick.modalCount}, body类名="${afterClick.bodyClass}"`, 'info');
            
            // 检查是否有弹窗出现
            const modal = this.findModal(iframeDoc);
            if (modal) {
                this.log(`检测到弹窗出现`, 'success');
                this.logElementInfo(modal, '弹窗元素');
            } else {
                this.log(`未检测到弹窗出现`, 'warning');
                
                // 检查是否有其他类型的弹窗或遮罩层
                const overlays = iframeDoc.querySelectorAll('[class*="overlay"], [class*="mask"], [class*="backdrop"]');
                if (overlays.length > 0) {
                    this.log(`发现 ${overlays.length} 个遮罩层元素`, 'info');
                }
                
                // 检查body是否有变化
                if (beforeClick.bodyClass !== afterClick.bodyClass) {
                    this.log(`body类名发生变化: "${beforeClick.bodyClass}" -> "${afterClick.bodyClass}"`, 'info');
                }
                
                if (beforeClick.bodyStyle !== afterClick.bodyStyle) {
                    this.log(`body样式发生变化: "${beforeClick.bodyStyle}" -> "${afterClick.bodyStyle}"`, 'info');
                }
            }
            
            // 等待3秒让用户查看弹窗内容
            this.log(`等待3秒查看弹窗内容...`, 'info');
            await this.sleep(3000);
            
            // 关闭弹窗
            await this.closeModal(iframeDoc);
            
            // 记录点击操作
            this.scrapedCount++;
            const mockData = {
                index: this.scrapedCount,
                timestamp: new Date().toISOString(),
                action: '点击了简历卡片',
                geekId: item.getAttribute('data-geek') || item.getAttribute('data-geekid') || 'unknown'
            };
            
            this.scrapedData.push(mockData);
            this.log(`成功点击第 ${this.scrapedCount} 个简历卡片`, 'success');
            this.notifySidepanel('DATA_SCRAPED', mockData);
            
        } catch (error) {
            this.log(`处理第 ${index + 1} 个简历项失败: ${error.message}`, 'error');
            throw error;
        }
    }
    
    findDetailButton(item) {
        // 根据Chrome开发者工具的选择器，正确的点击目标是 div.card-inner.common-wrap.has-viewed
        const clickableSelectors = [
            'div.card-inner.common-wrap.has-viewed',  // 最精确的选择器
            'div.card-inner.common-wrap',             // 去掉has-viewed类
            'div.card-inner',                         // 只保留card-inner
            '.candidate-card-wrap',                   // 卡片包装器
            '.col-2',                                 // 第二列（通常包含主要信息）
            'div[class*="card-inner"]',               // 包含card-inner的div
            'div[class*="card"]',                     // 任何包含card的div
            'div[class*="candidate"]'                 // 任何包含candidate的div
        ];
        
        for (const selector of clickableSelectors) {
            const element = item.querySelector(selector);
            if (element) {
                this.log(`找到可点击元素: ${selector}`, 'info');
                return element;
            }
        }
        
        // 如果都没找到，返回 li 元素本身
        this.log('未找到特定的点击区域，使用li元素本身', 'warning');
        return item;
    }
    
    isClickableElement(element) {
        // 对于 li 元素和 card-inner 元素，我们假设它们都是可点击的（用于显示简历详情）
        if (element.tagName === 'LI' || 
            element.classList.contains('card-inner') ||
            element.classList.contains('candidate-card-wrap')) {
            return true;
        }
        
        const style = window.getComputedStyle(element);
        return style.cursor === 'pointer' || 
               element.onclick !== null ||
               element.getAttribute('role') === 'button' ||
               element.classList.contains('clickable') ||
               element.classList.contains('btn') ||
               element.classList.contains('card-item');
    }
    
    async extractResumeData(iframeDoc) {
        try {
            // 查找弹窗内容
            const modalSelectors = [
                '[id*="boss-dynamic-dialog"]',
                '.modal-content',
                '.dialog-content',
                '[class*="modal"]',
                '[class*="dialog"]'
            ];
            
            let modal = null;
            for (const selector of modalSelectors) {
                modal = iframeDoc.querySelector(selector);
                if (modal) break;
            }
            
            if (!modal) {
                this.log('未找到弹窗内容', 'warning');
                return null;
            }
            
            // 提取简历数据
            const resumeData = {
                name: this.extractText(modal, ['.name', '[class*="name"]', 'h1', 'h2']),
                phone: this.extractText(modal, ['.phone', '[class*="phone"]', '[class*="tel"]']),
                email: this.extractText(modal, ['.email', '[class*="email"]', '[class*="mail"]']),
                experience: this.extractText(modal, ['.experience', '[class*="experience"]', '[class*="work"]']),
                education: this.extractText(modal, ['.education', '[class*="education"]', '[class*="edu"]']),
                skills: this.extractText(modal, ['.skills', '[class*="skills"]', '[class*="skill"]']),
                summary: this.extractText(modal, ['.summary', '[class*="summary"]', '[class*="desc"]']),
                rawContent: modal.innerText || modal.textContent || ''
            };
            
            this.log('成功提取简历数据', 'success');
            return resumeData;
            
        } catch (error) {
            this.log('提取简历数据时发生错误: ' + error.message, 'error');
            return null;
        }
    }
    
    extractText(container, selectors) {
        for (const selector of selectors) {
            const element = container.querySelector(selector);
            if (element) {
                return element.innerText || element.textContent || '';
            }
        }
        return '';
    }
    
    async closeModal(iframeDoc) {
        try {
            // 首先查找弹窗容器
            const modalSelectors = [
                '[id*="boss-dynamic-dialog"]',
                '.boss-dialog',
                '.boss-popup__wrapper',
                '.modal-content',
                '.dialog-content'
            ];
            
            let modal = null;
            for (const selector of modalSelectors) {
                modal = iframeDoc.querySelector(selector);
                if (modal) {
                    this.log(`找到弹窗容器: ${selector}`, 'info');
                    break;
                }
            }
            
            if (!modal) {
                this.log('未找到弹窗容器', 'warning');
                return;
            }
            
            // 在弹窗容器内查找关闭按钮
            const closeSelectors = [
                '.boss-popup__close i',           // Boss直聘的关闭按钮
                '.boss-dialog__close i',          // Boss直聘的关闭按钮变体
                'div.boss-popup__close i',        // 更具体的路径
                'div.boss-dialog__close i',       // 更具体的路径
                '.modal-close',
                '.dialog-close',
                '[class*="close"] i',
                'i[class*="close"]',
                'button[class*="close"]',
                '.el-dialog__close',
                '.ant-modal-close'
            ];
            
            let closeButton = null;
            for (const selector of closeSelectors) {
                closeButton = modal.querySelector(selector);
                if (closeButton) {
                    this.log(`在弹窗内找到关闭按钮: ${selector}`, 'info');
                    this.logElementInfo(closeButton, '弹窗关闭按钮');
                    break;
                }
            }
            
            if (closeButton) {
                closeButton.click();
                this.log('已点击弹窗关闭按钮', 'info');
                await this.sleep(500);
                return;
            }
            
            // 如果没找到关闭按钮，尝试按 ESC 键
            this.log('未找到关闭按钮，尝试使用 ESC 键', 'warning');
            const event = new KeyboardEvent('keydown', {
                key: 'Escape',
                code: 'Escape',
                keyCode: 27,
                which: 27,
                bubbles: true
            });
            iframeDoc.dispatchEvent(event);
            this.log('已发送 ESC 键事件', 'info');
            
            // 等待一下让弹窗关闭
            await this.sleep(500);
            
        } catch (error) {
            this.log('关闭弹窗时发生错误: ' + error.message, 'error');
        }
    }
    
    async checkIfNeedsScroll(iframeDoc, items, currentIndex) {
        try {
            const window = iframeDoc.defaultView || iframeDoc.parentWindow;
            const windowHeight = window.innerHeight;
            const scrollTop = window.pageYOffset || iframeDoc.documentElement.scrollTop;
            const documentHeight = iframeDoc.documentElement.scrollHeight;
            
            // 检查当前处理的元素是否在视窗内
            const currentItem = items[currentIndex];
            const rect = currentItem.getBoundingClientRect();
            const itemBottom = rect.bottom + scrollTop;
            
            this.log(`检查滚动需求: 当前元素底部位置=${Math.round(itemBottom)}, 窗口高度=${windowHeight}, 滚动位置=${scrollTop}`, 'info');
            
            // 如果当前元素的底部接近视窗底部，或者已经超出视窗，则需要滚动
            const viewportBottom = scrollTop + windowHeight;
            const needsScroll = itemBottom >= viewportBottom - 100; // 留100px缓冲，更容易触发滚动
            
            if (needsScroll) {
                this.log('当前元素接近或超出视窗底部，需要滚动', 'info');
            } else {
                this.log('当前元素仍在视窗内，无需滚动', 'info');
            }
            
            return needsScroll;
            
        } catch (error) {
            this.log('检查滚动需求时发生错误: ' + error.message, 'error');
            return false;
        }
    }
    
    async scrollToLoadMore(iframe) {
        try {
            // 检查是否还在运行
            if (!this.isRunning) {
                this.log('抓取已停止，取消滚动', 'info');
                return;
            }
            
            const window = iframe.contentWindow || window;
            const doc = iframe.contentDocument || document;
            
            // 获取当前滚动位置和页面高度
            const scrollHeight = doc.documentElement.scrollHeight;
            const currentScroll = window.pageYOffset || doc.documentElement.scrollTop;
            const windowHeight = window.innerHeight || doc.documentElement.clientHeight;
            
            this.log(`当前滚动位置: ${currentScroll}, 页面高度: ${scrollHeight}, 窗口高度: ${windowHeight}`, 'info');
            
            // 计算需要滚动的距离（滚动一个窗口高度的距离）
            const scrollDistance = windowHeight * 0.8; // 滚动80%的窗口高度
            const targetScroll = currentScroll + scrollDistance;
            
            if (targetScroll < scrollHeight - 100) {
                this.log(`滚动 ${Math.round(scrollDistance)} 像素加载更多内容`, 'info');
                
                // 平滑滚动
                window.scrollTo({
                    top: targetScroll,
                    behavior: 'smooth'
                });
                
                // 等待内容加载
                await this.sleep(2000);
                
                // 再次检查是否还在运行
                if (!this.isRunning) {
                    this.log('抓取已停止，取消后续滚动', 'info');
                    return;
                }
                
                // 检查是否有新内容加载
                const newScrollHeight = doc.documentElement.scrollHeight;
                if (newScrollHeight > scrollHeight) {
                    this.log(`检测到新内容已加载，页面高度从 ${scrollHeight} 增加到 ${newScrollHeight}`, 'info');
                } else {
                    this.log('没有检测到新内容加载，但继续处理现有内容', 'info');
                }
                
                // 不再递归滚动，让主循环重新查找和处理元素
                this.log('滚动完成，等待主循环重新处理', 'info');
                
            } else {
                this.log('已到达页面底部，无需滚动', 'info');
            }
            
        } catch (error) {
            this.log('滚动页面时发生错误: ' + error.message, 'error');
        }
    }
    
    logElementInfo(element, label) {
        try {
            this.log(`=== ${label} 详细信息 ===`, 'info');
            this.log(`标签名: ${element.tagName}`, 'info');
            this.log(`类名: ${element.className}`, 'info');
            this.log(`ID: ${element.id || '无'}`, 'info');
            
            // 生成CSS选择器
            const cssSelector = this.generateCSSSelector(element);
            this.log(`CSS选择器: ${cssSelector}`, 'info');
            
            // 生成XPath
            const xpath = this.generateXPath(element);
            this.log(`XPath: ${xpath}`, 'info');
            
            // 显示部分HTML
            const html = element.outerHTML.substring(0, 300);
            this.log(`HTML片段: ${html}...`, 'info');
            
            // 检查元素是否可见
            const style = window.getComputedStyle(element);
            this.log(`可见性: display=${style.display}, visibility=${style.visibility}`, 'info');
            this.log(`位置: ${element.offsetTop}, ${element.offsetLeft}`, 'info');
            this.log(`尺寸: ${element.offsetWidth}x${element.offsetHeight}`, 'info');
            
        } catch (error) {
            this.log(`输出元素信息时出错: ${error.message}`, 'error');
        }
    }
    
    generateCSSSelector(element) {
        if (element.id) {
            return `#${element.id}`;
        }
        
        let selector = element.tagName.toLowerCase();
        if (element.className) {
            const classes = element.className.split(' ').filter(c => c.trim());
            if (classes.length > 0) {
                selector += '.' + classes.join('.');
            }
        }
        
        // 添加父元素信息
        if (element.parentElement) {
            const parent = element.parentElement;
            if (parent.id) {
                selector = `#${parent.id} > ${selector}`;
            } else if (parent.className) {
                const parentClasses = parent.className.split(' ').filter(c => c.trim());
                if (parentClasses.length > 0) {
                    selector = `${parent.tagName.toLowerCase()}.${parentClasses.join('.')} > ${selector}`;
                }
            }
        }
        
        return selector;
    }
    
    generateXPath(element) {
        if (element.id) {
            return `//*[@id="${element.id}"]`;
        }
        
        let path = '';
        let current = element;
        
        while (current && current.nodeType === Node.ELEMENT_NODE) {
            let selector = current.tagName.toLowerCase();
            
            if (current.className) {
                const classes = current.className.split(' ').filter(c => c.trim());
                if (classes.length > 0) {
                    selector += `[@class="${current.className}"]`;
                }
            }
            
            // 添加索引
            const siblings = Array.from(current.parentElement?.children || [])
                .filter(sibling => sibling.tagName === current.tagName);
            if (siblings.length > 1) {
                const index = siblings.indexOf(current) + 1;
                selector += `[${index}]`;
            }
            
            path = selector + (path ? '/' + path : '');
            current = current.parentElement;
        }
        
        return '//' + path;
    }
    
    findModal(iframeDoc) {
        const modalSelectors = [
            '[id*="boss-dynamic-dialog"]',    // Boss直聘的动态弹窗
            '.boss-dialog',                   // Boss直聘的对话框
            '.boss-popup__wrapper',          // Boss直聘的弹窗包装器
            '.modal-content',
            '.dialog-content',
            '[class*="modal"]',
            '[class*="dialog"]',
            '.el-dialog',
            '.ant-modal'
        ];
        
        for (const selector of modalSelectors) {
            const modal = iframeDoc.querySelector(selector);
            if (modal) {
                this.log(`找到弹窗: ${selector}`, 'info');
                return modal;
            }
        }
        
        return null;
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    log(message, level = 'info') {
        console.log(`[ResumeScraper ${level.toUpperCase()}] ${message}`);
        this.notifySidepanel('LOG_MESSAGE', { message, level });
    }
    
    notifySidepanel(type, data = {}) {
        try {
            chrome.runtime.sendMessage({
                type,
                ...data
            });
        } catch (error) {
            console.error('发送消息到 sidepanel 失败:', error);
        }
    }
}

// 初始化抓取器
const scraper = new ResumeScraper();
