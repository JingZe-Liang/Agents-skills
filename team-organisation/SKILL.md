---
name: team-organisation
description: 管理科研团队工作区与论文组织流程。适用于维护团队文件夹、整理论文草稿、获取论文元数据/摘要、按用户维护的分类体系聚类论文、更新问题清单、生成论文分类归纳整理汇总、按主题或老师检索高水平论文，以及规范化保存该技能的工作产物。
---

# Team Organisation

## 总原则

- 把当前项目当作科研进度工作区；用户可直接维护团队文件、草稿和分类规则。
- 本 skill 有两个并列功能：**论文聚类整理** 和 **论文检索**。两者共享目录规范，但流程、工作区、产物和校验要求分开执行。
- 面向用户的论文产物必须放入 `Base/`；内部状态、缓存、ledger、检索笔记放入 `workspace/<skill-task>/`，不得散落到项目根目录。
- 用户编辑优先。已存在的分类文件、汇总文件、ledger、问题清单、检索笔记只能增量更新，不能无依据重建或覆盖用户内容。
- 以后新增能力时必须作为新的一级功能加入，并建立独立产物目录和独立内部工作区。

## 目录总览

首次使用任一功能时，若目录不存在，先创建：

```text
Base/
  Paper_Aggregation/
    草稿.md
    论文分类归纳整理.md
  Paper_Search/

workspace/
  paper_organisation/        # 聚类内部状态
  paper_search/
    <NN>_<Purpose>/
      evidence.md            # 轻量证据台账：来源、候选、判断依据、取舍结论
      notes/                 # 仅在争议/高风险条目需要时使用
      metadata/              # 必要的 BibTeX、摘要、页面缓存等结构化材料
```

- `Base/Paper_Aggregation/` 只放 `草稿.md` 和 `论文分类归纳整理.md` 两个面向用户文件。
- `Base/Paper_Search/` 每次检索生成一个 Markdown 汇总，文件名为递增编号加简洁目的。编号接续已有最大编号，目的词用英文或拼音，短而清楚。
- `workspace/` 只放内部产物：分类小文件、ledger、metadata、搜索日志、状态 hash、脚本输出。

## 功能一：论文聚类整理

用途：把用户给的草稿论文列表吸纳进既有分类体系，更新分类小文件，并生成 `Base/Paper_Aggregation/论文分类归纳整理.md`。

### 分类规则

- 论文分类管理必须使用 `workspace/paper_organisation/分类.md`。
- 用户会手动维护该文件；每次开始论文聚类/归档前，先读取它，并运行：

```bash
python3 .agents/skills/team-organisation/scripts/check_category_rules.py
```

- 若脚本返回 `changed` 或 `new`，说明分类体系相比上次变化，必须重新整理所有 category 小文件并重新生成 `论文分类归纳整理.md`；不能只增量处理新增论文。
- 如果 `分类.md` 不存在，先从现有 `categories/*.md` 生成一个初始版本，供用户后续维护。
- 处理完成后运行 `python3 .agents/skills/team-organisation/scripts/check_category_rules.py --update` 更新 `state/分类.sha256`。

### 聚类流程

1. 默认草稿为 `Base/Paper_Aggregation/草稿.md`；若用户指定其他文件，处理前同步或说明来源。
2. 先保证目录存在：`metadata/`、`crawl_drafts/`、`categories/`、`state/`。
3. 用 `scripts/parse_paper_draft.py` 解析草稿，生成或更新 ledger。ledger 必须记录原始编号、规范题名、链接/DOI/arXiv/OpenReview/BibTeX、重复关系、状态、目标分类和核验来源。
4. 搜索前先检查并读取 `分类.md`；分类按用户文件为准。若用户分类未覆盖，临时按任务域选择最接近类别，并在简介中说明不确定性。
5. 获取元数据时优先可靠来源：arXiv、OpenReview/forum、CVF、PMLR/ICML、AAAI、IEEE、ACM、Springer、ScienceDirect、MDPI、DOI、项目页、作者页、官方 GitHub。二级来源只用于定位或交叉验证。
6. 不能从题名臆测摘要、年份、会议或技术结论。每篇正式归档论文都要有可追踪来源和摘要/正文依据。
7. 搜不到或页面受限时，必须自动使用 Chrome 精确搜索题名和关键短语；只有 Chrome 仍找不到可靠来源时，才放入 `categories/99-问题清单.md`。
8. 已经处理成功的条目不得继续留在问题清单。`categories/99-问题清单.md` 只保留当前未解决条目；重复/合并、链接题名校正、Chrome 已解决记录写入 `crawl_drafts/` 审计文件。
9. 每个分类文件按年份升序排列，同年按题名稳定排序。
10. 每个 verified 条目格式固定：

```markdown
### Paper Title

- 年份/来源：2026, CVPR / arXiv
- 链接：<https://example.com>
- 简介：中文简介，说明论文任务、方法要点，以及为什么属于该类别。
```

### 聚类汇总文件

- 用户面向的最终文件固定为 `Base/Paper_Aggregation/论文分类归纳整理.md`。
- 不手工编辑最终汇总；先编辑 `categories/*.md`，再运行：

```bash
python3 .agents/skills/team-organisation/scripts/aggregate_papers.py \
  --categories-dir workspace/paper_organisation/categories \
  --output Base/Paper_Aggregation/论文分类归纳整理.md \
  --title 论文分类归纳整理
```

- `论文分类归纳整理.md` 的每个 `##` 小节下面必须给论文条目自动编号，格式为 `### 1. Paper Title`、`### 2. Paper Title`；每个小节单独从 1 开始。
- 分类小文件中可以不编号；编号由聚合脚本生成，避免重复手改。

### 聚类对账要求

完成前必须更新 ledger 并核对：

- 原始输入条数
- 解析候选条数
- 重复条数
- 已核验并写入分类文件条数
- 当前问题清单条数
- 总入账条数

最终回复必须报告对账结果。若数量不平衡，继续排查，不要声称完成。

## 功能二：论文检索

用途：按用户临时给出的主题、方向、老师、团队或关键词，检索并筛选真正值得读的高水平论文，形成一次独立调研报告。

### 检索任务初始化

- 当用户要求按主题、方向、老师、团队或关键词找论文时，使用此能力；用户会在请求里说明目标，不要把随机主题写死在 skill 里。
- 开始检索前先确定编号和目的名：运行 `python3 .agents/skills/team-organisation/scripts/init_paper_search.py <Purpose>`，用脚本返回的 `workspace` 和 `output` 路径。不能靠记忆决定编号。
- 论文检索必须连接 Chrome 做增强检索，用 Chrome 扩大覆盖面、检查搜索结果排序、打开作者主页/项目页/出版社页面，并对题名、venue、年份、DOI、摘要做精确核验。
- 每次检索只维护必要工作区记录，默认写入 `evidence.md`。记录应在筛选过程中产生，不为满足格式在最终决定后补写。`evidence.md` 至少包含：关键查询/入口、进入候选池的论文、可靠来源、入选/排除理由、用户特别要求的排除项。
- 只有当论文来源矛盾、主题边界模糊、需要多页交叉核验，或用户明确要求时，才为单篇论文建立 `notes/<slug>.md`。不要为每篇已明确入选或明确排除的论文机械创建笔记。
- `metadata/` 只保存会复用或能显著降低后续核验成本的结构化材料；普通搜索结果不需要缓存全文。

### 检索质量要求

- 只检索和筛选真正有影响力的论文：优先顶级会议、顶级期刊、权威综述、领域公认代表作、被高频引用或被重要团队持续使用的工作。不要用普通 B 会、低影响会议、无关 workshop、灌水期刊或来源不明网页凑数。
- 默认硬门槛：最终检索清单优先只收顶会顶刊和明确高影响代表作，例如 CVPR/ICCV/ECCV/NeurIPS/ICML/ICLR/AAAI/IJCAI/ACM MM，以及 IEEE TPAMI/TIP/TNNLS/TGRS、Information Fusion 等强相关高影响期刊。若某领域公认顶刊顶会另有惯例，可按任务说明，但必须在汇总中解释。
- 默认不纳入最终检索清单的降级来源：IEEE/CAA Journal of Automatica Sinica、IEEE Transactions on Multimedia、IEEE Transactions on Computational Imaging、IEEE ICME，以及同等影响力较低、B 区或普通会议/期刊。它们可以作为背景、参考链或候选线索，但不能因为作者是目标老师/团队就进入“核心入选论文”。
- 只有用户明确要求“尽量全收”“包括 B 区/普通会议/团队全部论文”时，才可把上述降级来源单独放入“补充论文/不优先阅读”小节；不得与核心顶会顶刊论文平级。
- 检索顺序必须从近到远：先查最近 1-3 年顶会顶刊和最新综述，再回溯奠基论文与经典高引论文。若用户要某位老师，先查该老师近年代表作和主页/Google Scholar/DBLP，再回溯其长期方向。
- 优先来源：Google Scholar、DBLP、Semantic Scholar、arXiv、OpenReview、CVF、PMLR/ICML、NeurIPS、ICLR、AAAI、IJCAI、IEEE TPAMI/TIP/TGRS/TNNLS、ACM MM/TOG/TOIS、Information Fusion、Nature/Science 系列、项目页和作者主页。二级网页只能辅助定位，不能替代可靠来源。
- Chrome 搜索结果只能作为发现线索；最终入选必须回到论文官网、出版社、作者主页、DBLP、Google Scholar、Semantic Scholar、OpenReview、arXiv 或其他可靠来源核验。
- 检索到候选论文后必须先评估再决定是否写入最终汇总；评估可以是简短的一行证据台账，不要求长笔记。明显低质量、弱相关或重复论文可批量记录排除理由，不要逐篇展开浪费上下文。

### 检索最终汇总

- 最终汇总必须按时间由近及远排列；同年优先顶刊/顶会、代表性和影响力更高者。单篇介绍必须比 `论文分类归纳整理.md` 更详细，至少包含：题名、年份/ venue、链接、作者/团队、核心问题、方法要点、主要贡献、影响力/可信度信号、与本次检索目标的关系、阅读建议。
- 输出到 `Base/Paper_Search/<NN>_<Purpose>.md`。文件结构建议包含：检索目标、检索范围与口径、近年核心论文、经典基础、排除/不优先论文、后续检索线索。
- 若检索结果不足，明确说明缺口和已查来源；不要用低质量论文补齐数量。

## 维护偏好

- 小文件优先：分类小文件是事实来源，汇总文件是生成物。
- 搜索日志放 `crawl_drafts/`；结构化记录放 `metadata/`；跨轮状态放 `state/`。
- 大量重复或格式化操作优先改脚本，不在对话里重复手写。
- Chrome 搜索过程只记录影响取舍的关键来源、受限页面和最终判断；避免把浏览过程流水账写进工作区。
