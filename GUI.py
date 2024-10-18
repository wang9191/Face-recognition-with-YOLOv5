from PySide2.QtWidgets import QApplication,QMessageBox,QTableWidgetItem
from PySide2.QtUiTools import QUiLoader
import psycopg2
import sys

# 导入相关库
# 定义一个类专门处理GUI
class Stats:

    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象

        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load("C:/Users/86183/Desktop/FaceRecognition-master/main.ui")
        self.ui.setWindowTitle('人脸识别')#设置窗口名称
        self.ui.c_button.clicked.connect(self.close_main_window)  # 按钮按下 执行函数self.close_main_window

        self.login = QUiLoader().load("C:/Users/86183/Desktop/FaceRecognition-master/login.ui")
        self.login.button3.clicked.connect(self.close_login_window)
        self.login.button1.clicked.connect(self.Sign_in)
        self.login.button2.clicked.connect(self.Register)

    def close_main_window(self):#关闭窗口
        self.ui.close()

    def add_cell(self, row, column, txt):  # 修改单个单元格的内容
        item = QTableWidgetItem()
        item.setText(txt)
        self.ui.table1.setItem(row, column, item)

    def init_table(self, tab_list):
        self.row = int(len(tab_list))  # 获得行数
        self.ui.table1.setRowCount(self.row)  # 初始化行数
        for i in range(self.row):
            temp = list(tab_list[i])
            for j in range(5):  # 循环写入5个属性
                self.add_cell(i, j, str(temp[j]))

    def close_login_window(self):  # 关闭窗口
        self.login.close()
        cur.close()
        conn.close()

    def add_cell(self, row, column, txt):  # 修改单个单元格的内容
        item = QTableWidgetItem()
        item.setText(txt)
        self.ui.table1.setItem(row, column, item)

    def init_table(self, tab_list):
        self.row = int(len(tab_list))  # 获得行数
        self.ui.table1.setRowCount(self.row)  # 初始化行数
        for i in range(self.row):
            temp = list(tab_list[i])
            for j in range(2):  # 循环写入2个属性
                self.add_cell(i, j, str(temp[j]))

    def Sign_in(self):
        user = self.login.user.text()  # 获取输入框的内容
        password = self.login.password.text()
        val = (user, password)
        cur.execute('select * from userinformation where uname = %s and upassword = %s;', val)
        result = cur.fetchall()  # 获取所有结果
        conn.commit()
        if result == []:
            QMessageBox.about(self.login, '提示', '密码错误或用户不存在')
        else:
            QMessageBox.about(self.login, '提示', '登录成功')
            self.login.close()
            mainWindow.show()

    def Register(self):
        user = self.login.user.text()  # 获取输入框的内容
        password = self.login.password.text()
        cur.execute(f'select * from userinformation where uname = \'%s\' ;' % (user))
        result = cur.fetchall()  # 获取所有结果
        conn.commit()
        val = (user, password)
        if result != []:
            QMessageBox.about(self.login, '提示', '用户已存在')
        else:
            cur.execute("insert into userinformation VALUES (%s,%s);", val)
            conn.commit()
            QMessageBox.about(self.login, '提示', '注册成功')

# 定义一个连接OpenGauss的函数
def create_conn():
    database = 'project'
    user = 'dboper'
    password = 'cqy123456?'
    host = '192.168.136.131'
    port = '26000'
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)  # 连接数据库
    return conn


#程序从这里执行************************************************************************************************************
app = QApplication([])
stats = Stats()

msgBox = QMessageBox()
try:
    conn = create_conn()
except Exception as e:
    msgBox.about(stats.ui, '提示窗口', str(e))

else:
    msgBox.about(stats.ui, '提示窗口', '数据库连接成功  ')#弹窗提示
    #msgBox.about(stats, '提示窗口', '数据库连接成功  ')  # 弹窗提示

    ######     获得student表的全部内容       ######
    cur = conn.cursor()  # 创建光标
    cur.execute("select * from Detect;")  # 执行SQL指令
    results = cur.fetchall()  # 获取所有结果
    conn.commit()
    ######       将数据写入UI               ######
    stats.init_table(results)

    stats.login.show()  # 登录界面显示

sys.exit(app.exec_())#事件处理循环  要不然程序一闪而过  死循环