import asyncio
import flet as ft

from core.scanner import (
    scan_code,
    scan_folder,
    save_report,
    save_pdf_report,
)

 
def main(page: ft.Page):

    page.title = "Python Security Platform"
    page.window.width = 1050
    page.window.height = 850
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#101820"
    page.padding = 25
    page.scroll = ft.ScrollMode.AUTO

    last_report = None

    code_field = ft.TextField(
        label="Paste Python Code",
        hint_text="Paste your Python code here...",
        multiline=True,
        min_lines=12,
        max_lines=20,
        expand=True,
        text_size=14,
        border_color="#344955",
        focused_border_color="#00D9A6",
        cursor_color="#00D9A6",
    )

    folder_field = ft.TextField(
        label="Project Folder Path",
        hint_text=r"C:\Users\YourName\Desktop\MyProject",
        expand=True,
        border_color="#344955",
        focused_border_color="#00D9A6",
    )

    status = ft.Text(
        "Ready to scan",
        color="#B0BEC5",
        size=14,
    )

    total_issues = ft.Text("0", size=25, weight=ft.FontWeight.BOLD)
    high_count = ft.Text("0", size=25, weight=ft.FontWeight.BOLD)
    medium_count = ft.Text("0", size=25, weight=ft.FontWeight.BOLD)
    low_count = ft.Text("0", size=25, weight=ft.FontWeight.BOLD)

    results = ft.Column(spacing=12)

    scan_code_button = ft.Button(
        "Scan Pasted Code",
        on_click=None,
    )

    scan_folder_button = ft.Button(
        "Scan Project Folder",
        on_click=None,
    )

    clear_button = ft.Button(
        "Clear",
        on_click=None,
    )

    json_button = ft.Button(
        "Export JSON",
        disabled=True,
        on_click=None,
    )

    pdf_button = ft.Button(
        "Export PDF",
        disabled=True,
        on_click=None,
    )

    def stat_card(title, value, color):

        value.color = color

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        title,
                        color="#B0BEC5",
                        size=13,
                    ),
                    value,
                ],
                spacing=8,
            ),
            bgcolor="#1B2A34",
            padding=18,
            border_radius=10,
            expand=True,
        )

    def update_summary(report):

        summary = report["summary"]

        total_issues.value = str(
            summary["total_issues"]
        )

        high_count.value = str(
            summary["high"]
        )

        medium_count.value = str(
            summary["medium"]
        )

        low_count.value = str(
            summary["low"]
        )

    def display_findings(findings):

        results.controls.clear()

        if not findings:

            results.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No issues were detected by the enabled scanners.",
                        color="#00D9A6",
                        size=16,
                    ),
                    bgcolor="#1B2A34",
                    padding=20,
                    border_radius=10,
                )
            )

            return

        severity_colors = {
            "HIGH": "#FF5252",
            "MEDIUM": "#FFB74D",
            "LOW": "#4FC3F7",
        }

        for finding in findings[:150]:

            severity = finding.get(
                "issue_severity",
                "UNKNOWN",
            ).upper()

            severity_color = severity_colors.get(
                severity,
                "#B0BEC5",
            )

            results.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        severity,
                                        color=severity_color,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        finding.get("test_id", ""),
                                        color="#B0BEC5",
                                    ),
                                    ft.Text(
                                        finding.get("scanner", ""),
                                        color="#00D9A6",
                                    ),
                                ],
                                wrap=True,
                            ),

                            ft.Divider(
                                color="#344955"
                            ),

                            ft.Text(
                                finding.get("issue_text", ""),
                                size=15,
                            ),

                            ft.Text(
                                "Confidence: "
                                + str(
                                    finding.get(
                                        "issue_confidence",
                                        "UNKNOWN",
                                    )
                                ),
                                color="#B0BEC5",
                            ),

                            ft.Text(
                                "File: "
                                + str(
                                    finding.get(
                                        "filename",
                                        "",
                                    )
                                ),
                                color="#B0BEC5",
                            ),

                            ft.Text(
                                "Line: "
                                + str(
                                    finding.get(
                                        "line_number",
                                        "",
                                    )
                                ),
                                color="#B0BEC5",
                            ),
                        ],
                        spacing=8,
                    ),
                    bgcolor="#1B2A34",
                    padding=15,
                    border_radius=10,
                )
            )

        if len(findings) > 150:

            results.controls.append(
                ft.Text(
                    f"Showing 150 of {len(findings)} findings.",
                    color="#B0BEC5",
                )
            )

    def set_buttons_disabled(disabled):

        scan_code_button.disabled = disabled
        scan_folder_button.disabled = disabled

        if disabled:
            json_button.disabled = True
            pdf_button.disabled = True

    async def run_code_scan(e):

        nonlocal last_report

        source_code = code_field.value or ""

        if not source_code.strip():

            status.value = "Please paste Python code first."
            page.update()
            return

        last_report = None
        results.controls.clear()

        set_buttons_disabled(True)

        status.value = "Scanning pasted code..."

        page.update()

        try:

            report = await asyncio.to_thread(
                scan_code,
                source_code,
            )

            last_report = report

            update_summary(report)
            display_findings(report["findings"])

            json_button.disabled = False
            pdf_button.disabled = False

            status.value = (
                "Scan completed | "
                f"Files: {report['files_scanned']} | "
                f"Issues: {report['summary']['total_issues']}"
            )

        except Exception as error:

            last_report = None

            status.value = (
                f"Scan Error: {error}"
            )

        finally:

            scan_code_button.disabled = False
            scan_folder_button.disabled = False

            page.update()

    async def run_folder_scan(e):

        nonlocal last_report

        folder_path = (
            folder_field.value or ""
        ).strip()

        if not folder_path:

            status.value = "Please enter a project folder path."
            page.update()
            return

        last_report = None
        results.controls.clear()

        set_buttons_disabled(True)

        status.value = "Scanning selected project..."

        page.update()

        try:

            report = await asyncio.to_thread(
                scan_folder,
                folder_path,
            )

            last_report = report

            update_summary(report)
            display_findings(report["findings"])

            json_button.disabled = False
            pdf_button.disabled = False

            status.value = (
                "Folder scan completed | "
                f"Files: {report['files_scanned']} | "
                f"Issues: {report['summary']['total_issues']}"
            )

        except Exception as error:

            last_report = None

            status.value = (
                f"Scan Error: {error}"
            )

        finally:

            scan_code_button.disabled = False
            scan_folder_button.disabled = False

            page.update()

    def clear_all(e):

        nonlocal last_report

        code_field.value = ""
        folder_field.value = ""

        last_report = None

        results.controls.clear()

        total_issues.value = "0"
        high_count.value = "0"
        medium_count.value = "0"
        low_count.value = "0"

        json_button.disabled = True
        pdf_button.disabled = True

        status.value = "Editor cleared. Ready to scan."

        page.update()

    def export_json(e):

        if last_report is None:
            status.value = "Complete a scan first."
            page.update()
            return

        try:

            report_path = save_report(last_report)

            status.value = (
                f"JSON report saved: {report_path}"
            )

        except Exception as error:

            status.value = (
                f"JSON Export Error: {error}"
            )

        page.update()

    def export_pdf(e):

        if last_report is None:
            status.value = "Complete a scan first."
            page.update()
            return

        try:

            report_path = save_pdf_report(last_report)

            status.value = (
                f"PDF report saved: {report_path}"
            )

        except Exception as error:

            status.value = (
                f"PDF Export Error: {error}"
            )

        page.update()

    scan_code_button.on_click = run_code_scan
    scan_folder_button.on_click = run_folder_scan
    clear_button.on_click = clear_all
    json_button.on_click = export_json
    pdf_button.on_click = export_pdf

    page.add(

        ft.Column(
            controls=[

                ft.Text(
                    "Python Security Platform",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color="#00D9A6",
                ),

                ft.Text(
                    "Local Python Security Scanner",
                    size=15,
                    color="#B0BEC5",
                ),

                ft.Divider(
                    color="#344955"
                ),

                ft.Text(
                    "1. Paste Code",
                    size=21,
                    weight=ft.FontWeight.BOLD,
                ),

                code_field,

                scan_code_button,

                ft.Divider(
                    color="#344955"
                ),

                ft.Text(
                    "2. Select Project Folder",
                    size=21,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "Enter the path of the project you want to scan.",
                    color="#B0BEC5",
                ),

                folder_field,

                scan_folder_button,

                clear_button,

                status,

                ft.Divider(
                    color="#344955"
                ),

                ft.Text(
                    "Security Overview",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Row(
                    controls=[
                        stat_card(
                            "Total Issues",
                            total_issues,
                            "#00D9A6",
                        ),

                        stat_card(
                            "High",
                            high_count,
                            "#FF5252",
                        ),
                    ],
                    wrap=True,
                ),

                ft.Row(
                    controls=[
                        stat_card(
                            "Medium",
                            medium_count,
                            "#FFB74D",
                        ),

                        stat_card(
                            "Low",
                            low_count,
                            "#4FC3F7",
                        ),
                    ],
                    wrap=True,
                ),

                ft.Divider(
                    color="#344955"
                ),

                ft.Text(
                    "Security Findings",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),

                results,

                ft.Divider(
                    color="#344955"
                ),

                ft.Text(
                    "Export Reports",
                    size=21,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Row(
                    controls=[
                        json_button,
                        pdf_button,
                    ],
                    wrap=True,
                ),

                ft.Text(
                    "Scans run locally. The application does not "
                    "execute the submitted Python code.",
                    color="#B0BEC5",
                    size=12,
                ),

            ],
            spacing=18,
        )
    )


ft.run(main)