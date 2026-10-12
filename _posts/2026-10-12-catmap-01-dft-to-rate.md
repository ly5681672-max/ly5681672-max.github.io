---
layout: post
title: "CatMAP中文学习笔记01：从DFT能量到反应速率"
description: "以Ti–Re催化1-己烯环氧化为例，理解反应能垒与速率常数"
date: 2026-10-12 12:00:00 +0800
categories: [catmap]
tags: [CatMAP, DFT, TST]
related_posts: false
---

# 一、为什么需要学习微观动力学？

DFT可以帮助我们计算吸附物种、反应中间体和过渡态的能量。

但是，仅凭这些能量，还不能直接判断催化剂的反应速率。

微观动力学的作用，是将反应能量与速率理论、表面覆盖度和基元反应网络联系起来。

## 二、从DFT能量到反应能垒

以Ti–Re催化剂的烯烃环氧化步骤为例。

模型中的初态为：

$$
\mathrm{OOH}^{\ast}+\mathrm{C}_{6}\mathrm{H}_{12}^{\ast}+\ast
$$

从CatMAP能量文件中提取：

- `OOH*`：-5.1042155 eV
- `C6H12*`：-26.1495385 eV
- `OOH-C6H12` 过渡态：-30.8089080 eV

采用模型中一致的能量参考系，初态能量为：

$$
G_{\mathrm{IS}} =
-5.1042155 - 26.1495385
= -31.2537540\ \mathrm{eV}
$$

前向自由能垒：

$$
\Delta G^{\ddagger} =
G_{\mathrm{TS}} - G_{\mathrm{IS}}
$$

$$
\Delta G^{\ddagger} =
-30.8089080 - (-31.2537540)
= 0.444846\ \mathrm{eV}
$$

这里的过渡态形成能来自NEB前向势垒映射，不能直接视为原始NEB绝对总能。

## 三、由能垒计算速率常数

根据简单过渡态理论：

$$
k = \frac{k_B T}{h}
\exp\left(-\frac{\Delta G^{\ddagger}}{k_B T}\right)
$$

其中：

- k_B：Boltzmann常数
- h：Planck常数
- T：绝对温度
- ΔG‡：反应自由能垒

假设温度为333.15 K，传输系数为1。

## 四、用Python手动计算

```python
import math

T = 333.15

G_OOH = -5.1042155
G_C6H12 = -26.1495385
G_TS = -30.8089080

G_IS = G_OOH + G_C6H12
barrier = G_TS - G_IS

kB_eV = 8.617333262145e-5
kB_SI = 1.380649e-23
h = 6.62607015e-34

k = (kB_SI * T / h) * math.exp(
    -barrier / (kB_eV * T)
)

print("反应能垒:", barrier, "eV")
print("前向速率常数:", f"{k:.4e}", "s^-1")
```

预期结果：

- 反应能垒约为0.444846 eV
- 前向速率常数约为1.29×10^6 s^-1

## 五、速率常数不等于TOF

对于这一涉及多个表面物种的基元反应，在简单平均场近似下，前向速率还与覆盖度有关：

$$
r_f =
k_f\theta_{\mathrm{OOH}}
\theta_{\mathrm{C_6H_{12}}}
\theta_{\ast}
$$

所以，能垒低并不意味着整体TOF一定高。

只有将完整反应网络、正逆反应以及表面物种守恒结合起来，才能进一步求解稳态覆盖度和产物生成速率。

## 六、本节总结

1. DFT提供反应能量信息。
2. 过渡态理论建立能垒与速率常数的联系。
3. 表面覆盖度决定反应发生的位点条件。
4. 完整微观动力学模型才能预测TOF。

## 参考资料

- [CatMAP官方文档](https://catmap.readthedocs.io/)
- [CatMAP官方GitHub](https://github.com/SUNCAT-Center/catmap)
- [本研究CatMAP代码仓库](https://github.com/ly5681672-max/catmap)
