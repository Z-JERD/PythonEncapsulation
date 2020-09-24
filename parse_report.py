import os
import csv

import xlrd
import xlwt
from xlutils.copy import copy


class FileHandle(object):
    """
    读写csv/xls文件
    """

    @staticmethod
    def read_csv(file_path, encode="utf-8"):
        """读取csv文件"""

        assert os.path.exists(file_path), '文件不存在'

        try:
            workbook = open(file=file_path, mode='r', encoding=encode)
        except Exception as e:
            assert False, '文件打开失败'

        worksheet = csv.reader(workbook)

        file_content = []

        for row in worksheet:

            row_content = [v.strip() for v in row]

            blank_line = [value for value in row_content if value]

            if not blank_line:
                continue

            file_content.append(row_content)

        return file_content

    @staticmethod
    def write_csv(file_path, file_content, file_mode=0, file_header=None):
        """
        写入csv文件
        :param file_path:
        :param file_content:
        :param file_mode: 0:写入 1：追加
        :param file_header:
        :return:
        """

        if os.path.exists(file_path) and file_mode == 1:
            mode = "a"
        else:
            mode = "w"

        with open(file_path, mode=mode, encoding="utf8", newline='') as f:

            file_writer = csv.writer(f)

            if file_header and isinstance(file_header, list):

                file_writer.writerow(file_header)

            for row in file_content:

                file_writer.writerow(row)

    @staticmethod
    def read_excel_file(file_path):
        """读取excel文件"""

        assert os.path.exists(file_path), '文件不存在'
        file_content = []

        try:
            workbook = xlrd.open_workbook(filename=file_path, on_demand=True)
        except Exception as e:
            assert False, '文件打开失败'

        worksheet = workbook.sheet_by_index(0)

        for row in worksheet.get_rows():

            row_content = []

            for index, c in enumerate(row):
                if c.ctype == 1:
                    row_content.append(c.value.strip())
                elif c.ctype == 2:
                    if c.value % 1 == 0:
                        row_content.append(int(c.value))
                    else:
                        row_content.append(c.value)
                elif c.ctype == 3:
                    try:
                        date_value = xlrd.xldate_as_datetime(c.value, 0).strftime('%Y-%m-%d %X')
                        show_date, show_time = date_value.split(" ")

                        if show_date == '1899-12-31':
                            row_content.append(show_time)
                        elif show_date != '1899-12-31' and show_time == '00:00:00':
                            row_content.append(show_date)
                        else:
                            row_content.append(date_value)
                    except Exception as e:
                        row_content.append(str(int(c.value)).strip())
                else:
                    row_content.append(str(c.value).strip())

            blank_line = [value for value in row_content if value]
            if not blank_line:
                continue

            file_content.append(row_content)
            
        return file_content

    @staticmethod
    def create_excel_file(file_path, file_content, file_mode=0, file_header=None, sheet_name="Sheet1"):
        """新建excel xlsx

        file_header:

            [
                ["报表", "院线月度结算"],
                ["院线", "北京红鲤鱼数字电影院线有限公司"],
                ["序号", "影院名称", "影院编码", "影片名称", "影片编码", "设备归属", "开始日期", "结束日期", "总场次", "总人次",
                 "总票房", "电影专项基金", "增值税率", "税金", "净票房", "分账比例", "分账片款"]
            ]

        file_content:

            [

                [
                    1, "1/2的魔法", "IMAX", "051400392020", "自购",	"2020/8/1", "2020/8/31", 1, 13, 720.00, 0, 0, 0, 720.00, "43%",
                    309.60
                ]
            ]
        """
        if os.path.exists(file_path) and file_mode == 1:
            """追加内容"""
            row_data = file_content
            workbook = xlrd.open_workbook(file_path)

            sheets = workbook.sheet_names()
            worksheet = workbook.sheet_by_name(sheets[0])

            rows_old = worksheet.nrows

            if file_header:
                old_num = rows_old - len(file_header)
            else:
                old_num = rows_old

            new_workbook = copy(workbook)
            new_worksheet = new_workbook.get_sheet(0)

            for i in range(0, len(row_data)):

                row_data[i][0] = old_num + i + 1

                for j in range(0, len(row_data[i])):
                    new_worksheet.write(i + rows_old, j, row_data[i][j])

            new_workbook.save(file_path)
        else:
            if file_header:
                row_data = file_header + file_content
            else:
                row_data = file_content

            workbook = xlwt.Workbook(encoding='utf-8')
            sheet = workbook.add_sheet(sheet_name, cell_overwrite_ok=True)

            for i in range(0, len(row_data)):
                for j in range(0, len(row_data[i])):
                    sheet.write(i, j, row_data[i][j])

            workbook.save(file_path)


if __name__ == "__main__":

    file_obj = FileHandle()






