import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os

def process_pdf():
    # 初始化 Tkinter 視窗 (不顯示主視窗)
    root = tk.Tk()
    root.withdraw()

    # 1. 讓使用者選擇 PDF 檔案
    pdf_path = filedialog.askopenfilename(
        title="請選擇 PDF 檔案",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
        print("未選擇檔案，程式結束。")
        return

    # 2. 詢問要搜尋並標註的文字
    search_text = simpledialog.askstring("輸入文字", f"請輸入要在 {os.path.basename(pdf_path)} 中搜尋並標註的文字：")

    if not search_text:
        messagebox.showwarning("警告", "未輸入關鍵字，程式結束。")
        return

    try:
        # 3. 開啟 PDF 並進行處理
        doc = fitz.open(pdf_path)
        found_count = 0

        for page in doc:
            # 搜尋頁面上的文字座標 (Rects)
            text_instances = page.search_for(search_text)
            
            # 在每個座標處添加螢光筆標註
            for inst in text_instances:
                annot = page.add_highlight_annot(inst)
                annot.set_colors(stroke=(1, 1, 0)) # 黃色 (RGB)
                annot.update()
                found_count += 1

        if found_count > 0:
            # 4. 另存新檔
            output_path = pdf_path.replace(".pdf", "_highlighted.pdf")
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            messagebox.showinfo("成功", f"處理完成！\n共標註了 {found_count} 個位置。\n檔案已儲存至：\n{output_path}")
            print(f"成功儲存至: {output_path}")
        else:
            messagebox.showinfo("提示", "在 PDF 中找不到指定的關鍵字。")
            doc.close()

    except Exception as e:
        messagebox.showerror("錯誤", f"處理過程中發生錯誤：\n{str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    process_pdf()
