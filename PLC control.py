from PIL import Image,ImageTk
import customtkinter as ctk
from tkinter import messagebox
import snap7
from snap7.client import Client
from snap7.type import Areas
from snap7.util import *
import logging
import threading
import time
#------------------- Window Login ------------------------#
connectapp = ctk.CTk(fg_color="#ffffff")
connectapp.title("Connect To PLC")
connectapp.geometry("400x500")
connectapp.resizable(False, False)
connectapp.iconbitmap("C:/Users/mehdi/Desktop/images/service.ico")

#------------------- Center Window Function ------------------------#
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

center_window(connectapp)

#------------------- Login Frame ------------------------#
frame = ctk.CTkFrame(master=connectapp, width=300, height=300, corner_radius=15)
frame.place(x=200, y=300, anchor=ctk.CENTER)
frame.pack_propagate(False)

ctk.CTkLabel(frame, text="Enter IP address", text_color="black").place(x=25, y=50)
IP_entry = ctk.CTkEntry(frame, width=100, placeholder_text="IP address")
IP_entry.place(x=150, y=50)

ctk.CTkLabel(frame, text="Enter Slot", text_color="black").place(x=25, y=100)
Slot_entry = ctk.CTkEntry(frame, width=100, placeholder_text="Slot")
Slot_entry.place(x=150, y=100)

ctk.CTkLabel(frame, text="Enter Rack", text_color="black").place(x=25, y=150)
Rack_entry = ctk.CTkEntry(frame, width=100, placeholder_text="Rack")
Rack_entry.place(x=150, y=150)

#----------------- Function connect to plc -------------------------------------------#
def connect_to_plc():
    ip = IP_entry.get()
    try:
        rack = int(Rack_entry.get())
        slot = int(Slot_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Slot and Rack must be numbers.")
        return
    client = snap7.client.Client()
    try:
        client.connect(ip, rack, slot)
        if client.get_connected():
            messagebox.showinfo("Success", f"Connected to PLC at {ip}")
            status = client.get_cpu_state()
            messagebox.showinfo("PLC Status:", status)
        else:
            messagebox.showerror("Failed", "Connection failed.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to PLC:\n{e}")
        return

    #------------------- Control Window ------------------------#
    app = ctk.CTkToplevel(fg_color="#ffffff")
    app.iconbitmap("service.ico")
    app.title("Industrial Fault Management And Control Platform IFMCP")
    app.geometry("850x550")
    app.resizable(False, False)
    
    center_window(app)

    #------------------ Image ------------------#
    app_image = Image.open("C:/Users/mehdi/Desktop/images/Gemini_Generated_Image_tnt61dtnt61dtnt6.png")
    app_photo = ctk.CTkImage(dark_image=app_image, size=(300, 300))
    image_label = ctk.CTkLabel(app, image=app_photo, text="")
    image_label.pack(pady=50, anchor="center")

    connectapp.withdraw()
   
    def on_main_window_close():
        app.destroy()
        connectapp.destroy()
    app.protocol("WM_DELETE_WINDOW", on_main_window_close)
    
    #------------------- Function Buttons ----------------------------------------#
    def timer_plc():
        timer=ctk.CTkToplevel()
        timer.title("Timer PLC")
        timer.geometry("850x500")
        timer.resizable(False,True)
        timer.focus_force()
        timer.grab_set()
        

        #------------------- Function scannetime -----------------------------------------------#
        def scannetime():
            logging.getLogger("snap7").setLevel(logging.CRITICAL)
            found_dbs=[]
            label_refs = {}
            
            for db_number in range(1,256):
                try:
                    db_data = client.db_read(db_number, 0, 1)
                    if db_data :
                        found_dbs.append(db_number)
                except RuntimeError:
                    continue
            
            def get_db_size():
                try:
                    max_attempt=512
                    for size in range(2, max_attempt + 1, 2):
                        try:
                            client.read_area(Areas.DB, db_number, 0, size)
                        except Exception as e:
                            if b'Address out of range' in str(e).encode():
                                return size - 2
                            elif b'invalid param' in str(e).encode():
                                return None
                    return max_attempt
                except Exception as e:
                    messagebox.showerror("⚠️ Read Error", f"An error occurred: {e}")
                    return None
            size_db=[]
            for i in range(0,len(found_dbs)):
                db_number=found_dbs[i]
                db_size = get_db_size()
                size_db.append(db_size)
            timer_db=[]
            for k in range(0,len(size_db)):
                if size_db[k]==16:
                    timer_db.append(found_dbs[k])
            
            for i, db_number in enumerate(timer_db):
                labeltimer = ctk.CTkLabel(timer, text=f"Timer {db_number}:\nPT: -- ms\nET: -- ms")
                labeltimer.place(x=50, y=80 + i * 60)
                label_refs[db_number] = labeltimer
                def make_pv_editor(dbn1, j):
                    def open_entry1():
                        pt_entry = ctk.CTkEntry(timer, placeholder_text="Enter PT")
                        pt_entry.place(x=400, y=80 + j * 80)
                        set_pt_btn.place_forget()

                        def ms_to_s5time(ms):
                            time_bases = [(10, 0b00), (100, 0b01), (1000, 0b10), (10000, 0b11)]
                            for base, code in time_bases:
                                value = ms // base
                                if 0 <= value <= 999:
                                    s5_value = (code << 12) | value
                                    return s5_value.to_bytes(2, byteorder='big')
                            raise ValueError("Time out of range for S5Time (max 9990 seconds)")
                            

                        def apply_new_pt():
                            try:
                                val1 = int(pt_entry.get())
                                pt_bytes = val1.to_bytes(4, byteorder='big', signed=True)
                                #pt_bytes = ms_to_s5time(val1)
                                client.write_area(Areas.DB, dbn1, 4, pt_bytes)
                                messagebox.showinfo("✅ Success", f"PT of Timer {dbn1} set to {val1} ms.")
                            except Exception as e:
                                messagebox.showerror("❌ Error", f"Failed to Set PT  Timer {dbn1}:\n{e}")
                        apply_btn1 = ctk.CTkButton(timer, text="Apply", command=apply_new_pt)
                        apply_btn1.place(x=500, y=80 + j * 80)
                    return open_entry1
                set_pt_btn = ctk.CTkButton(timer, text="Set PT", command=make_pv_editor(db_number, i))
                set_pt_btn.place(x=400, y=80 + i * 80)
                
            def up_timers():
                for db_number in timer_db:
                    try:
                        data = client.read_area(Areas.DB, db_number, 0, 16)
                        pt = get_time(data, 4)
                        et = get_time(data, 8)
                        #print(f" Timer {found_dbs[k]} PT",pt)
                        #print(f" Timer {found_dbs[k]} ET",et)
                        labeltimer = label_refs[db_number]
                        labeltimer.configure(text=f"Timer {db_number}:\nPT: {pt} ms\nET: {et} ms")
                    except Exception as e:
                        label_refs[db_number].configure(text=f"❌ Error in Timer {db_number}")
                timer.after(100, up_timers)
            up_timers()
                
                
               
        center_window(timer)          
        Scanne_Btn_Time=ctk.CTkButton(timer,text='Scan for Found Timer DBs',command=scannetime)
        Scanne_Btn_Time.place(x=150,y=50)
        
        
        
    #/**************** Counter PLC*****************************/
    
    def counter_plc():
        counter=ctk.CTkToplevel(fg_color="#ffffff")
        counter.title("Counter PLC")
        counter.geometry("850x450")
        counter.resizable(False,True)
        counter.focus_force()
        counter.grab_set()

        def scannecounter():
            logging.getLogger("snap7").setLevel(logging.CRITICAL)
            found_dbs1=[]
            label_refs1={}
            reset_btn_refs = {}

            for db_number1 in range(1,256):
                try:
                    db_data1=client.db_read(db_number1, 0, 1)
                    if db_data1:
                        found_dbs1.append(db_number1)
                except RuntimeError:
                    continue

            def get_db_size1():
                try:
                    max_attempt1=512
                    for size1 in range(2, max_attempt1 + 1, 2):
                        try:
                            client.read_area(Areas.DB, db_number1, 0, size1)
                        except Exception as e:
                            if b'Address out of range' in str(e).encode():
                                return size1 - 2
                            elif b'invalid param' in str(e).encode():
                                return None
                    return max_attempt1
                except Exception as e:
                    messagebox.showerror("⚠️ Read Error", f"An error occurred: {e}")
                    return None
            size_db1=[]
            for k in range(0,len(found_dbs1)):
                db_number1 = found_dbs1[k]
                db_size1=get_db_size1()
                size_db1.append(db_size1)

            counter_db = []
            for m in range(0,len(size_db1)):
                if size_db1[m] == 6:
                    counter_db.append(found_dbs1[m])
            
            for t, db_number1 in enumerate(counter_db):
                labelcounter = ctk.CTkLabel(counter, text=f"Counter {db_number1}:\nCV: -- Number\nPV: -- Number")
                labelcounter.place(x = 50, y = 80 + t*60)
                label_refs1[db_number1]=labelcounter
                
                def make_reset_func(dbn):
                    def reset_counter():
                        try:
                            zero_bytes = (0).to_bytes(2, byteorder='big')
                            client.write_area(Areas.DB, dbn, 4, zero_bytes)
                            messagebox.showinfo("Reset Done", f"Counter {dbn} has been reset.")
                        except Exception as e:
                            messagebox.showerror("⚠️ Reset Error", f"An error occurred while resetting counter {dbn}:\n{e}")
                    return reset_counter
                reset_btn = ctk.CTkButton(counter, text="Reset", command=make_reset_func(db_number1))
                reset_btn.place(x=250, y=80 + t * 60)
                reset_btn_refs[db_number1] = reset_btn

                def make_pv_editor(dbn, t):
                    def open_entry():
                        
                        pv_entry = ctk.CTkEntry(counter, placeholder_text="Enter PV")
                        pv_entry.place(x=400, y=80 + t * 80)
                        set_pv_btn.place_forget()

                        def apply_new_pv():
                            try:
                                val = int(pv_entry.get())
                                pv_bytes = val.to_bytes(2, byteorder='big', signed=True)
                                client.write_area(Areas.DB, dbn, 2, pv_bytes)
                                messagebox.showinfo("✅ Success", f"PV of Counter {dbn} set to {val}.")
                            except Exception as e:
                                messagebox.showerror("❌ Error", f"Failed to set PV for Counter {dbn}:\n{e}")
                        apply_btn = ctk.CTkButton(counter, text="Apply", command=apply_new_pv)
                        apply_btn.place(x=500, y=80 + t * 80)
                    return open_entry
                set_pv_btn = ctk.CTkButton(counter, text="Set PV", command=make_pv_editor(db_number1, t))
                set_pv_btn.place(x=400, y=80 + t * 80)
    
            def up_counters():
                for db_number1 in counter_db:
                    try:
                        data1 = client.read_area(Areas.DB, db_number1, 0, 6)
                        cv = get_int(data1, 4)
                        pv = get_int(data1, 2)
                        labelcounter = label_refs1[db_number1]
                        labelcounter.configure(text=f"Counter {db_number1}:\nCV: {cv} Number\nPV: {pv} Number")
                    except Exception as e:
                        label_refs1[db_number1].configure(text=f"❌ Error in Counter {db_number1}")
                
                counter.after(100, up_counters)
            up_counters()
                        
        center_window(counter)
        
        Scanne_Btn_Counter = ctk.CTkButton(counter, text='Scan for Found Counter DBs', command=scannecounter)
        Scanne_Btn_Counter.place(x=200,y=50)

        #--------------------------------- Controle Panel --------------------------------------------------------------------#

    def controlePanel():
        controle=ctk.CTkToplevel()
        controle.geometry("850x600")
        controle.title("Controle Panel")
        controle.resizable(False,True)
        controle.focus_force()
        controle.grab_set()
        
        frame_outputs = ctk.CTkFrame(controle,fg_color="#ffffff")
        frame_inputs = ctk.CTkFrame(controle,fg_color="#ffffff")
        
        output=ctk.CTkLabel(frame_outputs,text="Output Digital",text_color="white")
        output.place(x=60)
        
        output=ctk.CTkLabel(frame_outputs,text="Output Digital",text_color="black")
        output.place(x=60)
        
        entry_bool = ctk.CTkEntry(controle, width=250, placeholder_text="Input Bool")
        entry_bool.place(x=150, y=50)
        
        entry_int = ctk.CTkEntry(controle, width=250, placeholder_text="Input Real")
        entry_int.place(x=150, y=100)

        entry_int_add = ctk.CTkEntry(controle, width=100, placeholder_text="Input Addresse")
        entry_int_add.place(x=450, y=100)

        out_bool = ctk.CTkEntry(controle, width=250, placeholder_text="Output Bool")
        out_bool.place(x=150, y=150)

        out_int = ctk.CTkEntry(controle, width=250, placeholder_text="Output Real")
        out_int.place(x=150, y=200)

        out_int_add = ctk.CTkEntry(controle, width=100, placeholder_text="Output Addresse")
        out_int_add.place(x=450, y=200)
            
        
        def toggle_output(index):
           try:
               byte=index // 8
               bit = index % 8
               byte_len1 = (num_outputs + 7) // 8
               data = client.read_area(Areas.PA, 0, 0, byte_len1)#byte
               current = get_bool(data, byte, bit)
               set_bool(data, byte, bit, not current)
               client.write_area(Areas.PA, 0, 0, data)
           except Exception as e:
               messagebox.showerror("Write Error", f"Failed to toggle Q{index}: {e}")
        
        def update_output_status():
            try:
                byte_len = (num_outputs + 7) // 8
                data = client.read_area(Areas.PA, 0, 0, byte_len)
                for i, widget in enumerate(frame_outputs.winfo_children()):
                    if isinstance(widget, ctk.CTkButton):
                        state = get_bool(data, i // 8, i % 8)
                        widget.configure(text=f"Q{i}: {'ON' if state else 'OFF'}", fg_color=("green" if state else "red"))
            except:
                pass
            controle.after(1000, update_output_status)
        
        def show_output_buttons():
            for widget in frame_outputs.winfo_children():
                widget.destroy()
            for i in range(num_outputs):
                btn = ctk.CTkButton(frame_outputs, text=f"Q{i}: OFF", command=lambda i=i: toggle_output(i))
                btn.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            update_output_status()
        
        label_refs_analog={}
        label_refs_analog1={}
        
        def controlee():
            nonlocal label_refs_analog
            nonlocal label_refs_analog1
            nonlocal num_outputs
            try:
                entbool = int(entry_bool.get())
                entint = int(entry_int.get())
                outbool = int(out_bool.get())
                outint = int(out_int.get())
                #if outbool <= 0:
                    #raise ValueError
                num_outputs = outbool
                num_inputs = entbool
                entry_bool.place_forget()
                entry_int.place_forget()
                out_bool.place_forget()
                out_int.place_forget()
                entry_int_add.place_forget()
                out_int_add.place_forget()
                button_create.place_forget()
                frame_outputs.pack(pady=20)
                show_output_buttons()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number greater than 0")
            #----------------- Read from Input Analog ---------------------------------------------------#

            outanalogadd=int(out_int_add.get())
            inpanalogadd=int(entry_int_add.get())

            for t in range(outint):
                labelanalog = ctk.CTkLabel(controle, text=f"Output Analog QW{t}: --")
                labelanaloginput = ctk.CTkLabel(controle, text=f"Input Analog IW{t}: --")
                labelanalog.place(x=50 + 250*t, y=150)
                labelanaloginput.place(x=50 + 250*t, y=250)
                label_refs_analog[t] = labelanalog
                label_refs_analog1[t] = labelanaloginput
            
            def up_out_analog():
                for l in range(outint):
                    try:
                        start_add=outanalogadd+l
                        start_add1=start_add+1
                        dataoutanalog=client.read_area(Areas.PA, 0, start_add, 2)
                        datainputanalog=client.read_area(Areas.PE, 0, start_add1, 2)
                        valuer_analog_out=get_int(dataoutanalog,0)
                        valuer_analog_input=get_int(datainputanalog,0)
                        voltage = (valuer_analog_out / 27648.0) * 10.0
                        labelanalog = label_refs_analog[l]
                        labelanalog.configure(text=f"Output Analog QW {start_add}:{valuer_analog_out}\nVoltage:{voltage:.2f} V")
                        labelanaloginput.configure(text=f"Input Analog IW {start_add}:{valuer_analog_input}")
                    except Exception as e:
                        label_refs_analog[l].configure(text=f"❌ Error in Reading {start_add}")
                        label_refs_analog1[l].configure(text=f"❌ Error in Reading {start_add}")

                controle.after(100, up_out_analog)
            up_out_analog()
            
            #entbool = int(entry_bool.get())
            
            labelentbool = []
            def toggle_input():
                try:
                    entbool = int(entry_bool.get())
                    num_byte_entry = (entbool + 7) // 8
                    da=client.read_area(Areas['PE'], 0, 0, num_byte_entry)
                    
                    if len(labelentbool) != entbool:
                        for labell in labelentbool:
                            labell.destroy()
                        labelentbool.clear()
                    for i in range(entbool):
                        lbl = ctk.CTkLabel(controle, text=f"I{i}:")
                        lbl.place(x=10, y=500 + i * 30)
                        labelentbool.append(lbl)
                    for i in range(entbool):
                        statee=get_bool(da, i // 8, i % 8)
                        labelentbool[i].configure(text=f"I{i}: {statee}")
                except Exception as e:
                    labelentbool.configure(text=f"Error Reading")
                controle.after(500, toggle_input)
            toggle_input()
                        
                
                        
                

            

            
                
        
        button_create = ctk.CTkButton(controle, text='Go', command=controlee)
        button_create.place(x=150, y=250)

        num_outputs = 0
        center_window(controle)
    #--------------------------------------- DATA BLOCK ----------------------------------------------#
    def db_block():
        db_block=ctk.CTkToplevel()
        db_block.geometry("850x550")
        db_block.title("Data Block")
        db_block.resizable(True,True)
        db_block.focus_force()
        db_block.grab_set()

        def Read():
            logging.getLogger("snap7").setLevel(logging.CRITICAL)
            import re
            with open('C:/Users/mehdi/Desktop/mk/Data_block_1.db', 'r', encoding='utf-8') as file:
                content = file.read()
            variables = re.findall(r'\b(\w+)\s*:\s*(\w+);', content)
            bool_vars = [name for name, typ in variables if typ.lower() == "bool"]
            int_vars = [(name, i) for i, (name, typ) in enumerate(variables) if typ.lower() == "int"]
            
            
            target_db = None
            def read_bit_from_db(db_num, byte_index, bit_index):
                data = client.db_read(db_num, byte_index, 1)
                return get_bool(data, 0, bit_index)
            def write_bit_to_db(db_num, byte_index, bit_index, value):
                data = client.db_read(db_num, byte_index, 1)
                set_bool(data, 0, bit_index, value)
                client.db_write(db_num, byte_index, data)
            
            def read_int_from_db(db_num, byte_index):
                data = client.db_read(db_num, byte_index, 2)
                return get_int(data, 0)
            def write_int_to_db(db_num, byte_index, value):
                data = bytearray(2)
                set_int(data, 0, value)
                client.db_write(db_num, byte_index, data)
            
            def get_db_size(db_num):
                for size in range(2, 512, 2):
                    try:
                        client.read_area(Areas.DB, db_num, 0, size)
                    except Exception as e:
                        if b'Address out of range' in str(e).encode():
                            return size - 2
                        elif b'invalid param' in str(e).encode():
                            return None
                return 512
            
            target_db = None
            for dbn in range(1, 256):
                try:
                    client.db_read(dbn, 0, 1)
                    size = get_db_size(dbn)
                    if size == 4:  # 2 Bytes لـ Bools + 2 Bytes لـ Int
                        target_db = dbn
                        break
                except:
                    continue
            if target_db is None:
                raise Exception("لم يتم العثور على DB بالحجم المطلوب.")
            y = 200
            for i, var_name in enumerate(bool_vars):
                byte_index = i // 8
                bit_index = i % 8
                current_val = read_bit_from_db(target_db, byte_index, bit_index)
                btn_var = ctk.StringVar(value=str(current_val))
                
                def toggle(name=var_name, b_index=byte_index, bit_idx=bit_index, var=btn_var):
                    new_val = not read_bit_from_db(target_db, b_index, bit_idx)
                    write_bit_to_db(target_db, b_index, bit_idx, new_val)
                    var.set(str(new_val))
                
                ctk.CTkLabel(db_block, text=var_name).place(x=250, y=y)
                ctk.CTkButton(db_block, textvariable=btn_var, command=toggle).place(x=350, y=y)
                y += 40
            
            for name ,idx in int_vars:
                byte_index = 2  # Int بعد الـ Bool (التي حجمها 2 Bytes)
                val = read_int_from_db(target_db, byte_index)
                entry_var = ctk.StringVar(value=str(val))
                
                def write_int(var=entry_var, b_index=byte_index):
                    try:
                        new_val = int(var.get())
                        write_int_to_db(target_db, b_index, new_val)
                    except ValueError:
                        pass
                
                ctk.CTkLabel(db_block, text=name).place(x=250, y=y)
                ctk.CTkEntry(db_block, textvariable=entry_var, width=100).place(x=350, y=y)
                ctk.CTkButton(db_block, text="Write", command=write_int).place(x=460, y=y)
                y += 40
        
        read_button=ctk.CTkButton(db_block,text="Read",command=Read)
        read_button.place(x=350, y=150)
        
    #------------------ Topbar Buttons ------------------#
    topbar = ctk.CTkFrame(app, height=250, corner_radius=0, fg_color="#ffffff")
    topbar.pack(side="bottom", fill="x")
    def list_button_topbar(parent, icon_path, text, command=None):
        icon = ctk.CTkImage(light_image=Image.open(icon_path), size=(30, 30))
        btn = ctk.CTkButton(
            parent, image=icon, text=text,
            width=145, height=100,
            fg_color="#ffffff", hover_color="#ffffff",
            compound="top", anchor="center", corner_radius=5,
            font=("", 14), command=command, text_color="black"
        )
        btn.pack(side="left", padx=12, pady=35)

        def on_enter(e):
            btn.configure(fg_color="#1f1f1f", text_color="white")

        def on_leave(e):
            btn.configure(fg_color="#ffffff", text_color="black")

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    # Add buttons to topbar
    list_button_topbar(topbar, "C:/Users/mehdi/Desktop/images/home.png", "Home")
    list_button_topbar(topbar, "C:/Users/mehdi/Desktop/images/control-panel.png", "Control panel",command=controlePanel)
    list_button_topbar(topbar, "C:/Users/mehdi/Desktop/images/countdown.png", "Timer",command=timer_plc)
    list_button_topbar(topbar, "C:/Users/mehdi/Desktop/images/history.png", "Counter",command=counter_plc)
    list_button_topbar(topbar, "C:/Users/mehdi/Desktop/images/database.png", "Data Block",command=db_block)
    #--------------- Image Logo Company --------------------------------------------------------------------#
    logo_app=Image.open("C:/Users/mehdi/Desktop/images/IFMCP.jpg")
    logo_image=ctk.CTkImage(dark_image=logo_app,size=(200,150))
    logolabel=ctk.CTkLabel(app,image=logo_image,text="")
    logolabel.place(x=10, y=10)
    #------------------ Toolbar Buttons ------------------#
    def list_button_toolbar(parent, icon_path, text, rely, command=None):
        icon1 = ctk.CTkImage(light_image=Image.open(icon_path), size=(30, 30))
        btn1 = ctk.CTkButton(
        parent, image=icon1, text=text,
        width=145, height=100,
        fg_color="#ffffff", hover_color="#e0e0e0",
        compound="top", corner_radius=5,
        font=("", 14), command=command, text_color="black")
        btn1.place(relx=0.80, rely=rely)
        def on_enter1(e):
            btn1.configure(fg_color="#1f1f1f", text_color="white")
        def on_leave1(e):
            btn1.configure(fg_color="#ffffff", text_color="black")
        
        btn1.bind("<Enter>", on_enter1)
        btn1.bind("<Leave>", on_leave1)
    list_button_toolbar(app, "C:/Users/mehdi/Desktop/images/setting.png", "Setting", rely=0.05)
    list_button_toolbar(app, "C:/Users/mehdi/Desktop/images/smartphone.png", "Phone backup", rely=0.25)
    list_button_toolbar(app, "C:/Users/mehdi/Desktop/images/global-network.png", "PLC Communication", rely=0.45)

#------------------- Connect Button ------------------------#
Connexion = ctk.CTkButton(frame, text='Connecte', command=connect_to_plc)
Connexion.place(x=80, y=210)

#------------------- Welcome Image ------------------------#
welcome_app = Image.open("C:/Users/mehdi/Desktop/images/welcomelogin.png")
welcome_image = ctk.CTkImage(dark_image=welcome_app, size=(250, 100))
welcomeimg_label = ctk.CTkLabel(connectapp, image=welcome_image, text="")
welcomeimg_label.pack(pady=25, anchor="center")

#------------------- Mainloop ------------------------#
connectapp.mainloop()
