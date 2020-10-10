import tkinter as tk
from tkinter import filedialog
import pygame.mixer as mixer
import os
from tkinter import messagebox as msg
from mutagen.mp3 import MP3
import mysql.connector
class music(tk.Tk):
    def __init__(self):
        super().__init__()
        self.url=''
        self.position=0
        self.var,self.fast=0,0
        self.loc=''
        self.pause_var,self.mute_var=True,False
        self.previous_vol=0.0
        self.music_list=[]
        self.click=1
        # If database is not created, create a db named as 'music_player manually'

        self.mydb=mysql.connector.connect(user='root',password='Harshitraj12',host='localhost',auth_plugin='mysql_native_password',database='music_player')

        self.cur=self.mydb.cursor()

        # For checking table is created or not
        query='SHOW TABLES LIKE "songs"'
        self.cur.execute(query)
        result=self.cur.fetchone()
        if not result:
            query='CREATE TABLE songs(fav_songs VARCHAR(500),url VARCHAR(1000))'
            self.cur.execute(query)
            self.mydb.commit()

        

        self.geometry('700x600+300+50')
        self.title("Music Player by Python")
        self.wm_iconbitmap("icons\\main_icon.ico")  # Main icon of Music Player
        self.configure(bg='pale green')
        self.resizable(0,0)
        play_icon=tk.PhotoImage(file='icons\\load-music.png')
        self.pause_icon=tk.PhotoImage(file='icons\\pause.png')
        self.unpause_icon=tk.PhotoImage(file='icons\\play.png')
        stop_icon=tk.PhotoImage(file='icons\\stop.png')
        self.mute_icon=tk.PhotoImage(file='icons\\mute.png')
        self.unmute_icon=tk.PhotoImage(file='icons\\unmute.png')
        refresh_icon=tk.PhotoImage(file='icons\\refresh.png')

        fast_forward_icon=tk.PhotoImage(file='icons\\fast_forward.png')
        frame=tk.Frame(bg='skyblue')
        frame.pack(pady=20)
        tk.Label(frame,text='Total Duration',font='arial 12 bold',bg='skyblue').grid(row=0,column=0,pady=20)
        self.time_label=tk.Label(frame,font='arial 12 bold',bg='skyblue')
        self.time_label.grid(row=0,column=2)
        self.play_button=tk.Button(frame,image=play_icon,command=self.play)
        self.play_button.image=play_icon
        self.play_button.grid(row=2,column=0)
        self.pause_button=tk.Button(frame,image=self.pause_icon,command=self.pause)
        self.pause_button.image=self.pause_icon
        self.pause_button.grid(row=2,column=1)
        self.stop_button=tk.Button(frame,image=stop_icon,command=self.stop)
        self.stop_button.image=stop_icon
        self.stop_button.grid(row=2,column=2,padx=20)
        self.fast_forward_button=tk.Button(frame,image=fast_forward_icon,command=self.fast_forward)
        self.fast_forward_button.image=fast_forward_icon
        self.fast_forward_button.grid(row=2,column=3,padx=10)
        self.mute_button=tk.Button(frame,image=self.mute_icon,command=self.mute)
        self.mute_button.image=self.mute_icon
        self.mute_button.grid(row=2,column=4,padx=20)
        self.slider=tk.Scale(frame,from_=0,to=100,tickinterval=25,length=160,label='Volume',font='arial 10 bold',bg='violet')
        self.slider.grid(row=2,column=6)
        self.slider.bind('<ButtonRelease-1>',self.update_volume)
        self.list=tk.Listbox(font='arial 10 bold',width=50,bg='pink')
        self.list.pack(side='bottom',anchor='nw')
        tk.Button(text="Add Song",font='arial 12 bold',command=self.add).pack(side='left',anchor='se',pady=15)
        self.delete_button=tk.Button(text="Delete Song",font='arial 12 bold',command=self.delete)
        self.delete_button.pack(side='left',anchor='se',padx=20,pady=15)
        self.refresh_button=tk.Button(text='Refresh Playlist',image=refresh_icon,compound=tk.LEFT,font='arial 12 bold',command=self.refresh)
        self.refresh_button.pack(side='left',anchor='se',padx=10,pady=15)
        self.refresh_button.image=refresh_icon
        self.stop_button.configure(state='disabled')
        self.pause_button.configure(state='disabled')
        self.fast_forward_button.configure(state='disabled')
        self.mute_button.configure(state='disabled')
        self.slider.set(90)
        self.slider.configure(state='disabled')
        self.refresh_button.configure(state='disabled')
        self.hover()
        query='SELECT fav_songs FROM songs'
        self.cur.execute(query)
        self.result=self.cur.fetchall()
        if self.result:
            for i in self.result:
                i=''.join(i)
                self.list.insert(tk.END,i)
        

    def add(self):
        self.url=filedialog.askopenfilename(initialdir=os.getcwd(),title="Select file",filetypes=(("Mp3 Files","*.mp3"),))
        if self.url=='':
            pass
        else:
            self.base=os.path.basename(self.url)
            if self.click==1:
                file_url=[i[0] for i in self.result]
                self.click+=1
            else:
                query='SELECT fav_songs FROM songs'
                self.cur.execute(query)
                self.result=self.cur.fetchall()
                file_url=[i[0] for i in self.result]

            if self.base not in file_url:
                self.play_button.configure(state='normal')
                self.delete_button.configure(state='normal')
                query='INSERT INTO songs(fav_songs,url) VALUES (%s,%s)'
                self.cur.execute(query,(self.base,self.url))
                self.mydb.commit()
                self.refresh_button.configure(state='normal')

    def delete(self):
        try:
            if len(self.list.get(0,tk.END))!=0:
                sel=self.list.curselection()
                sel_val=self.list.get(self.list.curselection())
                self.list.delete(sel)
                query='DELETE FROM songs WHERE fav_songs = (%s)'
                self.cur.execute(query,(sel_val,))
                self.mydb.commit()
                self.music_list.append(sel_val)
                if len(self.music_list)!=0:
                    for i in self.music_list:
                        self.music_list.remove(i)
            else:
                msg.showwarning('Empty List','There is no item to delete')
        except Exception as err:
            msg.showerror('Not Selected','First, Select the music')

    def refresh(self):
        if len(self.list.get(0,tk.END))==0:
            query='SELECT fav_songs FROM songs'
            self.cur.execute(query)
            self.result=self.cur.fetchall()
            if self.result:
                for i in self.result:
                    i=''.join(i)
                    self.list.insert(tk.END,i)
        else:
            self.list.insert(tk.END,self.base)
        self.refresh_button.configure(state='disabled')
        
            
    def play(self):
        try:
            self.pause_button.configure(state='normal')
            self.slider.configure(state='normal')
            self.stop_button.configure(state='normal')
            self.fast_forward_button.configure(state='normal')
            self.mute_button.configure(state='normal')
            name=self.list.get(self.list.curselection())
            query = 'SELECT * FROM songs'
            self.cur.execute(query)
            result=self.cur.fetchall()
            if result:
                for music,url in result:
                    if music == name:
                        self.loc=url
            mixer.init()
            if mixer.music.get_busy()==False:
                self.var=0
            
            mixer.music.load(self.loc)
            mixer.music.play(0,self.var)
            song=MP3(self.loc)
            self.time_label.configure(text=f'{round(song.info.length/60,2)} min')
            
        except Exception as err:
            msg.showerror('Not Selected','First, Select the music')

    def pause(self): 
        try:   
            if self.pause_var==True:
                mixer.music.pause()
                self.pause_var=False
                self.pause_button.configure(image=self.unpause_icon)
                self.pause_button.image=self.unpause_icon

            else:
                mixer.music.unpause()
                self.pause_var=True
                self.pause_button.configure(image=self.pause_icon)
        except Exception as err:
            pass

    def stop(self):
        try:
            if mixer.music.get_busy()==True:
                mixer.music.stop()
                self.pause_button.configure(image=self.pause_icon)
                self.pause_button.configure(state='disabled')
                self.fast_forward_button.configure(state='disabled')
                self.stop_button.configure(state='disabled')
                self.slider.configure(state='disabled')
                self.mute_button.configure(state='disabled')
        except Exception as err:
            pass
         
    def fast_forward(self):
        try:
            if mixer.music.get_busy()==True:
                self.position=mixer.music.get_pos()/1000
                self.fast=self.position+0.000000000001
                mixer.music.play(0,self.fast)
        except Exception as err:
            pass
        
    def update_volume(self,event=None):
        try:
            if mixer.music.get_busy()==True:
                value=self.slider.get()
                value=round(value/100,2)
                mixer.music.set_volume(value)
        except Exception as err:
            pass


    def mute(self):
        try:
            if mixer.music.get_busy()==True:
                if self.mute_var==False:
                    self.previous_vol=self.slider.get()
                    self.slider.configure(state='disabled')
                    mixer.music.set_volume(0.0)
                    self.mute_var=True
                    self.mute_button.configure(image=self.unmute_icon)
                    self.mute_button.image=self.unmute_icon
                else:
                    self.mute_button.configure(image=self.mute_icon)
                    self.previous_vol=round(self.previous_vol/100,2)
                    mixer.music.set_volume(self.previous_vol)
                    self.slider.configure(state='normal')
                    self.mute_var=False
        except Exception as err:
            pass
    def hover(self):
        def play_events(event=None):
            '''Function to display bold hovering effect when mouse enters bold button'''
            self.child=tk.Toplevel()
            self.child.overrideredirect(1)  # Removes title bar of Toplevel window
            self.child.geometry("100x50+400+330")
            self.child.configure(bg="orange")
            label=tk.Label(self.child,text="Load and\nPlay Music",bg="orange",font="arial 10 bold")
            label.pack(pady=5)
            def destroy_at_2sec():
                '''Function for destroying child bold hover window after 2 seconds'''
                self.child.destroy()  # destroy Toplevel window at <Leave> event
            self.child.after(2000,destroy_at_2sec)

        def play_destroy(event=None):
            '''Function for destroying child bold hover window when mouse leave bold button'''
            self.child.destroy()

        # Binding bold_button for hovering effect
        self.play_button.bind("<Enter>",play_events)  # Activate when mouse enter the widget
        self.play_button.bind("<Leave>",play_destroy) # Activate when mouse leave the widget


        def pause_events(event=None):
            '''Function to display bold hovering effect when mouse enters bold button'''
            self.child=tk.Toplevel()
            self.child.overrideredirect(1)  # Removes title bar of Toplevel window
            self.child.geometry("100x50+470+330")
            self.child.configure(bg="orange")
            label=tk.Label(self.child,text="Pause and\nPlay Music",bg="orange",font="arial 10 bold")
            label.pack(pady=5)
            def destroy_at_2sec():
                '''Function for destroying child bold hover window after 2 seconds'''
                self.child.destroy()  # destroy Toplevel window at <Leave> event
            self.child.after(2000,destroy_at_2sec)

        def pause_destroy(event=None):
            '''Function for destroying child bold hover window when mouse leave bold button'''
            self.child.destroy()

        # Binding bold_button for hovering effect
        self.pause_button.bind("<Enter>",pause_events)  # Activate when mouse enter the widget
        self.pause_button.bind("<Leave>",pause_destroy) # Activate when mouse leave the widget



        def stop_events(event=None):
            '''Function to display bold hovering effect when mouse enters bold button'''
            self.child=tk.Toplevel()
            self.child.overrideredirect(1)  # Removes title bar of Toplevel window
            self.child.geometry("100x50+550+330")
            self.child.configure(bg="orange")
            label=tk.Label(self.child,text="Stop the Music",bg="orange",font="arial 10 bold")
            label.pack(pady=5)
            def destroy_at_2sec():
                '''Function for destroying child bold hover window after 2 seconds'''
                self.child.destroy()  # destroy Toplevel window at <Leave> event
            self.child.after(2000,destroy_at_2sec)

        def stop_destroy(event=None):
            '''Function for destroying child bold hover window when mouse leave bold button'''
            self.child.destroy()

        # Binding bold_button for hovering effect
        self.stop_button.bind("<Enter>",stop_events)  # Activate when mouse enter the widget
        self.stop_button.bind("<Leave>",stop_destroy) # Activate when mouse leave the widget


        def fast_forward_events(event=None):
            '''Function to display bold hovering effect when mouse enters bold button'''
            self.child=tk.Toplevel()
            self.child.overrideredirect(1)  # Removes title bar of Toplevel window
            self.child.geometry("100x50+650+330")
            self.child.configure(bg="orange")
            label=tk.Label(self.child,text="Fast Forward\nMusic",bg="orange",font="arial 10 bold")
            label.pack(pady=5)
            def destroy_at_2sec():
                '''Function for destroying child bold hover window after 2 seconds'''
                self.child.destroy()  # destroy Toplevel window at <Leave> event
            self.child.after(2000,destroy_at_2sec)

        def fast_forward_destroy(event=None):
            '''Function for destroying child bold hover window when mouse leave bold button'''
            self.child.destroy()

        # Binding bold_button for hovering effect
        self.fast_forward_button.bind("<Enter>",fast_forward_events)  # Activate when mouse enter the widget
        self.fast_forward_button.bind("<Leave>",fast_forward_destroy) # Activate when mouse leave the widget

        def list_events(event=None):
            '''Function to display bold hovering effect when mouse enters bold button'''
            self.child=tk.Toplevel()
            self.child.overrideredirect(1)  # Removes title bar of Toplevel window
            self.child.geometry("120x50+600+530")
            self.child.configure(bg="orange")
            label=tk.Label(self.child,text="Playlist Area",bg="orange",font="arial 10 bold")
            label.pack(pady=5)
            def destroy_at_2sec():
                '''Function for destroying child bold hover window after 2 seconds'''
                self.child.destroy()  # destroy Toplevel window at <Leave> event
            self.child.after(2000,destroy_at_2sec)

        def list_destroy(event=None):
            '''Function for destroying child bold hover window when mouse leave bold button'''
            self.child.destroy()

        # Binding bold_button for hovering effect
        self.list.bind("<Enter>",list_events)  # Activate when mouse enter the widget
        self.list.bind("<Leave>",list_destroy) # Activate when mouse leave the widget

        def mute_events(event=None):
            '''Function to display bold hovering effect when mouse enters bold button'''
            self.child=tk.Toplevel()
            self.child.overrideredirect(1)  # Removes title bar of Toplevel window
            self.child.geometry("100x50+700+330")
            self.child.configure(bg="orange")
            label=tk.Label(self.child,text="Mute/ Unmute",bg="orange",font="arial 10 bold")
            label.pack(pady=5)
            def destroy_at_2sec():
                '''Function for destroying child bold hover window after 2 seconds'''
                self.child.destroy()  # destroy Toplevel window at <Leave> event
            self.child.after(2000,destroy_at_2sec)

        def mute_destroy(event=None):
            '''Function for destroying child bold hover window when mouse leave bold button'''
            self.child.destroy()

        # Binding bold_button for hovering effect
        self.mute_button.bind("<Enter>",mute_events)  # Activate when mouse enter the widget
        self.mute_button.bind("<Leave>",mute_destroy) # Activate when mouse leave the widget


if __name__ == "__main__":
    obj=music()
    obj.mainloop()