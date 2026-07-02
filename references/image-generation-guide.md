# 插图制作经验总结

> 本文档总结团建文章配图项目的实践经验，供后续图片制作任务参考。
> 创建时间：2026-07-02
> 适用场景：Markdown 文档配图、封面图设计、内部插图制作

---

## 一、图片生成流程（标准工作流）

### 1.1 前期准备
- [ ] 读取目标 Markdown 文档，理解内容和结构
- [ ] 确定需要的图片类型：封面图 vs 内部插图
- [ ] 规划图片数量和内容（每张图对应一个核心概念）
- [ ] 检查现有图片资源，避免重复生成

### 1.2 图片生成
- [ ] 编写提示词（参考第三节模板）
- [ ] 使用 ImageGen 工具生成图片
- [ ] 并行生成独立图片（提高效率）

### 1.3 后期处理
- [ ] 重命名图片为语义化名称
- [ ] 移动到正确目录
- [ ] 更新 Markdown 文档引用
- [ ] 验证图片显示效果

---

## 二、设计风格规范

### 2.1 整体风格
- **风格**：扁平插画（Flat Illustration）
- **美学**：现代、专业、温暖
- **参考**：企业培训材料、教育 infographic

### 2.2 配色方案
| 角色 | 颜色 | 色值参考 | 使用场景 |
|------|------|----------|---------|
| 主色 | 青色（Teal Blue） | `#008080` 或渐变 | 标题、主图标、背景渐变 |
| 点缀色 | 暖橙色（Warm Orange） | `#FF8C42` | 强调元素、图标点缀 |
| 辅助色 | 珊瑚橙（Coral） | `#FF6F61` | 次要元素 |
| 背景 | 白色或浅灰 | `#FFFFFF` / `#F8F9FA` | 背景 |
| 文字 | 深灰或黑色 | `#333333` / `#000000` | 文字（如有） |

### 2.3 视觉元素
- **图标风格**：圆角、实心或线性图标，2-3 色填充
- **人物风格**：简约线条或色块人物，避免写实
- **布局**：干净留白，元素对齐，视觉层次清晰
- **边框**：圆角矩形卡片（radius: 12-16px）

---

## 三、提示词（Prompt）模板库

### 3.1 封面图提示词模板

**通用结构**：
```
[主题描述] + [风格声明] + [核心元素列举] + [配色方案] + [背景处理] + [文字预留] + [质量声明]
```

**示例 1：指南类封面**
```
Professional [主题] guide cover image, modern flat illustration style with teal and warm orange accent colors. 
Show [核心场景/人物]. Include subtle icons: [图标1], [图标2], [图标3]. 
Clean white background with soft gradient teal header area. 
Space for Chinese text '[标题]'. 
Professional, warm, approachable vibe suitable for corporate training material. 
High quality, vector-style illustration.
```

**示例 2：流程类封面**
```
[流程类型] event timeline cover illustration, vibrant flat design style with [主色] and [点缀色] colors. 
Visualize [流程阶段1], [流程阶段2], [流程阶段3] as [视觉隐喻]. 
Small illustrated figures doing different activities. 
Clean modern layout with space for Chinese text '[标题]'. 
Energetic but professional, perfect for event planning document cover. 
High quality illustration.
```

**示例 3：索引/总览类封面**
```
[主题] library cover illustration, comprehensive index page design, modern flat illustration style with teal blue, warm orange and purple accent colors. 
Center composition showing [核心视觉元素]. 
[分类图标1], [分类图标2], [分类图标3] floating around. 
Clean white background with soft gradient teal header. 
Space for Chinese title '[标题]'. 
Professional, vibrant, comprehensive resource library aesthetic. 
High quality vector-style illustration.
```

### 3.2 内部插图提示词模板

**通用结构**：
```
[内容描述] + [布局说明] + [配色方案] + [背景] + [风格声明]
```

**示例 1：流程/步骤图**
```
Flat illustration showing '[流程名称]' with [数字] steps, [配色] color scheme on white background. 
[数字] numbered circles connected by arrows: 
Step 1 shows [内容1] ([图标1]), 
Step 2 shows [内容2] ([图标2]), 
Step 3 shows [内容3] ([图标3]). 
Clean infographic style, each step has small label text area. 
Modern corporate training aesthetic, professional and clear.
```

**示例 2：模型/框架图**
```
Flat illustration of [模型名称] used in [场景], [配色] color palette on white background. 
[布局描述：四象限/圆形流程/时间线]: 
[元素1] ([图标1]), 
[元素2] ([图标2]), 
[元素3] ([图标3]), 
[元素4] ([图标4]). 
Connected by [连接方式]. 
Clean educational diagram style suitable for training materials. 
Each section has space for brief description text.
```

**示例 3：对比/选择图**
```
[内容类型] illustration, [布局：三列/左右对比] layout, [配色] color scheme. 
[选项A] ([图标A]), 
[选项B] ([图标B]), 
[选项C] ([图标C]). 
Each option as a visually distinct card with [内容描述]. 
Clean comparison chart style for [用途].
```

**示例 4：清单/准备图**
```
[主题] checklist flat illustration, organized [布局] layout, [配色] on white background. 
Show items needed for [场景]: [物品1], [物品2], [物品3], [物品4]. 
Each item as a cute flat icon with subtle label underneath. 
Clean supply checklist aesthetic, professional [用途] style.
```

---

## 四、图片规格建议

| 图片类型 | 推荐尺寸 | 用途 | 备注 |
|---------|---------|------|------|
| 封面图 | 1200×630 | 网页预览、社交分享 | 16:9 比例，文件大小 < 1MB |
| 内部插图（横向） | 900-1000×500-600 | 章节配图 | 根据内容调整高度 |
| 内部插图（纵向） | 800×600-800 | 流程、模型图 | 保持可读性 |
| 图标/小图 | 400-600×300-400 | 侧边栏、提示框 | 简洁为主 |

**尺寸选择原则**：
- 封面图：固定 1200×630（网页标准）
- 内部插图：根据内容复杂度选择，内容多→高，内容少→宽
- 所有图片：宽度不超过 1000px（适配移动端）

---

## 五、文件管理规范

### 5.1 目录结构
```
article-directory/
├── images/
│   ├── cover.png          # 封面图（通用名）
│   ├── illust-*.png       # 内部插图（语义化命名）
│   └── ...
├── article.md
└── ...
```

### 5.2 命名规范
| 图片类型 | 命名模式 | 示例 |
|---------|---------|------|
| 封面图 | `cover.png` 或 `*-cover.png` | `cover.png`, `guide-cover.png` |
| 内部插图 | `illust-<内容描述>.png` | `illust-4f-debrief.png`, `illust-timeline-overview.png` |
| 图标 | `icon-<名称>.png` | `icon-icebreaker.png` |

**命名原则**：
- 使用英文小写 + 连字符
- 描述图片内容，便于后续查找
- 避免泛泛的名称（如 `image1.png`）

### 5.3 存储位置
- **封面图**：与 Markdown 文档同目录的 `images/` 子目录
- **内部插图**：与引用它的 Markdown 文档同目录的 `images/` 子目录
- **通用素材**：项目根目录的 `images/` 目录

---

## 六、Markdown 引用规范

### 6.1 封面引用
在文档标题后、正文前插入封面图：
```markdown
# 文章标题

![封面](images/cover.png)

> 文章简介或说明...
```

### 6.2 内部插图引用
在相关章节内容后插入：
```markdown
## 章节标题

章节内容...

![插图描述](images/illust-xxx.png)

章节内容继续...
```

### 6.3 引用原则
- 每张插图紧跟相关文字（前后 3 段内）
- 使用描述性 alt 文本（便于无障碍访问）
- 相对路径引用（不从根目录开始）
- 图片下方可加简短说明（如需要）

---

## 七、提示词编写技巧

### 7.1 必备要素
1. **风格声明**：明确指定 "modern flat illustration style"
2. **配色方案**：明确主色和点缀色
3. **背景处理**：明确 "on white background" 或 "with gradient"
4. **质量声明**：结尾加 "High quality, vector-style illustration"
5. **文字预留**：如需加文字，说明 "Space for Chinese text '[标题]'"

### 7.2 避免的问题
- ❌ 提示词过于抽象："beautiful image"
- ❌ 配色模糊："colorful"
- ❌ 风格冲突：混合多种风格（如 "flat and realistic"）
- ❌ 元素过多：一张图包含太多概念，导致混乱

### 7.3 进阶技巧
- **使用参考图**：如有现有图片风格，可用 `image` 参数指定参考
- **迭代优化**：生成后不满意，调整提示词重新生成
- **批量生成**：独立图片可并行生成（节省时间）

---

## 八、常见问题与解决方案

### 8.1 图片生成失败
**问题**：ImageGen 返回错误或无响应
**解决**：
- 检查提示词是否包含不支持的内容
- 简化提示词，分步生成
- 检查输出目录是否存在

### 8.2 图片风格不统一
**问题**：同一项目的图片风格差异大
**解决**：
- 使用相同的配色方案描述
- 在提示词中重复相同的风格关键词
- 参考已生成的好图片，调整后续提示词

### 8.3 图片内容不准确
**问题**：生成图片与预期不符
**解决**：
- 在提示词中更详细地描述核心元素
- 使用 "showing [具体场景]" 明确场景
- 参考成功案例的提示词结构

### 8.4 文件管理混乱
**问题**：图片文件名无意义，难以管理
**解决**：
- 生成后立即重命名为语义化名称
- 按规范组织目录结构
- 更新文档引用后再移动文件

---

## 九、检查清单（生成图片前后）

### 生成前
- [ ] 已读取文档，理解内容
- [ ] 已规划图片数量和内容
- [ ] 已编写提示词（参考模板）
- [ ] 已确定图片尺寸和存储位置

### 生成后
- [ ] 已重命名图片为语义化名称
- [ ] 已移动到正确目录
- [ ] 已更新 Markdown 文档引用
- [ ] 已验证图片显示正常
- [ ] 已记录本次经验（如有新发现）

---

## 十、本次项目经验总结

### 10.1 成功做法
- ✅ 先读取所有文档，统一规划图片内容
- ✅ 使用一致的设计风格（青色+暖橙）
- ✅ 并行生成独立图片（节省时间）
- ✅ 生成后立即重命名和移动
- ✅ 更新文档引用后验证效果

### 10.2 可改进点
- 🔄 提示词可以更简洁（部分提示词过长）
- 🔄 可以先生成 1 张样例，确认风格后再批量生成
- 🔄 可以建立提示词模板库，避免重复编写

### 10.3 可复用资源
- **提示词模板**：本文档第三节
- **配色方案**：本文档第二节
- **文件规范**：本文档第五节

---

## 附录：快速参考卡

### A. 提示词速查
```
# 封面图
"[主题] cover image, modern flat illustration style with teal and warm orange. Show [场景]. Space for Chinese text. High quality illustration."

# 流程图
"Flat illustration showing [流程] with [数字] steps, teal and orange color scheme. Step 1 [内容], Step 2 [内容], Step 3 [内容]. Clean infographic style."

# 模型图
"Flat illustration of [模型], [配色] on white background. [元素1], [元素2], [元素3], [元素4] connected by arrows. Educational diagram style."
```

### B. 图片尺寸速查
- 封面：1200×630
- 横向插图：900-1000×500-600
- 纵向插图：800×600-800

### C. 文件命名速查
- 封面：`cover.png` 或 `*-cover.png`
- 插图：`illust-<内容>.png`
- 图标：`icon-<名称>.png`

---

**文档版本**：v1.0  
**最后更新**：2026-07-02  
**维护者**：AI Assistant  
**反馈**：如有新经验或问题，请更新本文档
