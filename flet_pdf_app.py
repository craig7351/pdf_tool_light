import flet as ft
import fitz
import os
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

def main(page: ft.Page):
    page.title = "PDF 批次標註大師 (Tkinter 混合版)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 800
    page.padding = 30
    
    # 隱藏 Tkinter 主視窗
    root = tk.Tk()
    root.withdraw()

    # UI 元件
    input_dir_text = ft.Text("尚未選擇...", italic=True, size=14)
    output_dir_text = ft.Text("尚未選擇...", italic=True, size=14)
    keyword_field = ft.TextField(label="要搜尋並變色的文字", hint_text="例如：Gemini", border_radius=10)
    status_text = ft.Text("", weight="bold")
    progress_bar = ft.ProgressBar(value=0, width=float("inf"), color="blue", visible=False)
    log_content = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=200)

    # 狀態
    state = {"input": "", "output": ""}

    # --- 混合式選取器 ---
    def pick_input_dir(e):
        path = filedialog.askdirectory(title="選擇輸入資料夾")
        if path:
            state["input"] = path
            input_dir_text.value = f"📂 輸入：{path}"
            page.update()

    def pick_output_dir(e):
        path = filedialog.askdirectory(title="選擇輸出資料夾")
        if path:
            state["output"] = path
            output_dir_text.value = f"📂 輸出：{path}"
            page.update()

    # --- 處理邏輯 ---
    def process_files(e):
        word = keyword_field.value.strip()
        if not state["input"] or not state["output"] or not word:
            status_text.value = "請填寫完整資訊！"
            status_text.color = "red"
            page.update()
            return

        files = list(Path(state["input"]).glob("*.pdf"))
        if not files:
            status_text.value = "無 PDF 檔案！"
            page.update()
            return

        status_text.value = "處理中..."
        status_text.color = "blue"
        progress_bar.visible = True
        progress_bar.value = 0
        log_content.controls.clear()
        page.update()

        for i, pdf_file in enumerate(files):
            try:
                doc = fitz.open(str(pdf_file))
                found = 0
                for page_obj in doc:
                    for inst in page_obj.search_for(word):
                        annot = page_obj.add_highlight_annot(inst)
                        annot.set_colors(stroke=(1, 1, 0))
                        annot.update()
                        found += 1
                doc.save(str(Path(state["output"]) / pdf_file.name), garbage=4, deflate=True)
                doc.close()
                log_content.controls.append(ft.Text(f"✅ {pdf_file.name} ({found})"))
            except Exception:
                log_content.controls.append(ft.Text(f"❌ {pdf_file.name} 失敗", color="red"))
            progress_bar.value = (i + 1) / len(files)
            page.update()

        status_text.value = "🎉 批次標註完成！"
        status_text.color = "green"
        page.update()

    # --- UI 佈局 ---
    page.add(
        ft.Column([
            ft.Text("PDF 批次標註大師", size=32, weight="bold", color="blue700"),
            ft.Text("整合 Tkinter 資料夾選擇與 Flet 質感介面", color="grey700"),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Step 1: 設定路徑", weight="bold", size=18),
                        ft.Row([
                            ft.ElevatedButton("選擇輸入資料夾", icon=ft.Icons.FOLDER_OPEN, on_click=pick_input_dir),
                            input_dir_text,
                        ]),
                        ft.Row([
                            ft.ElevatedButton("選擇輸出資料夾", icon=ft.Icons.CREATE_NEW_FOLDER, on_click=pick_output_dir),
                            output_dir_text,
                        ]),
                    ])
                )
            ),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Step 2: 輸入關鍵字", weight="bold", size=18),
                        keyword_field,
                    ])
                )
            ),
            ft.Container(
                padding=10,
                content=ft.Column([
                    ft.ElevatedButton("🚀 開始執行", width=float("inf"), on_click=process_files),
                    progress_bar,
                    status_text,
                ])
            ),
            ft.Text("處理日誌:", weight="bold"),
            ft.Container(
                content=log_content,
                border=ft.border.all(1, ft.Colors.GREY_300),
                padding=10,
                border_radius=10
            )
        ], spacing=20)
    )

if __name__ == "__main__":
    ft.run(main)
