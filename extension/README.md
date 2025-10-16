# 简历抓取浏览器插件

## 功能说明

这是一个用于自动抓取招聘网站简历数据的浏览器插件，支持：

- 自动识别目标 iframe 中的简历列表
- 批量点击简历项并抓取详细信息
- 自动处理弹窗和关闭操作
- 支持瀑布流页面的滚动加载
- 实时显示抓取进度和状态
- 数据导出功能

## 安装方法

1. 打开 Chrome 浏览器
2. 进入 `chrome://extensions/`
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择本插件的 `extension` 目录

## 使用方法

1. 安装插件后，访问目标招聘网站
2. 点击浏览器工具栏中的插件图标，打开侧边栏
3. 在侧边栏中点击"开始抓取"按钮
4. 插件将自动开始抓取简历数据
5. 抓取完成后可以点击"导出数据"保存结果

## 文件结构

```
extension/
├── manifest.json          # 插件配置文件
├── background.js          # 后台脚本
├── content.js            # 内容脚本（抓取逻辑）
├── sidepanel.html        # 侧边栏界面
├── sidepanel.js          # 侧边栏控制脚本
├── icons/                # 图标文件
│   ├── icon.svg         # SVG 图标源文件
│   ├── icon16.png       # 16x16 图标
│   ├── icon32.png       # 32x32 图标
│   ├── icon48.png       # 48x48 图标
│   └── icon128.png      # 128x128 图标
└── README.md            # 说明文档
```

## 图标生成

由于需要 PNG 格式的图标文件，请使用以下方法之一生成：

### 方法1：使用在线工具
1. 访问 https://convertio.co/svg-png/ 或类似工具
2. 上传 `icons/icon.svg` 文件
3. 分别生成 16x16、32x32、48x48、128x128 尺寸的 PNG 文件
4. 保存为对应的文件名

### 方法2：使用 ImageMagick
```bash
cd extension/icons
convert icon.svg -resize 16x16 icon16.png
convert icon.svg -resize 32x32 icon32.png
convert icon.svg -resize 48x48 icon48.png
convert icon.svg -resize 128x128 icon128.png
```

### 方法3：使用 Python PIL
```python
from PIL import Image
import cairosvg

# 将 SVG 转换为 PNG
cairosvg.svg2png(url='icon.svg', write_to='icon16.png', output_width=16, output_height=16)
cairosvg.svg2png(url='icon.svg', write_to='icon32.png', output_width=32, output_height=32)
cairosvg.svg2png(url='icon.svg', write_to='icon48.png', output_width=48, output_height=48)
cairosvg.svg2png(url='icon.svg', write_to='icon128.png', output_width=128, output_height=128)
```

## 注意事项

1. 插件需要访问目标网站的 iframe 内容，某些网站可能有跨域限制
2. 抓取速度已设置延迟，避免被网站检测为异常行为
3. 建议在测试环境中先验证功能正常后再正式使用
4. 请遵守目标网站的使用条款和 robots.txt 规定

## 技术实现

- **Manifest V3**: 使用最新的 Chrome 扩展 API
- **Side Panel**: 提供便捷的操作界面
- **Content Script**: 处理页面 DOM 操作
- **Background Script**: 处理消息传递和状态管理
- **Chrome Storage**: 本地数据存储
- **异步处理**: 支持大量数据的批量处理

## 开发说明

如需修改抓取逻辑，主要关注以下文件：
- `content.js`: 核心抓取逻辑
- `sidepanel.js`: 界面控制逻辑
- `manifest.json`: 权限和配置

抓取的目标元素路径可以在 `content.js` 中的选择器数组中修改。
