# 上传到 GitHub Pages（含自动更新引用数）

## 只需配置一次

1. 创建公开仓库 `你的GitHub用户名.github.io`。
2. 上传本项目的 **build.py、content-en.json、dist/、scripts/、.github/** 到仓库根目录。不要只上传 dist 里的文件；自动更新需要这些源文件和工作流。无需上传 assets 原始素材、简历、临时文件或视频原片。
3. 仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
4. 在 **Actions** 中启用工作流，选择 **Update Scholar and Deploy Pages → Run workflow**。默认分支使用 main 或 master。
5. 等待 build 和 deploy 完成，打开 `https://你的GitHub用户名.github.io/`。

你的 Scholar ID `aEts7nUAAAAJ` 已配置为默认值，**不必另外添加 Secret**。如果要覆盖，可在 Settings → Secrets and variables → Actions 新建名为 `GOOGLE_SCHOLAR_ID` 的 repository secret。

## 引用数怎样更新

- 推送到 main/master、手动运行或每天 UTC 08:17（北京时间16:17）时，工作流尝试获取 Scholar 总引用数。
- 成功后生成 `dist/assets/gs_data.json` 并随网页一起发布。徽章读取这个同站点文件，不直接从访客浏览器访问 Google Scholar。
- 只读取作者引用统计，避免逐篇访问产生不必要的请求。当前显示的是总引用数，不是单篇引用数。
- 成功结果保存在 GitHub Actions 缓存中；之后抓取失败会保留可用的上次结果及真实更新时间。缓存不是永久存储，可能被 GitHub 清理。也可将一次验证过的 gs_data.json 提交到 dist/assets/，作为长期备用数据。
- 尚无成功结果时仍显示横杠，不会用 0 或估算值冒充。Google Scholar 可能限制自动请求，因此无法保证每次抓取成功；GitHub Pages 能部署成功也不代表 Scholar 抓取成功。

## 如果仍然是横杠

在 Actions 查看 **Refresh citation total** 步骤日志。若出现访问限制或超时，稍后手动重试。网页发布步骤仍会正常运行，并给出引用更新警告。

首次成功后，打开 `https://你的GitHub用户名.github.io/assets/gs_data.json` 应看到 `scholar_id`、`citedby` 和 `updated`。如果 JSON 有数字而徽章没有，请确认页面引用了 assets/scholar.js，并刷新页面。

如果希望保存一份长期备用数据，将以上页面下载得到的真实 JSON 原样保存为 `dist/assets/gs_data.json` 后提交。不要手工修改其更新时间。

## 使用已准备好的上传包

解压 github-pages-ready.zip，将解压后的内容上传到仓库根目录，不要直接上传 ZIP，也不要把文件嵌套在额外一层文件夹中。必须包含 .github/workflows/pages.yml。

可通过 GitHub 仓库的 Add file → Upload files 上传。当前单个文件均小于 25 MiB。上传包只包含当前使用的展示媒体，不含已删除的生活相册、旧头像、原始素材和简历文件。

请使用公开仓库，根目录保留 build.py、content-en.json、dist、scripts、.github、tests 等文件和目录。Pages 的 Source 必须选 GitHub Actions。

## 验证范围

本地检查覆盖页面、资源路径、引用数字校验、零引用处理与失败时保留旧数据。GitHub Actions 的真正抓取和部署需要上述仓库启用后运行；本地配置完成并不等于已经在你的 GitHub 账户上执行成功。
