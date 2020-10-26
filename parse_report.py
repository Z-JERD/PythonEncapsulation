import os
import csv
import json
import ijson
import shutil
import decimal
import zipfile

from functools import partial

import yaml
import xlrd
import xlwt
from xlutils.copy import copy
from docxtpl import DocxTemplate


def messy_code(dir_path, dir_names):
    """
    文件名乱码处理

    文件显示： ╔╧║ú├└┴·/
                ╔╧║ú├└┴·/╓╨╙░╩²╫╓░µ╙░╞¼╙░╘║╖┼╙││╔╝¿╗π╫▄═│╝╞▒φ2020-07.xlsx

    :param dir_path: 文件路径
    :param dir_names: 文件名称
    :return:
    """
    try:
        old_file_path = os.path.join(dir_path, dir_names)

        dir_names = dir_names.encode('cp437').decode("gbk")

        new_file_path = os.path.join(dir_path, dir_names)

        os.rename(old_file_path, new_file_path)

    except Exception as e:
        new_file_path = os.path.join(dir_path, dir_names)

    os.chdir(new_file_path)

    for temp_name in os.listdir('.'):

        try:
            new_name = temp_name.encode('cp437').decode("gbk")

            os.rename(temp_name, new_name)

            temp_name = new_name

        except:
            # 如果已被正确识别为utf8编码时则不需再编码
            pass

        if os.path.isdir(temp_name):
            # 对子文件夹进行递归调用
            messy_code(os.getcwd(), temp_name)
            # 返回上级目录
            os.chdir('..')


def list_dir(dir_path):
    """获取目录下的文件

    dir_path_list: 目录下所有的文件夹（绝对路径）
    file_path_list: 目录下所有的文件（绝对路径）
    """

    dir_path_list = []
    file_path_list = []

    for path, dirs, files in os.walk(dir_path):

        for d in dirs:
            dir_name = os.path.join(path, d)

            dir_path_list.append(dir_name)

        for f in files:
            file_name = os.path.join(path, f)

            file_path_list.append(file_name)

    return dir_path_list, file_path_list


class FileHandle(object):
    """
    读写csv/xls文件
    """

    @staticmethod
    def read_csv(file_path, encode="utf8"):
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
        """读取excel文件
        参考文档：https://zhuanlan.zhihu.com/p/259583430
        """

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

    @staticmethod
    def create_yaml_file(file_path, file_content):
        """yaml文件常用于配置文件  PyYAML-5.3.1以上版本 可正常写入

        示例：
        yaml文件内容：
            age: 37
            children:
            - age: 15
              name: Jimmy Smith
            - age: 12
            name: Jenny Smith
            current_date: '2020-09-30'
            current_time: '2020-09-30 12:00:00'
            name: John Smith
            result: true
            spouse:
              age: 25
              name: Jane Smith
            subject:
            - Python
            - Java
            - Ruby

        对应的dict:
            {
              "age": 37,

              "name": 'John Smith',

              "result": True,

              "current_time": "2020-09-30 12:00:00",

              "current_date": "2020-09-30",

              "subject": ["Python", "Java", "Ruby"],

              "spouse": {"name": 'Jane Smith', "age": 25},

              "children": [
                      {"name": 'Jimmy Smith', "age": 15},
                      {"name": 'Jenny Smith', "age": 12}
                  ]
            }

        """
        with open(file_path, 'w', encoding='utf8') as f:
            yaml.safe_dump(file_content, f)

        return True

    @staticmethod
    def read_yaml_file(file_path):

        assert os.path .exists(file_path)

        with open(file_path, 'r', encoding='utf8') as f:

            content = yaml.safe_load(f)

            return content

    @staticmethod
    def create_simple_json_file(file_path, file_content, indent=4):
        """创建简单的json文件"""
        with open(file_path, 'w', encoding='utf8', newline='') as f:

            if indent > 0:
                json.dump(file_content, f, ensure_ascii=False, indent=indent)
            else:
                json.dump(file_content, f, ensure_ascii=False)

    @staticmethod
    def read_simple_json_file(file_path):
        """读取json文件"""

        assert os.path.exists(file_path), '文件不存在'

        with open(file_path, 'r', encoding='utf8') as f:
            res = json.load(f)

        return res

    @staticmethod
    def read_big_json_file(file_path, prefix=""):
        """ijson读取大文件
        prefix: None 读取全部内容
         prefix:"earth.europe.item" 读取europe中的内容

        {
          "earth": {
            "europe": [
              {
                "name": "Paris",
                "type": "city",
                "info": "aaa"
              },
              {
                "name": "Thames",
                "type": "river",
                "info": "sss"
              },
              {
                "name": "yyy",
                "type": "city",
                "info": "aaa"
              },
              {
                "name": "eee",
                "type": "river",
                "info": "sss"
              }
            ],
            "america": [
              {
                "name": "Texas",
                "type": "state",
                "info": "jjj"
              }
            ]
          }
        }

        """
        with open(file_path, 'r', encoding='utf-8') as f:

            file_gen = ijson.items(f, prefix)

            while True:
                try:
                    print(file_gen.__next__())
                except StopIteration as e:
                    print("数据读取完成")
                    break

    @staticmethod
    def read_txt_file(file_path, block_size=10 * 8):
        """读取大的文本文件， 分块读取"""

        with open(file_path, "r") as fp:
            for chunk in iter(partial(fp.read, block_size), ""):
                yield chunk

    @staticmethod
    def create_word_file(model_path, file_path,  file_content):
        """
        填充word模板
        :param model_path: 模板文件路径
        :param file_path: 新文件路径
        :param file_content: 填充的内容
        :return:
        模板文件内容：

          {{t1}}去了，有再来的时候；{{t2}}枯了，有再青的时候；{{t3}}谢了，有再开的时候。
        但是，聪明的，你告诉我，我们的日子为什么一去不复返呢？——是有人偷了他们罢：那是谁？又藏在何处呢？
        是他们自己逃走了罢：现在又到了哪里呢？

          我不知道他们给了我多少日子；但我的手确乎是渐渐空虚了。在默默里算着，八千多日子已经从我手中溜去；
        像{{t4}}上一滴水滴在大海里，我的日子滴在时间的流里，没有声音，也没有影子。我不禁头{{t5}}而{{t6}}了。

                                                                                {{t7}}年{{t8}}月{{t9}}日
        file_content:

             {
                't1': '燕子',
                't2': '杨柳',
                't3': '桃花',
                't4': '针尖',
                't5': '头涔涔',
                't6': '泪潸潸',
                't7': '2020',
                't8': '10',
                't9': '20',
            }
        """

        doc = DocxTemplate(model_path)
        doc.render(file_content)
        doc.save(file_path)

        return True

    def unzip_file(self, zip_path, remove_dir=False, subfile=False):
        """
        解压ZIP压缩包, 存在文件名乱码的情况
        :param zip_path:
        :param remove_dir 删除解压后的文件目录
        :param subfile    获取子文件路径
        :return:
        """
        current_path = os.getcwd()

        name_list = []

        path_file_list = []  # 获取所有的文件路径

        messy_name = False  # 存在乱码文件名

        with zipfile.ZipFile(file=zip_path, mode='r') as zf:

            zip_dir, zip_name = os.path.split(zip_path)[0], os.path.split(zip_path)[1]

            for name in zf.namelist():

                if not messy_name:
                    try:
                        name.encode('cp437').decode("gbk")
                        messy_name = True
                    except Exception as e:
                        pass

                name_list.append(name)

                zf.extract(name, zip_dir)

        name_list = sorted(name_list, key=lambda i: len(i))

        # 解压后的文件目录

        dir_name = name_list[0]

        try:
            encode_dir_name = dir_name.encode('cp437').decode("gbk")
        except Exception as e:
            encode_dir_name = dir_name

        dir_path = os.path.join(zip_dir, encode_dir_name)

        if messy_name:
            messy_code(zip_dir, dir_name)

        if subfile:
            path_dir_list, path_file_list = list_dir(dir_path)

        os.chdir(current_path)

        if remove_dir:

            try:
                os.removedirs(dir_path)
            except Exception as e:
                shutil.rmtree(dir_path)

        return path_file_list


if __name__ == "__main__":

    file_obj = FileHandle()
