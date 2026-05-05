import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.core.image import Image as CoreImage
import os
from android.permissions import request_permissions, Permission
from android.storage import app_storage_path, primary_external_storage_path

# 安卓权限请求（仅安卓生效）
if platform == 'android':
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

# 中文路径兼容
def cv2_imread(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

def cv2_imsave(path, img):
    cv2.imencode(".png", img)[1].tofile(path)

class WatermarkRemoverApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img_origin = None
        self.img_cv = None
        self.mask = None
        self.scale = 1.0
        self.ix, self.iy, self.fx, self.fy = -1, -1, -1, -1
        self.is_drawing = False
        self.image_widget = KivyImage()

    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 顶部按钮栏
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        btn_open = Button(text="打开图片", on_press=self.open_image, background_color=(0, 0.48, 0.76, 1))
        btn_save = Button(text="保存图片", on_press=self.save_image, background_color=(0.16, 0.66, 0.27, 1))
        btn_layout.add_widget(btn_open)
        btn_layout.add_widget(btn_save)
        
        # 图片显示区域
        self.image_widget.bind(on_touch_down=self.on_mouse_down)
        self.image_widget.bind(on_touch_move=self.on_mouse_move)
        self.image_widget.bind(on_touch_up=self.on_mouse_up)
        
        main_layout.add_widget(btn_layout)
        main_layout.add_widget(self.image_widget)
        
        return main_layout

    def open_image(self, instance):
        """打开图片（安卓适配）"""
        if platform == 'android':
            # 安卓指定图片路径（简化版，优先读取手机图片目录）
            img_path = os.path.join(primary_external_storage_path(), "Pictures")
            if not os.path.exists(img_path):
                self.show_popup("提示", "未找到图片目录")
                return
            # 取第一张图片（简化演示，实际可加文件选择器）
            img_files = [f for f in os.listdir(img_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            if not img_files:
                self.show_popup("提示", "图片目录无可用图片")
                return
            path = os.path.join(img_path, img_files[0])
        else:
            # PC端测试用文件选择
            from tkinter import filedialog
            path = filedialog.askopenfilename(filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp")])
        
        if not path:
            return
        
        self.img_origin = cv2_imread(path)
        if self.img_origin is None:
            self.show_popup("错误", "图片读取失败")
            return
        
        self.img_cv = self.img_origin.copy()
        h, w = self.img_cv.shape[:2]
        self.mask = np.zeros((h, w), dtype=np.uint8)
        
        # 计算缩放比例适配窗口
        win_w, win_h = Window.width, Window.height - 100  # 减去按钮高度
        self.scale = min(win_w / w, win_h / h)
        new_w, new_h = int(w * self.scale), int(h * self.scale)
        
        # 转换为Kivy纹理显示
        self.update_image_display()

    def update_image_display(self):
        """更新图片显示"""
        if self.img_cv is None:
            return
        h, w = self.img_cv.shape[:2]
        new_w, new_h = int(w * self.scale), int(h * self.scale)
        
        # 转换颜色空间并缩放
        img_rgb = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # 创建Kivy纹理
        texture = Texture.create(size=(new_w, new_h))
        texture.blit_buffer(img_resized.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical()  # 修复上下颠倒问题
        self.image_widget.texture = texture

    def on_mouse_down(self, instance, touch):
        """鼠标/触摸按下"""
        if not self.image_widget.collide_point(*touch.pos):
            return
        self.is_drawing = True
        self.ix, self.iy = touch.x, touch.y

    def on_mouse_move(self, instance, touch):
        """鼠标/触摸移动"""
        if not self.is_drawing or not self.image_widget.collide_point(*touch.pos):
            return
        self.fx, self.fy = touch.x, touch.y

    def on_mouse_up(self, instance, touch):
        """鼠标/触摸抬起"""
        if not self.is_drawing:
            return
        self.is_drawing = False
        
        # 转换坐标到原始图片尺寸
        x1 = int(self.ix / self.scale)
        y1 = int(self.iy / self.scale)
        x2 = int(self.fx / self.scale)
        y2 = int(self.fy / self.scale)
        
        # 绘制遮罩并去水印
        cv2.rectangle(self.mask, (x1, y1), (x2, y2), 255, -1)
        self.remove_watermark()

    def remove_watermark(self):
        """去水印处理"""
        if self.img_cv is None:
            return
        # 修复Inpaint算法
        result = cv2.inpaint(self.img_cv, self.mask, 3, cv2.INPAINT_NS)
        self.img_cv = result
        self.update_image_display()

    def save_image(self, instance):
        """保存图片（安卓适配）"""
        if self.img_cv is None:
            self.show_popup("错误", "无处理后的图片")
            return
        
        if platform == 'android':
            # 安卓保存到应用目录/图片目录
            save_path = os.path.join(primary_external_storage_path(), "Pictures", "removed_watermark.png")
        else:
            from tkinter import filedialog
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG图片", "*.png")])
        
        if save_path:
            cv2_imsave(save_path, self.img_cv)
            self.show_popup("成功", f"图片已保存到：{save_path}")

    def show_popup(self, title, content):
        """弹出提示框"""
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.8, 0.4))
        popup.open()

if __name__ == '__main__':
    WatermarkRemoverApp().run()