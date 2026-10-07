# -*- coding: utf-8 -*-
"""
Script tạo Báo cáo Môn học Cơ sở Dữ liệu Nâng cao (K32MCS1)
Học viên: Trần Duy Khải
Đề tài: Hệ thống Giám sát & Quản trị Thiết bị IoT Nhà Thông Minh (Smart Home IoT Management System)
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_report():
    doc = docx.Document()

    # --- Page setup (A4, Margins: Top 2cm, Bottom 2cm, Left 3cm, Right 2cm) ---
    section = doc.sections[0]
    section.page_width = Inches(8.27)   # A4 width
    section.page_height = Inches(11.69) # A4 height
    section.top_margin = Inches(0.79)   # 2.0 cm
    section.bottom_margin = Inches(0.79)# 2.0 cm
    section.left_margin = Inches(1.18)  # 3.0 cm
    section.right_margin = Inches(0.79) # 2.0 cm

    # Color palette (Academic Navy & Modern accents)
    COLOR_PRIMARY = RGBColor(26, 54, 93)     # Deep Navy #1A365D
    COLOR_SECONDARY = RGBColor(43, 108, 176) # Steel Blue #2B6CB0
    COLOR_ACCENT = RGBColor(49, 130, 206)    # Bright Accent #3182CE
    COLOR_TEXT = RGBColor(45, 55, 72)        # Slate Dark #2D3748
    COLOR_MUTED = RGBColor(113, 128, 150)    # Gray #718096

    # XML Helper Functions
    def set_cell_shading(cell, color_hex):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                          f'<w:top w:w="{top}" w:type="dxa"/>'
                          f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                          f'<w:left w:w="{left}" w:type="dxa"/>'
                          f'<w:right w:w="{right}" w:type="dxa"/>'
                          f'</w:tcMar>')
        tcPr.append(tcMar)

    def set_cell_borders(cell, top="none", bottom="none", left="none", right="none", 
                         color="CBD5E0", sz="4"):
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                            f'<w:top w:val="{top}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                            f'<w:left w:val="{left}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                            f'<w:bottom w:val="{bottom}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                            f'<w:right w:val="{right}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                            f'</w:tcBorders>')
        tcPr.append(borders)

    # Document Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = COLOR_TEXT

    # Header & Footer setup
    header = section.header
    header_p = header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = header_p.add_run("BÁO CÁO MÔN HỌC: CƠ SỞ DỮ LIỆU NÂNG CAO | HỌC VIÊN: TRẦN DUY KHẢI - K32MCS1")
    hrun.font.name = 'Times New Roman'
    hrun.font.size = Pt(8.5)
    hrun.font.color.rgb = COLOR_MUTED

    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun = footer_p.add_run("Trang bài làm - Học viên K32MCS1")
    frun.font.name = 'Times New Roman'
    frun.font.size = Pt(9)
    frun.font.color.rgb = COLOR_MUTED

    # Helpers for Content
    def add_title(text, level=1):
        p = doc.add_paragraph()
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.bold = True
        if level == 1:
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
            run.font.size = Pt(16)
            run.font.color.rgb = COLOR_PRIMARY
        elif level == 2:
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            run.font.size = Pt(13.5)
            run.font.color.rgb = COLOR_SECONDARY
        elif level == 3:
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(44, 62, 80)
        return p

    def add_p(text, bold_prefix=None, italic=False, space_after=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.25
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.name = 'Times New Roman'
            r_bold.font.size = Pt(12)
            r_bold.bold = True
            r_bold.font.color.rgb = COLOR_TEXT
        r_text = p.add_run(text)
        r_text.font.name = 'Times New Roman'
        r_text.font.size = Pt(12)
        r_text.italic = italic
        r_text.font.color.rgb = COLOR_TEXT
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.2
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.name = 'Times New Roman'
            r_bold.font.size = Pt(12)
            r_bold.bold = True
            r_bold.font.color.rgb = COLOR_TEXT
        r_text = p.add_run(text)
        r_text.font.name = 'Times New Roman'
        r_text.font.size = Pt(12)
        r_text.font.color.rgb = COLOR_TEXT
        return p

    def add_callout(text, title="LƯU Ý QUẢN TRỊ & TOÀN VẸN DỮ LIỆU:"):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_shading(cell, "F0F4F8")
        set_cell_borders(cell, left="single", color="1A365D", sz="24") # 3pt left border
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r_title = p.add_run(title + "\n")
        r_title.bold = True
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(11)
        r_title.font.color.rgb = COLOR_PRIMARY

        r_text = p.add_run(text)
        r_text.italic = True
        r_text.font.name = 'Times New Roman'
        r_text.font.size = Pt(11)
        r_text.font.color.rgb = RGBColor(45, 55, 72)
        
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_after = Pt(4)

    def add_code_block(sql_code, caption=None):
        if caption:
            p_cap = doc.add_paragraph()
            p_cap.paragraph_format.space_before = Pt(6)
            p_cap.paragraph_format.space_after = Pt(2)
            p_cap.paragraph_format.keep_with_next = True
            r_cap = p_cap.add_run(f"Mã lệnh SQL minh họa: {caption}")
            r_cap.bold = True
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(11)
            r_cap.font.color.rgb = COLOR_SECONDARY

        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_shading(cell, "F8F9FA")
        set_cell_borders(cell, top="single", bottom="single", left="single", right="single",
                         color="CBD5E0", sz="4")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        
        lines = sql_code.strip().split('\n')
        for idx, line in enumerate(lines):
            r = p.add_run(line + ('\n' if idx < len(lines)-1 else ''))
            r.font.name = 'Consolas'
            r.font.size = Pt(9.5)
            if line.strip().startswith('--'):
                r.font.color.rgb = RGBColor(108, 117, 125) # comment gray
                r.italic = True
            else:
                r.font.color.rgb = RGBColor(27, 38, 59)
                
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_after = Pt(4)

    def add_styled_table(headers, rows_data, col_widths=None):
        table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Header Row
        hdr_cells = table.rows[0].cells
        for idx, header_text in enumerate(headers):
            cell = hdr_cells[idx]
            cell.text = header_text
            set_cell_shading(cell, "1A365D") # Navy Header
            set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
            set_cell_borders(cell, top="single", bottom="single", left="single", right="single",
                             color="CBD5E0", sz="4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            run = p.runs[0]
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
        # Data Rows
        for r_idx, row_data in enumerate(rows_data):
            row_cells = table.rows[r_idx + 1].cells
            bg_color = "F7FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, cell_value in enumerate(row_data):
                cell = row_cells[c_idx]
                cell.text = str(cell_value)
                set_cell_shading(cell, bg_color)
                set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
                set_cell_borders(cell, top="single", bottom="single", left="single", right="single",
                                 color="E2E8F0", sz="4")
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                if c_idx == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.runs[0]
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10.5)
                run.font.color.rgb = COLOR_TEXT

        # Set column widths if provided
        if col_widths:
            for row in table.rows:
                for idx, width in enumerate(col_widths):
                    row.cells[idx].width = Inches(width)

        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_after = Pt(4)
        return table

    def add_image_box(img_path, caption, width_inch=5.8):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(img_path, width=Inches(width_inch))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(8)
            r_cap = p_cap.add_run(caption)
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(10.5)
            r_cap.italic = True
            r_cap.font.color.rgb = COLOR_MUTED

    # =========================================================================
    # TRANG BÌA (COVER PAGE)
    # =========================================================================
    p_b1 = doc.add_paragraph()
    p_b1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_b1.paragraph_format.space_before = Pt(10)
    p_b1.paragraph_format.space_after = Pt(2)
    r = p_b1.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\nTRƯỜNG ĐẠI HỌC BÁCH KHOA - ĐẠI HỌC ĐÀ NẴNG")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.bold = True
    r.font.color.rgb = COLOR_TEXT

    p_b2 = doc.add_paragraph()
    p_b2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_b2.paragraph_format.space_after = Pt(20)
    r = p_b2.add_run("KHOA CÔNG NGHỆ THÔNG TIN - BẬC CAO HỌC (THẠC SĨ)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = COLOR_SECONDARY

    # Separator line
    p_sep = doc.add_paragraph()
    p_sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sep.paragraph_format.space_after = Pt(40)
    r = p_sep.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    r.font.color.rgb = COLOR_MUTED

    # Title Box
    p_report = doc.add_paragraph()
    p_report.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_report.paragraph_format.space_after = Pt(8)
    r = p_report.add_run("BÁO CÁO BÀI TẬP CÁ NHÂN MÔN HỌC")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = COLOR_PRIMARY

    p_subject = doc.add_paragraph()
    p_subject.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subject.paragraph_format.space_after = Pt(24)
    r = p_subject.add_run("CƠ SỞ DỮ LIỆU NÂNG CAO")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(20)
    r.bold = True
    r.font.color.rgb = COLOR_PRIMARY

    p_topic = doc.add_paragraph()
    p_topic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_topic.paragraph_format.space_after = Pt(40)
    r = p_topic.add_run("ĐỀ TÀI:\nTHIẾT KẾ, TỐI ƯU VÀ QUẢN TRỊ CƠ SỞ DỮ LIỆU HỆ THỐNG SMART HOME IOT\n(ĐẶC TẢ CHI TIẾT 10 NGHIỆP VỤ & TRUY VẤN NÂNG CAO)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    r.font.color.rgb = COLOR_SECONDARY

    # Student Info Table
    info_table = doc.add_table(rows=4, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("Học viên thực hiện:", "TRẦN DUY KHẢI"),
        ("Lớp / Khóa học:", "K32MCS1 (Khoa học Máy tính)"),
        ("Môn học:", "Cơ sở Dữ liệu Nâng cao"),
        ("Hệ quản trị CSDL:", "MySQL 8.0 (3NF) & MongoDB (NoSQL) & Spark Engine")
    ]
    for idx, (label, val) in enumerate(info_data):
        row = info_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(3.8)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(3)
        r0 = p0.add_run(label)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(11.5)
        r0.bold = True
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(3)
        r1 = p1.add_run(val)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11.5)
        if idx == 0:
            r1.bold = True

    # Date at bottom
    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(80)
    r = p_date.add_run("Đà Nẵng – Năm 2026")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.italic = True
    r.font.color.rgb = COLOR_MUTED

    doc.add_page_break()

    # =========================================================================
    # TRANG TÓM TẮT & LỜI CAM ĐOAN
    # =========================================================================
    add_title("TÓM TẮT BÁO CÁO (EXECUTIVE SUMMARY)", level=1)
    add_p(
        "Báo cáo này trình bày toàn bộ kết quả nghiên cứu, thiết kế, cài đặt và kiểm thử mô hình cơ sở dữ liệu "
        "cho Hệ thống Quản trị Nhà Thông minh (Smart Home IoT Management System) thuộc khuôn khổ môn học Cơ sở Dữ liệu Nâng cao (Lớp K32MCS1). "
        "Hệ thống giải quyết bài toán cốt lõi trong kỷ nguyên IoT: vừa đảm bảo tính toàn vẹn giao dịch khắt khe theo chuẩn ACID "
        "đối với dữ liệu kinh doanh, bất động sản, phân quyền và hợp đồng thanh toán trên cơ sở dữ liệu quan hệ (RDBMS MySQL chuẩn 3NF), "
        "vừa đáp ứng khả năng lưu trữ, xử lý thông lượng cao đối với chuỗi dữ liệu thời gian thực (Telemetry stream) từ hàng triệu cảm biến "
        "thông qua kiến trúc phi quan hệ (NoSQL MongoDB) kết hợp hệ sinh thái phân tán Apache Hadoop và Spark."
    )
    add_p(
        "Đặc biệt, theo yêu cầu của giảng viên hướng dẫn, báo cáo tập trung làm rõ 10 nghiệp vụ cốt lõi của hệ thống. "
        "Mỗi nghiệp vụ được phân tích chi tiết ở 3 khía cạnh: (1) Mô tả nghiệp vụ và quy trình luồng dữ liệu, "
        "(2) Phương pháp quản trị cơ sở dữ liệu và bảo đảm tính toàn vẹn (Constraints, Foreign Keys, Indexes, Triggers, Transactions), "
        "và (3) Bộ truy vấn SQL hoàn chỉnh (từ mức thao tác dữ liệu DDL/DML đến các truy vấn báo cáo phân tích nâng cao sử dụng JOIN, GROUP BY, Window Functions)."
    )

    add_title("LỜI CAM ĐOAN HỌC THUẬT", level=2)
    add_p(
        "Tôi xin cam đoan đây là công trình báo cáo bài tập cá nhân được thực hiện độc lập bởi chính tôi - học viên Trần Duy Khải (Lớp K32MCS1) "
        "dưới sự hướng dẫn của giảng viên phụ trách môn học Cơ sở Dữ liệu Nâng cao. Mọi số liệu thực nghiệm, mô hình ERD, cấu trúc bảng 3NF, "
        "các câu lệnh truy vấn SQL, mã nguồn pipeline NoSQL/Big Data và Web Dashboard trình bày trong báo cáo đều được cài đặt, kiểm thử "
        "và vận hành thực tế trong cơ sở dữ liệu dự án."
    )
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(20)
    p_sign.paragraph_format.space_after = Pt(4)
    r_sign = p_sign.add_run("Học viên thực hiện\n\n\n\nTRẦN DUY KHẢI")
    r_sign.font.name = 'Times New Roman'
    r_sign.font.size = Pt(12)
    r_sign.bold = True

    doc.add_page_break()

    # =========================================================================
    # MỤC LỤC & DANH MỤC THUẬT NGỮ
    # =========================================================================
    add_title("MỤC LỤC TỔNG QUAN", level=1)
    toc_data = [
        ("LỜI MỞ ĐẦU", "Trang 4"),
        ("CHƯƠNG 1: TỔNG QUAN HỆ THỐNG VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU (GIAI ĐOẠN 1)", "Trang 5"),
        ("   1.1. Bối cảnh bài toán và phạm vi ứng dụng IoT Smart Home", "Trang 5"),
        ("   1.2. Mô hình Thực thể - Liên kết (ERD) và Quan hệ Dữ liệu", "Trang 6"),
        ("   1.3. Phân tích quá trình Chuẩn hóa Cơ sở Dữ liệu (1NF, 2NF, 3NF)", "Trang 7"),
        ("   1.4. Đặc tả chi tiết 9 Bảng Dữ liệu Quan hệ hệ thống smart_home_info", "Trang 8"),
        ("   1.5. Luận giải tính nhất quán giữa mô hình 7 bảng và 9 bảng hoàn chỉnh", "Trang 11"),
        ("CHƯƠNG 2: ĐẶC TẢ CHI TIẾT 10 NGHIỆP VỤ QUẢN TRỊ VÀ TRUY VẤN NÂNG CAO (GIAI ĐOẠN 2)", "Trang 12"),
        ("   2.1. Nghiệp vụ 1: Đăng ký tài khoản & Quản lý hồ sơ người dùng", "Trang 12"),
        ("   2.2. Nghiệp vụ 2: Thiết lập cấu trúc nhà và phân bổ phòng chức năng", "Trang 14"),
        ("   2.3. Nghiệp vụ 3: Phân quyền chia sẻ quyền quản trị và thành viên nhà (RBAC)", "Trang 16"),
        ("   2.4. Nghiệp vụ 4: Lắp đặt, kích hoạt và quản lý vòng đời thiết bị IoT", "Trang 18"),
        ("   2.5. Nghiệp vụ 5: Tra cứu, định vị và kiểm soát thiết bị theo tầng/phòng", "Trang 20"),
        ("   2.6. Nghiệp vụ 6: Đăng ký, kích hoạt và tự động gia hạn gói dịch vụ thuê bao", "Trang 22"),
        ("   2.7. Nghiệp vụ 7: Quản lý thanh toán hóa đơn & truy vết đối soát tài chính", "Trang 24"),
        ("   2.8. Nghiệp vụ 8: Giám sát công suất tiêu thụ điện & cảnh báo quá tải thiết bị", "Trang 26"),
        ("   2.9. Nghiệp vụ 9: Phát hiện thiết bị mất kết nối (Offline) & quản lý lịch bảo trì", "Trang 28"),
        ("   2.10. Nghiệp vụ 10: Thống kê doanh thu, tỷ lệ duy trì khách hàng & đối soát SLA", "Trang 30"),
        ("CHƯƠNG 3: MỞ RỘNG KIẾN TRÚC DỮ LIỆU LỚN VÀ WEB DASHBOARD GIÁM SÁT (GIAI ĐOẠN 3)", "Trang 32"),
        ("   3.1. Thách thức Big Data (3V) trong Telemetry IoT", "Trang 32"),
        ("   3.2. Thiết kế Cơ sở Dữ liệu NoSQL MongoDB và Aggregation Pipelines", "Trang 33"),
        ("   3.3. Xử lý phân tích dữ liệu lớn trên Apache Hadoop & Spark Engine", "Trang 35"),
        ("   3.4. Xây dựng Trung tâm Điều hành Web Dashboard (IoT Command Center)", "Trang 36"),
        ("      3.4.1. Màn hình Tổng quan Hệ thống (Executive Overview Dashboard)", "Trang 36"),
        ("      3.4.2. Màn hình Phân tích Năng lượng & Phụ tải Điện năng (Energy Analytics)", "Trang 37"),
        ("      3.4.3. Màn hình Giám sát An toàn & Cảnh báo Sự cố Bất thường (Anomaly Center)", "Trang 38"),
        ("      3.4.4. Màn hình Quản trị Kinh doanh & Hợp đồng Thuê bao (Subscription Insights)", "Trang 39"),
        ("   3.5. Kiểm thử tải hiệu năng và Quản trị CSDL quy mô lớn (7 Triệu bản ghi)", "Trang 40"),
        ("CHƯƠNG 4: BÀN LUẬN, ĐÁNH GIÁ VÀ GIẢI PHÁP TỐI ƯU CƠ SỞ DỮ LIỆU", "Trang 38"),
        ("   4.1. Đánh giá mô hình lưu trữ đa hệ (Hybrid Polyglot Persistence)", "Trang 38"),
        ("   4.2. Chiến lược chỉ mục (Indexing Strategy) và tối ưu hóa câu lệnh", "Trang 39"),
        ("   4.3. Đảm bảo an toàn, bảo mật thông tin và sao lưu phục hồi", "Trang 40"),
        ("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "Trang 41"),
        ("TÀI LIỆU THAM KHẢO & PHỤ LỤC", "Trang 42")
    ]
    for title_text, page_num in toc_data:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r1 = p.add_run(title_text)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11)
        if not title_text.startswith("   "):
            r1.bold = True
            r1.font.color.rgb = COLOR_PRIMARY
        r_dots = p.add_run(" " + "." * max(10, 85 - len(title_text) * 2) + " ")
        r_dots.font.name = 'Times New Roman'
        r_dots.font.color.rgb = COLOR_MUTED
        r2 = p.add_run(page_num)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(11)
        r2.bold = True

    add_title("DANH MỤC TỪ VIẾT TẮT VÀ THUẬT NGỮ", level=2)
    terms_headers = ["Ký hiệu / Viết tắt", "Thuật ngữ tiếng Anh", "Ý nghĩa trong hệ thống"]
    terms_rows = [
        ["RDBMS", "Relational Database Management System", "Hệ quản trị cơ sở dữ liệu quan hệ (sử dụng MySQL 8.0)"],
        ["NoSQL", "Not Only SQL", "Cơ sở dữ liệu phi quan hệ (sử dụng MongoDB lưu trữ telemetry)"],
        ["3NF", "Third Normal Form", "Dạng chuẩn 3 trong thiết kế cơ sở dữ liệu quan hệ"],
        ["ERD", "Entity - Relationship Diagram", "Sơ đồ thực thể - liên kết mô hình hóa nghiệp vụ"],
        ["IoT", "Internet of Things", "Mạng lưới vạn vật kết nối Internet (thiết bị cảm biến, điều hòa...)"],
        ["RBAC", "Role-Based Access Control", "Kiểm soát truy cập dựa trên vai trò (OWNER, ADMIN, MEMBER, GUEST)"],
        ["ACID", "Atomicity, Consistency, Isolation, Durability", "Bốn thuộc tính cốt lõi của giao dịch cơ sở dữ liệu quan hệ"],
        ["SLA", "Service Level Agreement", "Cam kết chất lượng dịch vụ giữa nhà cung cấp và khách hàng"],
        ["HDFS", "Hadoop Distributed File System", "Hệ thống tệp phân tán lưu trữ dữ liệu lớn"],
        ["ARPU", "Average Revenue Per User", "Chỉ số doanh thu trung bình trên mỗi khách hàng"],
        ["Telemetry", "Telemetry Data", "Dữ liệu đo đạc từ xa phát sinh tự động từ cảm biến (nhiệt, công suất)"]
    ]
    add_styled_table(terms_headers, terms_rows, [1.5, 2.5, 3.0])

    add_title("DANH MỤC HÌNH ẢNH MINH HỌA", level=2)
    figures_headers = ["Ký hiệu hình", "Tên hình ảnh minh họa", "Vị trí trong báo cáo"]
    figures_rows = [
        ["Hình 1.1", "Sơ đồ Thực thể - Liên kết (Entity - Relationship Diagram - ERD)", "Chương 1 (Mục 1.2)"],
        ["Hình 1.2", "Mô hình Dữ liệu Quan hệ (Relational Schema chuẩn 3NF)", "Chương 1 (Mục 1.2)"],
        ["Hình 3.1", "Giao diện Trực quan hóa Luồng Kiến trúc Dữ liệu NoSQL & Hadoop Data Lake", "Chương 3 (Mục 3.3)"],
        ["Hình 3.2", "Giao diện Tổng quan Hệ thống (Executive Overview Dashboard - IoT Command Center)", "Chương 3 (Mục 3.4.1)"],
        ["Hình 3.3", "Giao diện Phân tích Điện năng - Phụ tải Giờ Cao điểm EVN & Cơ cấu chủng loại", "Chương 3 (Mục 3.4.2)"],
        ["Hình 3.4", "Giao diện Giám sát An toàn & Cảnh báo Sự cố Bất thường Thời gian thực", "Chương 3 (Mục 3.4.3)"],
        ["Hình 3.5", "Giao diện Quản trị Kinh doanh & Đối soát SLA Hợp đồng Thuê bao", "Chương 3 (Mục 3.4.4)"],
        ["Hình 3.6", "Giao diện Trình diễn & Truy vấn Cơ sở Dữ liệu RDBMS MySQL quy mô 7 Triệu Bản ghi", "Chương 3 (Mục 3.5)"]
    ]
    add_styled_table(figures_headers, figures_rows, [1.5, 4.2, 1.5])

    doc.add_page_break()

    # =========================================================================
    # LỜI MỞ ĐẦU
    # =========================================================================
    add_title("LỜI MỞ ĐẦU", level=1)
    add_p(
        "Sự phát triển mạnh mẽ của cuộc Cách mạng Công nghiệp lần thứ tư đã đưa công nghệ Vạn vật kết nối (Internet of Things - IoT) "
        "thâm nhập sâu rộng vào đời sống thường nhật. Trong đó, mô hình Nhà thông minh (Smart Home) không còn dừng lại ở mức điều khiển "
        "thiết bị đơn lẻ mà đã phát triển thành các hệ sinh thái phức hợp bao gồm: tự động hóa môi trường sống, giám sát phụ tải điện năng, "
        "an ninh cảnh báo và cung cấp dịch vụ phần mềm theo mô hình thuê bao (SaaS - Software as a Service).",
        bold_prefix="1. Tính cấp thiết của đề tài: "
    )
    add_p(
        "Các hệ thống Smart Home đặt ra thách thức chưa từng có đối với kiến trúc cơ sở dữ liệu:",
        bold_prefix="2. Thách thức kỹ thuật: "
    )
    add_bullet(
        "Một mặt, hệ thống đòi hỏi tính chính xác, nhất quán tuyệt đối (ACID) đối với các thực thể quản trị kinh doanh: tài khoản người dùng, "
        "quyền sở hữu bất động sản, cấu trúc phòng ốc, hợp đồng thuê bao và hóa đơn tài chính. Bất kỳ một sự sai lệch nào trong thanh toán "
        "hoặc phân quyền đều có thể dẫn đến rủi ro pháp lý và an ninh nghiêm trọng.",
        bold_prefix="Tính toàn vẹn giao dịch (Transaction Integrity): "
    )
    add_bullet(
        "Mặt khác, hàng chục ngàn thiết bị IoT hoạt động liên tục phát sinh khối lượng khổng lồ dữ liệu viễn thám (telemetry) chuỗi thời gian "
        "với tần suất tính bằng giây/phút (nhiệt độ, độ ẩm, điện áp, công suất tiêu thụ). Mô hình quan hệ truyền thống sẽ nhanh chóng bị "
        "nghẽn cổ chai I/O nếu phải ghi nhận đồng thời cả hai luồng dữ liệu này.",
        bold_prefix="Áp lực dữ liệu lớn (Big Data Pressure): "
    )
    add_p(
        "Nhằm giải quyết toàn diện bài toán trên, báo cáo này triển khai mô hình kiến trúc lai (Hybrid Architecture / Polyglot Persistence): "
        "Sử dụng MySQL 8.0 được chuẩn hóa nghiêm ngặt về dạng chuẩn 3NF để quản trị 9 thực thể giao dịch lõi và cài đặt 10 nghiệp vụ kinh doanh; "
        "đồng thời tích hợp MongoDB và Hadoop/Spark để xử lý dòng dữ liệu lớn cảm biến.",
        bold_prefix="3. Giải pháp và Phạm vi nghiên cứu: "
    )

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 1: TỔNG QUAN HỆ THỐNG VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU (GIAI ĐOẠN 1)
    # =========================================================================
    add_title("CHƯƠNG 1: TỔNG QUAN HỆ THỐNG VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU (GIAI ĐOẠN 1)", level=1)
    
    add_title("1.1. Khảo sát nghiệp vụ và các thực thể hệ thống", level=2)
    add_p(
        "Hệ thống Smart Home IoT Management System được thiết kế nhằm quản lý vòng đời toàn diện của các thiết bị thông minh được lắp đặt "
        "tại các bất động sản (căn hộ, nhà phố, biệt thự) của khách hàng. Qua khảo sát nghiệp vụ thực tế, hệ thống bao gồm các nhóm đối tượng chính sau:"
    )
    add_bullet("Người dùng (Chủ sở hữu, thành viên gia đình, khách thuê).", bold_prefix="Nhóm Người dùng & Khách hàng: ")
    add_bullet("Căn hộ / Tòa nhà (Home) và các phân khu chức năng (Room) phân tầng rõ ràng.", bold_prefix="Nhóm Không gian & Vị trí: ")
    add_bullet("Chủng loại định danh chuẩn hóa (DeviceType) và Thiết bị vật lý thực tế (Device) kèm địa chỉ MAC, Serial Number.", bold_prefix="Nhóm Thiết bị IoT: ")
    add_bullet("Gói cước lưu trữ đám mây (SubscriptionPlan), Hợp đồng thuê bao căn hộ (HomeSubscription) và Hóa đơn giao dịch (Invoice).", bold_prefix="Nhóm Kinh doanh & Dịch vụ: ")

    add_title("1.2. Mô hình Thực thể - Liên kết (ERD) và Sơ đồ Quan hệ", level=2)
    add_p(
        "Dựa trên các mối quan hệ nghiệp vụ, mô hình Thực thể - Liên kết (Entity - Relationship Diagram - ERD) được xây dựng chặt chẽ. "
        "Hình 1.1 và Hình 1.2 thể hiện trực quan cấu trúc liên kết và sơ đồ quan hệ giữa các thực thể."
    )
    
    # Chèn ảnh ERD và Mô hình Quan hệ
    add_image_box("extracted_images/g1_image2.png", "Hình 1.1: Sơ đồ Thực thể - Liên kết (Entity - Relationship Diagram)", width_inch=5.8)
    add_image_box("extracted_images/g1_image1.png", "Hình 1.2: Mô hình Dữ liệu Quan hệ (Relational Schema)", width_inch=5.8)

    add_title("1.3. Phân tích quá trình Chuẩn hóa Cơ sở Dữ liệu (1NF, 2NF, 3NF)", level=2)
    add_p(
        "Để đảm bảo cơ sở dữ liệu không bị dư thừa dữ liệu (data redundancy) và loại trừ hoàn toàn các bất thường cập nhật (update anomaly), "
        "bất thường xóa (delete anomaly) và bất thường thêm mới (insert anomaly), mô hình dữ liệu đã được chuẩn hóa qua 3 bước nghiêm ngặt:"
    )
    add_p(
        "Tất cả các thuộc tính trong mỗi bảng đều mang giá trị nguyên tử (atomic value). Không có thuộc tính lặp "
        "(như danh sách thành viên hay danh sách thiết bị lưu dưới dạng mảng/chuỗi phân tách dấu phẩy trong bảng Home). "
        "Mỗi bảng đều có một Khóa chính (Primary Key) xác định duy nhất từng bản ghi.",
        bold_prefix="• Dạng chuẩn 1 (1NF): "
    )
    add_p(
        "Mô hình đạt 1NF và mọi thuộc tính không khóa đều phụ thuộc hàm toàn phần vào Khóa chính. "
        "Đặc biệt, với quan hệ nhiều - nhiều (N:N) giữa User và Home, hệ thống không gộp vào một bảng mà tách riêng bảng trung gian HomeMember "
        "với khóa chính phức hợp (home_id, user_id). Các thuộc tính role và joined_at phụ thuộc vào cả cặp khóa này (một người dùng giữ vai trò gì "
        "trong một ngôi nhà cụ thể), không có thuộc tính nào phụ thuộc vào một phần khóa chính. Các bảng còn lại đều có khóa đơn nên mặc nhiên thỏa mãn 2NF.",
        bold_prefix="• Dạng chuẩn 2 (2NF): "
    )
    add_p(
        "Mô hình đạt 2NF và không tồn tại phụ thuộc bắc cầu (transitive dependency) giữa các thuộc tính không khóa. Cụ thể: "
        "(1) Thông tin gói cước (tên gói, giá cước, hạn mức thiết bị) được tách thành bảng riêng SubscriptionPlan, không gộp vào HomeSubscription "
        "để tránh phụ thuộc bắc cầu (subscription_id -> plan_id -> price); (2) Thông tin chủng loại thiết bị (nhà sản xuất, model, công suất tối đa) "
        "được tách thành bảng DeviceType, không để trong bảng Device; (3) Hóa đơn tách thành bảng Invoice với quan hệ chặt chẽ tới hợp đồng.",
        bold_prefix="• Dạng chuẩn 3 (3NF): "
    )

    add_title("1.4. Đặc tả chi tiết 9 Bảng Dữ liệu Quan hệ hệ thống smart_home_info", level=2)
    add_p("Hệ thống cơ sở dữ liệu quan hệ hoàn chỉnh bao gồm 9 bảng được định nghĩa chi tiết như sau:")

    # Bảng 1: User
    add_p("1. Bảng `User` (Quản lý tài khoản khách hàng)", bold_prefix="Chi tiết: ")
    user_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    user_rows = [
        ["user_id", "INT AUTO_INCREMENT", "PRIMARY KEY", "Mã định danh duy nhất của người dùng"],
        ["full_name", "VARCHAR(100)", "NOT NULL", "Họ và tên đầy đủ của người dùng"],
        ["email", "VARCHAR(100)", "NOT NULL, UNIQUE", "Địa chỉ email (tên đăng nhập, chống trùng lặp)"],
        ["phone", "VARCHAR(20)", "NULL", "Số điện thoại liên hệ"],
        ["password_hash", "VARCHAR(255)", "NOT NULL", "Mật khẩu đã được mã hóa băm an toàn (SHA-256)"],
        ["created_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm tạo tài khoản"],
        ["updated_at", "DATETIME", "ON UPDATE CURRENT_TIMESTAMP", "Thời điểm cập nhật thông tin gần nhất"]
    ]
    add_styled_table(user_hdrs, user_rows, [1.5, 1.8, 1.8, 2.0])

    # Bảng 2: Home
    add_p("2. Bảng `Home` (Bất động sản / Nhà thông minh)", bold_prefix="Chi tiết: ")
    home_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    home_rows = [
        ["home_id", "INT AUTO_INCREMENT", "PRIMARY KEY", "Mã định danh duy nhất của ngôi nhà"],
        ["user_id", "INT", "FK -> User(user_id), NOT NULL", "Mã chủ sở hữu bất động sản (Owner)"],
        ["home_name", "VARCHAR(100)", "NOT NULL", "Tên nhận diện ngôi nhà (Biệt thự, Căn hộ...)"],
        ["address", "VARCHAR(255)", "NOT NULL", "Địa chỉ thực tế của ngôi nhà"],
        ["created_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm đăng ký nhà vào hệ thống"],
        ["updated_at", "DATETIME", "ON UPDATE CURRENT_TIMESTAMP", "Thời điểm cập nhật thông tin nhà"]
    ]
    add_styled_table(home_hdrs, home_rows, [1.5, 1.8, 1.8, 2.0])

    # Bảng 3: HomeMember
    add_p("3. Bảng `HomeMember` (Phân quyền thành viên & chia sẻ nhà)", bold_prefix="Chi tiết: ")
    hm_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    hm_rows = [
        ["home_id", "INT", "PK, FK -> Home(home_id)", "Mã ngôi nhà được chia sẻ quyền"],
        ["user_id", "INT", "PK, FK -> User(user_id)", "Mã người dùng được cấp quyền"],
        ["role", "ENUM", "NOT NULL (OWNER, ADMIN, MEMBER, GUEST)", "Vai trò phân quyền trong ngôi nhà"],
        ["joined_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm được cấp quyền vào nhà"]
    ]
    add_styled_table(hm_hdrs, hm_rows, [1.5, 1.8, 1.8, 2.0])

    # Bảng 4: Room
    add_p("4. Bảng `Room` (Phòng chức năng / Vị trí)", bold_prefix="Chi tiết: ")
    room_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    room_rows = [
        ["room_id", "INT AUTO_INCREMENT", "PRIMARY KEY", "Mã định danh duy nhất của phòng"],
        ["home_id", "INT", "FK -> Home(home_id), NOT NULL", "Mã ngôi nhà sở hữu phòng này"],
        ["room_name", "VARCHAR(50)", "NOT NULL", "Tên phòng (Phòng khách, Phòng ngủ master...)"],
        ["floor", "INT", "DEFAULT 1, CHECK (floor > 0)", "Tầng vị trí đặt phòng (tối thiểu tầng 1)"],
        ["created_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm tạo phòng"]
    ]
    add_styled_table(room_hdrs, room_rows, [1.5, 1.8, 1.8, 2.0])

    # Bảng 5: DeviceType
    add_p("5. Bảng `DeviceType` (Quy chuẩn danh mục thiết bị IoT)", bold_prefix="Chi tiết: ")
    dt_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    dt_rows = [
        ["type_id", "INT AUTO_INCREMENT", "PRIMARY KEY", "Mã định danh loại thiết bị"],
        ["type_name", "VARCHAR(50)", "NOT NULL", "Tên chuẩn loại thiết bị (Điều hòa, Đèn thông minh...)"],
        ["manufacturer", "VARCHAR(50)", "NOT NULL", "Nhà sản xuất (Daikin, Xiaomi, Philips, Tuya...)"],
        ["model", "VARCHAR(50)", "NOT NULL", "Mã model kỹ thuật"],
        ["protocol", "VARCHAR(20)", "DEFAULT 'WiFi'", "Giao thức kết nối (WiFi, Zigbee, Bluetooth, Matter)"],
        ["category", "VARCHAR(30)", "NOT NULL", "Nhóm phân loại (Lighting, Climate, Security, Energy)"],
        ["max_power_watt", "DECIMAL(6,1)", "DEFAULT 0.0", "Công suất tiêu thụ tối đa định mức (Watts)"],
        ["created_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm đưa model vào danh mục"]
    ]
    add_styled_table(dt_hdrs, dt_rows, [1.5, 1.8, 1.8, 2.0])

    # Bảng 6: Device
    add_p("6. Bảng `Device` (Thiết bị IoT vật lý)", bold_prefix="Chi tiết: ")
    dev_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    dev_rows = [
        ["device_id", "INT AUTO_INCREMENT", "PRIMARY KEY", "Mã định danh duy nhất của thiết bị vật lý"],
        ["room_id", "INT", "FK -> Room(room_id), NULL", "Phòng lắp đặt (SET NULL nếu phòng bị xóa)"],
        ["home_id", "INT", "FK -> Home(home_id), NOT NULL", "Ngôi nhà quản lý thiết bị"],
        ["type_id", "INT", "FK -> DeviceType(type_id), NOT NULL", "Chủng loại phần cứng thiết bị"],
        ["device_name", "VARCHAR(100)", "NOT NULL", "Tên gọi thân thiện người dùng đặt"],
        ["serial_number", "VARCHAR(50)", "NOT NULL, UNIQUE", "Số serial của nhà sản xuất"],
        ["mac_address", "VARCHAR(17)", "NOT NULL, UNIQUE", "Địa chỉ vật lý MAC (duy nhất trên toàn mạng)"],
        ["status", "ENUM", "DEFAULT 'OFFLINE' (ONLINE, OFFLINE, MAINTENANCE, FAULTY)", "Trạng thái vận hành hiện thời"],
        ["firmware_version", "VARCHAR(20)", "DEFAULT '1.0.0'", "Phiên bản phần mềm điều khiển"],
        ["installed_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm lắp đặt nghiệm thu"],
        ["last_active", "DATETIME", "NULL", "Thời điểm phát tín hiệu Heartbeat gần nhất"]
    ]
    add_styled_table(dev_hdrs, dev_rows, [1.5, 1.8, 1.8, 2.0])

    # Bảng 7: SubscriptionPlan
    add_p("7. Bảng `SubscriptionPlan` (Gói dịch vụ lưu trữ đám mây)", bold_prefix="Chi tiết: ")
    sp_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    sp_rows = [
        ["plan_id", "INT AUTO_INCREMENT", "PRIMARY KEY", "Mã gói cước dịch vụ"],
        ["plan_name", "VARCHAR(50)", "NOT NULL", "Tên gói cước (Free Tier, Standard, Premium...)"],
        ["duration_days", "INT", "NOT NULL, CHECK > 0", "Thời hạn hiệu lực của gói (ngày)"],
        ["price", "DECIMAL(10,2)", "NOT NULL, CHECK >= 0", "Đơn giá niêm yết (VNĐ)"],
        ["max_homes", "INT", "DEFAULT 1", "Số lượng nhà tối đa được áp dụng"],
        ["max_devices", "INT", "DEFAULT 10", "Số lượng thiết bị tối đa được kết nối"],
        ["cloud_storage_days", "INT", "DEFAULT 7", "Số ngày lưu trữ video/telemetry trên đám mây"],
        ["description", "TEXT", "NULL", "Mô tả chi tiết quyền lợi gói"]
    ]
    add_styled_table(sp_hdrs, sp_rows, [1.5, 1.8, 1.8, 2.0])

    # Bảng 8: HomeSubscription
    add_p("8. Bảng `HomeSubscription` (Hợp đồng thuê bao căn hộ)", bold_prefix="Chi tiết: ")
    hs_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    hs_rows = [
        ["subscription_id", "INT AUTO_INCREMENT", "PRIMARY KEY", "Mã hợp đồng thuê bao"],
        ["home_id", "INT", "FK -> Home(home_id), NOT NULL", "Căn hộ đăng ký sử dụng dịch vụ"],
        ["plan_id", "INT", "FK -> SubscriptionPlan(plan_id), NOT NULL", "Gói cước dịch vụ lựa chọn"],
        ["start_date", "DATE", "NOT NULL", "Ngày bắt đầu chu kỳ thuê bao"],
        ["end_date", "DATE", "NOT NULL, CHECK (end_date >= start_date)", "Ngày kết thúc chu kỳ thuê bao"],
        ["status", "ENUM", "DEFAULT 'ACTIVE' (ACTIVE, EXPIRED, CANCELLED)", "Trạng thái hợp đồng thuê bao"],
        ["auto_renew", "TINYINT(1)", "DEFAULT 1", "Cờ cho phép tự động gia hạn khi hết hạn (1: Bật, 0: Tắt)"],
        ["created_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm kích hoạt hợp đồng"]
    ]
    add_styled_table(hs_hdrs, hs_rows, [1.5, 1.8, 1.8, 2.0])

    # Bảng 9: Invoice
    add_p("9. Bảng `Invoice` (Hóa đơn và thanh toán)", bold_prefix="Chi tiết: ")
    inv_hdrs = ["Tên cột", "Kiểu dữ liệu", "Khóa / Ràng buộc", "Diễn giải ý nghĩa nghiệp vụ"]
    inv_rows = [
        ["invoice_id", "INT AUTO_INCREMENT", "PRIMARY KEY", "Mã số hóa đơn tài chính"],
        ["subscription_id", "INT", "FK -> HomeSubscription, NOT NULL", "Hợp đồng thuê bao phát sinh hóa đơn"],
        ["user_id", "INT", "FK -> User(user_id), NOT NULL", "Khách hàng chịu trách nhiệm thanh toán"],
        ["amount", "DECIMAL(10,2)", "NOT NULL, CHECK > 0", "Số tiền phải thanh toán (VNĐ)"],
        ["payment_method", "ENUM", "DEFAULT 'CREDIT_CARD' (CREDIT_CARD, BANK_TRANSFER, E_WALLET, CASH)", "Phương thức thanh toán giao dịch"],
        ["payment_status", "ENUM", "DEFAULT 'PENDING' (PENDING, PAID, FAILED, REFUNDED)", "Trạng thái xử lý thanh toán"],
        ["transaction_code", "VARCHAR(50)", "NULL, UNIQUE", "Mã tham chiếu đối soát cổng thanh toán"],
        ["paid_at", "DATETIME", "NULL", "Thời điểm hoàn tất thanh toán"],
        ["created_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Thời điểm phát hành hóa đơn"]
    ]
    add_styled_table(inv_hdrs, inv_rows, [1.5, 1.8, 1.8, 2.0])

    add_title("1.5. Luận giải tính nhất quán giữa mô hình 7 bảng sơ thảo và 9 bảng hoàn chỉnh", level=2)
    add_p(
        "Trong đề cương ban đầu của Giai đoạn 1 và báo cáo tóm tắt sơ bộ, hệ thống có đề cập đến 7 bảng nghiệp vụ. "
        "Tuy nhiên, khi tiến hành chuẩn hóa dữ liệu thực nghiệm theo tiêu chuẩn 3NF và triển khai hệ thống quản trị hoàn chỉnh, "
        "học viên đã bổ sung 2 bảng thực thể thiết yếu nhằm đảm bảo tính chặt chẽ học thuật và thực tiễn vận hành:",
        bold_prefix="Giải trình học thuật: "
    )
    add_bullet(
        "Quan hệ giữa User và Home là quan hệ nhiều - nhiều (N:N) do một ngôi nhà có thể có nhiều thành viên cùng chung sống, "
        "và một người dùng có thể là thành viên của nhiều căn hộ khác nhau. Nếu không tách bảng HomeMember, ta buộc phải lưu danh sách "
        "thành viên dưới dạng chuỗi trong bảng Home (vi phạm 1NF) hoặc trùng lặp bản ghi Home (vi phạm 2NF). Bảng HomeMember với khóa chính phức hợp "
        "(home_id, user_id) giải quyết triệt để bài toán phân quyền Role-Based Access Control (RBAC).",
        bold_prefix="Bổ sung bảng `HomeMember`: "
    )
    add_bullet(
        "Nếu gộp trực tiếp thông tin thuê bao vào bảng Home, mỗi căn hộ chỉ có thể gắn với một gói dịch vụ duy nhất và không thể lưu vết "
        "lịch sử các lần gia hạn, nâng cấp gói. Việc tách riêng HomeSubscription cho phép một căn hộ có nhiều chu kỳ thuê bao qua các năm "
        "mà không bị trùng lặp dữ liệu gói cước (đảm bảo 3NF).",
        bold_prefix="Bổ sung bảng `HomeSubscription`: "
    )
    add_callout(
        "Kết luận: Hệ thống 9 bảng là kiến trúc hoàn chỉnh, kế thừa và nâng cấp một cách nhất quán từ đề cương 7 bảng ban đầu, "
        "đảm bảo toàn vẹn chuẩn 3NF tuyệt đối trên toàn bộ cơ sở dữ liệu smart_home_info.",
        title="KẾT LUẬN VỀ TÍNH NHẤT QUÁN KIẾN TRÚC"
    )

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 2: ĐẶC TẢ CHI TIẾT 10 NGHIỆP VỤ QUẢN TRỊ VÀ TRUY VẤN NÂNG CAO (GIAI ĐOẠN 2)
    # =========================================================================
    add_title("CHƯƠNG 2: ĐẶC TẢ CHI TIẾT 10 NGHIỆP VỤ QUẢN TRỊ VÀ TRUY VẤN NÂNG CAO (GIAI ĐOẠN 2)", level=1)
    add_p(
        "Chương này là trọng tâm đánh giá của bài tập môn Cơ sở Dữ liệu Nâng cao theo yêu cầu của Giảng viên hướng dẫn: "
        "'10 nghiệp vụ phải ghi rõ, cách quản trị, cách viết truy vấn'. Dưới đây là đặc tả chi tiết và hoàn chỉnh cho toàn bộ 10 nghiệp vụ."
    )

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 1
    # -------------------------------------------------------------------------
    add_title("2.1. Nghiệp vụ 1: Đăng ký tài khoản & Quản lý hồ sơ người dùng (User Management)", level=2)
    add_p(
        "Người dùng tạo tài khoản trên hệ thống Smart Home. Mỗi tài khoản đại diện cho một chủ thể sở hữu hoặc thành viên sử dụng hệ thống. "
        "Hệ thống kiểm soát tính duy nhất của email trên toàn hệ thống để làm định danh đăng nhập. Mật khẩu bắt buộc phải được băm an toàn (SHA-256) "
        "trước khi lưu trữ. Hồ sơ người dùng có thể cập nhật số điện thoại, họ tên và tự động ghi nhận thời gian chỉnh sửa (updated_at).",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv1_gov = [
        ["Tạo tài khoản mới", "User", "email UNIQUE chặn trùng lặp; NOT NULL trên full_name và password_hash"],
        ["Cập nhật thông tin", "User", "ON UPDATE CURRENT_TIMESTAMP trên updated_at tự động đồng bộ thời gian"],
        ["Khóa / Xóa tài khoản", "User -> Cascade", "ON DELETE CASCADE tự động xóa liên đới các quyền trong HomeMember và giải phóng dữ liệu"],
        ["Tra cứu & Đăng nhập", "User", "Truy vấn tìm kiếm tối ưu qua B-Tree Index trên cột email"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv1_gov, [1.8, 1.5, 3.7])
    
    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv1_sql = """-- [NV1-Q1] Đăng ký tài khoản người dùng mới với mật khẩu mã hóa SHA-256
INSERT INTO User (full_name, email, phone, password_hash)
VALUES ('Trần Duy Khải', 'khai.tran@smarthome.vn', '0901234567', SHA2('MatKhauBiMat@2026', 256));

-- [NV1-Q2] Tra cứu thông tin hồ sơ người dùng theo email đăng nhập
SELECT user_id, full_name, email, phone, created_at, updated_at
FROM User
WHERE email = 'khai.tran@smarthome.vn';

-- [NV1-Q3] Thống kê tổng hợp số lượng nhà và thiết bị của từng người dùng (LEFT JOIN & GROUP BY)
SELECT
    u.user_id,
    u.full_name,
    u.email,
    COUNT(DISTINCT h.home_id)   AS tong_so_nha,
    COUNT(DISTINCT d.device_id) AS tong_thiet_bi
FROM User u
LEFT JOIN Home h    ON h.user_id = u.user_id
LEFT JOIN Device d  ON d.home_id = h.home_id
GROUP BY u.user_id, u.full_name, u.email
ORDER BY tong_thiet_bi DESC;

-- [NV1-Q4] Phát hiện tài khoản ảo: Tìm kiếm người dùng đã đăng ký nhưng chưa tạo bất động sản nào
SELECT u.user_id, u.full_name, u.email, u.created_at
FROM User u
LEFT JOIN Home h ON h.user_id = u.user_id
WHERE h.home_id IS NULL;"""
    add_code_block(nv1_sql, "Quản trị người dùng & thống kê danh mục tài sản")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 2
    # -------------------------------------------------------------------------
    add_title("2.2. Nghiệp vụ 2: Thiết lập cấu trúc nhà và phân bổ phòng chức năng (Home & Room Hierarchy)", level=2)
    add_p(
        "Chủ sở hữu đăng ký bất động sản (nhà phố, biệt thự, căn hộ chung cư) vào hệ thống. Mỗi ngôi nhà có tên định danh và địa chỉ thực tế. "
        "Để quản lý thiết bị trực quan, ngôi nhà được chia thành các phòng chức năng (phòng khách, phòng ngủ master, phòng bếp, sân vườn...) "
        "tương ứng với các tầng (floor) cụ thể. Phòng là thực thể vị trí không gian để gắn kết các thiết bị IoT.",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv2_gov = [
        ["Thêm nhà mới", "Home", "Khóa ngoại user_id tham chiếu User(user_id) đảm bảo chủ nhà phải tồn tại hợp lệ"],
        ["Thêm phòng vào nhà", "Room", "Khóa ngoại home_id tham chiếu Home(home_id); CHECK (floor > 0) ngăn số tầng âm/0"],
        ["Xóa nhà", "Home -> Cascade", "ON DELETE CASCADE tự động dọn dẹp các phòng thuộc nhà và hợp đồng thuê bao liên quan"],
        ["Xóa phòng chức năng", "Room -> Device", "ON DELETE SET NULL trên Device.room_id: thiết bị không bị xóa mất mà chuyển về trạng thái chưa gán phòng"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv2_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv2_sql = """-- [NV2-Q1] Khởi tạo bất động sản mới cho chủ sở hữu user_id = 1
INSERT INTO Home (user_id, home_name, address)
VALUES (1, 'Biệt thự Furama Resort Đà Nẵng', '105 Võ Nguyên Giáp, Khuê Mỹ, Ngũ Hành Sơn, Đà Nẵng');

-- [NV2-Q2] Phân bổ cấu trúc phòng chức năng theo các tầng cho ngôi nhà (Batch Insert)
INSERT INTO Room (home_id, room_name, floor) VALUES
(1, 'Sảnh đón khách',    1),
(1, 'Phòng khách lớn',   1),
(1, 'Phòng bếp & Bar',   1),
(1, 'Phòng ngủ Master',  2),
(1, 'Phòng làm việc',    2),
(1, 'Sân thượng & Spa',  3);

-- [NV2-Q3] Tổng hợp danh sách nhà và số lượng phòng chức năng của từng chủ hộ
SELECT
    h.home_id,
    u.full_name        AS chu_so_huu,
    h.home_name,
    h.address,
    COUNT(r.room_id)   AS tong_so_phong,
    h.created_at
FROM Home h
JOIN User u ON u.user_id = h.user_id
LEFT JOIN Room r ON r.home_id = h.home_id
GROUP BY h.home_id, u.full_name, h.home_name, h.address, h.created_at
ORDER BY tong_so_phong DESC;

-- [NV2-Q4] Truy vấn sơ đồ phân bổ phòng theo từng tầng của một căn nhà cụ thể
SELECT room_id, room_name, floor, created_at
FROM Room
WHERE home_id = 1
ORDER BY floor ASC, room_name ASC;"""
    add_code_block(nv2_sql, "Thiết lập phân cấp Nhà - Tầng - Phòng chức năng")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 3
    # -------------------------------------------------------------------------
    add_title("2.3. Nghiệp vụ 3: Phân quyền chia sẻ quyền quản trị và thành viên nhà (Home Member RBAC)", level=2)
    add_p(
        "Chủ nhà có nhu cầu chia sẻ quyền điều khiển thiết bị cho các thành viên trong gia đình hoặc khách thuê ngắn hạn. "
        "Mô hình Role-Based Access Control (RBAC) được áp dụng với 4 cấp độ phân quyền chặt chẽ: "
        "OWNER (chủ sở hữu tối cao, toàn quyền cấu hình và thanh toán), ADMIN (quản trị viên, được thêm/xóa thiết bị), "
        "MEMBER (thành viên thông thường, chỉ được bật/tắt thiết bị), và GUEST (khách, chỉ được xem trạng thái). "
        "Nghiệp vụ giải quyết mối quan hệ nhiều - nhiều (N:N) giữa thực thể User và Home.",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv3_gov = [
        ["Cấp quyền thành viên", "HomeMember", "Khóa chính phức hợp PRIMARY KEY (home_id, user_id) ngăn ngừa việc cấp quyền trùng lặp"],
        ["Thay đổi vai trò (Role)", "HomeMember", "ENUM('OWNER','ADMIN','MEMBER','GUEST') giới hạn chặt chẽ phạm vi giá trị hợp lệ"],
        ["Thu hồi quyền truy cập", "HomeMember", "DELETE theo cặp khóa (home_id, user_id); lập tức tước bỏ quyền truy cập vào API điều khiển"],
        ["Giao dịch chuyển quyền", "HomeMember + Home", "Sử dụng TRANSACTION ACID để đảm bảo một căn nhà luôn có đúng 1 chủ sở hữu duy nhất"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv3_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv3_sql = """-- [NV3-Q1] Cấp quyền thành viên cho người dùng vào căn nhà
INSERT INTO HomeMember (home_id, user_id, role) VALUES
(1, 2, 'ADMIN'),
(1, 3, 'MEMBER'),
(1, 4, 'GUEST')
ON DUPLICATE KEY UPDATE role = VALUES(role);

-- [NV3-Q2] Liệt kê toàn bộ thành viên và vai trò phân quyền của một căn nhà cụ thể
SELECT
    hm.home_id,
    h.home_name,
    u.user_id,
    u.full_name     AS ten_thanh_vien,
    u.email,
    u.phone,
    hm.role         AS vai_tro_truy_cap,
    hm.joined_at    AS ngay_gia_nhap
FROM HomeMember hm
JOIN User u ON u.user_id = hm.user_id
JOIN Home h ON h.home_id = hm.home_id
WHERE hm.home_id = 1
ORDER BY FIELD(hm.role, 'OWNER', 'ADMIN', 'MEMBER', 'GUEST');

-- [NV3-Q3] Điều chỉnh nâng cấp hoặc hạ cấp vai trò thành viên
UPDATE HomeMember
SET role = 'ADMIN'
WHERE home_id = 1 AND user_id = 3;

-- [NV3-Q4] Thu hồi quyền truy cập và xóa thành viên khỏi ngôi nhà
DELETE FROM HomeMember
WHERE home_id = 1 AND user_id = 4;"""
    add_code_block(nv3_sql, "Quản trị phân quyền thành viên theo mô hình RBAC")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 4
    # -------------------------------------------------------------------------
    add_title("2.4. Nghiệp vụ 4: Lắp đặt, kích hoạt và quản lý vòng đời thiết bị IoT (Device Provisioning)", level=2)
    add_p(
        "Kỹ thuật viên hoặc người dùng tiến hành lắp đặt thiết bị vật lý vào phòng. Mỗi thiết bị phải thuộc một chủng loại danh mục định danh "
        "đã được kiểm định (DeviceType) và sở hữu mã Serial Number cũng như địa chỉ MAC duy nhất toàn cầu. Vòng đời của thiết bị trải qua các "
        "trạng thái: OFFLINE (mới lắp đặt hoặc mất kết nối), ONLINE (hoạt động bình thường), MAINTENANCE (đang bảo dưỡng), FAULTY (bị hỏng cần thay thế). "
        "Hệ thống theo dõi phiên bản Firmware và thời điểm hoạt động gần nhất (last_active).",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv4_gov = [
        ["Đăng ký thiết bị mới", "Device", "Ràng buộc UNIQUE trên mac_address và serial_number chặn đứng thiết bị trùng lặp hoặc giả mạo"],
        ["Kiểm định loại thiết bị", "Device -> DeviceType", "Khóa ngoại type_id bảo đảm thông số công suất định mức và giao thức kết nối được kế thừa chuẩn"],
        ["Cập nhật trạng thái", "Device", "ENUM trạng thái ('ONLINE','OFFLINE','MAINTENANCE','FAULTY') kiểm soát chặt quy trình vận hành"],
        ["Cập nhật Heartbeat", "Device", "Cập nhật last_active = NOW() mỗi khi thiết bị phát tín hiệu sống về máy chủ"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv4_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv4_sql = """-- [NV4-Q1] Khai báo lắp đặt thiết bị vật lý mới vào phòng khách
INSERT INTO Device (room_id, home_id, type_id, device_name, serial_number, mac_address, status, firmware_version)
VALUES (2, 1, 1, 'Điều hòa Daikin Inverter PK', 'DK-2026-9901', 'A4:C1:38:9B:21:01', 'ONLINE', 'v2.1.0');

-- [NV4-Q2] Cập nhật tín hiệu sống (Heartbeat) và phiên bản Firmware thiết bị
UPDATE Device
SET last_active = NOW(),
    firmware_version = 'v2.2.0',
    status = 'ONLINE'
WHERE mac_address = 'A4:C1:38:9B:21:01';

-- [NV4-Q3] Thống kê số lượng thiết bị theo từng chủng loại phần cứng và nhà sản xuất
SELECT
    dt.type_name,
    dt.manufacturer,
    dt.protocol,
    dt.max_power_watt,
    COUNT(d.device_id) AS so_luong_dang_dung
FROM DeviceType dt
LEFT JOIN Device d ON d.type_id = dt.type_id
GROUP BY dt.type_id, dt.type_name, dt.manufacturer, dt.protocol, dt.max_power_watt
ORDER BY so_luong_dang_dung DESC;

-- [NV4-Q4] Chuyển trạng thái thiết bị sang diện bảo trì khi kỹ thuật viên tiếp nhận
UPDATE Device
SET status = 'MAINTENANCE'
WHERE device_id = 1;"""
    add_code_block(nv4_sql, "Quy trình kích hoạt và quản lý trạng thái thiết bị IoT")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 5
    # -------------------------------------------------------------------------
    add_title("2.5. Nghiệp vụ 5: Tra cứu, định vị và kiểm soát thiết bị theo tầng/phòng (Device Location Query)", level=2)
    add_p(
        "Người dùng trên ứng dụng di động cần xem sơ đồ thiết bị trực quan theo cấu trúc không gian ngôi nhà: tầng 1 gồm những phòng nào, "
        "mỗi phòng đang có bao nhiêu thiết bị, trạng thái hoạt động (bật/tắt, online/offline) và vị trí của từng cảm biến. "
        "Hệ thống cũng cần phát hiện những thiết bị chưa được gán vào phòng nào (thiết bị mới quét thấy trên mạng LAN) để nhắc nhở người dùng.",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv5_gov = [
        ["Định vị thiết bị", "Device + Room", "Khóa ngoại room_id liên kết thiết bị vào vị trí phòng cụ thể"],
        ["Tối ưu hóa tìm kiếm", "Device Index", "Thiết lập Compound Index (home_id, room_id, status) tăng tốc độ lọc thiết bị theo không gian"],
        ["Xử lý phòng bị xóa", "Device.room_id", "ON DELETE SET NULL: Bảo vệ thiết bị không bị mất dữ liệu, tự động rơi vào nhóm 'Chưa phân phòng'"],
        ["Toàn vẹn cây phân cấp", "Room -> Home", "Đảm bảo tính nhất quán: Thiết bị thuộc phòng R của nhà H thì Device.home_id phải trùng khớp"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv5_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv5_sql = """-- [NV5-Q1] Liệt kê toàn bộ thiết bị theo từng tầng và phòng của ngôi nhà home_id = 1
SELECT
    COALESCE(r.floor, 0)     AS tang,
    COALESCE(r.room_name, 'Chưa gán phòng') AS ten_phong,
    d.device_name,
    dt.type_name,
    d.status,
    d.mac_address,
    dt.max_power_watt
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
LEFT JOIN Room r   ON r.room_id = d.room_id
WHERE d.home_id = 1
ORDER BY r.floor ASC, r.room_name ASC, d.device_name ASC;

-- [NV5-Q2] Thống kê tổng số lượng thiết bị và thiết bị đang ONLINE theo từng phòng
SELECT
    r.room_name,
    r.floor,
    COUNT(d.device_id)                          AS tong_thiet_bi,
    SUM(CASE WHEN d.status = 'ONLINE' THEN 1 ELSE 0 END)  AS thiet_bi_online,
    SUM(CASE WHEN d.status = 'OFFLINE' THEN 1 ELSE 0 END) AS thiet_bi_offline
FROM Room r
LEFT JOIN Device d ON d.room_id = r.room_id
WHERE r.home_id = 1
GROUP BY r.room_id, r.room_name, r.floor
ORDER BY r.floor ASC;

-- [NV5-Q3] Tìm các thiết bị chưa được phân bổ vào phòng nào (room_id IS NULL)
SELECT d.device_id, d.device_name, d.mac_address, d.status, d.installed_at
FROM Device d
WHERE d.home_id = 1 AND d.room_id IS NULL;

-- [NV5-Q4] Gán thiết bị vào một phòng cụ thể sau khi đã cấu hình vị trí
UPDATE Device
SET room_id = 2
WHERE device_id = 1 AND home_id = 1;"""
    add_code_block(nv5_sql, "Truy vấn không gian phân cấp Nhà - Tầng - Phòng - Thiết bị")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 6
    # -------------------------------------------------------------------------
    add_title("2.6. Nghiệp vụ 6: Đăng ký, kích hoạt và tự động gia hạn gói dịch vụ thuê bao (Subscription Lifecycle)", level=2)
    add_p(
        "Để sử dụng các tính năng cao cấp (lưu trữ video an ninh đám mây, thông báo đẩy AI, sao lưu dữ liệu), chủ hộ phải đăng ký gói dịch vụ. "
        "Mỗi gói có thời hạn (30 ngày, 90 ngày, 365 ngày), giá cước và giới hạn số lượng thiết bị/nhà kết nối. Hợp đồng thuê bao (HomeSubscription) "
        "quản lý ngày bắt đầu (start_date), ngày kết thúc (end_date), cờ tự động gia hạn (auto_renew) và trạng thái (ACTIVE, EXPIRED, CANCELLED). "
        "Hệ thống định kỳ quét các gói sắp hết hạn để thông báo gia hạn hoặc tự động tái tục.",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv6_gov = [
        ["Đăng ký gói thuê bao", "HomeSubscription", "CHECK (end_date >= start_date) đảm bảo tính hợp lệ logic của khoảng thời gian thuê bao"],
        ["Kiểm soát hạn mức gói", "Device vs Subscription", "Kiểm tra số thiết bị hiện tại COUNT(device_id) <= max_devices của gói cước trước khi thêm thiết bị"],
        ["Tự động gia hạn", "HomeSubscription", "Nếu auto_renew = 1 và đến ngày hết hạn, hệ thống tự động sinh kỳ thuê bao mới và tạo hóa đơn Invoice tương ứng"],
        ["Hủy gói cước", "HomeSubscription", "Chuyển trạng thái status = 'CANCELLED', duy trì dịch vụ đến hết chu kỳ end_date hiện tại"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv6_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv6_sql = """-- [NV6-Q1] Đăng ký gói thuê bao Standard (30 ngày) cho ngôi nhà home_id = 1
INSERT INTO HomeSubscription (home_id, plan_id, start_date, end_date, status, auto_renew)
VALUES (1, 2, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'ACTIVE', 1);

-- [NV6-Q2] Quét danh sách các hợp đồng thuê bao sắp hết hạn trong vòng 7 ngày tới để gửi thông báo
SELECT
    hs.subscription_id,
    h.home_name,
    u.full_name     AS chu_nha,
    u.email,
    sp.plan_name,
    hs.end_date,
    DATEDIFF(hs.end_date, CURDATE()) AS so_ngay_con_lai,
    hs.auto_renew
FROM HomeSubscription hs
JOIN Home h             ON h.home_id = hs.home_id
JOIN User u             ON u.user_id = h.user_id
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
WHERE hs.status = 'ACTIVE'
  AND hs.end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
ORDER BY hs.end_date ASC;

-- [NV6-Q3] Tự động gia hạn thêm 30 ngày cho hợp đồng có auto_renew = 1 khi hết hạn
UPDATE HomeSubscription
SET start_date = end_date,
    end_date   = DATE_ADD(end_date, INTERVAL 30 DAY),
    status     = 'ACTIVE'
WHERE subscription_id = 1 AND auto_renew = 1 AND end_date <= CURDATE();

-- [NV6-Q4] Cập nhật trạng thái EXPIRED cho các gói quá hạn mà không bật tự động gia hạn
UPDATE HomeSubscription
SET status = 'EXPIRED'
WHERE end_date < CURDATE() AND status = 'ACTIVE' AND auto_renew = 0;

-- [NV6-Q5] Kiểm tra hạn mức thiết bị của ngôi nhà so với gói thuê bao đang kích hoạt
SELECT
    h.home_id,
    h.home_name,
    sp.plan_name,
    sp.max_devices,
    COUNT(d.device_id) AS thiet_bi_hien_tai,
    (sp.max_devices - COUNT(d.device_id)) AS slot_con_lai
FROM Home h
JOIN HomeSubscription hs ON hs.home_id = h.home_id AND hs.status = 'ACTIVE'
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
LEFT JOIN Device d       ON d.home_id = h.home_id
WHERE h.home_id = 1
GROUP BY h.home_id, h.home_name, sp.plan_name, sp.max_devices;"""
    add_code_block(nv6_sql, "Vòng đời quản lý thuê bao và kiểm soát hạn mức dịch vụ")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 7
    # -------------------------------------------------------------------------
    add_title("2.7. Nghiệp vụ 7: Quản lý thanh toán hóa đơn & truy vết đối soát tài chính (Billing Reconciliation)", level=2)
    add_p(
        "Mỗi khi hợp đồng thuê bao được tạo hoặc gia hạn, hệ thống tự động phát hành một hóa đơn thanh toán (Invoice). "
        "Hóa đơn lưu giữ số tiền (amount), phương thức thanh toán (CREDIT_CARD, BANK_TRANSFER, E_WALLET), trạng thái (PENDING, PAID, FAILED, REFUNDED) "
        "và mã giao dịch tham chiếu từ cổng thanh toán đối tác (transaction_code). Việc xử lý thanh toán đòi hỏi tính toàn vẹn giao dịch tuyệt đối (ACID) "
        "để tránh tình trạng tiền đã trừ nhưng dịch vụ chưa được kích hoạt.",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv7_gov = [
        ["Phát hành hóa đơn", "Invoice", "CHECK (amount > 0); Khóa ngoại subscription_id và user_id đảm bảo thông tin đối soát hợp lệ"],
        ["Xử lý thanh toán an toàn", "Invoice + HomeSubscription", "Bắt buộc sử dụng TRANSACTION (START TRANSACTION ... COMMIT) khi cập nhật trạng thái PAID"],
        ["Chống gian lận thanh toán", "Invoice", "Ràng buộc UNIQUE trên transaction_code ngăn chặn việc ghi nhận lặp một mã giao dịch từ cổng thanh toán"],
        ["Truy vết lịch sử giao dịch", "Invoice Index", "Index trên user_id và created_at phục vụ xuất sao kê giao dịch cho khách hàng trong 10ms"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv7_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv7_sql = """-- [NV7-Q1] Khởi tạo hóa đơn thanh toán mới ở trạng thái chờ (PENDING)
INSERT INTO Invoice (subscription_id, user_id, amount, payment_method, payment_status)
VALUES (1, 1, 150000.00, 'BANK_TRANSFER', 'PENDING');

-- [NV7-Q2] Giao dịch xử lý hoàn tất thanh toán (ACID Transaction)
START TRANSACTION;

-- Cập nhật hóa đơn sang PAID kèm mã đối soát ngân hàng
UPDATE Invoice
SET payment_status = 'PAID',
    transaction_code = 'VNPAY-2026-88776655',
    paid_at = NOW()
WHERE invoice_id = 1 AND payment_status = 'PENDING';

-- Kích hoạt trạng thái hợp đồng thuê bao tương ứng
UPDATE HomeSubscription
SET status = 'ACTIVE'
WHERE subscription_id = (SELECT subscription_id FROM Invoice WHERE invoice_id = 1);

COMMIT;

-- [NV7-Q3] Tra cứu lịch sử thanh toán hóa đơn của một người dùng
SELECT
    i.invoice_id,
    sp.plan_name,
    h.home_name,
    i.amount,
    i.payment_method,
    i.payment_status,
    i.transaction_code,
    i.paid_at
FROM Invoice i
JOIN HomeSubscription hs ON hs.subscription_id = i.subscription_id
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
JOIN Home h              ON h.home_id = hs.home_id
WHERE i.user_id = 1
ORDER BY i.created_at DESC;

-- [NV7-Q4] Báo cáo các hóa đơn nợ đọng quá hạn chưa thanh toán (PENDING > 3 ngày)
SELECT
    i.invoice_id,
    u.full_name,
    u.email,
    u.phone,
    i.amount,
    i.created_at,
    DATEDIFF(NOW(), i.created_at) AS so_ngay_no
FROM Invoice i
JOIN User u ON u.user_id = i.user_id
WHERE i.payment_status = 'PENDING'
  AND i.created_at < DATE_SUB(NOW(), INTERVAL 3 DAY)
ORDER BY i.created_at ASC;"""
    add_code_block(nv7_sql, "Xử lý giao dịch thanh toán ACID và đối soát công nợ")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 8
    # -------------------------------------------------------------------------
    add_title("2.8. Nghiệp vụ 8: Giám sát công suất tiêu thụ điện & cảnh báo quá tải thiết bị (Power Consumption)", level=2)
    add_p(
        "Một trong những tính năng quan trọng nhất của hệ thống Smart Home là giám sát phụ tải điện năng nhằm tối ưu hóa chi phí và "
        "đảm bảo an toàn phòng cháy chữa cháy. Mỗi loại thiết bị đều có thông số công suất tiêu thụ tối đa (max_power_watt) trong danh mục DeviceType. "
        "Hệ thống cần tổng hợp công suất đỉnh theo từng phòng, từng ngôi nhà và tự động phát hiện các phòng có tổng công suất vượt ngưỡng an toàn (ví dụ > 3000W) "
        "để gửi cảnh báo tức thì tới gia chủ và ngắt bớt phụ tải không ưu tiên.",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv8_gov = [
        ["Định mức công suất", "DeviceType", "max_power_watt DECIMAL(6,1) định nghĩa công suất thiết kế chuẩn của phần cứng"],
        ["Giám sát thời gian thực", "Device + DeviceType", "Truy vấn kết hợp giữa trạng thái ONLINE của thiết bị và định mức công suất danh định"],
        ["Phát hiện quá tải", "Room & Home Aggregation", "HAVING SUM(max_power_watt) > Threshold: lọc nhanh các phòng vượt định mức chịu tải của aptomat"],
        ["Xếp hạng thiết bị", "Device Analytics", "Sử dụng hàm phân tích xếp hạng (DENSE_RANK) để xác định các thiết bị ngốn điện nhiều nhất"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv8_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv8_sql = """-- [NV8-Q1] Tính toán tổng công suất thiết kế tối đa theo từng phòng của ngôi nhà
SELECT
    r.room_id,
    r.room_name,
    r.floor,
    COUNT(d.device_id)                 AS tong_thiet_bi,
    COALESCE(SUM(dt.max_power_watt), 0) AS tong_cong_suat_watt
FROM Room r
LEFT JOIN Device d     ON d.room_id = r.room_id
LEFT JOIN DeviceType dt ON dt.type_id = d.type_id
WHERE r.home_id = 1
GROUP BY r.room_id, r.room_name, r.floor
ORDER BY tong_cong_suat_watt DESC;

-- [NV8-Q2] Top 5 thiết bị có công suất tiêu thụ điện lớn nhất trong toàn bộ hệ thống
SELECT
    d.device_id,
    d.device_name,
    h.home_name,
    r.room_name,
    dt.type_name,
    dt.max_power_watt
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
JOIN Home h        ON h.home_id = d.home_id
LEFT JOIN Room r   ON r.room_id = d.room_id
ORDER BY dt.max_power_watt DESC
LIMIT 5;

-- [NV8-Q3] Cảnh báo an toàn điện: Phát hiện các phòng có tổng công suất thiết bị ONLINE vượt ngưỡng 3000 Watts
SELECT
    h.home_name,
    r.room_name,
    r.floor,
    COUNT(d.device_id)       AS so_thiet_bi_online,
    SUM(dt.max_power_watt)   AS tong_cong_suat_online_watt
FROM Room r
JOIN Home h        ON h.home_id = r.home_id
JOIN Device d      ON d.room_id = r.room_id
JOIN DeviceType dt ON dt.type_id = d.type_id
WHERE d.status = 'ONLINE'
GROUP BY h.home_name, r.room_id, r.room_name, r.floor
HAVING SUM(dt.max_power_watt) > 3000
ORDER BY tong_cong_suat_online_watt DESC;

-- [NV8-Q4] Thống kê tổng phụ tải định mức theo từng nhóm phân loại thiết bị (Category)
SELECT
    dt.category,
    COUNT(d.device_id)       AS so_luong_thiet_bi,
    SUM(dt.max_power_watt)   AS tong_cong_suat_watt,
    AVG(dt.max_power_watt)   AS cong_suat_trung_binh_watt
FROM DeviceType dt
JOIN Device d ON d.type_id = dt.type_id
GROUP BY dt.category
ORDER BY tong_cong_suat_watt DESC;"""
    add_code_block(nv8_sql, "Phân tích phụ tải điện năng và cảnh báo an toàn phòng cháy")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 9
    # -------------------------------------------------------------------------
    add_title("2.9. Nghiệp vụ 9: Phát hiện thiết bị mất kết nối (Offline) & quản lý lịch bảo trì (Device Health Check)", level=2)
    add_p(
        "Các thiết bị IoT hoạt động phụ thuộc vào kết nối WiFi/Zigbee và nguồn điện. Nếu thiết bị không phát tín hiệu Heartbeat "
        "trong một khoảng thời gian quy định (ví dụ quá 24 giờ), hệ thống sẽ đánh dấu là OFFLINE và gửi thông báo kiểm tra. "
        "Đối với các thiết bị báo lỗi phần cứng hoặc hỏng hóc, trạng thái được chuyển thành FAULTY hoặc MAINTENANCE để điều phối "
        "kỹ thuật viên xử lý bảo hành, thay thế linh kiện theo đúng quy trình biểu mẫu kỹ thuật.",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv9_gov = [
        ["Quét mất kết nối", "Device Index", "Index trên cột last_active và status cho phép batch job quét hàng triệu thiết bị trong vài chục mili giây"],
        ["Tự động chuyển trạng thái", "Device Batch Update", "UPDATE Device SET status = 'OFFLINE' WHERE last_active < NOW() - INTERVAL 24 HOUR"],
        ["Gắn vết bảo trì", "Device", "Chuyển trạng thái sang MAINTENANCE khi kỹ thuật viên lập biên bản kiểm tra bảo dưỡng"],
        ["Theo dõi SLA vận hành", "System Availability", "Tính toán chỉ số sẵn sàng thiết bị Availability % = (Online / Total) * 100%"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv9_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv9_sql = """-- [NV9-Q1] Quét các thiết bị mất kết nối quá 24 giờ kể từ lần hoạt động gần nhất
SELECT
    d.device_id,
    d.device_name,
    h.home_name,
    COALESCE(r.room_name, 'Chưa rõ') AS phong,
    d.mac_address,
    d.last_active,
    TIMESTAMPDIFF(HOUR, d.last_active, NOW()) AS so_gio_mat_ket_noi
FROM Device d
JOIN Home h      ON h.home_id = d.home_id
LEFT JOIN Room r ON r.room_id = d.room_id
WHERE d.status = 'ONLINE'
  AND (d.last_active < DATE_SUB(NOW(), INTERVAL 24 HOUR) OR d.last_active IS NULL)
ORDER BY d.last_active ASC;

-- [NV9-Q2] Tự động cập nhật trạng thái OFFLINE cho các thiết bị không phản hồi Heartbeat
UPDATE Device
SET status = 'OFFLINE'
WHERE status = 'ONLINE'
  AND d.last_active < DATE_SUB(NOW(), INTERVAL 24 HOUR);

-- [NV9-Q3] Báo cáo danh sách thiết bị gặp sự cố hoặc đang trong diện bảo trì kèm thông tin liên hệ chủ nhà
SELECT
    d.device_id,
    d.device_name,
    d.serial_number,
    d.status,
    h.home_name,
    u.full_name     AS chu_so_huu,
    u.phone         AS sdt_lien_he,
    d.last_active
FROM Device d
JOIN Home h ON h.home_id = d.home_id
JOIN User u ON u.user_id = h.user_id
WHERE d.status IN ('FAULTY', 'MAINTENANCE')
ORDER BY d.status DESC, d.last_active ASC;

-- [NV9-Q4] Thống kê tỷ lệ sức khỏe thiết bị (Online Rate %) trên toàn bộ hệ thống
SELECT
    COUNT(device_id)                                            AS tong_thiet_bi,
    SUM(CASE WHEN status = 'ONLINE' THEN 1 ELSE 0 END)          AS so_online,
    SUM(CASE WHEN status = 'OFFLINE' THEN 1 ELSE 0 END)         AS so_offline,
    SUM(CASE WHEN status = 'MAINTENANCE' THEN 1 ELSE 0 END)     AS so_bao_tri,
    SUM(CASE WHEN status = 'FAULTY' THEN 1 ELSE 0 END)          AS so_hong_hoc,
    ROUND(SUM(CASE WHEN status = 'ONLINE' THEN 1 ELSE 0 END) * 100.0 / COUNT(device_id), 2) AS ty_le_online_phan_tram
FROM Device;"""
    add_code_block(nv9_sql, "Giám sát sức khỏe thiết bị và quản trị quy trình bảo trì")

    # -------------------------------------------------------------------------
    # NGHIỆP VỤ 10
    # -------------------------------------------------------------------------
    add_title("2.10. Nghiệp vụ 10: Thống kê doanh thu, tỷ lệ gia hạn & đối soát chỉ số SLA (Executive Analytics)", level=2)
    add_p(
        "Ban giám đốc và bộ phận tài chính cần các báo cáo kinh doanh chuyên sâu để đánh giá hiệu quả vận hành: "
        "Doanh thu lũy kế theo từng gói dịch vụ, xu hướng doanh thu hàng tháng/quý, tỷ lệ khách hàng gia hạn dịch vụ (Retention Rate) "
        "so với tỷ lệ rời bỏ (Churn Rate), và doanh thu trung bình trên mỗi khách hàng (ARPU - Average Revenue Per User). "
        "Các truy vấn này sử dụng các kỹ thuật SQL nâng cao như Window Functions (OVER, PARTITION BY), Aggregation nâng cao và gom nhóm đa chiều.",
        bold_prefix="a) Mô tả nghiệp vụ: "
    )
    add_p("Cơ chế quản trị và ràng buộc toàn vẹn:", bold_prefix="b) Cách quản trị cơ sở dữ liệu: ")
    nv10_gov = [
        ["Bảo mật dữ liệu tài chính", "Database Views & RBAC", "Tạo các View thống kê doanh thu và chỉ cấp quyền SELECT cho tài khoản kế toán/SuperAdmin"],
        ["Toàn vẹn số liệu đối soát", "Invoice PAID", "Chỉ tổng hợp doanh thu từ các hóa đơn có trạng thái payment_status = 'PAID'"],
        ["Tối ưu truy vấn phân tích", "Date Indexing", "Index trên cột created_at và paid_at của bảng Invoice đảm bảo truy vấn phạm vi ngày siêu tốc"],
        ["Tính toán KPI tự động", "Window Functions", "Sử dụng hàm cửa sổ SUM(...) OVER() để tính doanh thu lũy kế mà không cần tạo bảng tạm"]
    ]
    add_styled_table(["Thao tác quản trị", "Bảng liên quan", "Ràng buộc & Giải pháp CSDL"], nv10_gov, [1.8, 1.5, 3.7])

    add_p("c) Hệ thống câu lệnh truy vấn SQL:", bold_prefix="Truy vấn SQL: ")
    nv10_sql = """-- [NV10-Q1] Thống kê tổng doanh thu thực thu và số lượng giao dịch theo từng gói cước
SELECT
    sp.plan_id,
    sp.plan_name,
    sp.price                            AS gia_niem_yet,
    COUNT(i.invoice_id)                 AS so_luot_thanh_toan,
    COALESCE(SUM(i.amount), 0)          AS tong_doanh_thu_vnd,
    AVG(i.amount)                       AS gia_tri_trung_binh_hoa_don
FROM SubscriptionPlan sp
LEFT JOIN HomeSubscription hs ON hs.plan_id = sp.plan_id
LEFT JOIN Invoice i           ON i.subscription_id = hs.subscription_id AND i.payment_status = 'PAID'
GROUP BY sp.plan_id, sp.plan_name, sp.price
ORDER BY tong_doanh_thu_vnd DESC;

-- [NV10-Q2] Báo cáo doanh thu theo tháng kèm tính toán doanh thu lũy kế (Window Function)
SELECT
    DATE_FORMAT(paid_at, '%Y-%m')       AS thang_nam,
    COUNT(invoice_id)                   AS so_hoa_don_thanh_toan,
    SUM(amount)                         AS doanh_thu_thang_vnd,
    SUM(SUM(amount)) OVER (ORDER BY DATE_FORMAT(paid_at, '%Y-%m')) AS doanh_thu_luy_ke_vnd
FROM Invoice
WHERE payment_status = 'PAID' AND paid_at IS NOT NULL
GROUP BY DATE_FORMAT(paid_at, '%Y-%m')
ORDER BY thang_nam ASC;

-- [NV10-Q3] Đo lường chỉ số giữ chân khách hàng (Retention Rate): Thống kê tỷ lệ thuê bao bật tự động gia hạn
SELECT
    sp.plan_name,
    COUNT(hs.subscription_id)                           AS tong_hop_dong,
    SUM(CASE WHEN hs.auto_renew = 1 THEN 1 ELSE 0 END)  AS so_bat_tu_dong_gia_han,
    SUM(CASE WHEN hs.auto_renew = 0 THEN 1 ELSE 0 END)  AS so_tat_gia_han,
    ROUND(SUM(CASE WHEN hs.auto_renew = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(hs.subscription_id), 2) AS ty_le_du_kien_tai_tuc_pct
FROM HomeSubscription hs
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
GROUP BY sp.plan_id, sp.plan_name;

-- [NV10-Q4] Doanh thu trung bình trên mỗi khách hàng (ARPU - Average Revenue Per User)
SELECT
    COUNT(DISTINCT u.user_id)           AS tong_so_khach_hang,
    SUM(i.amount)                       AS tong_toan_bo_doanh_thu,
    ROUND(SUM(i.amount) / COUNT(DISTINCT u.user_id), 2) AS arpu_doanh_thu_tb_tren_user
FROM User u
JOIN Invoice i ON i.user_id = u.user_id AND i.payment_status = 'PAID';"""
    add_code_block(nv10_sql, "Phân tích tài chính doanh nghiệp và báo cáo chỉ số KPI nâng cao")

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 3: MỞ RỘNG KIẾN TRÚC DỮ LIỆU LỚN VÀ WEB DASHBOARD GIÁM SÁT (GIAI ĐOẠN 3)
    # =========================================================================
    add_title("CHƯƠNG 3: MỞ RỘNG KIẾN TRÚC DỮ LIỆU LỚN VÀ WEB DASHBOARD GIÁM SÁT (GIAI ĐOẠN 3)", level=1)

    add_title("3.1. Thách thức Big Data (3V) trong Telemetry IoT", level=2)
    add_p(
        "Bước sang Giai đoạn 3, hệ thống đối mặt với bài toán dữ liệu lớn thực sự từ mạng lưới hàng chục ngàn thiết bị IoT hoạt động 24/7:",
        bold_prefix="Đặc tính dữ liệu lớn: "
    )
    add_bullet(
        "Mỗi thiết bị gửi gói tin định kỳ 5 phút/lần. Với 10.000 thiết bị, hệ thống ghi nhận gần 3 triệu bản ghi mỗi ngày, "
        "tạo áp lực lưu trữ hàng trăm Gigabytes chỉ trong vài tháng.",
        bold_prefix="1. Volume (Dung lượng lớn): "
    )
    add_bullet(
        "Thông lượng ghi (Write throughput) cao điểm lên tới hàng ngàn bản ghi/giây khi có sự kiện thay đổi trạng thái đồng loạt.",
        bold_prefix="2. Velocity (Tốc độ phát sinh cao): "
    )
    add_bullet(
        "Dữ liệu cảm biến đo lường (nhiệt độ, độ ẩm, điện áp, công suất, cường độ tín hiệu WiFi RSSI) và nhật ký thao tác lệnh (Action, Payload JSON) "
        "có cấu trúc bán cấu trúc biến đổi linh hoạt, không cố định.",
        bold_prefix="3. Variety (Đa dạng cấu trúc): "
    )

    add_title("3.2. Thiết kế Cơ sở Dữ liệu NoSQL MongoDB và Aggregation Pipelines", level=2)
    add_p(
        "Để giải tỏa áp lực ghi cho MySQL, cơ sở dữ liệu phi quan hệ MongoDB được thiết lập song song làm tầng lưu trữ Telemetry:",
        bold_prefix="Mô hình NoSQL MongoDB: "
    )
    add_p(
        "Lưu trữ chuỗi thời gian các chỉ số viễn thám đo lường từ thiết bị: `timestamp`, `device_id`, `room_id`, `home_id`, `category`, "
        "`status`, `metrics: { temperature, humidity, power_watts, voltage, rssi_dbm }`, `is_anomaly`, `anomaly_reason`.",
        bold_prefix="• Collection 1: `device_telemetry`: "
    )
    add_p(
        "Lưu trữ lịch sử thực thi các lệnh điều khiển: `timestamp`, `log_id`, `device_id`, `home_id`, `action`, `source` (MOBILE_APP/WEB/VOICE), `status`, `latency_ms`.",
        bold_prefix="• Collection 2: `command_logs`: "
    )
    add_p("Chiến lược Compound Indexing trên MongoDB:", bold_prefix="Tối ưu hóa chỉ mục NoSQL: ")
    mongo_indexes = [
        ["db.device_telemetry.createIndex({ device_id: 1, timestamp: -1 })", "Vẽ biểu đồ chuỗi thời gian cho từng thiết bị trên Mobile App trong dưới 5ms"],
        ["db.device_telemetry.createIndex({ home_id: 1, timestamp: -1 })", "Tổng hợp phụ tải điện năng tức thời của toàn căn hộ"],
        ["db.device_telemetry.createIndex({ is_anomaly: 1, anomaly_reason: 1 })", "Quét cực nhanh các bản ghi phát hiện sự cố quá nhiệt hoặc quá tải"],
        ["db.command_logs.createIndex({ source: 1, status: 1 })", "Đối soát tỷ lệ lỗi và độ trễ phản hồi của các kênh điều khiển"]
    ]
    add_styled_table(["Cú pháp Index MongoDB", "Mục tiêu tối ưu hóa truy vấn"], mongo_indexes, [3.8, 3.2])

    add_title("3.3. Xử lý phân tích dữ liệu lớn trên Apache Hadoop & Spark Engine", level=2)
    add_p(
        "Kiến trúc dữ liệu phân tán nhiều tầng (Multi-tier Big Data Pipeline) được xây dựng hoàn chỉnh, kết nối liền mạch giữa luồng viễn thám "
        "tốc độ cao và các batch job phân tích thông minh:",
        bold_prefix="Kiến trúc xử lý phân tán: "
    )
    add_bullet("Dữ liệu telemetry sau khi lưu trữ trên MongoDB định kỳ được trích xuất và nén dưới định dạng Parquet trên hệ thống tệp phân tán HDFS.", bold_prefix="Tầng lưu trữ HDFS: ")
    add_bullet("Engine tính toán trong bộ nhớ (In-memory) PySpark đọc dữ liệu Parquet, thực thi các tác vụ MapReduce phân tán để tính toán phụ tải điện trung bình theo khung giờ và phát hiện bất thường dựa trên thuật toán Z-score.", bold_prefix="Tầng phân tích Apache Spark: ")
    add_bullet("Kết quả tổng hợp được đẩy ngược về bảng dữ liệu tinh gọn trong MySQL để phục vụ ứng dụng Web hiển thị báo cáo điều hành.", bold_prefix="Tầng phục vụ (Serving Layer): ")
    
    # Chèn ảnh giao diện Luồng Pipeline
    add_image_box("extracted_images/ui_pipeline.png", "Hình 3.1: Giao diện Trực quan hóa Luồng Kiến trúc Dữ liệu Đa tầng NoSQL & Hadoop Data Lake", width_inch=5.8)
    add_p(
        "Hình 3.1 mô tả trực quan cấu trúc luồng dữ liệu 5 tầng được tích hợp trên Dashboard: Từ tầng cảm biến IoT (IoT Edge Sensors) "
        "truyền qua giao thức MQTT/JSON, nạp vào MongoDB Hot Storage, đẩy sang Hadoop HDFS Cold Storage dạng Parquet phân vùng theo thời gian "
        "(year/month/day), xử lý qua Spark Processing Jobs và phục vụ trực tiếp cho Serving Layer.",
        italic=True
    )

    add_title("3.4. Xây dựng Trung tâm Điều hành Web Dashboard (IoT Command Center)", level=2)
    add_p(
        "Hệ thống phát triển một ứng dụng Web tương tác (IoT Command Center) hoàn chỉnh đặt tại thư mục `dashboard/` "
        "sử dụng Python Flask Framework (`app.py`), kết nối quản trị đa hệ CSDL qua `db_manager.py`, với giao diện Dark Mode "
        "hiện đại tích hợp thư viện Tailwind CSS, Chart.js và biểu tượng Lucide Icons. Trung tâm điều hành bao gồm 5 màn hình giám sát chuyên sâu:",
        bold_prefix="Kiến trúc Web Dashboard: "
    )

    # 3.4.1 Tổng quan
    add_title("3.4.1. Màn hình Tổng quan Hệ thống (Executive Overview Dashboard)", level=3)
    add_p(
        "Màn hình tổng quan cung cấp cái nhìn toàn cảnh về tình trạng vận hành của toàn bộ hệ sinh thái Smart Home:",
        bold_prefix="Chức năng giám sát: "
    )
    add_bullet("5 thẻ KPI đầu bảng: Tổng số căn hộ (16 căn hộ), Tổng thiết bị (30 thiết bị), Tổng bản ghi dữ liệu (13,500+ Telemetry Logs), Trạng thái luồng Hadoop Streaming (ON/OFF), và Chỉ số kết nối CSDL Live Engine.", bold_prefix="Thẻ KPI điều hành: ")
    add_bullet("Đồ thị đường biến thiên phụ tải điện năng 24 giờ phản ánh sát thực tế nhu cầu sử dụng năng lượng.", bold_prefix="Biểu đồ phụ tải 24h: ")
    add_bullet("Biểu đồ cơ cấu phụ tải theo phòng và Bảng xếp hạng tiêu thụ điện của các căn hộ giúp nhận diện ngay căn hộ tiêu tốn nhiều năng lượng nhất.", bold_prefix="Bảng xếp hạng & Cơ cấu: ")
    add_image_box("extracted_images/ui_overview.png", "Hình 3.2: Giao diện Tổng quan Hệ thống (Executive Overview Dashboard - IoT Command Center)", width_inch=5.8)

    # 3.4.2 Phân tích Năng lượng
    add_title("3.4.2. Màn hình Phân tích Năng lượng & Phụ tải Điện năng (Energy Analytics)", level=3)
    add_p(
        "Màn hình phân tích chuyên sâu dữ liệu điện năng tiêu thụ (kWh) được tính toán tự động qua Spark Jobs:",
        bold_prefix="Phân tích năng lượng EVN: "
    )
    add_bullet("Đồ thị cột thể hiện sản lượng điện tiêu thụ từng ngày trong tuần, làm rõ sự biến thiên giữa ngày thường và ngày cuối tuần.", bold_prefix="Sản lượng theo ngày: ")
    add_bullet("Phân tích cơ cấu giờ cao điểm EVN: Chỉ ra khung giờ cao điểm (11h-13h trưa và 18h-22h tối) chiếm tới 54.2% tổng phụ tải, hỗ trợ kích hoạt chế độ Eco-Smart tiết kiệm 15-25% chi phí.", bold_prefix="Phụ tải Giờ cao điểm: ")
    add_bullet("Bảng chi tiết điện năng tiêu thụ và dự toán cước phí lũy kế của toàn bộ 16 căn hộ bất động sản.", bold_prefix="Chi tiết cước phí 16 căn hộ: ")
    add_image_box("extracted_images/ui_energy.png", "Hình 3.3: Giao diện Phân tích Điện năng - Phụ tải Giờ Cao điểm EVN & Cơ cấu chủng loại", width_inch=5.8)

    # 3.4.3 Giám sát An toàn & Bất thường
    add_title("3.4.3. Màn hình Giám sát An toàn & Cảnh báo Sự cố Bất thường (Anomaly Center)", level=3)
    add_p(
        "Màn hình giám sát sức khỏe thiết bị và phát hiện bất thường thời gian thực ứng dụng thuật toán Z-score và đối soát quy chuẩn `DeviceType`:",
        bold_prefix="Hệ thống cảnh báo đa cấp: "
    )
    add_bullet("Phát hiện nhiệt độ tăng vọt tại phòng bếp đạt 48°C - 52°C, lập tức kích hoạt còi hú báo cháy và thông báo khẩn cấp đến ứng dụng chủ hộ.", bold_prefix="Cảnh báo Quá nhiệt (CRITICAL): ")
    add_bullet("Phát hiện Điều hòa Panasonic 2.0HP tiêu thụ tới 2450W (vượt > 135% định mức thiết kế 1800W), cảnh báo nguy cơ chập cháy aptomat.", bold_prefix="Cảnh báo Quá tải công suất (HIGH): ")
    add_bullet("Ghi nhận cảm biến và công tắc mất kết nối WiFi kéo dài, tự động đưa vào danh sách kiểm tra bảo trì.", bold_prefix="Thiết bị mất kết nối (MEDIUM): ")
    add_image_box("extracted_images/ui_anomaly.png", "Hình 3.4: Giao diện Giám sát An toàn & Cảnh báo Sự cố Bất thường Thời gian thực", width_inch=5.8)

    # 3.4.4 Kinh doanh & Thuê bao
    add_title("3.4.4. Màn hình Quản trị Kinh doanh & Hợp đồng Thuê bao (Subscription Insights)", level=3)
    add_p(
        "Màn hình theo dõi dòng tiền dịch vụ đám mây và kiểm toán tuân thủ chính sách lưu trữ dữ liệu:",
        bold_prefix="Báo cáo kinh doanh & SLA: "
    )
    add_bullet("Biểu đồ phân bổ doanh thu theo từng gói cước: Gói Enterprise Lifetime (499k) và Premium Pro (199k) đóng góp hơn 85% tổng doanh thu.", bold_prefix="Cơ cấu doanh thu dịch vụ: ")
    add_bullet("Kiểm toán tuân thủ vòng đời dữ liệu (Data Retention SLA): Đối soát thời hạn lưu trữ HDFS (7 ngày cho Free, 30 ngày cho Standard, 90 ngày cho Premium, 365 ngày cho Enterprise) đạt tỷ lệ tuân thủ 100%.", bold_prefix="Kiểm toán tuân thủ SLA: ")
    add_image_box("extracted_images/ui_business.png", "Hình 3.5: Giao diện Quản trị Kinh doanh & Đối soát SLA Hợp đồng Thuê bao", width_inch=5.8)

    add_title("3.5. Kiểm thử tải hiệu năng và Quản trị CSDL quy mô lớn (7 Triệu bản ghi)", level=2)
    add_p(
        "Để chứng minh khả năng đáp ứng thực tế khi hệ thống mở rộng quy mô lớn, học viên đã xây dựng bộ công cụ kiểm thử tải "
        "và giao diện quản trị dữ liệu quy mô 7,000,000 bản ghi trên 9 bảng dữ liệu quan hệ chuẩn 3NF:",
        bold_prefix="Thực nghiệm quy mô lớn: "
    )
    add_bullet(
        "File `fast_load_to_mysql.py` sử dụng kỹ thuật Bulk Insert kết hợp tắt tạm kiểm tra khóa ngoại (FOREIGN_KEY_CHECKS=0) "
        "và nạp qua file CSV tạm, cho phép nạp 1 triệu bản ghi vào cơ sở dữ liệu MySQL chỉ trong vòng dưới 45 giây.",
        bold_prefix="Kỹ thuật nạp nhanh (Fast Load): "
    )
    add_bullet(
        "File `test_model_integrity.py` và `check_data_integrity.sql` kiểm tra tự động 100% tính toàn vẹn tham chiếu, "
        "đảm bảo không có bản ghi mồ côi (orphan records), không có khóa ngoại gãy và chỉ số thống kê hoàn toàn chính xác.",
        bold_prefix="Kiểm tra toàn vẹn tự động: "
    )
    add_image_box("extracted_images/ui_rdbms.png", "Hình 3.6: Giao diện Trình diễn & Truy vấn Cơ sở Dữ liệu RDBMS MySQL quy mô 7 Triệu Bản ghi", width_inch=5.8)
    add_p(
        "Hình 3.6 minh họa giao diện tích hợp trực tiếp trên Web Dashboard cho phép ban quản trị phân trang (pagination), "
        "tìm kiếm lọc bản ghi và kiểm tra tính toàn vẹn dữ liệu của 9 bảng RDBMS MySQL chuẩn 3NF một cách trực quan, "
        "đáp ứng hoàn hảo cả hai yêu cầu: Quản trị giao dịch chặt chẽ và Trực quan hóa dữ liệu lớn thời gian thực.",
        italic=True
    )

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 4: BÀN LUẬN, ĐÁNH GIÁ VÀ GIẢI PHÁP TỐI ƯU CƠ SỞ DỮ LIỆU
    # =========================================================================
    add_title("CHƯƠNG 4: BÀN LUẬN, ĐÁNH GIÁ VÀ GIẢI PHÁP TỐI ƯU CƠ SỞ DỮ LIỆU", level=1)

    add_title("4.1. Đánh giá mô hình lưu trữ đa hệ (Hybrid Polyglot Persistence)", level=2)
    add_p(
        "Việc phân tách ranh giới rõ ràng giữa CSDL Quan hệ (MySQL) và CSDL Phi quan hệ (NoSQL MongoDB) mang lại những ưu thế vượt trội:",
        bold_prefix="Ưu điểm của Polyglot Persistence: "
    )
    eval_headers = ["Tiêu chí đánh giá", "Mô hình quan hệ thuần túy (Only MySQL)", "Mô hình lai (MySQL + MongoDB + Big Data)"]
    eval_rows = [
        ["Toàn vẹn giao dịch", "Rất tốt (ACID tuyệt đối)", "Rất tốt cho dữ liệu nghiệp vụ; Eventual Consistency cho telemetry"],
        ["Tốc độ ghi Telemetry", "Kém (Dễ nghẽn khóa bảng, I/O chậm)", "Xuất sắc (MongoDB write throughput gấp 8-10 lần MySQL)"],
        ["Linh hoạt cấu trúc", "Kém (Mỗi cảm biến mới phải ALTER TABLE)", "Rất cao (Document NoSQL lưu trữ schema-less)"],
        ["Khả năng mở rộng (Scale)", "Khó khăn (Scale up tốn kém)", "Dễ dàng (Scale out phân tán ngang với Sharding/HDFS)"],
        ["Phức tạp quản trị", "Thấp (Chỉ duy trì 1 database)", "Trung bình (Đòi hỏi quản lý luồng đồng bộ dữ liệu)"]
    ]
    add_styled_table(eval_headers, eval_rows, [1.8, 2.6, 2.6])

    add_title("4.2. Chiến lược chỉ mục (Indexing Strategy) và tối ưu hóa câu lệnh", level=2)
    add_p(
        "Trong quá trình vận hành cơ sở dữ liệu quan hệ, việc đánh chỉ mục đúng cách đóng vai trò sống còn đối với hiệu năng hệ thống. "
        "Các nguyên tắc tối ưu hóa sau đã được áp dụng triệt để:",
        bold_prefix="Quy tắc đánh chỉ mục: "
    )
    add_bullet(
        "Được tự động tạo B-Tree Index, giúp các câu lệnh tìm kiếm theo mã định danh đạt độ phức tạp O(log N).",
        bold_prefix="1. Khóa chính (Primary Key): "
    )
    add_bullet(
        "Tất cả các cột khóa ngoại (user_id, home_id, room_id, type_id, subscription_id, plan_id) đều được tạo Index để tối ưu các phép JOIN bảng.",
        bold_prefix="2. Khóa ngoại (Foreign Keys): "
    )
    add_bullet(
        "Tạo chỉ mục phức hợp theo quy tắc cột có tính chọn lọc cao đứng trước: `(home_id, room_id, status)` trên bảng Device, "
        "và `(status, end_date)` trên bảng HomeSubscription.",
        bold_prefix="3. Chỉ mục phức hợp (Composite Indexes): "
    )
    add_bullet(
        "Sử dụng công cụ `EXPLAIN` trước khi đưa các câu truy vấn phức tạp vào vận hành để đảm bảo MySQL thực thi thông qua Index Scan thay vì Full Table Scan.",
        bold_prefix="4. Phân tích kế hoạch thực thi (Execution Plan): "
    )

    add_title("4.3. Đảm bảo an toàn, bảo mật thông tin và sao lưu phục hồi", level=2)
    add_p(
        "Hệ thống cơ sở dữ liệu thiết lập các cơ chế an ninh nhiều lớp:",
        bold_prefix="Bảo mật và an toàn dữ liệu: "
    )
    add_bullet("Mật khẩu tài khoản được mã hóa một chiều qua hàm SHA256; dữ liệu đường truyền được bảo vệ bằng TLS/SSL.", bold_prefix="Mã hóa dữ liệu: ")
    add_bullet("Áp dụng nguyên tắc đặc quyền tối thiểu (Principle of Least Privilege). Tài khoản ứng dụng Web chỉ có quyền DML (SELECT, INSERT, UPDATE, DELETE), không có quyền DDL (DROP, ALTER).", bold_prefix="Phân quyền truy cập CSDL: ")
    add_bullet("Thiết lập lịch sao lưu tự động hàng ngày (mysqldump logic backup) kết hợp lưu trữ nhị phân binlog phục vụ khôi phục theo thời điểm (Point-in-Time Recovery).", bold_prefix="Sao lưu và phục hồi thảm họa: ")

    doc.add_page_break()

    # =========================================================================
    # KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # =========================================================================
    add_title("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", level=1)
    
    add_title("1. Kết quả đạt được", level=2)
    add_p("Sau quá trình thực hiện bài tập cá nhân môn học Cơ sở Dữ liệu Nâng cao, học viên đã hoàn thành xuất sắc các mục tiêu đề ra:")
    add_bullet("Thiết kế hoàn chỉnh mô hình thực thể liên kết ERD và sơ đồ quan hệ chuẩn hóa 3NF cho 9 bảng nghiệp vụ, loại trừ triệt để dị thường dữ liệu.", bold_prefix="• Giai đoạn 1: ")
    add_bullet("Cài đặt thành công script DDL/DML, hoàn thành đầy đủ và sâu sắc 10 nghiệp vụ kinh doanh với 41 câu lệnh truy vấn SQL nâng cao minh họa rõ cách thức quản trị và toàn vẹn dữ liệu.", bold_prefix="• Giai đoạn 2: ")
    add_bullet("Mở rộng thành công kiến trúc Big Data với MongoDB, Hadoop/Spark, xây dựng Web Dashboard trực quan và kiểm thử tải vững chắc trên 1.000.000 bản ghi.", bold_prefix="• Giai đoạn 3: ")

    add_title("2. Hướng phát triển và mở rộng", level=2)
    add_p("Trong tương lai, mô hình cơ sở dữ liệu có thể tiếp tục được nâng cấp theo các hướng chuyên sâu:")
    add_bullet("Áp dụng kỹ thuật phân vùng bảng (Table Partitioning) theo tháng đối với bảng Invoice và dữ liệu đo lường.", bold_prefix="• Phân vùng dữ liệu: ")
    add_bullet("Tích hợp cụm bộ nhớ đệm phân tán Redis (In-memory caching) để lưu trạng thái trực tiếp của thiết bị, giảm tải 80% truy vấn đọc từ MySQL.", bold_prefix="• Bộ nhớ đệm Redis: ")
    add_bullet("Nghiên cứu ứng dụng các mô hình học máy (Machine Learning) trên Apache Spark MLlib để dự báo phụ tải điện năng và phát hiện nguy cơ chập cháy tự động.", bold_prefix="• Phân tích dự báo AI: ")

    doc.add_page_break()

    # =========================================================================
    # TÀI LIỆU THAM KHẢO & PHỤ LỤC
    # =========================================================================
    add_title("TÀI LIỆU THAM KHẢO", level=1)
    refs = [
        "1. Silberschatz, A., Korth, H. F., & Sudarshan, S. (2020). Database System Concepts (7th ed.). McGraw-Hill Education.",
        "2. Elmasri, R., & Navathe, S. B. (2015). Fundamentals of Database Systems (7th ed.). Pearson.",
        "3. MySQL 8.0 Reference Manual. Oracle Corporation. URL: https://dev.mysql.com/doc/refman/8.0/en/",
        "4. MongoDB Manual (Version 7.0). MongoDB, Inc. URL: https://www.mongodb.com/docs/manual/",
        "5. Chambers, B., & Zaharia, M. (2018). Spark: The Definitive Guide: Big Data Processing Made Simple. O'Reilly Media.",
        "6. Kleppmann, M. (2017). Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems. O'Reilly Media.",
        "7. Giáo trình Cơ sở Dữ liệu Nâng cao - Khoa Công nghệ Thông tin, Đại học Bách khoa - Đại học Đà Nẵng."
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    add_title("PHỤ LỤC: DANH MỤC BIỂU MẪU KỸ THUẬT IOT", level=2)
    add_p(
        "Hệ thống quản lý đi kèm các biểu mẫu kỹ thuật chuẩn hóa phục vụ công tác bàn giao và bảo trì thực tế tại công trình "
        "(được lưu trữ tại thư mục `phụ lục/`):",
        bold_prefix="Danh mục tài liệu đính kèm: "
    )
    add_bullet("BM_IOT_02_Commissioning_Form.pdf: Biểu mẫu kiểm định và nghiệm thu thiết bị IoT trước khi đưa vào vận hành.", bold_prefix="1. Biểu mẫu nghiệm thu: ")
    add_bullet("BM_IOT_03_Commissioning_Test_Record.pdf: Biên bản ghi nhận kết quả chạy thử nghiệm tải thiết bị.", bold_prefix="2. Biên bản kiểm thử: ")
    add_bullet("BM_IOT_04_Maintenance_Log.pdf: Sổ nhật ký bảo trì, bảo dưỡng và xử lý sự cố thiết bị tại căn hộ.", bold_prefix="3. Nhật ký bảo trì: ")
    add_bullet("mau-bien-ban-ban-giao-thiet-bi-3.doc: Mẫu biên bản bàn giao thiết bị hoàn chỉnh cho khách hàng.", bold_prefix="4. Biên bản bàn giao: ")

    # Save Document
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    output_filename = "Bao_Cao_Mon_Hoc_CSDLNC_Tran_Duy_Khai_K32MCS1.docx"
    try:
        doc.save(output_filename)
        print(f"Báo cáo Word đã được tạo thành công: {output_filename}")
    except PermissionError:
        fallback_filename = "Bao_Cao_Mon_Hoc_CSDLNC_Tran_Duy_Khai_K32MCS1_CapNhat.docx"
        doc.save(fallback_filename)
        print(f"File chính đang mở trong Word, đã lưu phiên bản cập nhật mới nhất vào: {fallback_filename}")

if __name__ == "__main__":
    create_report()
