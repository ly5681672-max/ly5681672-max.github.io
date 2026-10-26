---
layout: post
title: "catmap-05-knowledge-points"
date: 2026-10-21 10:00:00 +0800
---

https://chatgpt.com/s/t_6ad8227edc648191b3ab63a526ab3a42

1.Ti-W Ti-Ta这种环氧化过渡态能量低于初态的 catmap上述处理方法不当 导致得到的TOF偏低❌


![2026-10-21-catmap-05-knowledge-points.md-2026-10-22_17-31-13-9b27b7c5](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-10-21-catmap-05-knowledge-points.md-2026-10-22_17-31-13-9b27b7c5.png)

2.Codex复现多次主线跑偏 如何根据官网进行微观动力学分析

https://chatgpt.com/s/t_6adac97015d08191ba75914f6b7cd42d

3.对于catmap 八步机理模型 如何处理DFT得到的数据和catmap输入数据对应关系

H:\catmap\catmap\lyq_alkene_epoxidation\2-creating_microkinetic_model\energies_dft_neb.txt
H:\catmap\catmap\lyq_alkene_epoxidation\2-creating_microkinetic_model\alkene_epoxidation.mkm

八步显式 OOH* 模型的输入文件和已归档动力学结果，主要在以下位置：

**模型与能量输入**

- `.mkm` 反应模型：[alkene_epoxidation.mkm](</H:/catmap/catmap/lyq_alkene_epoxidation/2-creating_microkinetic_model/alkene_epoxidation.mkm>)  
  `H:\catmap\catmap\lyq_alkene_epoxidation\2-creating_microkinetic_model\alkene_epoxidation.mkm`
- Gibbs/NEB 能量输入：[energies_dft_neb.txt](</H:/catmap/catmap/lyq_alkene_epoxidation/2-creating_microkinetic_model/energies_dft_neb.txt>)  
  `H:\catmap\catmap\lyq_alkene_epoxidation\2-creating_microkinetic_model\energies_dft_neb.txt`
- 原始模型运行脚本：[run_ooh_analysis.py](</H:/catmap/catmap/lyq_alkene_epoxidation/2-creating_microkinetic_model/run_ooh_analysis.py>)  
  `H:\catmap\catmap\lyq_alkene_epoxidation\2-creating_microkinetic_model\run_ooh_analysis.py`
- 该目录还归档有旧运行输出：[alkene_epoxidation.log](</H:/catmap/catmap/lyq_alkene_epoxidation/2-creating_microkinetic_model/alkene_epoxidation.log>)、[alkene_epoxidation_dft.pkl](</H:/catmap/catmap/lyq_alkene_epoxidation/2-creating_microkinetic_model/alkene_epoxidation_dft.pkl>)。它们是原始运行产物，不应与下方整理后的 14 位点结果表混为一谈。

**覆盖度、TOF 与 DRC 汇总**

- 14 位点覆盖度与 TOF：[14_SITE_TOF_COVERAGE.csv](</H:/catmap/catmap/catmap_code_collection_20261013/analyses/explicit_OOH_8step_validation/conditional_DRC_OOH_TOF_14sites/data/14_SITE_TOF_COVERAGE.csv>)  
  `H:\catmap\catmap\catmap_code_collection_20261013\analyses\explicit_OOH_8step_validation\conditional_DRC_OOH_TOF_14sites\data\14_SITE_TOF_COVERAGE.csv`
- 14 位点条件性 DRC：[14_SITE_CONDITIONAL_DRC.csv](</H:/catmap/catmap/catmap_code_collection_20261013/analyses/explicit_OOH_8step_validation/conditional_DRC_OOH_TOF_14sites/data/14_SITE_CONDITIONAL_DRC.csv>)
- DRC 数值门控：[DRC_NUMERICAL_GATE.csv](</H:/catmap/catmap/catmap_code_collection_20261013/analyses/explicit_OOH_8step_validation/conditional_DRC_OOH_TOF_14sites/data/DRC_NUMERICAL_GATE.csv>)

**逐步速率与覆盖度**

目录：  
`H:\catmap\catmap\catmap_code_collection_20261013\analyses\explicit_OOH_8step_validation\stepwise_kinetics_oxygen_transfer\data\`

其中包括：

- Ti–Co 八步速率常数：`TICO_8STEP_RATE_CONSTANTS.csv`
- Ti–Co 正逆及净反应速率：`TICO_8STEP_REACTION_RATES.csv`
- Ti–Co 稳态覆盖度：`TICO_STEADY_STATE_COVERAGES.csv`
- Ti–Co 氧转移与产物 TOF 核对：`TICO_OXYGEN_TRANSFER_TOF.csv`
- 14 位点氧转移/产物 TOF 汇总：`14SITE_OXYGEN_TRANSFER_TOF.csv`

**高精度逐位点求解根**

各位点求解根和相关数据按位点存放在：

`H:\catmap\catmap\catmap_code_collection_20261013\analyses\explicit_OOH_8step_validation\multisite_conditional_replay_20261021\sites\`

该目录下有 `ti`、`tico`、`tife` 等位点子目录。数值根用于追溯和复核；汇总表更方便查看覆盖度和 TOF。

上述整理结果属于八步模型下的条件性/暂定结果，数值求解结果不等于 NEB 能量映射已完成物理验证。查阅时建议先看 `14_SITE_TOF_COVERAGE.csv`；若要核对单个位点的稳态覆盖度和求根来源，再查对应的 `sites\<位点>` 子目录。


![2026-10-21-catmap-05-knowledge-points.md-2026-10-23_10-52-36-617ee17c](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-10-21-catmap-05-knowledge-points.md-2026-10-23_10-52-36-617ee17c.png)

3.Codex对于复现项目非常容易跑偏 需要 主线纠偏！

第一阶段： 下载 CatMAP 官方 GitHub 源代码及完整 tutorials 教程，使用官方原始文件逐步复现，不修改示例反应网络、输入数据和参数。

第二阶段： 依次完成官方教程中的输入文件生成、微观动力学模型求解、模型优化与绘图分析。

第三阶段： 官方案例复现通过后，再使用你已经认可的 energies_dft_neb.txt，独立复现 1-己烯环氧化

4.运行catmap 需要引用 

Vijay, S., H. Heenen, H., Singh, A. R., Chan, K., & Voss, J. (2024). Number of sites‐based solver for determining coverages from steady‐state mean‐field micro‐kinetic models. Journal of Computational Chemistry, 45(9), 546-551.
