# 领域专家与知识图谱｜部署、检索和验收

## 模块职责

- 独立网页 `/domain-experts/`：AI × 科研知识学习、烯烃环氧化两条主线。
- 可点击的原生 SVG 知识图谱及研究时间轴：专家—研究兴趣边来自人工整理；论文关系来自 ORCID 与 OpenAlex 作者ID身份匹配。
- 10位领域专家资料、机构、研究主题和官方链接；不扩展或修改其他网站功能。
- 每周一约08:23北京时间由 GitHub Actions 定时检索并在数据验证通过后自动更新 `_data/domain_expert_updates.json`；默认展示过去180天相关文献。另有 ChatGPT 每周研究简报任务，其与网站同步相互独立。

## 安全与科研质量

1. 原始研究模型、DFT/NEB/TOF数据及网站已有论文列表均不修改。
2. 作者匹配：ORCID -> OpenAlex author ID -> OpenAlex work authorship；无法核验身份则该次运行失败并保留已发布数据。
3. 文献要求 DOI、合理日期、作者身份匹配、题名/摘要领域关键词；按 DOI 去重。标题和摘要筛选只是规则相关性，不能代表论文结论已核验。
4. 未设 ORCID 的作者仅显示专家资料，不按名字自动关联论文。首次同步前显示“尚未建立可验证的在线检索结果”，不捏造论文。
5. 每次同步保存运行 JSON 报告为 Actions artifact，API 身份错误则非零退出，禁止覆盖旧有数据。
6. GitHub Actions 共享出口 IP 的免密 OpenAlex 每日预算已耗尽（HTTP 429，2026-11-13 实测）；为保证定时更新，必须在仓库 Actions Secrets 配置个人免费 `OPENALEX_API_KEY`。未配置时仅运行离线测试；定时发布会明确报错并保留旧数据。不要把密钥放入网页或提交仓库。

## 最小执行和验证

```bash
python3 -m unittest discover -s tests -p test_sync_domain_experts.py -v
node --check assets/js/domain-experts.js
python3 scripts/sync_domain_experts.py --dry-run
bundle exec jekyll build
```

- 前两条为离线测试；第三条需要连接 OpenAlex；第四条需要已有网站 Gem 依赖。
- 只读检查：Actions -> Sync domain-expert research -> Run workflow -> `dry-run`。需要提前在 GitHub Actions Secrets 配置 `OPENALEX_API_KEY`。
- 应用：Actions -> Run workflow -> `apply`，只提交验证过的 `_data/domain_expert_updates.json`；定时运行会自动应用。
- 查看 GitHub Actions 运行日志，确认 author ID 解析、报告、DOI 数、成功提交和 Pages 构建；失败时不得声称已经自动更新。
- 手机端实际打开 `/domain-experts/` 测试横向滑动、节点点击、研究分类切换、官方链接和深色模式。

## 数据来源

专家官方研究组网站、ORCID、OpenAlex和 DOI 原始论文记录。代表性研究节点为人工精选而非文献计量自动推断。

## 专家个人时间轴与期刊筛选

每位专家均有独立时间轴。有效检索后，按发表日期显示论文、期刊、DOI、相关主题及优先期刊标识。优先期刊名单定义在 `scripts/sync_domain_experts.py` 的 `PRIORITY_JOURNALS`，不等于 Clarivate SCI/JCR 官方核验。网页上的“研究线索”来自标题/摘要关键词匹配，不是论文的已证实关键发现。关键发现必须阅读正文后由研究者核验，再维护独立的人工证据数据，禁止根据关键词自动编造。若 API key 未配置或调用失败，保留旧数据并显示状态。
