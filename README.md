# 赵柏宁的个人学术主页

英文版，依据提供的简历和公开论文页面整理。保留 AcadHomepage 的双栏个人资料、顶部导航、论文条目和学术履历布局，改为无需 Jekyll 的静态版本。模板原作者 Yi Ren 的 MIT 许可见 LICENSE。

## 修改内容

- `content-en.json`：英文介绍、论文、教育、实习、研究和荣誉。后续增加 `content-zh.json` 并扩展生成器即可支持双语。
- `build.py`：页面结构与生成器，修改后运行 `python build.py`。
- `dist/assets/style.css`：桌面和手机样式。
- `assets/image.jpg`：用户提供的头像原图；发布副本为 `dist/assets/portrait.jpg`。
- `dist/assets/publications/`：论文配图和官方演示视频；每个条目的 `media` 字段配置图片、替代文字和可选视频。视频静音自动循环播放并保留暂停控件，图片可打开原尺寸。
- `dist/index.html`：可以直接双击打开的完整主页。

## 发布到 GitHub Pages

自动更新引用数的 GitHub Pages 部署步骤见 **GITHUB-PAGES.md**。请上传 build.py、content-en.json、dist/、scripts/、.github/，在仓库 Settings → Pages 选择 GitHub Actions。仅上传 dist 文件仍可显示静态网页，但不会运行引用抓取任务。

## 内容核对

已收录 10 篇代表论文，末尾另设 All Publications：28 篇（19 篇正式发表、9 篇预印本或在审稿件），包含用户本次提供的 20 篇及核对到的 8 篇早期成果。完整列表保存在 content-en.json 的 bibliography 字段；使用英文参考文献格式，完整作者以名字首字母加姓氏呈现，B. Zhao 加粗，刊会名斜体。正式发表条目在各作者分组内按年份倒序排列。用户明确要求展示的在审稿件及投稿去向按其提供的内容标注，不代表已录用。谷歌学术本次无法直接访问，早期成果通过出版社、DOI 和文献索引交叉核对，尚不能保证与其 Scholar 列表完全一致。

简历中的总引用量、政治面貌和企业内部性能指标未放入页面。原始 Word 简历不会随网站发布。导师信息未在简历中明确，因此未推测填写。

核对来源与说明见 SOURCES.md。页面未接入分析追踪或引用量爬虫。

作者显示规则：完整保留所有作者，按姓氏加名字首字母缩写（如 Zhao B），并加粗 Baining Zhao。会议／期刊及年份显示在作者下面，不再显示一句话简介或在图片上覆盖标签。论文资源链接采用 GitHub README 风格的扁平双色文字徽章，不依赖图标或外部徽章图片服务。样式文件使用内容版本号，更新后自动加载新样式。

侧栏按 google scholar、邮箱、电话排列；电话依据简历并按本人要求展示。

## 本地素材存放约定

用户将头像原图移动到了 `assets/image.jpg`。后续合成视频、视频封面和其他生成素材统一保存在项目根目录的 `assets/` 下，可按项目分类，例如 `assets/publications/`。发布时将需要使用的文件复制到 `dist/assets/`，并更新页面引用。`assets/` 是本地素材目录，`dist/assets/` 是网页发布副本；不要只将新生成的成品保存在临时目录或发布目录中。

WorldVLN 当前最终版视频与封面：`assets/worldvln-selected.mp4`、`assets/worldvln-selected.jpg`；网页发布副本位于 `dist/assets/publications/`。

有 GitHub Code 链接的论文自动显示 Shields.io Stars 徽章，点击可打开仓库。数量由外部服务获取并缓存，无需手填；受外部服务可用性影响。

## Latest bibliography layout

Research Highlights shows six demo cards. All Publications contains 30 records, ordered by author position (requested order breaks ties), with only Working Papers separated and numbering continuous. Education includes honors and research on separate lines. scholar_metrics in content-en.json controls the static citation badge; an unavailable value renders a dash, never zero. Scholar completeness and two newly added early-work sources are documented in SOURCES.md.

引用数现已接入 scripts/update_scholar.py 与 .github/workflows/pages.yml；网页通过 assets/scholar.js 读取 gs_data.json，静态字段仅作备用。详见 GITHUB-PAGES.md。页面最后的 Beyond Research 展示六张已选照片。
