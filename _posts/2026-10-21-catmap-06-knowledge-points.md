---
layout: post
title: "catmap-06-knowledge-points"
date: 2026-10-21 10:00:00 +0800
---

1.己烯环氧化微观动力学推导公式

$$
\boxed{
TOF=
\underbrace{\frac{k_BT}{h}
e^{-\Delta G_{\rm RDS}^{\ddagger}/k_BT}}_{\text{本征动力学}}
\cdot
\underbrace{K_{\rm C_6H_{12}}
\frac{P_{\rm C_6H_{12}}}{P^\circ}}_{\text{己烯吸附}}
\cdot
\underbrace{\theta_{\rm OOH}}_{\text{关键中间体}}
\cdot
\underbrace{\theta_*^2}_{\text{可用位点}}
}
$$

https://chatgpt.com/s/t_6adef2dfa5c48191840d3435346903eb

2.H:\catmap\Official_catmap_epoxidation\hexene_epoxidation\output_variables\mkm_job.py 修改色度条间隔方法

$$
\text{刻度间隔}=\max\left(\left\lfloor\frac{29}{n_{\mathrm{ticks}}}\right\rfloor,1\right)
$$

https://chatgpt.com/s/t_6ae004391abc8191af4be2e93670bbde

3.增加TOF DRC 相关的分析模块

![2026-10-21-catmap-06-knowledge-points.md-2026-10-27_10-58-21-2902420f](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-10-21-catmap-06-knowledge-points.md-2026-10-27_10-58-21-2902420f.png)

https://chatgpt.com/s/t_6ae0132142108191b204f47ab0f00278

4.如果我想说明OOH物种是动力学筛选后的关键物种 我下一步电子机制中会重点分析OOH吸附能相关 的 **桥连 OOH 稳定化的电子调控机制** 这里是选择OOH 吸附能与 logTOF 高相关性还是 OOH 覆盖度与 logTOF\* 相关性 这种**逻辑过渡**有无权威文献支持？

2016 年 Physical Chemistry Chemical Physics 的原位 Raman 研究，已经在 TS-1 丙烯环氧化中观察到：骨架 Ti 物种含量、Ti–OOH 活性中间体数量和丙烯转化率之间存在正相关关系。这篇文献与你希望通过覆盖度关联催化活性来识别关键中间体的思路非常接近

https://chatgpt.com/s/t_6ae016130d048191b3b9328f22cc40ed

5.对于小论文研究内容一，核心的逻辑 判断 OOH* 究竟是重要的反应前驱体、显著控制速率的中间体，还是主要表现为表面累积物种？

具体操作输出了OOH相关动力学位点数据 https://chatgpt.com/s/t_6ae01a7468d08191b8c1efd11ba4bb1b 未成功 数据维度有误

![2026-10-21-catmap-06-knowledge-points.md-2026-10-27_15-50-47-c300f19a](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-10-21-catmap-06-knowledge-points.md-2026-10-27_15-50-47-c300f19a.png)

调整绝对容差后没有解决数据维度的问题

核验失败究竟来自求根过程、数值判据，还是稳态本身不满足要求？

原因1：收敛精度与实际反应速率的数量级不匹配

5.强化C6H12O火山关系 做出的绘图等相关调整


