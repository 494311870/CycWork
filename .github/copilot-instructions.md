# CycWork Project - AI Agent Instructions

## Project Overview
This is a quantitative finance project focused on implementing index inclusion effect arbitrage strategies (指数纳入效应套利策略). The project workspace currently contains research documents and is set up for developing trading algorithms and analysis tools.

## Project Structure and Context
- **Core Documents**: Two key files contain the project requirements and specifications:
  - `作业3 （学生用）指数纳入效应套利策略的实现.docx` - Main project documentation
  - `作业3 （学生用）指数纳入效应套利策略的实现.xlsx` - Data analysis and calculations
- **Development Stage**: This project is in early stages, currently containing specification documents

## Expected Development Patterns

### Code Organization
When implementing code for this project, expect to create:
- **Data processing modules** for handling financial market data
- **Strategy implementation** files for arbitrage algorithms
- **Backtesting frameworks** for validating strategies
- **Visualization tools** for performance analysis

### Financial Domain Conventions
- Use consistent naming for financial concepts (e.g., `inclusion_date`, `announcement_date`, `rebalancing_period`)
- Implement proper data validation for financial time series
- Handle market holidays and trading calendar considerations
- Follow risk management principles in strategy implementation

### Development Workflow
- **Data Sources**: Expect integration with financial data providers
- **Testing**: Implement both unit tests for individual components and backtesting for strategies
- **Documentation**: Maintain clear documentation of mathematical models and assumptions
- **Performance**: Focus on computational efficiency for large-scale data processing

## Key Implementation Areas

### Index Inclusion Effect Analysis
- Track announcement and inclusion dates for index changes
- Calculate abnormal returns around inclusion events
- Implement statistical significance testing

### Arbitrage Strategy Development
- Develop position sizing algorithms
- Implement risk controls and stop-loss mechanisms
- Create portfolio optimization routines

### Data Management
- Handle multiple data frequencies (daily, intraday)
- Implement data cleaning and outlier detection
- Manage corporate actions and stock splits

## Technical Considerations
- **Language Choice**: Python typically preferred for quantitative finance (pandas, numpy, scipy)
- **Performance**: Consider vectorized operations for large datasets
- **Dependencies**: Expect use of financial libraries (quantlib, zipline, backtrader)
- **Data Storage**: Plan for efficient storage of time series data

## Getting Started
1. Review the specification documents to understand requirements
2. Set up development environment with financial data analysis libraries
3. Implement data ingestion pipeline first
4. Develop strategy logic incrementally with proper testing
5. Create visualization tools for strategy performance analysis



## Submit log specifications

为保证历史清晰与自动化（例如生成变更日志、触发 CI 分支规则），本项目遵循基于 "Conventional Commits" 的简化规范：

- 格式：

    <type>(<scope>): <short summary>

    - type（必需）：feat | fix | docs | style | refactor | perf | test | chore | build | ci | revert
    - scope（可选）：受影响模块或目录，例如 `assets`, `scripts`, `scenes`, `ui`。
    - short summary（必需）：总长不超过 72 个字符，首字母小写，不以句号结束。

- 主体（可选）：空行后写更详细的变更说明。行宽建议 100 字以内。

- 页脚（可选）：用于引用 issue 或标注 BREAKING CHANGE。例如：


        BREAKING CHANGE: 描述破坏性变更的简要说明

        或者引用 issue：

            `Fixes Issue-123`, `See Issue-45`

- 示例：

- 示例（type 保持英文，日志内容请使用中文）：

    feat(scripts): 添加 TileSpawner 组件以生成方格

    fix(ui): 修复小屏幕下按钮布局溢出问题

    docs: 更新 README，补充 Cocos Creator 3.8.7 的构建步骤说明


---
*This workspace is configured for quantitative finance development. When implementing features, prioritize data integrity, computational efficiency, and proper statistical methodology.*