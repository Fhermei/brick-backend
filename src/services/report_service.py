"""
Report Service - Generate advanced PDF reports with full task details
"""

import io
import uuid
from datetime import datetime
from typing import Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from sqlalchemy.orm import Session

from src.core.kpi import compute_bur, get_bur_status, get_kar_status


class ReportService:
    @staticmethod
    def generate_organization_report(
        db: Session,
        org_id: uuid.UUID,
        org_name: str,
        currency: str,
        projects_data: list,
        tasks_data: list,
        expenses_data: list,
        kpis_data: list,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> bytes:
        """Generate advanced PDF report with full task details and analytics"""
        
        buffer = io.BytesIO()
        
        # Determine if this is a project report
        is_project_report = len(projects_data) == 1
        
        # Set page size - landscape for more columns
        page_size = landscape(A4) if not is_project_report else A4
        page_size = A4  # Using A4 portrait for better readability
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=page_size,
            leftMargin=12*mm,
            rightMargin=12*mm,
            topMargin=15*mm,
            bottomMargin=15*mm,
            title=f"Brick SPMES Report - {org_name}",
            author="Brick SPMES System"
        )
        
        styles = getSampleStyleSheet()
        
        # Define custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#059669'),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        subsection_style = ParagraphStyle(
            'Subsection',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#475569'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.whitesmoke,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=7,
            leading=9,
            alignment=TA_LEFT
        )
        
        table_cell_center = ParagraphStyle(
            'TableCellCenter',
            parent=styles['Normal'],
            fontSize=7,
            leading=9,
            alignment=TA_CENTER
        )
        
        metric_value_style = ParagraphStyle(
            'MetricValue',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        metric_label_style = ParagraphStyle(
            'MetricLabel',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        )
        
        story = []
        
        # ============================================================
        # TITLE SECTION
        # ============================================================
        if is_project_report:
            project = projects_data[0]
            report_title = f"PROJECT REPORT: {project['title']}"
            filename_prefix = f"Project_Report_{project['title']}"
        else:
            report_title = f"ORGANIZATION REPORT: {org_name}"
            filename_prefix = f"Org_Report_{org_name}"
        
        story.append(Paragraph(report_title, title_style))
        story.append(Paragraph(f"Generated on: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
        if date_from and date_to:
            story.append(Paragraph(f"Reporting Period: {date_from.strftime('%B %d, %Y')} to {date_to.strftime('%B %d, %Y')}", subtitle_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # ============================================================
        # KEY METRICS CARDS
        # ============================================================
        total_budget = sum(p.get('total_budget', 0) for p in projects_data)
        total_spent = sum(p.get('total_spent', 0) for p in projects_data)
        total_tasks = len(tasks_data)
        completed_tasks = len([t for t in tasks_data if t.get('status') == 'completed'])
        overdue_tasks = len([t for t in tasks_data if t.get('is_overdue') or (t.get('due_date') and t.get('status') != 'completed')])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        bur = compute_bur(total_spent, total_budget) if total_budget > 0 else 0
        bur_info = get_bur_status(bur)
        
        # Create metrics in a table
        metrics_data = [
            ["Total Budget", "Total Spent", "Remaining", "BUR"],
            [f"{currency} {total_budget:,.0f}", f"{currency} {total_spent:,.0f}", f"{currency} {(total_budget - total_spent):,.0f}", f"{bur:.1f}%"],
            ["Total Tasks", "Completed", "Overdue", "Completion Rate"],
            [f"{total_tasks}", f"{completed_tasks}", f"{overdue_tasks}", f"{completion_rate:.1f}%"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.3 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0, 2), (3, 2), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.HexColor('#475569')),
            ('TEXTCOLOR', (0, 2), (3, 2), colors.HexColor('#475569')),
            ('ALIGN', (0, 0), (3, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (3, -1), 9),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (3, 2), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (3, -1), 6),
            ('TOPPADDING', (0, 0), (3, -1), 6),
            ('VALIGN', (0, 0), (3, -1), 'MIDDLE'),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # ============================================================
        # PROJECT BREAKDOWN (for org report)
        # ============================================================
        if not is_project_report and projects_data:
            story.append(Paragraph("PROJECT BREAKDOWN", section_style))
            
            project_table_data = [["#", "Project Name", "Budget", "Spent", "Remaining", "BUR", "Status", "Tasks"]]
            for idx, project in enumerate(projects_data, 1):
                project_bur = compute_bur(project.get('total_spent', 0), project.get('total_budget', 0)) if project.get('total_budget', 0) > 0 else 0
                project_tasks = [t for t in tasks_data if t.get('project_id') == project.get('id')]
                
                # BUR color indicator
                bur_color = "#22c55e" if project_bur < 80 else "#eab308" if project_bur < 100 else "#ef4444"
                
                project_table_data.append([
                    str(idx),
                    project.get('title', 'Unknown')[:35],
                    f"{currency} {project.get('total_budget', 0):,.0f}",
                    f"{currency} {project.get('total_spent', 0):,.0f}",
                    f"{currency} {(project.get('total_budget', 0) - project.get('total_spent', 0)):,.0f}",
                    Paragraph(f'<font color="{bur_color}">{project_bur:.0f}%</font>', table_cell_center),
                    project.get('status', 'N/A').upper(),
                    str(len(project_tasks))
                ])
            
            project_table = Table(project_table_data, colWidths=[0.35 * inch, 1.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.5 * inch, 0.5 * inch, 0.5 * inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (7, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (7, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (7, -1), 'LEFT'),
                ('ALIGN', (2, 1), (6, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (7, -1), 7),
                ('FONTNAME', (0, 0), (7, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (7, -1), 4),
                ('TOPPADDING', (0, 0), (7, -1), 4),
                ('GRID', (0, 0), (7, -1), 0.3, colors.HexColor('#cbd5e1')),
                ('VALIGN', (0, 0), (7, -1), 'MIDDLE'),
            ]))
            story.append(project_table)
            story.append(Spacer(1, 0.15 * inch))
        
        # ============================================================
        # TASKS DETAILS (COMPREHENSIVE)
        # ============================================================
        if tasks_data:
            story.append(Paragraph("TASKS DETAILS", section_style))
            
            # Comprehensive task table with all fields
            task_table_data = [[
                "#", "Task ID", "Task Name", "Priority", "Status", 
                "Assigned To", "Due Date", "Overdue", "Budget", "Spent", "Remaining", "Payment Method"
            ]]
            
            # Calculate totals for task budget
            total_task_budget = 0
            total_task_spent = 0
            
            for idx, task in enumerate(tasks_data[:50], 1):
                task_budget = task.get('budget_allocated', 0)
                task_spent = task.get('total_spent', 0)
                total_task_budget += task_budget
                total_task_spent += task_spent
                
                # Priority color
                priority = task.get('priority', 'medium')
                priority_colors = {
                    'urgent': '#ef4444', 'high': '#f97316', 
                    'medium': '#eab308', 'low': '#22c55e'
                }
                priority_color = priority_colors.get(priority, '#64748b')
                
                # Status display
                status = task.get('status', 'todo')
                status_display = status.replace('_', ' ').title()
                
                # Overdue check
                is_overdue = task.get('is_overdue', False)
                overdue_text = "Yes" if is_overdue else "No"
                overdue_color = "#ef4444" if is_overdue else "#22c55e"
                
                # Assigned to
                assigned_to = task.get('assigned_to_name', 'Unassigned')
                additional_assignees = task.get('additional_assignees', [])
                if additional_assignees:
                    assigned_to += f" +{len(additional_assignees)}"
                
                task_table_data.append([
                    str(idx),
                    task.get('id', '')[:8],
                    task.get('title', 'Unknown')[:30],
                    Paragraph(f'<font color="{priority_color}">{priority.upper()}</font>', table_cell_center),
                    status_display,
                    assigned_to,
                    task.get('due_date', 'N/A')[:10] if task.get('due_date') else 'N/A',
                    Paragraph(f'<font color="{overdue_color}">{overdue_text}</font>', table_cell_center),
                    f"{currency} {task_budget:,.0f}",
                    f"{currency} {task_spent:,.0f}",
                    f"{currency} {(task_budget - task_spent):,.0f}",
                    task.get('payment_method', 'N/A') if task.get('payment_method') else 'N/A'
                ])
            
            # Add total row
            task_table_data.append([
                "", "", "TOTAL", "", "", "", "", "",
                f"{currency} {total_task_budget:,.0f}",
                f"{currency} {total_task_spent:,.0f}",
                f"{currency} {(total_task_budget - total_task_spent):,.0f}",
                ""
            ])
            
            # Calculate column widths
            col_widths = [0.3 * inch, 0.6 * inch, 1.6 * inch, 0.5 * inch, 0.7 * inch, 0.8 * inch, 0.6 * inch, 0.5 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, 0.6 * inch]
            
            task_table = Table(task_table_data, colWidths=col_widths, repeatRows=1)
            task_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (11, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (11, 0), colors.whitesmoke),
                ('BACKGROUND', (0, -1), (11, -1), colors.HexColor('#f1f5f9')),
                ('FONTNAME', (0, 0), (11, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (11, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (11, -1), 6),
                ('ALIGN', (0, 0), (11, -1), 'LEFT'),
                ('ALIGN', (8, 1), (10, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (11, -1), 3),
                ('TOPPADDING', (0, 0), (11, -1), 3),
                ('GRID', (0, 0), (11, -1), 0.2, colors.HexColor('#cbd5e1')),
                ('VALIGN', (0, 0), (11, -1), 'MIDDLE'),
            ]))
            story.append(task_table)
            story.append(Spacer(1, 0.15 * inch))
            
            # Task Analytics Section
            story.append(Paragraph("TASK ANALYTICS", subsection_style))
            
            # Calculate task statistics
            status_counts = {}
            priority_counts = {}
            for task in tasks_data:
                status = task.get('status', 'todo')
                priority = task.get('priority', 'medium')
                status_counts[status] = status_counts.get(status, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            analytics_data = [
                ["Status Distribution", "Count", "Percentage", "Priority Distribution", "Count", "Percentage"],
                ["To Do", status_counts.get('todo', 0), f"{(status_counts.get('todo', 0)/total_tasks*100):.0f}%",
                 "Urgent", priority_counts.get('urgent', 0), f"{(priority_counts.get('urgent', 0)/total_tasks*100):.0f}%"],
                ["In Progress", status_counts.get('in_progress', 0), f"{(status_counts.get('in_progress', 0)/total_tasks*100):.0f}%",
                 "High", priority_counts.get('high', 0), f"{(priority_counts.get('high', 0)/total_tasks*100):.0f}%"],
                ["Review", status_counts.get('review', 0), f"{(status_counts.get('review', 0)/total_tasks*100):.0f}%",
                 "Medium", priority_counts.get('medium', 0), f"{(priority_counts.get('medium', 0)/total_tasks*100):.0f}%"],
                ["To Be Tested", status_counts.get('to_be_tested', 0), f"{(status_counts.get('to_be_tested', 0)/total_tasks*100):.0f}%",
                 "Low", priority_counts.get('low', 0), f"{(priority_counts.get('low', 0)/total_tasks*100):.0f}%"],
                ["Blocked", status_counts.get('blocked', 0), f"{(status_counts.get('blocked', 0)/total_tasks*100):.0f}%", "", "", ""],
                ["Completed", status_counts.get('completed', 0), f"{(status_counts.get('completed', 0)/total_tasks*100):.0f}%", "", "", ""]
            ]
            
            analytics_table = Table(analytics_data, colWidths=[1.1 * inch, 0.5 * inch, 0.6 * inch, 1.1 * inch, 0.5 * inch, 0.6 * inch])
            analytics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#059669')),
                ('BACKGROUND', (3, 0), (5, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (5, 0), colors.whitesmoke),
                ('FONTSIZE', (0, 0), (5, -1), 7),
                ('FONTNAME', (0, 0), (5, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (5, -1), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (5, -1), 4),
                ('TOPPADDING', (0, 0), (5, -1), 4),
                ('GRID', (0, 0), (5, -1), 0.3, colors.HexColor('#cbd5e1')),
            ]))
            story.append(analytics_table)
            story.append(Spacer(1, 0.15 * inch))
        
        # ============================================================
        # EXPENSES DETAILS (for project report)
        # ============================================================
        if is_project_report and expenses_data:
            story.append(PageBreak())
            story.append(Paragraph("EXPENSES DETAILS", section_style))
            
            expense_table_data = [["#", "Task", "Category", "Amount", "Payment Method", "Submitted By", "Date", "Status"]]
            total_expenses = 0
            
            for idx, expense in enumerate(expenses_data, 1):
                amount = expense.get('amount', 0)
                total_expenses += amount
                
                expense_table_data.append([
                    str(idx),
                    expense.get('task_title', 'Unknown')[:25],
                    expense.get('category', 'N/A'),
                    f"{currency} {amount:,.0f}",
                    expense.get('payment_method', 'N/A'),
                    expense.get('user_name', 'N/A'),
                    expense.get('created_at', 'N/A')[:10] if expense.get('created_at') else 'N/A',
                    expense.get('status', 'N/A')
                ])
            
            # Add total row
            expense_table_data.append(["", "", "TOTAL", f"{currency} {total_expenses:,.0f}", "", "", "", ""])
            
            expense_table = Table(expense_table_data, colWidths=[0.35 * inch, 1.5 * inch, 0.8 * inch, 0.7 * inch, 0.8 * inch, 0.8 * inch, 0.7 * inch, 0.6 * inch])
            expense_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (7, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (7, 0), colors.whitesmoke),
                ('BACKGROUND', (0, -1), (7, -1), colors.HexColor('#f1f5f9')),
                ('FONTNAME', (0, 0), (7, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (7, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (7, -1), 7),
                ('ALIGN', (0, 0), (7, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (7, -1), 4),
                ('TOPPADDING', (0, 0), (7, -1), 4),
                ('GRID', (0, 0), (7, -1), 0.3, colors.HexColor('#cbd5e1')),
            ]))
            story.append(expense_table)
            story.append(Spacer(1, 0.15 * inch))
            
            # Expense by category summary
            story.append(Paragraph("EXPENSES BY CATEGORY", subsection_style))
            
            category_totals = {}
            for expense in expenses_data:
                cat = expense.get('category', 'Other')
                category_totals[cat] = category_totals.get(cat, 0) + expense.get('amount', 0)
            
            category_data = [["Category", "Total Amount", "Percentage"]]
            for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                percentage = (total / total_expenses * 100) if total_expenses > 0 else 0
                category_data.append([cat.capitalize(), f"{currency} {total:,.0f}", f"{percentage:.1f}%"])
            
            category_table = Table(category_data, colWidths=[1.5 * inch, 1.2 * inch, 1 * inch])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('FONTSIZE', (0, 0), (2, -1), 8),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (2, -1), 'LEFT'),
                ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (2, -1), 5),
                ('TOPPADDING', (0, 0), (2, -1), 5),
                ('GRID', (0, 0), (2, -1), 0.3, colors.HexColor('#cbd5e1')),
            ]))
            story.append(category_table)
        
        # ============================================================
        # KPI SUMMARY
        # ============================================================
        if kpis_data:
            story.append(PageBreak())
            story.append(Paragraph("KEY PERFORMANCE INDICATORS (KPIs)", section_style))
            
            kpi_table_data = [["#", "KPI Name", "Target", "Actual", "KAR", "Status", "Period"]]
            
            for idx, kpi in enumerate(kpis_data, 1):
                kar = kpi.get('kar', 0)
                status = kpi.get('status', 'critical')
                
                status_color = "#22c55e" if status == "good" else "#3b82f6" if status == "satisfactory" else "#eab308" if status == "warning" else "#ef4444"
                status_display = "Good" if status == "good" else "Satisfactory" if status == "satisfactory" else "Warning" if status == "warning" else "Critical"
                
                period = ""
                if kpi.get('period_start') and kpi.get('period_end'):
                    period = f"{kpi.get('period_start')[:10]} to {kpi.get('period_end')[:10]}"
                
                kpi_table_data.append([
                    str(idx),
                    kpi.get('indicator_name', 'Unknown')[:35],
                    f"{kpi.get('target_value', 0):,.0f} {kpi.get('unit', '')}",
                    f"{kpi.get('actual_value', 0):,.0f} {kpi.get('unit', '')}" if kpi.get('actual_value') else "Not set",
                    f"{kar:.0f}%" if kar else "0%",
                    Paragraph(f'<font color="{status_color}">{status_display}</font>', table_cell_center),
                    period
                ])
            
            kpi_table = Table(kpi_table_data, colWidths=[0.35 * inch, 1.8 * inch, 0.8 * inch, 0.8 * inch, 0.5 * inch, 0.7 * inch, 1.2 * inch])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (6, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (6, 0), colors.whitesmoke),
                ('FONTSIZE', (0, 0), (6, -1), 7),
                ('FONTNAME', (0, 0), (6, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (6, -1), 'LEFT'),
                ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (6, -1), 4),
                ('TOPPADDING', (0, 0), (6, -1), 4),
                ('GRID', (0, 0), (6, -1), 0.3, colors.HexColor('#cbd5e1')),
            ]))
            story.append(kpi_table)
        
        # ============================================================
        # FOOTER
        # ============================================================
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("─" * 80, styles['Normal']))
        story.append(Spacer(1, 0.05 * inch))
        story.append(Paragraph(f"Report generated by Brick SPMES Project Management System", styles['Normal']))
        story.append(Paragraph(f"© 2026 Brick SPMES. All rights reserved. | Report ID: {uuid.uuid4().hex[:8].upper()}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Return both the PDF bytes and the filename suggestion
        return buffer.getvalue()


report_service = ReportService()