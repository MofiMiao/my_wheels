"""
 ***********************************************************************************************
 *                                                                                             *
 *                                                                                             *
 *                    File Name : read_db.py                                                   *
 *                                                                                             *
 *                   Programmer : Mofi.Miao                                                    *
 *                                                                                             *
 *                   Start Date : 2021.09.18                                                   *
 *                                                                                             *
 *                  Last Update : 2021.09.18                                                   *
 *                                                                                             *
 *---------------------------------------------------------------------------------------------*
 Db2Excel：目的在于将.db文件的内容读取至excel表格
 Excel2Db：目的在于将excel表格写入.db文件
 Db2Excel2: pandas实现的db转excel
 注：目前这个是为听歌软件服务的，所以index没有写入
 """

import sqlite3 as sqlite
from xlwt import *
import xlrd
import pandas as pd


class Db2Excel:
    def __init__(self, path):
        self.path = path
        self.db = sqlite.connect(self.path)
        self.cur = self.db.cursor()
        self.xlspath = self.path[0:self.path.rfind('.')] + '.xls'

    def sqlite_get_col_names(self, table):
        query = 'select * from  %s' % table
        self.cur.execute(query)
        return [tuple[0] for tuple in self.cur.description]

    def dict_factory(self, row):
        d = {}
        for idx, col in enumerate(self.cur.description):
            d[col[0]] = row[idx]
        return d

    def sqlite_query(self, table, col='*', where=''):
        if where != '':
            query = 'select %s from %s where %s' % (col, table, where)
        else:
            query = 'select %s from %s ' % (col, table)
        self.cur.execute(query)
        return self.cur.fetchall()

    def sqlite_to_workbook(self, table, workbook):
        ws = workbook.add_sheet(table)
        print('create table %s.' % table)
        # for colx, heading in enumerate(self.sqlite_get_col_names(self.cur, table)):
        for colx, heading in enumerate(self.sqlite_get_col_names(table)):
            ws.write(0, colx, heading)
        for rowy, row in enumerate(self.sqlite_query(table)):
            for colx, text in enumerate(row):
                print(text)
                ws.write(rowy + 1, colx, text)

    def save_excel(self):
        tbl_name = []

        print("<%s> --> <%s>" % (self.path, self.xlspath))
        w = Workbook()
        for tbl_name in [row[0] for row in
                         self.sqlite_query('sqlite_master', 'tbl_name', 'type = \'table\'')]:
            self.sqlite_to_workbook(tbl_name, w)
        if tbl_name:
            w.save(self.xlspath)

    def get_table(self):
        table = [row[0] for row in
                 self.sqlite_query('sqlite_master', 'tbl_name', 'type = \'table\'')]

    def __del__(self):
        self.cur.close()
        self.db.close()


class Excel2Db:
    def __init__(self, dbName):
        # if os.path.exists(dbName):
        #     os.remove(dbName)
        # print("初始化数据库实例")
        self.conn = sqlite.connect(dbName)

    def __del__(self):
        # print("释放数据库实例")
        self.conn.close()

    def ExcelToDb(self, excelName):
        work_book = pd.read_excel(excelName, sheet_name=None)
        for table, df in work_book.items():
            df.to_sql(table, self.conn, if_exists='replace', index=False)
        self.conn.commit()


def get_excel_sheet(excel_name: str) -> list:
    work_book = xlrd.open_workbook(excel_name)
    sheet_names = work_book.sheet_names()

    return sheet_names


class Db2Excel2:
    def __init__(self, path):
        self.path = path
        self.db = sqlite.connect(self.path)
        self.cur = self.db.cursor()

    def __del__(self):
        self.cur.close()
        self.db.close()

    def get_table(self):
        table = [row[0] for row in
                 self.sqlite_query('sqlite_master', 'tbl_name', 'type = \'table\'')]
        return table

    def sqlite_query(self, table, col='*', where=''):
        if where != '':
            query = 'select %s from %s where %s' % (col, table, where)
        else:
            query = 'select %s from %s ' % (col, table)
        self.cur.execute(query)
        return self.cur.fetchall()

    def db_to_xlsx(self, file_name=None):
        if not file_name:
            self.xlspath = self.path[0:self.path.rfind('.')] + '.xlsx'
        else:
            self.xlspath = file_name
        writer = pd.ExcelWriter(file_name)
        for sheet_name in self.get_table():
            df = pd.read_sql_query("select * from %s" % sheet_name, self.db)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()


if __name__ == "__main__":
    # db1 = Db2Excel(r"E:\Workspace\Python_workspace\get_svn\123.db")
    # db1.save_excel()

    # db2 = Excel2Db(r"123.db")
    # db2.ExcelToDb(r"123.xlsx")
    db1 = Db2Excel2(r"E:\Workspace\Python_workspace\get_svn\123.db")
    db1.db_to_xlsx("123.xlsx")
