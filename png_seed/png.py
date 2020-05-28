# -*- coding:utf-8 -*-
'''
png.py
Created on 2020/2/13 17:13
Copyright (c) 2020/2/13,ZZ 版权所有.
@author: ZZ
'''
import requests
from requests.exceptions import RequestException
import Tkinter as tk
import ttk
from bs4 import BeautifulSoup
import bs4
from Tkinter import *
from tkFileDialog import askdirectory
import os
import sys

class DB():
  def __init__(self):
      self.window = tk.Tk()  #创建window窗口
      self.window.title("Crawler Pics")  # 定义窗口名称
      # self.window.resizable(0,0)  # 禁止调整窗口大小
      self.menu = ttk.Combobox(self.window,width=6)
      self.path = StringVar()
      self.lab1 = tk.Label(self.window, text = "目标路径:")
      self.lab2 = tk.Label(self.window, text="选择分类:")
      self.lab3 = tk.Label(self.window, text="爬取页数:")
      self.page = tk.Entry(self.window, width=5)
      self.input = tk.Entry(self.window, textvariable = self.path, width=80)  # 创建一个输入框,显示图片存放路径
      self.info = tk.Text(self.window, height=20)   # 创建一个文本展示框，并设置尺寸

      self.menu['value'] = ('DX','XQT', 'HSW', 'MTK', 'YYZ','DZH')
      self.menu.current(0)

      # 添加一个按钮，用于选择图片保存路径
      self.t_button = tk.Button(self.window, text='选择路径', relief=tk.RAISED, width=8, height=1, command=self.select_Path)
      # 添加一个按钮，用于触发爬取功能
      self.t_button1 = tk.Button(self.window, text='爬取', relief=tk.RAISED, width=8, height=1,command=self.download)
      # 添加一个按钮，用于触发清空输出框功能
      self.c_button2 = tk.Button(self.window, text='清空输出', relief=tk.RAISED,width=8, height=1, command=self.cle)

  def gui_arrang(self):
      """完成页面元素布局，设置各部件的位置"""
      self.lab1.grid(row=0,column=0)
      self.lab2.grid(row=1, column=0)
      self.menu.grid(row=1, column=1,sticky=W)
      self.lab3.grid(row=2, column=0,padx=5,pady=5,sticky=tk.W)
      self.page.grid(row=2, column=1,sticky=W)
      self.input.grid(row=0,column=1)
      self.info.grid(row=3,rowspan=5,column=0,columnspan=3,padx=15,pady=15)
      self.t_button.grid(row=0,column=2,padx=5,pady=5,sticky=tk.W)
      self.t_button1.grid(row=1,column=2)
      self.c_button2.grid(row=0,column=3,padx=5,pady=5,sticky=tk.W)

  def get_cid(self):
      category = {
          'DX': 2,
          'XQT': 6,
          'HSW': 7,
          'MTK': 3,
          'YYZ': 4,
          'DZH': 5
      }
      cid = None
      if self.menu.get() == "DX":
          cid = category["DX"]
      elif self.menu.get() == "XQT":
          cid = category["XQT"]
      elif self.menu.get() == "HSW":
          cid = category["HSW"]
      elif self.menu.get() == "MTK":
          cid = category["MTK"]
      elif self.menu.get() == "YYZ":
          cid = category["YYZ"]
      elif self.menu.get() == "DZH":
          cid = category["DZH"]
      return cid

  def select_Path(self):
      """选取本地路径"""
      path_ = askdirectory()
      self.path.set(path_)

  def get_html(self, url, header=None):
      """请求初始url"""
      response = requests.get(url, headers=header)
      try:
          if response.status_code == 200:
              # print(response.status_code)
              # print(response.text)
              return response.text
          return None
      except RequestException:
          print("请求失败")
          return None

  def parse_html(self, html, list_data):
      """提取img的名称和图片url，并将名称和图片地址以字典形式返回"""
      soup = BeautifulSoup(html, 'html.parser')
      img = soup.find_all('img')
      for t in img:
          if isinstance(t, bs4.element.Tag):
             # print(t)
             name = t.get('alt')
             img_src = t.get('src')
             list_data.append([name, img_src])
      dict_data = dict(list_data)
      return dict_data

  def get_image_content(self, url):
         """请求图片url，返回二进制内容"""
         print("正在下载", url)
         self.info.insert('end',"正在下载:"+url+'\n')
         try:
             r = requests.get(url)
             if r.status_code == 200:
                 return r.content
             return None
         except RequestException:
             return None

  def download(self):
     base_url = 'https://www.buxiuse.com/?'
     for i in range(1, int(self.page.get())+1):
         url = base_url + 'cid=' + str(self.get_cid()) + '&' + 'page=' + str(i)
         print(url)
         header = {
             'Accept': 'text/html,application/xhtml+xml,application/xml;q = 0.9, image/webp,image/apng,*/*;q='
                       '0.8',
             'Accept-Encoding': 'gzip,deflate,br',
             'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
             'Cache-Control': 'max-age=0',
             'Connection': 'keep-alive',
             'Host': 'www.dbmeinv.com',
             'Upgrade-Insecure-Requests': '1',
             'User-Agent': 'Mozilla/5.0(WindowsNT6.1;Win64;x64) AppleWebKit/537.36(KHTML, likeGecko) Chrome/'
                           '70.0.3538.102Safari/537.36 '
         }
         list_data = []
         html = self.get_html(url)
         # print(html)
         dictdata = self.parse_html(html, list_data)


         root_dir = self.input.get()
         case_list = ["DX", "XQT", "HSW", "MTK", "YYZ", "DZH"]

         for t in case_list:
             if not os.path.exists(root_dir + '/pics'):
                 os.makedirs(root_dir + '/pics')
             if not os.path.exists((root_dir + '/pics/' + str(t)).encode('gbk')):
                 os.makedirs((root_dir + '/pics/' + str(t)).encode('gbk'))


         if self.menu.get() == "DX":
             save_path = root_dir + '/pics/' + 'DX'
             for t in dictdata.items():
                 try:
                     # file_path = '{0}/{1}.{2}'.format(save_path, t[1], 'jpg')
                     file_path = save_path + '/' + t[0] + 'q' + '.jpg'
                     if not os.path.exists(file_path):  # 判断是否存在文件，不存在则爬取
                         with open(file_path, 'wb') as f:
                             f.write(self.get_image_content(t[1]))
                             f.close()
                             print('文件保存成功')
                 except:
                     continue

         elif self.menu.get() == "XQT":
             save_path = root_dir + '/pics/' + 'XQT'
             for t in dictdata.items():
                 try:
                     # file_path = '{0}/{1}.{2}'.format(save_path, t[1], 'jpg')
                     file_path = save_path + '/' + t[0] + 'q' + '.jpg'
                     if not os.path.exists(file_path):  # 判断是否存在文件，不存在则爬取
                         with open(file_path, 'wb') as f:
                             f.write(self.get_image_content(t[1]))
                             f.close()
                             print('文件保存成功')
                 except:
                     continue

         elif self.menu.get() == "HSW":
             save_path = root_dir + '/pics/' + 'HSW'
             for t in dictdata.items():
                 try:
                     # file_path = '{0}/{1}.{2}'.format(save_path, t[1], 'jpg')
                     file_path = save_path + '/' + t[0] + 'q' + '.jpg'
                     if not os.path.exists(file_path):  # 判断是否存在文件，不存在则爬取
                         with open(file_path, 'wb') as f:
                             f.write(self.get_image_content(t[1]))
                             f.close()
                             print('文件保存成功')
                 except :
                     continue

         elif self.menu.get() == "MTK":
             save_path = root_dir + '/pics/' + 'MTK'
             for t in dictdata.items():
                 try:
                     # file_path = '{0}/{1}.{2}'.format(save_path, t[1], 'jpg')
                     file_path = save_path + '/' + t[0] + 'q' + '.jpg'
                     if not os.path.exists(file_path):  # 判断是否存在文件，不存在则爬取
                         with open(file_path, 'wb') as f:
                             f.write(self.get_image_content(t[1]))
                             f.close()
                             print('文件保存成功')
                 except:
                     continue

         elif self.menu.get() == "YYZ":
             save_path = root_dir + '/pics/' + 'YYZ'
             for t in dictdata.items():
                 try:
                     # file_path = '{0}/{1}.{2}'.format(save_path, t[1], 'jpg')
                     file_path = save_path + '/' + t[0] + 'q' + '.jpg'
                     if not os.path.exists(file_path):  # 判断是否存在文件，不存在则爬取
                         with open(file_path, 'wb') as f:
                             f.write(self.get_image_content(t[1]))
                             f.close()
                             print('文件保存成功')
                 except :
                     continue

         elif self.menu.get() == "DZH":
             save_path = root_dir + '/pics/' + 'DZH'
             for t in dictdata.items():
                 try:
                     # file_path = '{0}/{1}.{2}'.format(save_path, t[1], 'jpg')
                     file_path = save_path + '/' + t[0] + 'q' + '.jpg'
                     if not os.path.exists(file_path):  # 判断是否存在文件，不存在则爬取
                         with open(file_path, 'wb') as f:
                             f.write(self.get_image_content(t[1]))
                             f.close()
                             print('文件保存成功')
                 except:
                     continue

  def cle(self):
     """定义一个函数，用于清空输出框的内容"""
     self.info.delete(1.0,"end")  # 从第一行清除到最后一行


if __name__ == '__main__':


    reload(sys)
    sys.setdefaultencoding('utf-8')
    t = DB()
    t.gui_arrang()
    tk.mainloop()

