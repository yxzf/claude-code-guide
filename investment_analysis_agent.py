#!/usr/bin/env python3
"""
智能投资分析Agent
自动化分析知识星球收藏的投资内容，生成结构化投资分析报告
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class PostData:
    """帖子数据结构"""
    content: str
    timestamp: str
    date: str
    source: str
    title: str
    author: str = ""

class InvestmentAnalysisAgent:
    """智能投资分析Agent"""

    def __init__(self, output_dir: str = "./investment_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.posts_data: List[PostData] = []
        self.date_range: tuple = None

    def extract_posts_from_favorites(self, start_date: str, end_date: str) -> List[PostData]:
        """
        从知识星球收藏夹提取帖子数据

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            List[PostData]: 提取的帖子数据列表
        """
        print(f"🚀 开始提取 {start_date} 到 {end_date} 的收藏内容...")

        # 这里是对应的MCP Chrome调用逻辑的Python表示
        # 实际执行时需要通过Claude Code的tool调用

        extraction_steps = [
            "1. 访问知识星球收藏夹: https://wx.zsxq.com/favorites",
            "2. 系统性提取所有帖子内容",
            "3. 解析每个帖子的详细信息",
            "4. 按日期范围过滤帖子",
            "5. 构建PostData对象列表"
        ]

        # 示例数据结构 - 实际使用时通过MCP Chrome工具获取
        sample_posts = [
            PostData(
                content="示例投资分析内容...",
                timestamp="2025-09-14 20:30",
                date="2025-09-14",
                source="基业长虹1.0",
                title="示例投资主题",
                author="分析师"
            )
        ]

        return self._filter_posts_by_date(sample_posts, start_date, end_date)

    def _filter_posts_by_date(self, posts: List[PostData], start_date: str, end_date: str) -> List[PostData]:
        """按日期范围过滤帖子"""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        filtered_posts = []
        for post in posts:
            try:
                post_dt = datetime.strptime(post.date, "%Y-%m-%d")
                if start_dt <= post_dt <= end_dt:
                    filtered_posts.append(post)
            except ValueError:
                continue

        return filtered_posts

    def group_posts_by_date(self, posts: List[PostData]) -> Dict[str, List[PostData]]:
        """按日期分组帖子"""
        grouped = {}
        for post in posts:
            date = post.date
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(post)
        return grouped

    def analyze_daily_themes(self, posts: List[PostData]) -> Dict[str, Any]:
        """分析单日投资主题"""
        if not posts:
            return {}

        # 提取关键词和主题
        themes = self._extract_investment_themes(posts)
        companies = self._extract_company_mentions(posts)
        technologies = self._extract_technology_trends(posts)

        analysis = {
            "post_count": len(posts),
            "main_themes": themes,
            "key_companies": companies,
            "technology_trends": technologies,
            "investment_logic": self._generate_investment_logic(posts),
            "risk_factors": self._identify_risk_factors(posts)
        }

        return analysis

    def _extract_investment_themes(self, posts: List[PostData]) -> List[str]:
        """提取投资主题"""
        theme_keywords = {
            "医疗设备": ["医疗设备", "器械", "联影", "迈瑞", "开立"],
            "国产算力": ["算力", "芯片", "AI", "GPU", "寒武纪", "海光"],
            "光通信": ["光通信", "光模块", "CPO", "盛科通信", "网络设备"],
            "存储芯片": ["存储", "HBM", "DDR", "闪存", "兆易创新"],
            "新能源": ["新能源", "锂电", "光伏", "风电", "储能"],
            "军工": ["军工", "国防", "航空", "航天", "雷达"]
        }

        detected_themes = []
        all_content = " ".join([post.content for post in posts])

        for theme, keywords in theme_keywords.items():
            for keyword in keywords:
                if keyword in all_content:
                    detected_themes.append(theme)
                    break

        return list(set(detected_themes))

    def _extract_company_mentions(self, posts: List[PostData]) -> List[str]:
        """提取公司提及"""
        # 简化的公司名称提取逻辑
        company_pattern = r'([A-Z][a-z]+(?:[A-Z][a-z]+)*|[\u4e00-\u9fff]+(?:股份|科技|医疗|医药|电子|通信|新材料|智能|数据|网络|系统|装备|制造|工业|能源|环保))'

        companies = set()
        for post in posts:
            matches = re.findall(company_pattern, post.content)
            companies.update(matches)

        return list(companies)[:10]  # 返回前10个

    def _extract_technology_trends(self, posts: List[PostData]) -> List[str]:
        """提取技术趋势"""
        tech_keywords = [
            "AI", "人工智能", "机器学习", "深度学习",
            "5G", "6G", "物联网", "边缘计算",
            "CPO", "硅光", "光子", "量子",
            "HBM", "DDR5", "存算一体",
            "新能源", "储能", "氢能", "碳中和"
        ]

        detected_tech = []
        all_content = " ".join([post.content for post in posts])

        for tech in tech_keywords:
            if tech in all_content:
                detected_tech.append(tech)

        return detected_tech

    def _generate_investment_logic(self, posts: List[PostData]) -> str:
        """生成投资逻辑"""
        themes = self._extract_investment_themes(posts)
        if not themes:
            return "暂无明确投资主题"

        logic_templates = {
            "医疗设备": "医疗设备行业受益于招标回暖和海外市场拓展，Q3有望迎来业绩拐点",
            "国产算力": "国产算力迎来产业化拐点，政策支持力度加大，技术突破带来投资机会",
            "光通信": "AI算力需求驱动光通信技术升级，CPO等前沿技术产业化提速",
            "存储芯片": "存储芯片涨价趋势明确，国产替代和技术升级双重驱动"
        }

        main_theme = themes[0] if themes else "综合"
        return logic_templates.get(main_theme, "多元化投资机会，关注技术创新和政策催化")

    def _identify_risk_factors(self, posts: List[PostData]) -> List[str]:
        """识别风险因素"""
        risk_keywords = [
            ("政策风险", ["政策", "监管", "集采", "贸易摩擦"]),
            ("技术风险", ["技术", "研发", "创新", "突破"]),
            ("市场风险", ["竞争", "市场", "需求", "景气度"]),
            ("估值风险", ["估值", "泡沫", "高位", "回调"])
        ]

        identified_risks = []
        all_content = " ".join([post.content for post in posts])

        for risk_type, keywords in risk_keywords:
            if any(keyword in all_content for keyword in keywords):
                identified_risks.append(risk_type)

        return identified_risks

    def generate_daily_report(self, date: str, posts: List[PostData], analysis: Dict[str, Any]) -> str:
        """生成日度投资分析报告"""
        report_template = f"""# {date}投资收藏分析

## 📅 日期：{date}
**收藏数量**：{analysis['post_count']}个帖子
**主要主题**：{', '.join(analysis['main_themes']) if analysis['main_themes'] else '综合投资'}

---

## 📊 核心内容摘要

### 🎯 主要投资主题
{self._format_themes_section(analysis['main_themes'], posts)}

### 🏢 重点关注公司
{self._format_companies_section(analysis['key_companies'])}

### 🚀 技术趋势
{self._format_tech_section(analysis['technology_trends'])}

---

## 💡 投资策略分析

### 📈 投资逻辑
{analysis['investment_logic']}

### ⚠️ 风险提示
{self._format_risks_section(analysis['risk_factors'])}

### 🎯 投资建议
{self._generate_investment_advice(analysis)}

---

## 📋 详细内容列表

{self._format_posts_detail(posts)}

---
*分析时间: {datetime.now().strftime("%Y年%m月%d日")}*
*数据来源: 知识星球收藏内容*
"""
        return report_template

    def _format_themes_section(self, themes: List[str], posts: List[PostData]) -> str:
        """格式化主题部分"""
        if not themes:
            return "- 综合投资主题，涵盖多个行业领域"

        section = ""
        for i, theme in enumerate(themes, 1):
            section += f"\n#### {i}. {theme}\n"
            section += f"- **投资逻辑**: {self._get_theme_logic(theme)}\n"
            section += f"- **关键催化剂**: {self._get_theme_catalysts(theme)}\n"

        return section

    def _format_companies_section(self, companies: List[str]) -> str:
        """格式化公司部分"""
        if not companies:
            return "- 暂无明确重点公司提及"

        return "\n".join([f"- **{company}**" for company in companies[:8]])

    def _format_tech_section(self, technologies: List[str]) -> str:
        """格式化技术部分"""
        if not technologies:
            return "- 暂无明确技术趋势"

        return "\n".join([f"- {tech}" for tech in technologies])

    def _format_risks_section(self, risks: List[str]) -> str:
        """格式化风险部分"""
        if not risks:
            return "1. 市场风险：整体市场波动影响\n2. 行业风险：行业景气度变化"

        return "\n".join([f"{i+1}. {risk}" for i, risk in enumerate(risks)])

    def _format_posts_detail(self, posts: List[PostData]) -> str:
        """格式化帖子详细列表"""
        if not posts:
            return "暂无具体内容"

        details = ""
        for i, post in enumerate(posts, 1):
            details += f"\n### 帖子{i}：{post.title or '投资分析'}\n"
            details += f"**时间**: {post.timestamp}\n"
            details += f"**来源**: {post.source}\n"
            details += f"**摘要**: {post.content[:200]}...\n"

        return details

    def _get_theme_logic(self, theme: str) -> str:
        """获取主题投资逻辑"""
        logic_map = {
            "医疗设备": "招标数据回暖，Q3有望迎来业绩拐点，海外市场快速拓展",
            "国产算力": "先进制程产能扩张，政策支持力度加大，产业化拐点显现",
            "光通信": "AI算力需求驱动技术升级，CPO等前沿技术产业化加速",
            "存储芯片": "供需格局改善，国产替代深化，技术创新带来增量市场"
        }
        return logic_map.get(theme, "技术创新驱动，政策支持，市场需求增长")

    def _get_theme_catalysts(self, theme: str) -> str:
        """获取主题催化剂"""
        catalyst_map = {
            "医疗设备": "Q3财报验证，海外订单落地，设备更新政策",
            "国产算力": "政策催化密集期，先进制程产能释放，国产替代加速",
            "光通信": "AI应用爆发，技术标准确立，5G建设提速",
            "存储芯片": "涨价趋势延续，新技术量产，下游需求回暖"
        }
        return catalyst_map.get(theme, "政策支持，技术突破，市场需求")

    def _generate_investment_advice(self, analysis: Dict[str, Any]) -> str:
        """生成投资建议"""
        themes = analysis['main_themes']
        if not themes:
            return "建议关注市场热点轮动，保持适度分散配置"

        advice = "**配置建议**:\n"
        for theme in themes:
            weight = self._get_theme_weight(theme)
            advice += f"- {theme}板块 ({weight}) - {self._get_theme_strategy(theme)}\n"

        return advice

    def _get_theme_weight(self, theme: str) -> str:
        """获取主题权重建议"""
        weight_map = {
            "医疗设备": "25-30%",
            "国产算力": "20-25%",
            "光通信": "15-20%",
            "存储芯片": "10-15%"
        }
        return weight_map.get(theme, "5-10%")

    def _get_theme_strategy(self, theme: str) -> str:
        """获取主题策略"""
        strategy_map = {
            "医疗设备": "关注Q3业绩拐点，重点配置龙头企业",
            "国产算力": "把握政策催化，关注技术突破标的",
            "光通信": "聚焦AI驱动需求，关注技术创新公司",
            "存储芯片": "关注涨价受益标的，布局技术升级"
        }
        return strategy_map.get(theme, "关注龙头企业，适度配置")

    def create_comprehensive_summary(self, date_range: tuple, all_analysis: Dict[str, Dict]) -> str:
        """创建综合投资策略汇总"""
        start_date, end_date = date_range

        # 汇总所有主题
        all_themes = set()
        all_companies = set()
        all_risks = set()

        for daily_analysis in all_analysis.values():
            all_themes.update(daily_analysis.get('main_themes', []))
            all_companies.update(daily_analysis.get('key_companies', []))
            all_risks.update(daily_analysis.get('risk_factors', []))

        summary_template = f"""# {start_date}至{end_date}投资收藏综合汇总

## 📅 分析周期：{start_date} - {end_date}
**数据来源**：基业长虹1.0知识星球收藏内容
**分析时间**：{datetime.now().strftime("%Y年%m月%d日")}

---

## 🎯 核心投资主题总结

{self._format_comprehensive_themes(all_themes)}

---

## 💰 综合投资配置策略

{self._format_comprehensive_strategy(all_themes)}

---

## 🏢 重点关注标的

{self._format_comprehensive_companies(list(all_companies)[:15])}

---

## ⚠️ 风险提示与应对

{self._format_comprehensive_risks(list(all_risks))}

---

## 📈 后续跟踪要点

{self._generate_tracking_points(all_themes)}

---

## 🎯 总结

{self._generate_comprehensive_conclusion(all_themes, date_range)}

---
*文档创建时间: {datetime.now().strftime("%Y年%m月%d日")}*
*数据来源: 知识星球收藏内容分析*
"""
        return summary_template

    def _format_comprehensive_themes(self, themes: set) -> str:
        """格式化综合主题"""
        if not themes:
            return "本期未发现明确的核心投资主题"

        formatted = ""
        for i, theme in enumerate(themes, 1):
            formatted += f"\n### {i}. {theme}\n"
            formatted += f"**投资逻辑**: {self._get_theme_logic(theme)}\n"
            formatted += f"**配置权重**: {self._get_theme_weight(theme)}\n"
            formatted += f"**关键催化剂**: {self._get_theme_catalysts(theme)}\n"

        return formatted

    def _format_comprehensive_strategy(self, themes: set) -> str:
        """格式化综合策略"""
        if not themes:
            return "建议保持均衡配置，关注市场轮动机会"

        strategy = "**核心配置组合** (100%仓位):\n\n"
        remaining_weight = 100

        for theme in themes:
            weight_str = self._get_theme_weight(theme)
            weight_num = int(weight_str.split('-')[0])
            strategy += f"#### {theme}板块 ({weight_str})\n"
            strategy += f"- {self._get_theme_strategy(theme)}\n\n"
            remaining_weight -= weight_num

        if remaining_weight > 0:
            strategy += f"#### 其他机会 ({remaining_weight}%)\n"
            strategy += "- 关注市场热点轮动，保持适度灵活性\n"

        return strategy

    def _format_comprehensive_companies(self, companies: List[str]) -> str:
        """格式化综合公司列表"""
        if not companies:
            return "暂无明确重点关注公司"

        formatted = ""
        for i, company in enumerate(companies, 1):
            formatted += f"{i}. **{company}** - 重点关注\n"

        return formatted

    def _format_comprehensive_risks(self, risks: List[str]) -> str:
        """格式化综合风险"""
        if not risks:
            return "1. 市场系统性风险\n2. 行业政策风险\n3. 公司基本面风险"

        formatted = ""
        for i, risk in enumerate(risks, 1):
            formatted += f"{i}. **{risk}**: {self._get_risk_description(risk)}\n"

        return formatted

    def _get_risk_description(self, risk: str) -> str:
        """获取风险描述"""
        risk_desc = {
            "政策风险": "国际贸易摩擦、行业监管政策变化可能影响投资预期",
            "技术风险": "技术突破进度不及预期，产业化进程可能延缓",
            "市场风险": "行业景气度波动，市场情绪变化影响估值",
            "估值风险": "部分标的估值偏高，存在回调压力"
        }
        return risk_desc.get(risk, "需要密切关注相关风险因素")

    def _generate_tracking_points(self, themes: set) -> str:
        """生成跟踪要点"""
        points = [
            "**业绩验证**: 关注Q3财报季相关公司业绩表现",
            "**政策催化**: 跟踪行业政策和支持措施落地情况",
            "**技术进展**: 关注关键技术突破和产业化进度",
            "**市场趋势**: 监控下游需求变化和行业景气度",
            "**估值水平**: 评估市场估值合理性，把握买入时机"
        ]

        return "\n".join([f"{i+1}. {point}" for i, point in enumerate(points)])

    def _generate_comprehensive_conclusion(self, themes: set, date_range: tuple) -> str:
        """生成综合结论"""
        start_date, end_date = date_range
        theme_count = len(themes)

        if theme_count == 0:
            return "本期收藏内容相对分散，建议保持谨慎观望，关注市场主线机会。"
        elif theme_count <= 2:
            return f"本期投资主题相对集中，建议重点配置{'/'.join(themes)}等核心赛道，把握结构性机会。"
        else:
            return f"本期投资机会多元化，涵盖{theme_count}个主要领域，建议均衡配置，关注轮动机会。"

    def run_analysis(self, start_date: str, end_date: str) -> None:
        """执行完整的投资分析流程"""
        print(f"🚀 启动投资分析Agent")
        print(f"📅 分析时间范围: {start_date} - {end_date}")

        # 第一步：提取帖子数据
        print("\n📊 第一步：提取收藏帖子数据...")
        posts = self.extract_posts_from_favorites(start_date, end_date)
        print(f"✅ 成功提取 {len(posts)} 个帖子")

        # 第二步：按日期分组
        print("\n📋 第二步：按日期分组帖子...")
        grouped_posts = self.group_posts_by_date(posts)
        print(f"✅ 分组到 {len(grouped_posts)} 个日期")

        # 第三步：分析每日内容并生成报告
        print("\n📝 第三步：生成日度分析报告...")
        all_analysis = {}

        for date, daily_posts in sorted(grouped_posts.items()):
            print(f"  📅 分析 {date} ({len(daily_posts)} 个帖子)")

            # 分析当日内容
            analysis = self.analyze_daily_themes(daily_posts)
            all_analysis[date] = analysis

            # 生成日度报告
            report = self.generate_daily_report(date, daily_posts, analysis)

            # 保存报告文件
            filename = f"投资收藏分析-{date}.md"
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"  ✅ 生成报告: {filename}")

        # 第四步：生成综合汇总
        print("\n📊 第四步：生成综合汇总报告...")
        summary = self.create_comprehensive_summary((start_date, end_date), all_analysis)

        summary_filename = f"投资收藏分析-{start_date}至{end_date}综合汇总.md"
        summary_filepath = self.output_dir / summary_filename

        with open(summary_filepath, 'w', encoding='utf-8') as f:
            f.write(summary)

        print(f"✅ 生成综合汇总: {summary_filename}")

        # 完成总结
        print(f"\n🎉 投资分析完成!")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"📊 日度报告: {len(all_analysis)} 个")
        print(f"📋 综合汇总: 1 个")
        print(f"💡 主要投资主题: {self._get_all_themes(all_analysis)}")

    def _get_all_themes(self, all_analysis: Dict[str, Dict]) -> str:
        """获取所有投资主题"""
        all_themes = set()
        for analysis in all_analysis.values():
            all_themes.update(analysis.get('main_themes', []))
        return ', '.join(all_themes) if all_themes else '综合投资'


def main():
    """主函数 - 命令行调用示例"""
    import sys

    if len(sys.argv) != 3:
        print("使用方法: python investment_analysis_agent.py <开始日期> <结束日期>")
        print("日期格式: YYYY-MM-DD")
        print("示例: python investment_analysis_agent.py 2025-09-12 2025-09-14")
        return

    start_date = sys.argv[1]
    end_date = sys.argv[2]

    # 创建Agent并执行分析
    agent = InvestmentAnalysisAgent()
    agent.run_analysis(start_date, end_date)


if __name__ == "__main__":
    main()