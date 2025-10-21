#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作业3 指数纳入效应套利策略的实现
Index Inclusion Arbitrage Strategy Implementation
"""

import pandas as pd
import numpy as np
from scipy import stats
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Configure matplotlib for Chinese display
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class ArbitrageStrategyAnalyzer:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.results = {}
        
    def calculate_excess_return(self, row):
        """计算超额收益率"""
        # Abret = Dretwd - Beta * Dretwdos
        return row['Dretwd'] - row['Beta'] * row['Dretwdos']
    
    def solve_question1(self):
        """问题一：利用纳入和剔除股票来做套利"""
        print("=" * 80)
        print("问题一：计算纳入和剔除股票的超额收益")
        print("=" * 80)
        
        # Read Q1 data
        df = pd.read_excel(self.excel_file, sheet_name='Q1数据')
        
        # Calculate excess returns if not already in the data
        if 'Abret' in df.columns and df['Abret'].isna().all():
            df['Abret'] = df.apply(self.calculate_excess_return, axis=1)
        elif 'Abret' not in df.columns:
            df['Abret'] = df.apply(self.calculate_excess_return, axis=1)
        
        # Chgsmp04: 1=纳入, 2=剔除
        included = df[df['Chgsmp04'] == 1]
        excluded = df[df['Chgsmp04'] == 2]
        
        # Table 1: Calculate statistics for each time window
        table1_results = []
        
        for twind in range(6):
            # Included stocks
            inc_data = included[included['twind'] == twind]['Abret'].dropna()
            inc_n = len(inc_data)
            inc_mean = inc_data.mean() * 10000  # Convert to base points
            inc_stderr = inc_data.std() / np.sqrt(inc_n) * 10000 if inc_n > 0 else 0
            
            # Excluded stocks
            exc_data = excluded[excluded['twind'] == twind]['Abret'].dropna()
            exc_n = len(exc_data)
            exc_mean = exc_data.mean() * 10000
            exc_stderr = exc_data.std() / np.sqrt(exc_n) * 10000 if exc_n > 0 else 0
            
            # T-test for difference
            if inc_n > 0 and exc_n > 0:
                t_stat, p_value = stats.ttest_ind(inc_data, exc_data)
                difference = inc_mean - exc_mean
            else:
                difference = inc_mean - exc_mean
                p_value = np.nan
            
            table1_results.append({
                'twind': twind,
                'inc_n': inc_n,
                'inc_mean': inc_mean,
                'inc_stderr': inc_stderr,
                'exc_n': exc_n,
                'exc_mean': exc_mean,
                'exc_stderr': exc_stderr,
                'difference': difference,
                'p_value': p_value
            })
        
        self.results['table1'] = pd.DataFrame(table1_results)
        print("\n表1：纳入和剔除股票超额收益率")
        print(self.results['table1'])
        
        # Table 2: Calculate returns for arbitrage strategy
        table2_results = []
        
        for twind in range(6):
            # Included stocks returns
            inc_ret = included[included['twind'] == twind]['Dretwd'].dropna()
            inc_n = len(inc_ret)
            inc_mean = inc_ret.mean() * 10000
            inc_stderr = inc_ret.std() / np.sqrt(inc_n) * 10000 if inc_n > 0 else 0
            
            # Excluded stocks returns
            exc_ret = excluded[excluded['twind'] == twind]['Dretwd'].dropna()
            exc_n = len(exc_ret)
            exc_mean = exc_ret.mean() * 10000
            exc_stderr = exc_ret.std() / np.sqrt(exc_n) * 10000 if exc_n > 0 else 0
            
            # Arbitrage strategy: long included, short excluded
            arb_return = inc_mean - exc_mean
            
            # T-test
            if inc_n > 0 and exc_n > 0:
                t_stat, p_value = stats.ttest_ind(inc_ret, exc_ret)
            else:
                p_value = np.nan
            
            table2_results.append({
                'twind': twind,
                'inc_n': inc_n,
                'inc_mean': inc_mean,
                'inc_stderr': inc_stderr,
                'exc_n': exc_n,
                'exc_mean': exc_mean,
                'exc_stderr': exc_stderr,
                'arb_return': arb_return,
                'p_value': p_value
            })
        
        self.results['table2'] = pd.DataFrame(table2_results)
        print("\n表2：套利策略收益")
        print(self.results['table2'])
        
        return self.results['table1'], self.results['table2']
    
    def solve_question2(self):
        """问题二：寻找匹配样本"""
        print("\n" + "=" * 80)
        print("问题二：寻找匹配样本")
        print("=" * 80)
        
        # Read Q2 data - skip the description rows
        df = pd.read_excel(self.excel_file, sheet_name='Q2数据', skiprows=3, header=None)
        df.columns = ['Stkcd', 'Annonce', 'Chgsmp04', 'Nnindcd', 'Beta', 'Markettype', 'Stkcd1', 'Beta1']
        
        # Convert numeric columns
        df['Stkcd'] = pd.to_numeric(df['Stkcd'], errors='coerce')
        df['Beta'] = pd.to_numeric(df['Beta'], errors='coerce')
        df['Stkcd1'] = pd.to_numeric(df['Stkcd1'], errors='coerce')
        df['Beta1'] = pd.to_numeric(df['Beta1'], errors='coerce')
        
        # Find matching stocks with beta difference < 0.01
        matches = []
        
        # Group by Stkcd (included stock)
        for stkcd in df['Stkcd'].unique():
            if pd.isna(stkcd):
                continue
            
            # Get the beta of the included stock
            included_row = df[df['Stkcd'] == stkcd].iloc[0]
            beta = included_row['Beta']
            if pd.isna(beta):
                continue
            
            # Find all candidate matching stocks
            candidates = df[df['Stkcd'] == stkcd]
            
            # Find best match with smallest beta difference
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
        
        self.results['table3'] = pd.DataFrame(matches)
        print("\n表3：匹配结果")
        print(self.results['table3'])
        
        return self.results['table3']
    
    def calculate_bh_return(self, sheet_name, label):
        """计算Buy & Hold return"""
        print(f"\n处理 {label}...")
        
        # Read the full sheet
        df_full = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
        
        # Find the matching pairs table (表1)
        pairs_start = None
        for i in range(len(df_full)):
            if pd.notna(df_full.iloc[i, 1]) and '表1' in str(df_full.iloc[i, 1]):
                pairs_start = i + 1  # Skip to header
                break
        
        if pairs_start is None:
            print(f"警告：在 {sheet_name} 中未找到匹配样本表")
            return [0] * 10
        
        # Read pairs - read header and get the unique pairs
        pairs_header_row = pairs_start
        pairs_data_start = pairs_start + 1
        
        # Find where pairs data ends (look for empty rows)
        pairs_data_end = pairs_data_start
        while pairs_data_end < len(df_full) and pd.notna(df_full.iloc[pairs_data_end, 0]):
            pairs_data_end += 1
        
        # Read matching pairs
        pairs_df = df_full.iloc[pairs_data_start:pairs_data_end, [0, 4]].copy()
        pairs_df.columns = ['Stkcd', 'Stkcd1']
        
        # Convert stock codes to numeric, handling both formats
        def convert_stock_code(code):
            if pd.isna(code):
                return np.nan
            try:
                # Remove leading zeros and convert to int
                return int(str(code).replace(' ', ''))
            except:
                return np.nan
        
        pairs_df['Stkcd'] = pairs_df['Stkcd'].apply(convert_stock_code)
        pairs_df['Stkcd1'] = pairs_df['Stkcd1'].apply(convert_stock_code)
        pairs_df = pairs_df.dropna()
        
        # For Q4 data, take only the first match for each included stock
        pairs_df = pairs_df.drop_duplicates(subset=['Stkcd'], keep='first')
        
        print(f"找到 {len(pairs_df)} 对匹配股票")
        print(pairs_df)
        
        # Find the return data section (starts with Stkcd/Annonce)
        returns_start = None
        for i in range(pairs_data_end, len(df_full)):
            if pd.notna(df_full.iloc[i, 0]) and str(df_full.iloc[i, 0]) == 'Stkcd':
                returns_start = i + 1  # Skip header
                break
        
        if returns_start is None:
            print(f"警告：在 {sheet_name} 中未找到收益率数据")
            return [0] * 10
        
        # Read all return data
        returns_df = df_full.iloc[returns_start:].copy()
        
        # Determine the column structure based on number of columns
        num_cols = returns_df.shape[1]
        if num_cols >= 12:
            # Q3 format with all columns
            returns_df.columns = ['Stkcd', 'Annonce', 'Nnindcd', 'Beta', 'Markettype', 
                                  'Chgsmp04', 'Dretwd', 'trddt', 'twind', 'Stkcd1', 'Beta1', 'Dretwd1']
        elif num_cols >= 8:
            # Q4 format with fewer columns
            returns_df.columns = ['Stkcd', 'Annonce', 'Chgsmp04', 'Dretwd', 'trddt', 'twind', 'Stkcd1', 'Dretwd1']
        else:
            print(f"警告：列数不匹配，实际列数为 {num_cols}")
            return [0] * 10
        
        # Convert to numeric
        returns_df['Stkcd'] = pd.to_numeric(returns_df['Stkcd'], errors='coerce')
        returns_df['Stkcd1'] = pd.to_numeric(returns_df['Stkcd1'], errors='coerce')
        returns_df['twind'] = pd.to_numeric(returns_df['twind'], errors='coerce')
        returns_df['Dretwd'] = pd.to_numeric(returns_df['Dretwd'], errors='coerce')
        returns_df['Dretwd1'] = pd.to_numeric(returns_df['Dretwd1'], errors='coerce')
        
        # Clean data
        returns_df = returns_df.dropna(subset=['Stkcd', 'Stkcd1', 'twind'])
        
        print(f"收益率数据行数: {len(returns_df)}")
        
        # Calculate Buy & Hold returns for each day
        daily_returns = []
        
        for day in range(1, 11):
            pair_returns = []
            valid_pairs = 0
            
            for _, pair in pairs_df.iterrows():
                stkcd = pair['Stkcd']
                stkcd1 = pair['Stkcd1']
                
                # Get returns for this pair at this time window
                inc_data = returns_df[
                    (returns_df['Stkcd'] == stkcd) & 
                    (returns_df['twind'] == day)
                ]
                
                exc_data = returns_df[
                    (returns_df['Stkcd'] == stkcd) & 
                    (returns_df['Stkcd1'] == stkcd1) & 
                    (returns_df['twind'] == day)
                ]
                
                if len(inc_data) > 0 and len(exc_data) > 0:
                    inc_ret = inc_data.iloc[0]['Dretwd']
                    exc_ret = exc_data.iloc[0]['Dretwd1']
                    
                    if pd.notna(inc_ret) and pd.notna(exc_ret):
                        # Buy included stock, short matched stock
                        pair_ret = inc_ret - exc_ret
                        pair_returns.append(pair_ret)
                        valid_pairs += 1
            
            # Equal-weighted portfolio return
            if len(pair_returns) > 0:
                daily_ret = np.mean(pair_returns) * 10000  # Convert to base points
                daily_returns.append(daily_ret)
                print(f"Day {day}: {len(pair_returns)} 有效配对, 平均收益 = {daily_ret:.2f} bp")
            else:
                daily_returns.append(0)
                print(f"Day {day}: 无有效数据")
        
        return daily_returns
    
    def solve_question3(self):
        """问题三：利用匹配样本构建套利策略"""
        print("\n" + "=" * 80)
        print("问题三：计算Marina套利策略收益")
        print("=" * 80)
        
        returns = self.calculate_bh_return('Q3数据', '问题三')
        self.results['table4'] = returns
        
        print(f"\n表4：问题三 Buy & Hold Returns (base points)")
        for i, ret in enumerate(returns, 1):
            print(f"Day {i}: {ret:.2f}")
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, 11), returns, marker='o', linewidth=2)
        plt.xlabel('交易日', fontsize=12)
        plt.ylabel('收益率 (基点)', fontsize=12)
        plt.title('问题三：Marina套利策略收益', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('/tmp/q3_returns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return returns
    
    def solve_question4(self):
        """问题四：套利策略在牛熊市中的稳健性检验"""
        print("\n" + "=" * 80)
        print("问题四：不同市场环境下的策略检验")
        print("=" * 80)
        
        # Q4-1: 2022年6月 (牛市)
        returns_2022 = self.calculate_bh_return('Q4_1数据', '2022年6月（牛市）')
        self.results['table5'] = returns_2022
        print(f"\n表5：2022年6月 Buy & Hold Returns (base points)")
        for i, ret in enumerate(returns_2022, 1):
            print(f"Day {i}: {ret:.2f}")
        
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, 11), returns_2022, marker='o', linewidth=2, color='green')
        plt.xlabel('交易日', fontsize=12)
        plt.ylabel('收益率 (基点)', fontsize=12)
        plt.title('表5：2022年6月牛市环境套利策略收益', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('/tmp/q4_1_returns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Q4-2: 2023年6月 (非牛熊市)
        returns_2023 = self.calculate_bh_return('Q4_2数据', '2023年6月（非牛熊市）')
        self.results['table6'] = returns_2023
        print(f"\n表6：2023年6月 Buy & Hold Returns (base points)")
        for i, ret in enumerate(returns_2023, 1):
            print(f"Day {i}: {ret:.2f}")
        
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, 11), returns_2023, marker='o', linewidth=2, color='blue')
        plt.xlabel('交易日', fontsize=12)
        plt.ylabel('收益率 (基点)', fontsize=12)
        plt.title('表6：2023年6月非牛熊市环境套利策略收益', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('/tmp/q4_2_returns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Q4-3: 2024年6月 (熊市)
        returns_2024 = self.calculate_bh_return('Q4_3数据', '2024年6月（熊市）')
        self.results['table7'] = returns_2024
        print(f"\n表7：2024年6月 Buy & Hold Returns (base points)")
        for i, ret in enumerate(returns_2024, 1):
            print(f"Day {i}: {ret:.2f}")
        
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, 11), returns_2024, marker='o', linewidth=2, color='red')
        plt.xlabel('交易日', fontsize=12)
        plt.ylabel('收益率 (基点)', fontsize=12)
        plt.title('表7：2024年6月熊市环境套利策略收益', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('/tmp/q4_3_returns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return returns_2022, returns_2023, returns_2024
    
    def generate_report(self, template_file, output_file):
        """生成结果报告文档 - 基于模板填充"""
        print("\n" + "=" * 80)
        print("生成结果报告文档 - 基于模板填充")
        print("=" * 80)
        
        # Load template document
        doc = Document(template_file)
        print(f"已加载模板文档: {template_file}")
        print(f"模板包含 {len(doc.tables)} 个表格")
        
        # Fill Table 1 - Question 1: Excess returns
        print("\n填充表1：纳入和剔除股票超额收益率...")
        table1_data = self.results['table1']
        table1 = doc.tables[0]  # First table in template
        
        # Table 1 structure: rows 1-8 for data, columns 2-7 for twind 0-5
        rows_mapping = [
            ('inc_n', 1),
            ('inc_mean', 2),
            ('inc_stderr', 3),
            ('exc_n', 4),
            ('exc_mean', 5),
            ('exc_stderr', 6),
            ('difference', 7),
            ('p_value', 8)
        ]
        
        for col_name, row_idx in rows_mapping:
            for t in range(6):
                value = table1_data.loc[t, col_name]
                if pd.notna(value):
                    if col_name in ['inc_n', 'exc_n']:
                        table1.cell(row_idx, t+2).text = str(int(value))
                    elif col_name == 'p_value':
                        table1.cell(row_idx, t+2).text = f"{value:.4f}"
                    else:
                        table1.cell(row_idx, t+2).text = f"{value:.2f}"
        
        print(f"表1填充完成")
        
        # Fill Table 2 - Question 1: Arbitrage strategy returns
        print("\n填充表2：Mac的套利策略收益...")
        table2_data = self.results['table2']
        table2 = doc.tables[1]  # Second table in template
        
        # Table 2 structure: same as table 1
        rows_mapping2 = [
            ('inc_n', 1),
            ('inc_mean', 2),
            ('inc_stderr', 3),
            ('exc_n', 4),
            ('exc_mean', 5),
            ('exc_stderr', 6),
            ('arb_return', 7),
            ('p_value', 8)
        ]
        
        for col_name, row_idx in rows_mapping2:
            for t in range(6):
                value = table2_data.loc[t, col_name]
                if pd.notna(value):
                    if col_name in ['inc_n', 'exc_n']:
                        table2.cell(row_idx, t+2).text = str(int(value))
                    elif col_name == 'p_value':
                        table2.cell(row_idx, t+2).text = f"{value:.4f}"
                    else:
                        table2.cell(row_idx, t+2).text = f"{value:.2f}"
        
        print(f"表2填充完成")
        
        # Fill Table 3 - Question 2: Matching pairs
        print("\n填充表3：匹配结果...")
        table3_data = self.results['table3']
        table3 = doc.tables[2]  # Third table in template
        
        # Fill matching pairs (up to 6 pairs as the table has 6 data rows)
        for i, row in table3_data.iterrows():
            if i < 6:  # Template has 6 empty rows
                table3.cell(i+1, 0).text = str(int(row['Stkcd']))
                table3.cell(i+1, 1).text = str(int(row['Stkcd1']))
        
        print(f"表3填充完成：{min(len(table3_data), 6)} 对匹配")
        
        # Fill Table 4 - Question 3: Daily returns
        print("\n填充表4：Marina套利策略收益...")
        returns = self.results['table4']
        table4 = doc.tables[3]  # Fourth table in template
        
        # Fill returns in row 1 (row 0 is header with days 1-10)
        for i, ret in enumerate(returns):
            table4.cell(1, i).text = f"{ret:.2f}"
        
        print(f"表4填充完成")
        
        # Fill Table 5 - Question 4.1: 2022 returns
        print("\n填充表5：2022年6月收益...")
        returns_2022 = self.results['table5']
        table5 = doc.tables[4]  # Fifth table in template
        
        for i, ret in enumerate(returns_2022):
            table5.cell(1, i).text = f"{ret:.2f}"
        
        print(f"表5填充完成")
        
        # Fill Table 6 - Question 4.2: 2023 returns
        print("\n填充表6：2023年6月收益...")
        returns_2023 = self.results['table6']
        table6 = doc.tables[5]  # Sixth table in template
        
        for i, ret in enumerate(returns_2023):
            table6.cell(1, i).text = f"{ret:.2f}"
        
        print(f"表6填充完成")
        
        # Fill Table 7 - Question 4.3: 2024 returns
        print("\n填充表7：2024年6月收益...")
        returns_2024 = self.results['table7']
        table7 = doc.tables[6]  # Seventh table in template
        
        for i, ret in enumerate(returns_2024):
            table7.cell(1, i).text = f"{ret:.2f}"
        
        print(f"表7填充完成")
        
        # Save document
        doc.save(output_file)
        print(f"\n结果报告已保存至：{output_file}")


def main():
    """主函数"""
    excel_file = '作业3 （学生用）指数纳入效应套利策略的实现.xlsx'
    template_file = '作业3 （学生用）指数纳入效应套利策略的实现.docx'
    output_file = '作业3_指数纳入效应套利策略实现结果.docx'
    
    print("=" * 80)
    print("作业3：指数纳入效应套利策略的实现")
    print("=" * 80)
    print()
    
    # Initialize analyzer
    analyzer = ArbitrageStrategyAnalyzer(excel_file)
    
    # Solve all questions
    analyzer.solve_question1()
    analyzer.solve_question2()
    analyzer.solve_question3()
    analyzer.solve_question4()
    
    # Generate report using template
    analyzer.generate_report(template_file, output_file)
    
    print("\n" + "=" * 80)
    print("所有问题已完成！结果已保存。")
    print("=" * 80)


if __name__ == '__main__':
    main()
