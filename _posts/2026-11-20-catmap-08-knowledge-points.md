---
layout: post
title: "catmap-08-knowledge-points"
date: 2026-11-20 20:30:23 +0800
---

1.catmap微观动力学求解表观级数

![2026-11-20-catmap-08-knowledge-points.md-2026-11-20_20-33-25-e317ab50](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-11-20-catmap-08-knowledge-points.md-2026-11-20_20-33-25-e317ab50.png)

![2026-11-20-catmap-08-knowledge-points.md-2026-11-20_20-31-56-fe1110c5](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-11-20-catmap-08-knowledge-points.md-2026-11-20_20-31-56-fe1110c5.png)

https://mp.weixin.qq.com/s/VePuCbIvaqaM3VTTdZaBvQ?scene=1&click_id=317724623

2.火山图反着来火山中心，其中OH覆盖度过高
![2026-11-20-catmap-08-knowledge-points.md-2026-11-23_08-57-48-3b5c3710](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-11-20-catmap-08-knowledge-points.md-2026-11-23_08-57-48-3b5c3710.png)

发现另一个问题 不能按照活性位为1 因为Ha OOH可以同时吸附在Ti-O-M上 和原来的假设每个活性位只能吸附一个原子是不一致的 这里有必要认为是多个吸附点

多位点吸附模型

一个是这个解离吸附是否是可逆的 另一个HaOOH_s解离后的共吸附态 这么写是否正确
![2026-11-20-catmap-08-knowledge-points.md-2026-11-23_16-15-38-9f007f50](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-11-20-catmap-08-knowledge-points.md-2026-11-23_16-15-38-9f007f50.png)

解离吸附可逆性https://chatgpt.com/s/t_6b03f8835cd48191a75e84a895de7b90
共吸附态 当中 只能认为己烯吸附是可逆的https://chatgpt.com/s/t_6b03f8ba43ac8191aa556164ad54a292

当前考虑的多位点吸附模型
titi 活性最高 需要调整 但是火山图规范
![2026-11-20-catmap-08-knowledge-points.md-2026-11-23_17-10-27-ac423942](https://raw.githubusercontent.com/ly5681672-max/ly5681672-max.github.io/main/assets/img/learning-notes/2026-11-20-catmap-08-knowledge-points.md-2026-11-23_17-10-27-ac423942.png)


怀疑是标度关系和catmap能量转换掩盖了原来的环氧化能垒大于氢转移能垒

还是不能去掉共吸附态 其次处理标度关系
通过调整catmap内置的标度关系参数

还发现问题 catmap求解出来的不是真根
**"不是真根"的根源不是求解器不够强，而是 CatMAP 的验收判据量的是预处理尺度、且它的投影算子会造出残差为零的非物理不动点。**所以真根只能这样认定：用原始 s⁻¹ 残差对 kBT/h 归一化（G1）+ 通量闭合恒等式（G4）+ 容量上界否证（G5）+ 非回显（G6） 四者交叉，其中任何单一条都会漏（ti 和 tizr 在 G1 上比 tini 还漂亮）。
按这套判据，15 面 × 21 λ = 315 个格点里，过全部门的目前只有 tini 全段（λ=0–1）、timn 全段（21/21）、tire λ≤0.90，其余 12 面在真面 λ=1 上无根
