"""
Reporter Service
Generates weekly reports, exports, and progress visualizations.
"""
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import csv
import io
from pathlib import Path
import asyncio
import aiohttp
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
from io import BytesIO
import base64

logger = structlog.get_logger()

class ReportType(Enum):
    WEEKLY_SUMMARY = "weekly_summary"
    PROGRESS_REPORT = "progress_report"
    GROCERY_LIST = "grocery_list"
    FULL_EXPORT = "full_export"

class ExportFormat(Enum):
    PDF = "pdf"
    HTML = "html"
    CSV = "csv"
    JSON = "json"

@dataclass
class WeeklyMetrics:
    """Weekly progress metrics for reporting."""
    weight_change_kg: float
    body_fat_change: Optional[float]
    avg_calories: float
    avg_protein: float
    avg_carbs: float
    avg_fats: float
    workout_adherence: float
    habit_completion: float
    avg_sleep_hours: float
    avg_steps: int
    avg_hrv: Optional[float]
    mood_score: Optional[float]

@dataclass
class ProgressData:
    """Historical progress data for charts."""
    dates: List[datetime]
    weights: List[float]
    body_fat: List[Optional[float]]
    calories: List[float]
    protein: List[float]
    carbs: List[float]
    fats: List[float]
    workout_adherence: List[float]
    habit_completion: List[float]
    sleep_hours: List[float]
    steps: List[int]
    hrv: List[Optional[float]]
    mood_scores: List[Optional[float]]

@dataclass
class GroceryItem:
    """Grocery list item."""
    name: str
    quantity: str
    unit: str
    category: str
    aisle: Optional[str]
    estimated_cost: Optional[float]
    recipe_sources: List[str]

@dataclass
class WeeklyReport:
    """Complete weekly report data."""
    user_id: str
    program_id: str
    week_number: int
    report_date: datetime
    metrics: WeeklyMetrics
    progress_data: ProgressData
    grocery_list: List[GroceryItem]
    adjustments: List[Dict[str, Any]]
    recommendations: List[str]
    achievements: List[str]
    next_week_preview: Dict[str, Any]

class ReporterService:
    """Service for generating reports and exports."""
    
    def __init__(self):
        self.logger = structlog.get_logger()
        self.styles = getSampleStyleSheet()
        self._setup_matplotlib()
    
    def _setup_matplotlib(self):
        """Configure matplotlib for consistent styling."""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    async def generate_weekly_report(self, user_id: str, program_id: str, 
                                   week_number: int) -> WeeklyReport:
        """Generate comprehensive weekly report data."""
        self.logger.info("Generating weekly report", 
                        user_id=user_id, program_id=program_id, week_number=week_number)
        
        # Fetch data from various services
        metrics = await self._fetch_weekly_metrics(user_id, program_id, week_number)
        progress_data = await self._fetch_progress_data(user_id, program_id, week_number)
        grocery_list = await self._fetch_grocery_list(user_id, program_id, week_number)
        adjustments = await self._fetch_adjustments(user_id, program_id, week_number)
        recommendations = await self._generate_recommendations(metrics, adjustments)
        achievements = await self._identify_achievements(metrics, progress_data)
        next_week_preview = await self._generate_next_week_preview(user_id, program_id, week_number)
        
        return WeeklyReport(
            user_id=user_id,
            program_id=program_id,
            week_number=week_number,
            report_date=datetime.now(),
            metrics=metrics,
            progress_data=progress_data,
            grocery_list=grocery_list,
            adjustments=adjustments,
            recommendations=recommendations,
            achievements=achievements,
            next_week_preview=next_week_preview
        )
    
    async def export_report(self, report: WeeklyReport, 
                          report_type: ReportType, 
                          export_format: ExportFormat) -> Tuple[bytes, str]:
        """Export report in specified format."""
        self.logger.info("Exporting report", 
                        report_type=report_type.value, format=export_format.value)
        
        if report_type == ReportType.WEEKLY_SUMMARY:
            return await self._export_weekly_summary(report, export_format)
        elif report_type == ReportType.PROGRESS_REPORT:
            return await self._export_progress_report(report, export_format)
        elif report_type == ReportType.GROCERY_LIST:
            return await self._export_grocery_list(report, export_format)
        elif report_type == ReportType.FULL_EXPORT:
            return await self._export_full_data(report, export_format)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
    
    async def generate_signed_url(self, content: bytes, filename: str, 
                                expiration_hours: int = 24) -> str:
        """Generate signed URL for secure file access."""
        # In production, this would integrate with S3/MinIO
        # For now, return a placeholder
        return f"https://storage.example.com/signed/{filename}?expires={expiration_hours}h"
    
    async def _fetch_weekly_metrics(self, user_id: str, program_id: str, 
                                  week_number: int) -> WeeklyMetrics:
        """Fetch weekly metrics from database."""
        # Mock data - in production this would query the database
        return WeeklyMetrics(
            weight_change_kg=-0.8,
            body_fat_change=-0.3,
            avg_calories=1850,
            avg_protein=165,
            avg_carbs=180,
            avg_fats=65,
            workout_adherence=0.85,
            habit_completion=0.92,
            avg_sleep_hours=7.2,
            avg_steps=8500,
            avg_hrv=45.2,
            mood_score=7.8
        )
    
    async def _fetch_progress_data(self, user_id: str, program_id: str, 
                                 week_number: int) -> ProgressData:
        """Fetch historical progress data for charts."""
        # Mock data - in production this would query TimescaleDB
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=12)
        
        dates = []
        weights = []
        calories = []
        protein = []
        carbs = []
        fats = []
        workout_adherence = []
        habit_completion = []
        sleep_hours = []
        steps = []
        
        current_date = start_date
        base_weight = 75.0
        base_calories = 2000
        
        while current_date <= end_date:
            dates.append(current_date)
            
            # Simulate realistic progress
            week_progress = (current_date - start_date).days / 7
            weight_trend = base_weight - (week_progress * 0.5)
            weights.append(weight_trend + np.random.normal(0, 0.2))
            
            calorie_trend = base_calories - (week_progress * 25)
            calories.append(calorie_trend + np.random.normal(0, 50))
            protein.append(165 + np.random.normal(0, 10))
            carbs.append(180 + np.random.normal(0, 20))
            fats.append(65 + np.random.normal(0, 5))
            
            workout_adherence.append(0.85 + np.random.normal(0, 0.1))
            habit_completion.append(0.92 + np.random.normal(0, 0.05))
            sleep_hours.append(7.2 + np.random.normal(0, 0.5))
            steps.append(8500 + int(np.random.normal(0, 1000)))
            
            current_date += timedelta(days=1)
        
        return ProgressData(
            dates=dates,
            weights=weights,
            body_fat=[None] * len(dates),  # Not tracked daily
            calories=calories,
            protein=protein,
            carbs=carbs,
            fats=fats,
            workout_adherence=workout_adherence,
            habit_completion=habit_completion,
            sleep_hours=sleep_hours,
            steps=steps,
            hrv=[None] * len(dates),  # Not tracked daily
            mood_scores=[None] * len(dates)  # Not tracked daily
        )
    
    async def _fetch_grocery_list(self, user_id: str, program_id: str, 
                                week_number: int) -> List[GroceryItem]:
        """Fetch grocery list for the week."""
        # Mock data - in production this would come from meal planner
        return [
            GroceryItem("Chicken Breast", "2", "lbs", "Protein", "Meat", 12.99, ["Meal 1", "Meal 3"]),
            GroceryItem("Salmon", "1", "lb", "Protein", "Seafood", 15.99, ["Meal 2"]),
            GroceryItem("Brown Rice", "2", "cups", "Grains", "Grains", 3.99, ["Meal 1", "Meal 4"]),
            GroceryItem("Sweet Potato", "3", "medium", "Vegetables", "Produce", 4.99, ["Meal 2", "Meal 5"]),
            GroceryItem("Broccoli", "2", "heads", "Vegetables", "Produce", 5.99, ["Meal 1", "Meal 3"]),
            GroceryItem("Greek Yogurt", "32", "oz", "Dairy", "Dairy", 6.99, ["Snack 1", "Snack 2"]),
            GroceryItem("Almonds", "1", "cup", "Nuts", "Nuts", 8.99, ["Snack 1"]),
            GroceryItem("Banana", "7", "medium", "Fruits", "Produce", 4.99, ["Snack 2"]),
        ]
    
    async def _fetch_adjustments(self, user_id: str, program_id: str, 
                               week_number: int) -> List[Dict[str, Any]]:
        """Fetch program adjustments for the week."""
        # Mock data - in production this would come from progress analyzer
        return [
            {
                "type": "calorie_adjustment",
                "value": -150,
                "reason": "Weight loss plateau detected",
                "confidence": 0.85
            },
            {
                "type": "workout_volume",
                "value": 0.1,
                "reason": "Improved recovery indicators",
                "confidence": 0.78
            },
            {
                "type": "habit_focus",
                "value": "sleep_optimization",
                "reason": "Sleep quality below target",
                "confidence": 0.92
            }
        ]
    
    async def _generate_recommendations(self, metrics: WeeklyMetrics, 
                                      adjustments: List[Dict[str, Any]]) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        if metrics.workout_adherence < 0.8:
            recommendations.append("Consider shorter, more frequent workouts to improve consistency")
        
        if metrics.avg_sleep_hours < 7:
            recommendations.append("Focus on sleep hygiene to support recovery and weight loss")
        
        if metrics.avg_steps < 8000:
            recommendations.append("Add 10-minute walks throughout the day to increase daily activity")
        
        if metrics.mood_score and metrics.mood_score < 7:
            recommendations.append("Consider stress management techniques to support overall wellness")
        
        return recommendations
    
    async def _identify_achievements(self, metrics: WeeklyMetrics, 
                                   progress_data: ProgressData) -> List[str]:
        """Identify user achievements for the week."""
        achievements = []
        
        if metrics.weight_change_kg < -0.5:
            achievements.append("Met weight loss target for the week")
        
        if metrics.workout_adherence >= 0.8:
            achievements.append("Maintained excellent workout consistency")
        
        if metrics.habit_completion >= 0.9:
            achievements.append("Outstanding habit completion rate")
        
        if metrics.avg_steps >= 8000:
            achievements.append("Exceeded daily step goal consistently")
        
        return achievements
    
    async def _generate_next_week_preview(self, user_id: str, program_id: str, 
                                        week_number: int) -> Dict[str, Any]:
        """Generate preview of next week's program."""
        # Mock data - in production this would come from program generator
        return {
            "week_number": week_number + 1,
            "calorie_target": 1800,
            "macro_targets": {
                "protein": 170,
                "carbs": 175,
                "fats": 60
            },
            "workout_focus": "Strength progression",
            "habit_focus": "Sleep optimization",
            "key_changes": [
                "Increased protein target by 5g",
                "Added deload week for recovery",
                "New mindfulness practice introduced"
            ]
        }
    
    async def _export_weekly_summary(self, report: WeeklyReport, 
                                   export_format: ExportFormat) -> Tuple[bytes, str]:
        """Export weekly summary report."""
        if export_format == ExportFormat.PDF:
            return await self._generate_weekly_pdf(report)
        elif export_format == ExportFormat.HTML:
            return await self._generate_weekly_html(report)
        else:
            raise ValueError(f"Unsupported format for weekly summary: {export_format}")
    
    async def _export_progress_report(self, report: WeeklyReport, 
                                    export_format: ExportFormat) -> Tuple[bytes, str]:
        """Export detailed progress report with charts."""
        if export_format == ExportFormat.PDF:
            return await self._generate_progress_pdf(report)
        elif export_format == ExportFormat.HTML:
            return await self._generate_progress_html(report)
        else:
            raise ValueError(f"Unsupported format for progress report: {export_format}")
    
    async def _export_grocery_list(self, report: WeeklyReport, 
                                 export_format: ExportFormat) -> Tuple[bytes, str]:
        """Export grocery list."""
        if export_format == ExportFormat.PDF:
            return await self._generate_grocery_pdf(report)
        elif export_format == ExportFormat.CSV:
            return await self._generate_grocery_csv(report)
        else:
            raise ValueError(f"Unsupported format for grocery list: {export_format}")
    
    async def _export_full_data(self, report: WeeklyReport, 
                              export_format: ExportFormat) -> Tuple[bytes, str]:
        """Export full program data."""
        if export_format == ExportFormat.JSON:
            return await self._generate_full_json(report)
        else:
            raise ValueError(f"Unsupported format for full export: {export_format}")
    
    async def _generate_weekly_pdf(self, report: WeeklyReport) -> Tuple[bytes, str]:
        """Generate weekly summary PDF."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph(f"Week {report.week_number} Progress Report", title_style))
        story.append(Spacer(1, 20))
        
        # Summary metrics
        story.append(Paragraph("Weekly Summary", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        
        metrics_data = [
            ["Metric", "Value", "Target"],
            ["Weight Change", f"{report.metrics.weight_change_kg:.1f} kg", "-0.5 to -1.0 kg"],
            ["Calories (avg)", f"{report.metrics.avg_calories:.0f}", "1800-2000"],
            ["Protein (avg)", f"{report.metrics.avg_protein:.0f}g", "160-180g"],
            ["Workout Adherence", f"{report.metrics.workout_adherence:.1%}", "≥80%"],
            ["Habit Completion", f"{report.metrics.habit_completion:.1%}", "≥90%"],
            ["Sleep (avg)", f"{report.metrics.avg_sleep_hours:.1f}h", "7-9h"],
            ["Steps (avg)", f"{report.metrics.avg_steps:,}", "≥8000"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Achievements
        if report.achievements:
            story.append(Paragraph("This Week's Achievements", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            for achievement in report.achievements:
                story.append(Paragraph(f"• {achievement}", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Recommendations
        if report.recommendations:
            story.append(Paragraph("Recommendations", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            for rec in report.recommendations:
                story.append(Paragraph(f"• {rec}", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Next week preview
        story.append(Paragraph("Next Week Preview", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        preview = report.next_week_preview
        story.append(Paragraph(f"Week {preview['week_number']}: {preview['workout_focus']}", self.styles['Normal']))
        story.append(Paragraph(f"Calorie Target: {preview['calorie_target']} kcal", self.styles['Normal']))
        story.append(Paragraph(f"Habit Focus: {preview['habit_focus']}", self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), f"week_{report.week_number}_summary.pdf"
    
    async def _generate_weekly_html(self, report: WeeklyReport) -> Tuple[bytes, str]:
        """Generate weekly summary HTML."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Week {report.week_number} Progress Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background: #f5f5f5; padding: 15px; border-radius: 8px; }}
                .achievements {{ background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Week {report.week_number} Progress Report</h1>
                <p>Generated on {report.report_date.strftime('%B %d, %Y')}</p>
            </div>
            
            <h2>Weekly Summary</h2>
            <div class="metrics">
                <div class="metric-card">
                    <h3>Weight Change</h3>
                    <p>{report.metrics.weight_change_kg:.1f} kg</p>
                </div>
                <div class="metric-card">
                    <h3>Avg Calories</h3>
                    <p>{report.metrics.avg_calories:.0f}</p>
                </div>
                <div class="metric-card">
                    <h3>Workout Adherence</h3>
                    <p>{report.metrics.workout_adherence:.1%}</p>
                </div>
                <div class="metric-card">
                    <h3>Habit Completion</h3>
                    <p>{report.metrics.habit_completion:.1%}</p>
                </div>
            </div>
            
            <div class="achievements">
                <h2>Achievements</h2>
                <ul>
                    {''.join(f'<li>{achievement}</li>' for achievement in report.achievements)}
                </ul>
            </div>
            
            <div class="recommendations">
                <h2>Recommendations</h2>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8'), f"week_{report.week_number}_summary.html"
    
    async def _generate_progress_pdf(self, report: WeeklyReport) -> Tuple[bytes, str]:
        """Generate progress report PDF with charts."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph(f"Progress Report - Week {report.week_number}", title_style))
        story.append(Spacer(1, 20))
        
        # Generate charts
        weight_chart = await self._create_weight_chart(report.progress_data)
        macro_chart = await self._create_macro_chart(report.progress_data)
        adherence_chart = await self._create_adherence_chart(report.progress_data)
        
        # Add charts to PDF
        story.append(Paragraph("Weight Progress", self.styles['Heading2']))
        story.append(Image(weight_chart, width=6*inch, height=3*inch))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Macro Tracking", self.styles['Heading2']))
        story.append(Image(macro_chart, width=6*inch, height=3*inch))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Adherence Trends", self.styles['Heading2']))
        story.append(Image(adherence_chart, width=6*inch, height=3*inch))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), f"progress_report_week_{report.week_number}.pdf"
    
    async def _generate_progress_html(self, report: WeeklyReport) -> Tuple[bytes, str]:
        """Generate progress report HTML with embedded charts."""
        # Generate chart data as base64 images
        weight_chart_b64 = await self._create_weight_chart_base64(report.progress_data)
        macro_chart_b64 = await self._create_macro_chart_base64(report.progress_data)
        adherence_chart_b64 = await self._create_adherence_chart_base64(report.progress_data)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Progress Report - Week {report.week_number}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .chart {{ margin: 20px 0; text-align: center; }}
                .chart img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>Progress Report - Week {report.week_number}</h1>
            
            <h2>Weight Progress</h2>
            <div class="chart">
                <img src="data:image/png;base64,{weight_chart_b64}" alt="Weight Progress Chart">
            </div>
            
            <h2>Macro Tracking</h2>
            <div class="chart">
                <img src="data:image/png;base64,{macro_chart_b64}" alt="Macro Tracking Chart">
            </div>
            
            <h2>Adherence Trends</h2>
            <div class="chart">
                <img src="data:image/png;base64,{adherence_chart_b64}" alt="Adherence Trends Chart">
            </div>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8'), f"progress_report_week_{report.week_number}.html"
    
    async def _generate_grocery_pdf(self, report: WeeklyReport) -> Tuple[bytes, str]:
        """Generate grocery list PDF."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph(f"Week {report.week_number} Grocery List", title_style))
        story.append(Spacer(1, 20))
        
        # Group items by category
        categories = {}
        for item in report.grocery_list:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        # Create table for each category
        for category, items in categories.items():
            story.append(Paragraph(category, self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            table_data = [["Item", "Quantity", "Unit", "Aisle", "Estimated Cost"]]
            for item in items:
                table_data.append([
                    item.name,
                    item.quantity,
                    item.unit,
                    item.aisle or "N/A",
                    f"${item.estimated_cost:.2f}" if item.estimated_cost else "N/A"
                ])
            
            grocery_table = Table(table_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 1*inch, 1.2*inch])
            grocery_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(grocery_table)
            story.append(Spacer(1, 20))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), f"grocery_list_week_{report.week_number}.pdf"
    
    async def _generate_grocery_csv(self, report: WeeklyReport) -> Tuple[bytes, str]:
        """Generate grocery list CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Item", "Quantity", "Unit", "Category", "Aisle", "Estimated Cost", "Recipe Sources"])
        
        # Items
        for item in report.grocery_list:
            writer.writerow([
                item.name,
                item.quantity,
                item.unit,
                item.category,
                item.aisle or "",
                f"${item.estimated_cost:.2f}" if item.estimated_cost else "",
                ", ".join(item.recipe_sources)
            ])
        
        return output.getvalue().encode('utf-8'), f"grocery_list_week_{report.week_number}.csv"
    
    async def _generate_full_json(self, report: WeeklyReport) -> Tuple[bytes, str]:
        """Generate full program data export as JSON."""
        export_data = {
            "export_info": {
                "user_id": report.user_id,
                "program_id": report.program_id,
                "export_date": report.report_date.isoformat(),
                "week_number": report.week_number
            },
            "weekly_metrics": {
                "weight_change_kg": report.metrics.weight_change_kg,
                "body_fat_change": report.metrics.body_fat_change,
                "avg_calories": report.metrics.avg_calories,
                "avg_protein": report.metrics.avg_protein,
                "avg_carbs": report.metrics.avg_carbs,
                "avg_fats": report.metrics.avg_fats,
                "workout_adherence": report.metrics.workout_adherence,
                "habit_completion": report.metrics.habit_completion,
                "avg_sleep_hours": report.metrics.avg_sleep_hours,
                "avg_steps": report.metrics.avg_steps,
                "avg_hrv": report.metrics.avg_hrv,
                "mood_score": report.metrics.mood_score
            },
            "progress_data": {
                "dates": [d.isoformat() for d in report.progress_data.dates],
                "weights": report.progress_data.weights,
                "calories": report.progress_data.calories,
                "protein": report.progress_data.protein,
                "carbs": report.progress_data.carbs,
                "fats": report.progress_data.fats,
                "workout_adherence": report.progress_data.workout_adherence,
                "habit_completion": report.progress_data.habit_completion,
                "sleep_hours": report.progress_data.sleep_hours,
                "steps": report.progress_data.steps
            },
            "grocery_list": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "category": item.category,
                    "aisle": item.aisle,
                    "estimated_cost": item.estimated_cost,
                    "recipe_sources": item.recipe_sources
                }
                for item in report.grocery_list
            ],
            "adjustments": report.adjustments,
            "recommendations": report.recommendations,
            "achievements": report.achievements,
            "next_week_preview": report.next_week_preview
        }
        
        return json.dumps(export_data, indent=2).encode('utf-8'), f"full_export_week_{report.week_number}.json"
    
    async def _create_weight_chart(self, progress_data: ProgressData) -> BytesIO:
        """Create weight progress chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 7-day moving average
        weights = np.array(progress_data.weights)
        dates = np.array(progress_data.dates)
        
        # Calculate 7-day moving average
        window = 7
        weights_ma = np.convolve(weights, np.ones(window)/window, mode='valid')
        dates_ma = dates[window-1:]
        
        ax.plot(dates, weights, 'o-', alpha=0.3, label='Daily Weight')
        ax.plot(dates_ma, weights_ma, 'r-', linewidth=2, label='7-Day Average')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Weight (kg)')
        ax.set_title('Weight Progress')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=45)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    async def _create_macro_chart(self, progress_data: ProgressData) -> BytesIO:
        """Create macro tracking chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        dates = progress_data.dates
        
        ax.plot(dates, progress_data.protein, 'b-', label='Protein', linewidth=2)
        ax.plot(dates, progress_data.carbs, 'g-', label='Carbs', linewidth=2)
        ax.plot(dates, progress_data.fats, 'r-', label='Fats', linewidth=2)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Grams')
        ax.set_title('Macro Tracking')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=45)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    async def _create_adherence_chart(self, progress_data: ProgressData) -> BytesIO:
        """Create adherence trends chart."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        dates = progress_data.dates
        
        # Workout adherence
        ax1.plot(dates, progress_data.workout_adherence, 'b-', linewidth=2)
        ax1.set_ylabel('Workout Adherence')
        ax1.set_title('Adherence Trends')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
        
        # Habit completion
        ax2.plot(dates, progress_data.habit_completion, 'g-', linewidth=2)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Habit Completion')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)
        
        # Format x-axis dates
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    async def _create_weight_chart_base64(self, progress_data: ProgressData) -> str:
        """Create weight chart and return as base64 string."""
        buffer = await self._create_weight_chart(progress_data)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    async def _create_macro_chart_base64(self, progress_data: ProgressData) -> str:
        """Create macro chart and return as base64 string."""
        buffer = await self._create_macro_chart(progress_data)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    async def _create_adherence_chart_base64(self, progress_data: ProgressData) -> str:
        """Create adherence chart and return as base64 string."""
        buffer = await self._create_adherence_chart(progress_data)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
