import sys

from PySide6.QtWidgets import QApplication, QCalendarWidget
from PySide6.QtGui import QColor, QBrush
from PySide6.QtCore import Signal

from managers import DiaryManager
from PySide6.QtCore import QDate

StyleSheet = """
/*顶部导航区域*/
#qt_calendar_navigationbar {
    background-color: rgb(0, 188, 212);
    min-height: 100px;
}


/*上一个月按钮和下一个月按钮(从源码里找到的objectName)*/
#qt_calendar_prevmonth, #qt_calendar_nextmonth {
    border: none; /*去掉边框*/
    margin-top: 64px;
    color: white;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    border-radius: 18px; /*看来近似椭圆*/
    font-weight: bold; /*字体加粗*/
    qproperty-icon: none; /*去掉默认的方向键图片，当然也可以自定义*/
    background-color: transparent;/*背景颜色透明*/
}
#qt_calendar_prevmonth {
    qproperty-text: "<"; /*修改按钮的文字*/
}
#qt_calendar_nextmonth {
    qproperty-text: ">";
}
#qt_calendar_prevmonth:hover, #qt_calendar_nextmonth:hover {
    background-color: rgba(225, 225, 225, 100);
}
#qt_calendar_prevmonth:pressed, #qt_calendar_nextmonth:pressed {
    background-color: rgba(235, 235, 235, 100);
}


/*年,月控件*/
#qt_calendar_yearbutton, #qt_calendar_monthbutton {
    color: white;
    margin: 18px;
    min-width: 60px;
    border-radius: 30px;
}
#qt_calendar_yearbutton:hover, #qt_calendar_monthbutton:hover {
    background-color: rgba(225, 225, 225, 100);
}
#qt_calendar_yearbutton:pressed, #qt_calendar_monthbutton:pressed {
    background-color: rgba(235, 235, 235, 100);
}


/*年份输入框*/
#qt_calendar_yearedit {
    min-width: 50px;
    color: white;
    background: transparent;/*让输入框背景透明*/
}
#qt_calendar_yearedit::up-button { /*往上的按钮*/
    width: 20px;
    subcontrol-position: right;/*移动到右边*/
}
#qt_calendar_yearedit::down-button { /*往下的按钮*/
    width: 20px;
    subcontrol-position: left; /*移动到左边去*/
}


/*月份选择菜单*/
CalendarWidget QToolButton QMenu {
     background-color: white;
}
CalendarWidget QToolButton QMenu::item {
    padding: 10px;
}
CalendarWidget QToolButton QMenu::item:selected:enabled {
    background-color: rgb(230, 230, 230);
}
CalendarWidget QToolButton::menu-indicator {
    /*image: none;去掉月份选择下面的小箭头*/
    subcontrol-position: right center;/*右边居中*/
}


/*下方的日历表格*/
#qt_calendar_calendarview {
    outline: 0px;/*去掉选中后的虚线框*/
    selection-background-color: rgb(0, 188, 212); /*选中背景颜色*/
}
"""


class CalendarInterface(QCalendarWidget):
    calendar_switchTo_editor_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("MarkedCalendar")
        self.diary_manager = DiaryManager()
        self.dates = []
        self.load_diary_dates()
        self.marked_dates = []

        self.clicked.connect(self.date_clicked)

        # 应用样式表
        self.setStyleSheet(StyleSheet)

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)

        if date in self.dates:
            painter.save()
            # 设置半透明的红色
            painter.setBrush(QBrush(QColor(255, 0, 0, 128)))
            # 绘制较大的椭圆
            painter.drawEllipse(rect.center(), 15, 15)
            painter.restore()

    def load_diary_dates(self):
        self.dates = self.diary_manager.get_all_dates()
        self.dates = [
            QDate.fromString(date_str, "yyyy-MM-dd")
            for date_str in self.diary_manager.get_all_dates()
        ]

    def date_clicked(self, date):
        print(date)
        date = date.toString("yyyy-MM-dd")
        print(date)
        self.calendar_switchTo_editor_signal.emit(date)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = CalendarInterface()
    window.show()
    sys.exit(app.exec())
