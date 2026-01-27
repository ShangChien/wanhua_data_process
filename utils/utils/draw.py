import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw
import xlsxwriter
from io import BytesIO

# ========= 参数 =========
input_csv = "input.csv"
output_xlsx = "output_with_rdkit_images.xlsx"
img_size = (250, 250)
image_col_name = "rdkit_2d_structure"

# ========= 读取 CSV =========
df = pd.read_csv(input_csv)

# ========= 创建 Excel =========
workbook = xlsxwriter.Workbook(output_xlsx)
worksheet = workbook.add_worksheet("data")

# 写表头
for col_idx, col_name in enumerate(df.columns):
    worksheet.write(0, col_idx, col_name)

img_col_idx = len(df.columns)
worksheet.write(0, img_col_idx, image_col_name)

# ========= 写数据 + 图片 =========
for row_idx, row in df.iterrows():
    excel_row = row_idx + 1

    # 普通字段
    for col_idx, value in enumerate(row):
        worksheet.write(excel_row, col_idx, value)

    smiles = row["smiles"]
    mol = Chem.MolFromSmiles(smiles)

    if mol:
        img = Draw.MolToImage(mol, size=img_size)

        # 保存到内存
        image_data = BytesIO()
        img.save(image_data, format="PNG")
        image_data.seek(0)

        # 插入图片
        worksheet.insert_image(
            excel_row,
            img_col_idx,
            "mol.png",
            {
                "image_data": image_data,
                "x_scale": 1,
                "y_scale": 1,
                "object_position": 1,  # 图片随单元格移动/缩放
            },
        )

        # 调整行高 / 列宽
        worksheet.set_row(excel_row, 150)
        worksheet.set_column(img_col_idx, img_col_idx, 35)

# ========= 保存 =========
workbook.close()
print(f"完成：已生成 {output_xlsx}")
