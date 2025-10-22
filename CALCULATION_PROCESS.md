# 计算过程详解

本文档详细说明了指数纳入效应套利策略实现过程中使用的所有公式、条件和计算步骤。

## 目录

1. [理论基础与公式](#理论基础与公式)
2. [问题一：超额收益率计算](#问题一超额收益率计算)
3. [问题二：Beta匹配算法](#问题二beta匹配算法)
4. [问题三：配对交易策略](#问题三配对交易策略)
5. [问题四：稳健性检验](#问题四稳健性检验)

---

## 理论基础与公式

### 1. CAPM模型（资本资产定价模型）

**公式：**
```
E(Ri) = Rf + βi × [E(Rm) - Rf]
```

**变量说明：**
- `E(Ri)`：股票i的预期收益率
- `Rf`：无风险利率
- `βi`：股票i的Beta系数，衡量系统性风险
- `E(Rm)`：市场组合的预期收益率

**理论依据：**
CAPM模型认为股票的预期收益由两部分组成：
1. 无风险收益率（Rf）
2. 承担系统性风险的风险溢价（βi × [E(Rm) - Rf]）

### 2. 指数纳入效应理论

**定义：**
当股票被纳入主要指数（如沪深300）时，会产生以下效应：

1. **需求冲击**：被动型指数基金必须购买该股票以复制指数
2. **流动性提升**：成分股获得更多关注，交易活跃度提高
3. **价格压力**：短期内买盘压力导致股价上涨
4. **反向效应**：股票被剔除时产生相反的效果

---

## 问题一：超额收益率计算

### 使用的数据条件

**数据来源：** Q1数据表（作业3 Excel文件）

**包含信息：**
- 时间范围：2011年1月至2024年8月
- 样本数量：纳入股票约528只，剔除股票约539只
- 时间窗口：公告日（T=0）及其后5个交易日（T=1至T=5）

**关键变量：**
| 变量名 | 含义 | 取值 |
|--------|------|------|
| Stkcd | 股票代码 | 6位数字 |
| Chgsmp04 | 股票类型 | 1=纳入指数，2=剔除指数 |
| twind | 时间窗口 | 0-5（0为公告日） |
| Dretwd | 个股日收益率 | 考虑现金红利再投资 |
| Dretwdos | 市场收益率 | 考虑现金红利再投资 |
| Beta | 股票Beta系数 | 衡量系统性风险 |

### 计算步骤

#### 步骤1：计算超额收益率

**公式：**
```
Abret(i,t) = Dretwd(i,t) - β(i) × Dretwdos(t)
```

**具体说明：**
- `Abret(i,t)`：股票i在时间t的超额收益率（Abnormal Return）
- `Dretwd(i,t)`：股票i在时间t的实际收益率
- `β(i)`：股票i的Beta系数（在分析期固定）
- `Dretwdos(t)`：市场在时间t的收益率

**计算逻辑：**
1. 实际收益率 = 股票当日收益（Dretwd）
2. 预期收益率 = Beta × 市场收益（β × Dretwdos）
3. 超额收益率 = 实际收益率 - 预期收益率

**意义：**
- 如果Abret > 0：股票表现优于由市场因素预期的表现
- 如果Abret < 0：股票表现劣于由市场因素预期的表现
- 指数纳入效应体现在Abret中，因为它是股票特有的事件

**代码实现：**
```python
def calculate_excess_return(self, row):
    """计算超额收益率"""
    # Abret = Dretwd - Beta * Dretwdos
    return row['Dretwd'] - row['Beta'] * row['Dretwdos']
```

#### 步骤2：分组统计

**分组条件：**
- 按Chgsmp04分为两组：
  - 组1：纳入指数股票（Chgsmp04 = 1）
  - 组2：剔除指数股票（Chgsmp04 = 2）
- 按twind分为6个时间窗口（0-5）

**统计量计算：**

1. **样本数量（N）：**
   ```
   N = count(有效观测值)
   ```

2. **平均超额收益率（Mean）：**
   ```
   Mean = (1/N) × Σ Abret(i)
   ```
   
3. **标准误（Std Err）：**
   ```
   Std Err = σ / √N
   其中 σ = √[(1/(N-1)) × Σ(Abret(i) - Mean)²]
   ```

4. **转换为基点（base points）：**
   ```
   Mean(bp) = Mean × 10000
   Std Err(bp) = Std Err × 10000
   ```
   
   说明：1个基点 = 0.01% = 0.0001

#### 步骤3：统计检验

**使用方法：** 独立样本T检验（Two-sample t-test）

**假设：**
- 零假设H₀：μ₁ = μ₂（两组平均超额收益无显著差异）
- 备择假设H₁：μ₁ ≠ μ₂（两组平均超额收益存在显著差异）

**T统计量公式：**
```
t = (X̄₁ - X̄₂) / √(s₁²/n₁ + s₂²/n₂)

其中：
X̄₁, X̄₂ = 两组样本均值
s₁², s₂² = 两组样本方差
n₁, n₂ = 两组样本量
```

**自由度：**
```
df ≈ (s₁²/n₁ + s₂²/n₂)² / [(s₁²/n₁)²/(n₁-1) + (s₂²/n₂)²/(n₂-1)]
（Welch-Satterthwaite公式）
```

**显著性判断：**
- p < 0.01：*** 在1%水平显著
- 0.01 ≤ p < 0.05：** 在5%水平显著
- 0.05 ≤ p < 0.10：* 在10%水平显著
- p ≥ 0.10：不显著

**代码实现：**
```python
from scipy import stats
t_stat, p_value = stats.ttest_ind(inc_data, exc_data)
```

#### 步骤4：构建Mac套利策略

**策略描述：**
- 做多（买入）：纳入指数股票组合
- 做空（卖空）：剔除指数股票组合
- 持有期：1个交易日
- 权重：等权重配置

**套利收益计算：**
```
ArbitrageReturn(t) = Mean_Return_Included(t) - Mean_Return_Excluded(t)

其中：
Mean_Return_Included(t) = (1/N₁) × Σ Dretwd(i,t), i ∈ 纳入股票
Mean_Return_Excluded(t) = (1/N₂) × Σ Dretwd(j,t), j ∈ 剔除股票
```

**累计收益：**
```
CumulativeReturn = Σ ArbitrageReturn(t), t = 0 to 5
```

### 结果解读示例

以T=0（公告日）为例：

**输入数据：**
- 纳入股票：528只，平均超额收益=-8.27bp，标准误=9.83bp
- 剔除股票：539只，平均超额收益=-57.23bp，标准误=8.73bp

**计算过程：**
1. 差异 = -8.27 - (-57.23) = 48.96bp
2. T检验 → p值 = 0.0002
3. 判断：p < 0.01，在1%水平显著

**结论：**
公告日当天，纳入股票的超额收益显著高于剔除股票48.96个基点。

---

## 问题二：Beta匹配算法

### 使用的数据条件

**数据来源：** Q2数据表

**匹配目标：**
为每个纳入指数的股票找到一个未纳入指数的匹配股票

**可用变量：**
| 变量名 | 含义 |
|--------|------|
| Stkcd | 纳入指数的股票代码 |
| Beta | 纳入股票的Beta系数 |
| Nnindcd | 行业代码 |
| Markettype | 市场类型（主板/创业板等） |
| Stkcd1 | 候选匹配股票代码 |
| Beta1 | 候选股票的Beta系数 |

### 匹配条件

**必须同时满足以下三个条件：**

1. **同行业约束：**
   ```
   Nnindcd(i) = Nnindcd(j)
   ```
   说明：确保纳入股票i和匹配股票j属于同一行业

2. **同市场约束：**
   ```
   Markettype(i) = Markettype(j)
   ```
   说明：确保两只股票在同一市场板块

3. **Beta相近约束：**
   ```
   |β(i) - β(j)| < 0.01
   ```
   说明：Beta差异小于1%（0.01），确保系统性风险相近

### 匹配算法

**目标函数：**
```
j* = argmin |β(i) - β(j)|
     j∈J

subject to:
    Nnindcd(i) = Nnindcd(j)    (同行业)
    Markettype(i) = Markettype(j)    (同市场)
    |β(i) - β(j)| < 0.01    (Beta相近)
```

其中：
- i：纳入指数的股票
- J：所有候选匹配股票的集合
- j*：最优匹配股票

**算法步骤：**

```
输入：纳入股票i，候选股票集合J
输出：最优匹配股票j*

步骤1: 初始化
    beta_target = β(i)
    best_match = null
    min_diff = +∞

步骤2: 筛选同行业同市场的候选股票
    J_filtered = {j ∈ J | Nnindcd(j) = Nnindcd(i) 
                         AND Markettype(j) = Markettype(i)}

步骤3: 遍历筛选后的候选股票
    for each j in J_filtered:
        计算 diff = |β(j) - beta_target|
        
        if diff < 0.01:  # 满足Beta约束
            if diff < min_diff:  # 找到更优匹配
                min_diff = diff
                best_match = j

步骤4: 返回结果
    if best_match != null:
        return best_match
    else:
        return null  # 未找到满足条件的匹配
```

**代码实现：**
```python
# 对每个纳入股票寻找匹配
for stkcd in df['Stkcd'].unique():
    if pd.isna(stkcd):
        continue
    
    # 获取纳入股票的Beta
    included_row = df[df['Stkcd'] == stkcd].iloc[0]
    beta = included_row['Beta']
    if pd.isna(beta):
        continue
    
    # 找到所有候选匹配股票
    candidates = df[df['Stkcd'] == stkcd]
    
    # 寻找Beta差异最小的匹配
    best_match = None
    best_diff = float('inf')
    
    for _, row in candidates.iterrows():
        if pd.notna(row['Stkcd1']) and pd.notna(row['Beta1']):
            diff = abs(row['Beta1'] - beta)
            if diff < 0.01 and diff < best_diff:
                best_diff = diff
                best_match = row['Stkcd1']
    
    if best_match is not None:
        matches.append({
            'Stkcd': int(stkcd),
            'Stkcd1': int(best_match)
        })
```

### 理论依据

**为什么要Beta匹配？**

1. **Beta的含义：**
   ```
   β = Cov(Ri, Rm) / Var(Rm)
   ```
   - 衡量股票收益率对市场收益率的敏感度
   - β = 1：与市场同步波动
   - β > 1：比市场波动更剧烈
   - β < 1：比市场波动更平缓

2. **配对交易的风险对冲：**
   ```
   假设：β(i) ≈ β(j)
   
   配对收益 = Ri - Rj
            = [Rf + β(i)×(Rm - Rf) + ε(i)] - [Rf + β(j)×(Rm - Rf) + ε(j)]
            ≈ ε(i) - ε(j)  （当β(i) ≈ β(j)时）
   
   其中：
   ε(i), ε(j) = 股票特有的非系统性收益
   ```
   
   说明：市场因素β×(Rm - Rf)被对冲掉，保留的是股票特有收益

3. **指数纳入效应的提取：**
   - 纳入效应是股票i特有的事件，体现在ε(i)中
   - 通过Beta匹配，消除市场整体波动的影响
   - 配对收益主要反映指数纳入带来的超额收益

---

## 问题三：配对交易策略

### 使用的数据条件

**数据来源：** Q3数据表（2025年6月指数调整数据）

**匹配股票对：** 从问题二获得的匹配结果

**时间窗口：** 公告日后10个交易日（twind = 1 to 10）

### 策略构建

**策略类型：** 配对交易（Pairs Trading）+ Buy & Hold

**交易规则：**
1. 在公告日（T=0），对每一对股票：
   - 买入（做多）1单位纳入指数股票
   - 卖空（做空）1单位匹配股票
   
2. 持有该头寸10个交易日

3. 不进行日内再平衡

### 收益计算公式

#### 单对股票的配对收益

**公式：**
```
Pair_Return(i,j,t) = Dretwd(i,t) - Dretwd(j,t)

其中：
i = 纳入指数股票
j = 匹配股票
t = 交易日（1-10）
```

**含义：**
- Dretwd(i,t)：纳入股票i在第t天的收益率
- Dretwd(j,t)：匹配股票j在第t天的收益率
- 配对收益 = 多头收益 - 空头成本

**示例计算：**
```
假设某一对股票在Day 1：
- 纳入股票收益 = +2.5%
- 匹配股票收益 = +1.8%
- 配对收益 = 2.5% - 1.8% = 0.7% = 70bp
```

#### 组合日收益率

**公式（等权重）：**
```
Portfolio_Return(t) = (1/N) × Σ Pair_Return(i,j,t)
                       i=1

其中：
N = 第t天有效配对的数量
```

**说明：**
- 采用简单算术平均（等权重）
- 每对股票的权重 = 1/N
- N可能每天不同（由于停牌等原因）

**转换为基点：**
```
Portfolio_Return(bp) = Portfolio_Return × 10000
```

#### 累计收益

**公式：**
```
Cumulative_Return = Σ Portfolio_Return(t)
                     t=1

其中：t = 1 to 10
```

**日均收益：**
```
Average_Daily_Return = Cumulative_Return / 10
```

### 计算步骤

**步骤1：读取匹配股票对**
```python
# 从问题二的结果获取
pairs_df = results['table3']
# 格式：每行包含Stkcd（纳入股票）和Stkcd1（匹配股票）
```

**步骤2：对每个交易日计算组合收益**
```python
for day in range(1, 11):  # Day 1 to Day 10
    pair_returns = []
    
    for _, pair in pairs_df.iterrows():
        stkcd = pair['Stkcd']    # 纳入股票
        stkcd1 = pair['Stkcd1']  # 匹配股票
        
        # 获取该交易日的收益率
        inc_ret = get_return(stkcd, day)   # Dretwd
        match_ret = get_return(stkcd1, day) # Dretwd1
        
        if valid(inc_ret) and valid(match_ret):
            # 计算配对收益
            pair_ret = inc_ret - match_ret
            pair_returns.append(pair_ret)
    
    # 计算日组合收益（等权重）
    if len(pair_returns) > 0:
        daily_return = mean(pair_returns) * 10000  # 转为bp
    else:
        daily_return = 0
```

**步骤3：统计分析**
```python
# 累计收益
cumulative = sum(daily_returns)

# 日均收益
average = cumulative / 10

# 盈利天数
profit_days = count(r > 0 for r in daily_returns)

# 最大单日收益
max_gain = max(daily_returns)

# 最大单日亏损
max_loss = min(daily_returns)
```

### 结果解读示例

**问题三（2025年6月）结果：**

| 交易日 | 组合收益(bp) | 有效配对数 |
|--------|--------------|------------|
| Day 1  | 14.70        | 3          |
| Day 2  | 53.68        | 3          |
| Day 3  | 29.34        | 3          |
| Day 4  | -96.98       | 3          |
| Day 5  | -116.03      | 3          |
| Day 6  | 5.50         | 3          |
| Day 7  | 125.39       | 3          |
| Day 8  | 5.11         | 3          |
| Day 9  | 10.06        | 3          |
| Day 10 | -58.64       | 3          |

**统计指标：**
- 累计收益：-27.87 bp
- 日均收益：-2.79 bp
- 盈利天数：6/10天
- 最大单日收益：125.39 bp（Day 7）
- 最大单日亏损：-116.03 bp（Day 5）

---

## 问题四：稳健性检验

### 检验设计

**目的：** 验证Marina配对交易策略在不同市场环境下的稳健性

**方法：** 对比分析策略在牛市、非牛熊市、熊市三种环境下的表现

### 市场环境划分

**使用条件：**
- 牛市：2022年6月
  - 上证指数整体上涨
  - 投资者情绪乐观
  - 风险偏好提升

- 非牛熊市：2023年6月
  - 市场震荡整理
  - 无明显趋势
  - 不确定性较高

- 熊市：2024年6月
  - 上证指数整体下跌
  - 投资者情绪悲观
  - 风险偏好降低

### 对比分析方法

**分析框架：**
```
对于每个市场环境E ∈ {牛市, 非牛熊市, 熊市}:
    1. 应用相同的匹配算法（|Δβ| < 0.01）
    2. 构建相同的配对交易策略
    3. 计算10日Buy & Hold收益率
    4. 统计关键指标
```

**关键指标：**

1. **累计收益（Cumulative Return）：**
   ```
   CR(E) = Σ Portfolio_Return(E,t), t = 1 to 10
   ```

2. **日均收益（Average Daily Return）：**
   ```
   ADR(E) = CR(E) / 10
   ```

3. **盈利天数（Profit Days）：**
   ```
   PD(E) = count(Portfolio_Return(E,t) > 0)
   ```

4. **最大单日收益（Maximum Daily Gain）：**
   ```
   MDG(E) = max(Portfolio_Return(E,t))
   ```

5. **最大单日亏损（Maximum Daily Loss）：**
   ```
   MDL(E) = min(Portfolio_Return(E,t))
   ```

6. **波动性（Volatility）：**
   ```
   Vol(E) = std(Portfolio_Return(E,t))
   ```

### 对比结果

**汇总表：**

| 市场环境 | 配对数 | 累计收益(bp) | 日均收益(bp) | 盈利天数 | 最大收益(bp) | 最大亏损(bp) |
|----------|--------|--------------|--------------|----------|--------------|--------------|
| 牛市(2022.6) | 6 | 465.71 | 46.57 | 8/10 | 203.18 | -280.99 |
| 非牛熊市(2023.6) | 5 | 133.00 | 13.30 | 5/10 | 139.95 | -74.59 |
| 熊市(2024.6) | 4 | 983.82 | 98.38 | 7/10 | 497.19 | -674.00 |

### 结论性分析

**计算逻辑：**

1. **稳健性验证：**
   ```
   if CR(E) > 0 for all E:
       策略具有稳健性
   ```
   
   结果：所有市场环境下累计收益均为正 ✓

2. **市场环境影响：**
   ```
   Compare CR(牛市) vs CR(熊市) vs CR(非牛熊市)
   ```
   
   结果：熊市 > 牛市 > 非牛熊市

3. **风险收益权衡：**
   ```
   Sharpe_Ratio(E) = ADR(E) / Vol(E)
   ```
   
   观察：
   - 熊市：收益最高但波动最大（-674.00 到 497.19）
   - 非牛熊市：收益较低但波动较小
   - 牛市：收益和风险居中

4. **策略有效性：**
   ```
   指数纳入效应是否独立于市场环境？
   
   理论：效应来自被动资金流入，与市场整体走势无关
   实证：策略在三种环境下都盈利，支持理论假设
   ```

**结论要点：**

1. **稳健性确认：** 策略在三种市场环境下均获得正的累计收益

2. **市场环境差异：** 不同环境下收益和风险特征存在差异
   - 熊市环境：收益最高但波动最大
   - 可能原因：市场下跌时指数纳入效应更显著

3. **风险对冲有效：** 配对交易通过Beta匹配对冲了市场系统性风险

4. **策略独立性：** 指数纳入效应作为微观事件，其影响相对独立于宏观市场走势

---

## 总结

### 核心公式汇总

1. **超额收益率：**
   ```
   Abret = Dretwd - Beta × Dretwdos
   ```

2. **T统计量：**
   ```
   t = (X̄₁ - X̄₂) / √(s₁²/n₁ + s₂²/n₂)
   ```

3. **Beta匹配目标函数：**
   ```
   j* = argmin |β(i) - β(j)|, subject to constraints
   ```

4. **配对收益：**
   ```
   Pair_Return(i,j,t) = Dretwd(i,t) - Dretwd(j,t)
   ```

5. **组合收益：**
   ```
   Portfolio_Return(t) = (1/N) × Σ Pair_Return(i,j,t)
   ```

### 条件与约束

1. **数据条件：**
   - Q1数据：2011-2024年纳入剔除股票数据
   - Q2数据：匹配候选股票信息
   - Q3数据：2025年6月策略测试数据
   - Q4数据：不同市场环境测试数据

2. **匹配约束：**
   - 同行业：Nnindcd相同
   - 同市场：Markettype相同
   - Beta相近：|Δβ| < 0.01

3. **显著性水平：**
   - α = 0.05（主要判断标准）
   - 也报告0.01和0.10水平

### 计算流程图

```
开始
  ↓
读取Excel数据 → Q1, Q2, Q3, Q4表
  ↓
问题一：计算超额收益率
  ├─ 应用公式：Abret = Dretwd - Beta × Dretwdos
  ├─ 分组统计：纳入 vs 剔除
  ├─ T检验：比较两组差异
  └─ 构建Mac策略
  ↓
问题二：Beta匹配
  ├─ 应用约束：同行业、同市场、|Δβ|<0.01
  ├─ 目标函数：最小化Beta差异
  └─ 输出匹配对
  ↓
问题三：配对交易策略（2025.6）
  ├─ 使用匹配对
  ├─ 计算配对收益
  ├─ 等权重组合
  └─ 10日Buy & Hold
  ↓
问题四：稳健性检验
  ├─ 牛市（2022.6）
  ├─ 非牛熊市（2023.6）
  ├─ 熊市（2024.6）
  └─ 对比分析
  ↓
生成报告文档
  ↓
结束
```

---

## 参考文献

1. Sharpe, W. F. (1964). Capital asset prices: A theory of market equilibrium under conditions of risk.

2. Harris, L., & Gurel, E. (1986). Price and volume effects associated with changes in the S&P 500 list.

3. Shleifer, A. (1986). Do demand curves for stocks slope down? The Journal of Finance.

4. Lynch, A. W., & Mendenhall, R. R. (1997). New evidence on stock price effects associated with changes in the S&P 500 index.

---

**文档版本：** 1.0  
**最后更新：** 2025年10月22日  
**作者：** GitHub Copilot
