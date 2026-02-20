#需要安装PyQt5
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import *

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://www.google.com"))
        self.setCentralWidget(self.browser)
        self.showMaximized()
        
        # 导航栏
        navbar = QToolBar()
        self.addToolBar(navbar)
        
        # 后退按钮
        back_btn = QAction('◀', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)
        
        # 前进按钮
        forward_btn = QAction('▶', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)
        
        # 刷新按钮
        reload_btn = QAction('⟳', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)
        
        # 主页按钮
        home_btn = QAction('🏠', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)
        
        # 地址栏
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        
        # 书签按钮
        bookmark_btn = QAction('⭐', self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark_btn)
        
        # 更新URL栏
        self.browser.urlChanged.connect(self.update_url)
        
        # 加载进度
        self.browser.loadProgress.connect(self.update_progress)
        self.browser.loadFinished.connect(self.load_finished)
        
        # 状态栏
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # 书签菜单
        self.bookmarks = []
        self.create_bookmark_menu()
        
        # 历史记录
        self.history = []
        
        # 设置窗口属性
        self.setWindowTitle('Python简单浏览器')
        self.setWindowIcon(QIcon('icon.png') if os.path.exists('icon.png') else QIcon())
        
    def navigate_home(self):
        self.browser.setUrl(QUrl("http://www.google.com"))
        
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        self.browser.setUrl(QUrl(url))
        self.history.append(url)
        
    def update_url(self, q):
        self.url_bar.setText(q.toString())
        self.setWindowTitle(self.browser.page().title() + ' - Python简单浏览器')
        
    def add_bookmark(self):
        url = self.browser.url().toString()
        title = self.browser.page().title()
        
        if url not in self.bookmarks:
            self.bookmarks.append({'url': url, 'title': title})
            self.update_bookmark_menu()
            self.status.showMessage(f'已添加书签: {title}', 2000)
        
    def create_bookmark_menu(self):
        menubar = self.menuBar()
        self.bookmark_menu = menubar.addMenu('书签')
        
        # 添加管理书签的选项
        manage_action = QAction('管理书签', self)
        manage_action.triggered.connect(self.manage_bookmarks)
        self.bookmark_menu.addAction(manage_action)
        self.bookmark_menu.addSeparator()
        
    def update_bookmark_menu(self):
        self.bookmark_menu.clear()
        
        manage_action = QAction('管理书签', self)
        manage_action.triggered.connect(self.manage_bookmarks)
        self.bookmark_menu.addAction(manage_action)
        self.bookmark_menu.addSeparator()
        
        for bookmark in self.bookmarks:
            action = QAction(bookmark['title'], self)
            action.setData(bookmark['url'])
            action.triggered.connect(lambda checked, url=bookmark['url']: self.browser.setUrl(QUrl(url)))
            self.bookmark_menu.addAction(action)
            
    def manage_bookmarks(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('管理书签')
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        list_widget = QListWidget()
        for bookmark in self.bookmarks:
            item = QListWidgetItem(f"{bookmark['title']}\n{bookmark['url']}")
            item.setData(Qt.UserRole, bookmark)
            list_widget.addItem(item)
            
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton('删除')
        def delete_bookmark():
            current = list_widget.currentItem()
            if current:
                bookmark = current.data(Qt.UserRole)
                self.bookmarks.remove(bookmark)
                list_widget.takeItem(list_widget.row(current))
                self.update_bookmark_menu()
                
        delete_btn.clicked.connect(delete_bookmark)
        btn_layout.addWidget(delete_btn)
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec_()
        
    def update_progress(self, progress):
        self.status.showMessage(f'加载中... {progress}%')
        
    def load_finished(self):
        self.status.showMessage('完成', 2000)
        
    def keyPressEvent(self, event):
        # 快捷键
        if event.key() == Qt.Key_F5:
            self.browser.reload()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_T:
                self.new_tab()
            elif event.key() == Qt.Key_W:
                self.close_current_tab()
                
    def new_tab(self):
        # 简单的多标签页功能
        tab_browser = QWebEngineView()
        tab_browser.setUrl(QUrl("http://www.google.com"))
        
        # 创建新的标签页
        if not hasattr(self, 'tab_widget'):
            # 将central widget转换为tab widget
            self.tab_widget = QTabWidget()
            self.tab_widget.addTab(self.browser, self.browser.page().title())
            self.setCentralWidget(self.tab_widget)
            
            # 将原浏览器移到tab中
            self.tab_widget.setCurrentWidget(self.browser)
            
        self.tab_widget.addTab(tab_browser, "新标签页")
        self.tab_widget.setCurrentWidget(tab_browser)
        
        # 连接信号
        tab_browser.urlChanged.connect(lambda q, browser=tab_browser: 
                                      self.update_tab_title(browser, q))
        
    def close_current_tab(self):
        if hasattr(self, 'tab_widget') and self.tab_widget.count() > 1:
            current = self.tab_widget.currentWidget()
            self.tab_widget.removeTab(self.tab_widget.currentIndex())
            current.deleteLater()
            
    def update_tab_title(self, browser, url):
        index = self.tab_widget.indexOf(browser)
        if index >= 0:
            self.tab_widget.setTabText(index, browser.page().title())

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Python简单浏览器')
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建浏览器窗口
    browser = SimpleBrowser()
    
    # 显示窗口
    browser.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
