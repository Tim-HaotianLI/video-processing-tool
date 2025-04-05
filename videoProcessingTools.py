# 以下内容的设置在：File->Editor->File and Code Templates->python script

# -*- coding = utf-8 -*-
# @time : 2024/11/17 21:48
# @Author : 
# @File : videoProcessingTools.py
# @Software : PyCharm

import tkinter as tk
from tkinter import Canvas
import cv2
from PIL import Image, ImageTk
import math

class VideoPlayer():
    def __init__(self, master, video_path):
        self.master = master
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)

        self.original_frame = None
        self.playing = False  # Flag to indicate if video is currently playing
        self.nowFrame = 0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.timer = None

        self.bbox_start = None
        self.bbox = None

        with open("./item.txt", "r") as fp:
            self.item = int(fp.read())

        self.f = 2.5
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)//self.f)
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)//self.f)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_widgets()

    def on_close(self):
        try:
            with open("./item.txt","w") as fp:
                fp.write(str(self.item))
            print("Data saved successfully!")
        except Exception as e:
            print(f"Failed to save data: {e}")

        self.master.destroy()

    def create_widgets(self):


        self.controls_frame = tk.Frame(self.master, bg="lightgray", padx=10, pady=10)
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.btn_prev = tk.Button(self.controls_frame, text="←_Frame", command=self.show_prev_frame, width=18)
        self.btn_prev.pack(pady=5)

        self.btn_play = tk.Button(self.controls_frame, text="▶ Play", command=self.play_video, width=18)
        self.btn_play.pack(pady=5)

        self.btn_stop = tk.Button(self.controls_frame, text="⏸ Pause", command=self.stop_video, width=18)
        self.btn_stop.pack(pady=5)

        self.btn_next = tk.Button(self.controls_frame, text="Frame_→", command=self.show_next_frame, width=18)
        self.btn_next.pack(pady=5)


        # 跳转功能区域
        jump_controls_frame = tk.LabelFrame(self.controls_frame, text="Jump to Frame", bg="lightgray", padx=10, pady=10)
        jump_controls_frame.pack(pady=10, fill=tk.X)

        frame_controls = tk.Frame(jump_controls_frame, bg="lightgray")
        frame_controls.pack(pady=5)

        self.frame_input = tk.Entry(frame_controls, width=10, justify=tk.CENTER)
        self.frame_input.insert(0, str(self.nowFrame + 1))
        self.frame_input.pack(side=tk.LEFT, padx=5)

        self.total_frames_label = tk.Label(frame_controls, text=f"/ {self.total_frames}", bg="lightgray")
        self.total_frames_label.pack(side=tk.LEFT)

        self.btn_apply = tk.Button(jump_controls_frame, text="Applied", command=self.jump_to_frame, width=10)
        self.btn_apply.pack(side=tk.LEFT, padx=5)



        # 导出功能区域
        export_controls_frame = tk.LabelFrame(self.controls_frame, text="Export Video", bg="lightgray", padx=10, pady=10)
        export_controls_frame.pack(pady=15, fill=tk.X)


        self.export_start_frame = tk.Entry(export_controls_frame, width=15, justify=tk.CENTER)
        self.export_start_frame.insert(0, "Start Frame")
        self.export_start_frame.pack(pady=5)

        self.export_end_frame = tk.Entry(export_controls_frame, width=15, justify=tk.CENTER)
        self.export_end_frame.insert(0, "End Frame")
        self.export_end_frame.pack(pady=5)


        self.file_name = tk.Entry(export_controls_frame, width=10, justify=tk.CENTER)
        self.file_name.insert(0, str(self.item))
        self.file_name.pack(side=tk.LEFT, padx=5)

        self.file_type = tk.Label(export_controls_frame, text=f".mp4", bg="lightgray")
        self.file_type.pack(side=tk.LEFT)


        self.btn_export = tk.Button(self.controls_frame, text="Export Cropped", command=self.export_video, width=18)
        self.btn_export.pack(pady=5)

        self.video_frame = tk.Frame(self.master, bg = "white", padx=10, pady=10)
        self.video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 左侧视频
        tk.Label(self.video_frame, text="Original Video", bg="white", font=("Arial", 12, "bold")).pack(pady=5)
        self.left_canvas = tk.Canvas(self.video_frame, width=self.width, height=self.height, bg="black")
        self.left_canvas.bind("<ButtonPress-1>", self.start_box)
        self.left_canvas.bind("<B1-Motion>", self.update_box)
        self.left_canvas.bind("<ButtonRelease-1>", self.end_bbox)
        self.left_canvas.pack(pady=10)


        # 右侧视频
        tk.Label(self.video_frame, text="Cropped Area", bg="white", font=("Arial", 12, "bold")).pack(pady=5)
        self.right_canvas = tk.Canvas(self.video_frame, width=self.width, height=self.height,bg="black")
        self.right_canvas.pack(pady=10)

        self.show_frame()

    def start_box(self,event):
        self.stop_video()
        self.bbox_start = (event.x, event.y)

    def update_box(self,event):
        if self.bbox_start:
            x0, y0 = self.bbox_start
            x1, y1 = event.x, event.y
            self.bbox = (x0, y0, x1, y1)
            self.update_canvas()

    def end_bbox(self,event):
        # self.play_video()
        if self.bbox_start:
            x0, y0 = self.bbox_start
            x1, y1 = event.x, event.y
            self.bbox = (min(x0,x1), min(y0, y1), max(x0, x1), max(y0,y1))
            self.bbox_start = None

    def show_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # if self.nowFrame is None:
            #     self.nowFrame = 0

            self.original_frame = frame.copy()
            frame = cv2.resize(self.original_frame, (self.width, self.height)) # 将原图缩小

            self.left_img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.left_canvas.create_image(0,0,anchor=tk.NW, image=self.left_img)

            self.left_canvas.update_idletasks()
            # self.right_canvas.create_image(0, 0, anchor=tk.NW, image=self.left_img)

    def update_canvas(self):
        if self.original_frame is not None:
            frame = cv2.resize(self.original_frame, (self.width, self.height))
            print("Now Frame:", self.nowFrame)
            if self.bbox:
                x0, y0, x1, y1 = self.bbox
                cv2.rectangle(frame, (x0, y0), (x1, y1), (0,255,0), 2)

            self.left_img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.left_canvas.create_image(0, 0, anchor = tk.NW, image=self.left_img)
            self.left_canvas.update_idletasks()

    def update_cropped_canvas(self):
        if self.original_frame is not None and self.bbox:
            x0, y0, x1, y1 = self.bbox
            frame = cv2.resize(self.original_frame, (self.width, self.height))
            cropped = frame[y0:y1, x0:x1]
            h, w, c = cropped.shape
            h_scale = self.height/h
            w_scale = self.width/w
            if h_scale < w_scale:
                cropped = cv2.resize(cropped, (int(w * h_scale), self.height))
            else:
                cropped = cv2.resize(cropped, (self.width, int(h * w_scale)))
            print(cropped.shape)

            self.right_img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)))
            self.right_canvas.create_image(0,0, anchor=tk.NW, image=self.right_img)

    def update_frame(self):
        if self.cap.isOpened() and self.playing:
            ret, frame = self.cap.read()
            if ret:

                self.nowFrame += 1
                self.original_frame = frame.copy()
                self.update_canvas()
                self.update_cropped_canvas()
                self.update_frame_input()
            else:
                print(f"Failed to read frame at position {self.nowFrame}")
                self.stop_video()
                return
        self.timer = self.master.after(int(1000 // self.fps), self.update_frame)

    def jump_to_frame(self):
        try:
            frame_num = int(self.frame_input.get().strip()) - 1
            if 0<=frame_num<self.total_frames:
                self.stop_video()
                self.nowFrame = frame_num
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.nowFrame)

                ret, frame = self.cap.read()
                if ret:
                    self.original_frame = frame.copy()
                    self.update_canvas()
                    self.update_cropped_canvas()
                self.update_frame_input()

        except ValueError:
            print("Invalid Input. Please enter a valid frame number.")

    def update_frame_input(self):
        self.frame_input.delete(0, tk.END)
        self.frame_input.insert(0, str(self.nowFrame + 1))

    def show_prev_frame(self):
        self.stop_video()
        if self.cap.isOpened() and self.playing == False:
            if self.nowFrame == 0:
                pass
            elif self.nowFrame > 0:
                self.nowFrame -= 1
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.nowFrame)

                if not self.cap.grab():
                    print(f"Failed to grab frame {self.nowFrame}")
                    return

                ret, frame = self.cap.read()
                if ret:
                    self.original_frame = frame.copy()
                    self.update_canvas()
                    self.update_cropped_canvas()
                    self.update_frame_input()
                else:
                    print(f"Failed to read frame {self.nowFrame}")

    def show_next_frame(self):
        self.stop_video()
        if self.cap.isOpened() and self.playing == False:
            if self.nowFrame == self.total_frames-1:
                pass
            elif self.nowFrame < self.total_frames:
                self.nowFrame += 1
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.nowFrame)

                ret, frame = self.cap.read()
                if ret:
                    if self.nowFrame is not None:
                        self.original_frame = frame.copy()
                        self.update_canvas()
                        self.update_cropped_canvas()
                        self.update_frame_input()

    def play_video(self):
        if self.playing == False:
            self.playing = True
            self.update_frame()
        elif self.playing ==True:
            pass

    def stop_video(self):
        self.playing = False
        if self.timer:
            self.master.after_cancel(self.timer)
            self.timer = None

    def export_video(self):
        try:
            start_frame = int(self.export_start_frame.get().strip())
            end_frame = int(self.export_end_frame.get().strip())
            print(f"start_frame: {start_frame}   end_frame: {end_frame}")
        except ValueError:
            print("Invalid frame range input.")
            return

        if not (0 <= start_frame < end_frame <= self.total_frames):
            print("Frame range out of bounds.")
            return

        # with open("./item.txt", "r") as fp:
        #     item = int(fp.read())

        self.item = int(self.file_name.get().strip())

        x0, y0, x1, y1 = self.bbox
        x0 = int(self.f * x0)
        y0 = int(self.f * y0)
        x1 = int(self.f * x1)
        y1 = int(self.f * y1)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        cropped_writer = cv2.VideoWriter(f"./result/{self.item}.mp4",fourcc,self.fps,(int(x1-x0), int(y1-y0)))

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        for fn in range(start_frame, end_frame):
            ret, frame = self.cap.read()
            if not ret:
                print(f"Failed to read frame {fn}")
                break

            if self.bbox:
                x0, y0, x1, y1 = self.bbox
                x0 = int(self.f * x0)
                y0 = int(self.f * y0)
                x1 = int(self.f * x1)
                y1 = int(self.f * y1)
                print(f"x0, y0, x1, y1: {x0, y0, x1, y1}")
                cropped_frame = frame[y0:y1, x0:x1]
                cropped_frame = cv2.resize(cropped_frame, (int(x1-x0), int(y1-y0)))
                cropped_writer.write(cropped_frame)

        cropped_writer.release()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.nowFrame)

        self.item += 1
        self.file_name.delete(0, tk.END)
        self.file_name.insert(0, str(self.item))

        # item += 1
        # with open("./item.txt", "w") as fp:
        #     fp.write(str(item))

    def run(self):
        self.master.mainloop()

if __name__=="__main__":
    root = tk.Tk()
    video_path = "./data/testing.mp4"
    player = VideoPlayer(root, video_path)
    player.run()