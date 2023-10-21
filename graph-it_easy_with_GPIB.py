from win32api import GetMonitorInfo, MonitorFromPoint
from tkinter.filedialog import asksaveasfile, askopenfile
import tkinter as tk
from tkinter import simpledialog
from tkinter import font, Menu, colorchooser, messagebox
from tkfontchooser import askfont
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.patches as pat
from numpy import random, arange, geomspace, linspace
from sympy import parse_expr
import configparser
import pathlib
import timeit
from datetime import datetime
import os
import pyvisa
class TDS210():
    ########### REQUIREMENTS FOR GPIB ##########
    # NI VISA For Windows 11 64 Bit, (2022 Q3) Or (2023 Q2) Installed
    # PyVISA 1.13.0 Or Latest Version
    # Tektronix TDS 210/220 Oscilloscope Or Equivalent With GPIB Interface
    # Tested With (NI GPIB-USB-HS+) Controller
    # Tested Using Python Version 3.11.4 64 Bit
    # This Class Assumes That Pyvisa And NI-VISA Are Installed And Working Correctly.

    # Both List (TDS_FUNCTS And TDS_CMDS) Indices Must Correlate. 
    # At The Present Time, There Are 158 Indices (Functions And Commands) In Both List.
    TDS_FUNCTS=['**** UTILITIES ****','oscope_self_cal','oscope_auto_set','oscope_factory_set','oscope_reset',
        'oscope_clear','oscope_frontpanel_lock, NONE','oscope_save_setup, 1','oscope_recall_setup, 1',
        '**** DISPLAY ****','set_disp_style, VECTORS','set_disp_persistence, OFF','set_disp_format,YT',
        'set_disp_contrast, 75','get_display_style','get_display_persistence','get_display_format',
        'get_display_contrast','**** VERTICAL ****','set_vert_select, CH1, ON','set_vert_bandwidth, OFF, CH1',
        'set_vert_coupling, DC, CH1','set_vert_position, 2, CH1','set_vert_probe, 10, CH1','set_vert_scale, 2, CH1',
        'set_vert_math, "CH1 + CH2"','get_vert_select_waveform, MATH','get_vert_select_all','get_vert_bandwidth, CH1',
        'get_vert_coupling, CH1','get_vert_position, CH1','get_vert_probe, CH1','get_vert_scale, CH1','get_vert_math',
        '**** HORIZONTAL ****','set_horiz_main_scale, 5.0E-4','set_horiz_main_position, 0.0','set_horiz_view, MAIN',
        'set_horiz_delay_scale, 250E-6','set_horiz_delay_position, 0.0','get_horiz_all','get_horiz_main',
        'get_horiz_main_scale','get_horiz_main_position','get_horiz_view','get_horiz_delay_scale',
        'get_horiz_delay_position','**** TRIGGER ****','set_trig_force','set_trig_50%','set_trig_mode, AUTO',
        'set_trig_type, EDGE','set_trig_level, 1.5','set_trig_edge_coupling, DC','set_trig_edge_slope, RISE',
        'set_trig_edge_source, CH1','set_trig_holdoff_value, 5.0e-7','set_trig_video_polarity, NORMAL',
        'set_trig_video_source, CH1','set_trig_video_sync, LINE','get_trig','get_trig_main','get_trig_mode',
        'get_trig_type','get_trig_level','get_trig_edge_coupling','get_trig_edge_slope','get_trig_edge_source',
        'get_trig_holdoff','get_trig_video_polarity','get_trig_video_source','get_trig_video_sync',
        'get_trig_state','**** ACQUIRE ****','set_acquire_mode, AVERAGE','set_acquire_num_average, 16',
        'set_acquire_state, RUN','set_acquire_stopafter, SEQUENCE','get_acquire_all','get_acquire_mode',
        'get_acquire_num_average','get_acquire_state','get_acquire_stopafter','**** MEASURE ****',
        'set_meas1_source, CH1','set_meas1_type, FREQ','set_meas2_source, CH1','set_meas2_type, PK2PK',
        'set_meas3_source, CH2','set_meas3_type, PERIOD','set_meas4_source, CH2','set_meas4_type, MEAN',
        'set_immed_source, CH1','set_immed_type, PK2PK','get_meas_settings','get_meas1_source','get_meas1_type',
        'get_meas1_value','get_meas1_units','get_meas2_source','get_meas2_type','get_meas2_value','get_meas2_units',
        'get_meas3_source','get_meas3_type','get_meas3_value','get_meas3_units','get_meas4_source','get_meas4_type',
        'get_meas4_value','get_meas4_units','get_immed_source','get_immed_type','get_immed_value','get_immed_units',
        '**** DATA,CURVE,WFMPRE ****','set_data_init','set_data_destination, REFA','set_data_encoding, ASCII',
        'set_data_source, CH2','set_data_start, 1','set_data_stop, 2500','set_data_width, 1','get_data_info',
        'get_curve_xdata','get_curve_ydata','get_data_destination','get_data_encoding','get_data_source','get_data_start',
        'get_data_stop','get_data_width','get_waveform_num_pts','get_waveform_xincr','get_waveform_yoffset',
        'get_waveform_ymult','get_waveform_yzero','**** CURSOR ****','set_cursor_type, HBARS',
        'set_cursor_source, CH1','set_hbars_pos1, 0.0','set_hbars_pos2, 5.5','set_vbars_pos1, -2.0E-3',
        'set_vbars_pos2, 2.0E-3','set_vbars_units, SECONDS','get_cursor','get_cursor_type','get_cursor_source',
        'get_hbars_pos1','get_hbars_pos2','get_hbars_units','get_cursor_hbars','get_hbars_delta','get_vbars_pos1',
        'get_vbars_pos2','get_vbars_units','get_cursors_vbars','get_vbars_delta']
    def __init__(self, function): # function Contains Function Name And Arguments As String. See TDS_FUNCTS
        super().__init__()
        self.args=[]# Make Sure All Arguments Are In Correct Format Before Call.
        args=function.split(",")# Extract Function And Arguments Into List
        if args[0][-1]=='*':return # cbo Section Seperators
        if len(args)>=1:# Sets Function
            self.args.append(str(args[0]).replace(" ", ""))# Function Argument
            self.funct=str(args[0]).replace(" ", "")
        if len(args)>=2:# Delete Unwanted Characters And Make Sure UpperCase Is Used For Arguments
            args[1]=str(args[1]).replace(" ", "")
            self.args.append(str(args[1]).upper())
        else:self.args.append('')
        if len(args)==3:# Sets Channel
            args[2]=str(args[2]).replace(" ", "")# Mostly Values
            self.args.append(str(args[2].upper()))    
        else:self.args.append('')
        self.ctrl_port='' # Controller Port
        self.oscope_address='5' # Oscilloscope Port
        self.rm=pyvisa.ResourceManager()
        self.rtn_val='' # String, Returned Value
        for i, items in enumerate(TDS210.TDS_FUNCTS):# Find Index Based On Function Text Instead Of Using cbo Index.
            if self.funct in items:                            # This Allows TDS210 Class To Be Used Without GUI Later.
                self.index=i
                break
    def __str__(self):
        def gpib_initialize():#********** Controller  Initialization **********
            try:
                global res
                msg1='GPIB Bus Could Take Up To 30 Seconds To Initialize.\n'
                msg2='You Will Be Prompted When Completed!\n'
                msg3='Press OK Button To Start.'
                msg=msg1+msg2+msg3
                messagebox.showinfo('GPIB Bus Initialization', msg)
                res=self.rm.list_resources() # Time Consuming
                ctrl=self.rm.open_resource('GPIB::INTFC')
                interface_name=ctrl.resource_manufacturer_name
                self.ctrl_port=str(ctrl.resource_name)[ctrl.resource_name.find("'")+1:ctrl.resource_name.find(':')]
                self.rtn_val='Initialization Passed'
                interface_stat=self.rtn_val
                msg1=interface_name+' Controller Initialization Complete!\n'
                if len(res)!=0:msg2='Instruments Detected @ '+str(self.rm.list_resources())
                else:msg2='No Instruments Detected Connected To GPIB Bus!'
                messagebox.showinfo(interface_name+' GPIB Bus Initialization', msg1+msg2)
                Gpib_Initialized.set(True)
                return interface_stat
            except Exception as e:
                self.rtn_val='Initialization Failed'
                interface_stat='Initialization Failed'
                msg1='Exception occurred while code execution:\n'
                msg2=repr(e)+'GPIB Bus Controller Initialization'
                messagebox.showerror('GPIB Controller Initialization',msg1+msg2)
                return 'break'
        def oscope_initialize():#********** Oscilloscope Initialization **********        
            if not Oscope_Initialized.get():
                try:
                    global Oscope
                    if len(res)>=1:
                        oscope_port=str(self.ctrl_port+'::'+self.oscope_address+'::INSTR')
                        if oscope_port in res:
                            Oscope=self.rm.open_resource(oscope_port)
                            idn=Oscope.query("*IDN?")
                            if idn!='0' and idn!='':
                                Oscope.timeout=100000# 100s
                                Oscope.write_termination='\n'
                                Oscope.read_termination='\n'
                                Oscope.write("DISPLAY:CONTRAST 75")
                                self.rtn_val='Initialization Passed'
                                name=idn.split(',')
                                oscope_name=name[0]+ ' '+name[1]
                                msg1=oscope_name+' Initialization Complete!\n'
                                msg2='Oscilloscope Detected @ '+str(oscope_port)
                                msg3='\nOscilloscope IDN: '+str(idn)
                                messagebox.showinfo(oscope_name+' Oscilloscope Initialization',msg1+msg2+msg3)
                                Oscope_Initialized.set(True)
                                return self.rtn_val
                        else:
                            self.rtn_val='Initialization Failed'
                            msg1='Oscilloscope Not Detected!\n'
                            msg2='Please Make Sure That The Instrument Is Powered On\n'
                            msg3='And The GPIB Cable Is Connected To The Instrument.\n'
                            msg4='Then Try Again!'
                            msg=msg1+msg2+msg3+msg4
                            messagebox.showerror('Oscilloscope Initialization',msg)
                            return self.rtn_val
                    else:    
                            msg1='Oscilloscope Initialization Failed!\n'
                            msg2='No Oscilloscope Detected Connected To GPIB Bus!'
                            messagebox.showerror('Oscilloscope Initialization', msg1+msg2)
                            Oscope_Initialized.set(False)
                            self.rtn_val='Failed'
                            return self.rtn_val
                except Exception as e:
                    self.rtn_val='Initialization Failed'
                    msg1='Exception occurred while code execution:\n'
                    msg2=repr(e)+'GPIB Bus "oscope_initialize()"'
                    messagebox.showerror('Oscilloscope Initialization',msg1+msg2)
                    return 'break'
            else: return str(Oscope_Initialized.get())    
        def oscope_self_cal():# Returns "PASS", "FAIL"        
            try:
                msg1='The Oscilloscope Self Calibration Could Take Several\n'
                msg2='Minutes To Complete! Remove All Probes From The\n'
                msg3='Oscilloscope Inputs And Allow At Least A 5 Minute\n'
                msg4='Warm-Up Period Before Continuing. You Will Be Prompted\n'
                msg5='When Completed! Press OK Button To Start Self Cal.'
                msg=msg1+msg2+msg3+msg4+msg5
                messagebox.showinfo('Oscilloscope Self Calibration',msg)
                Oscope.write("CAL:INTERNAL;*OPC?")
                busy='1'
                while busy=='1':
                    busy=Oscope.query("BUSY?")# Busy "1", Not Busy "0"
                self.rtn_val=Oscope.query("CAL:STATUS?")# "PASS", "FAIL"
                if 'PASS' in self.rtn_val:messagebox.showinfo('Oscilloscope Self Calibration',self.rtn_val)
                elif 'FAIL' in self.rtn_val:
                    msg='Make Sure All Probes Are Disconnected And Try Again!\n'
                    messagebox.showerror('Oscilloscope Self Calibration',msg+self.rtn_val)
                return 'break'
            except Exception as e:
                msg1='Exception occurred while code execution:\n'
                msg2='Function = TDS210.oscope_self_calibrate()'
                msg2=repr(e)+'Command = CAL:INTERNAL;*OPC?'
                messagebox.showerror('Oscilloscope Self Calibration',msg1+msg2+msg3)
                return 'break'
        def oscope_auto_set():    
            try:
                Oscope.write("AUTOSET EXECUTE;*OPC?")
                busy='1'
                while busy=='1':
                    busy=(Oscope.query("BUSY?"))# Busy "1", Not Busy "0"
                self.rtn_val='OK'
                return(self.rtn_val)
            except Exception as e:
                msg1='Exception occurred while code execution:\n'
                msg2=repr(e)+'GPIB Bus "oscope_autoset()"'
                messagebox.showerror('Oscilloscope Autoset',msg1+msg2)
                return 'break'
        def gpib_send():
            # '****XXXX*****' Indicates Group Seperators For Easy Access
            TDS_CMDS=['****UTIL****','CAL:INTERNAL','AUTOSET EXECUTE','FACTORY','*RST',
                '*CLS',str('LOCK '+self.args[1]),str('SAVE:SETUP '+self.args[1]),str('RECALL:SETUP '+self.args[1]),
                '****DISPLAY****',str('DISPLAY:STYLE '+self.args[1]),str('DISPLAY:PERSISTENCE '+self.args[1]),
                str('DISPLAY:FORMAT '+self.args[1]),str('DISPLAY:CONTRAST '+self.args[1]),'DISPLAY:STYLE?',
                'DISPLAY:PERSISTENCE?','DISPLAY:FORMAT?','DISPLAY:CONTRAST?','****VERT****',
                str('SELECT:'+self.args[1]+' '+self.args[2]),str(self.args[2]+':BANDWIDTH '+self.args[1]),
                str(self.args[2]+':COUPLING '+self.args[1]),str(self.args[2]+':POSITION '+self.args[1]),
                str(self.args[2]+':PROBE '+self.args[1]),str(self.args[2]+':SCALE '+self.args[1]),
                str('MATH:DEFINE '+self.args[1]),'select:'+self.args[1]+'?','SELECT?',str(self.args[1]+':BANDWIDTH?'),
                str(self.args[1]+':COUPLING?'),str(self.args[1]+':POSITION?'),str(self.args[1]+':PROBE?'),
                str(self.args[1]+':SCALE?'),"MATH:DEFINE?",'****HORIZ****',str('HORIZONTAL:SCALE '+self.args[1]),
                str('HORIZONTAL:POSITION '+self.args[1]),str('HORIZONTAL:VIEW '+self.args[1]),
                str('HORIZONTAL:DELAY:SCALE '+self.args[1]),str('HORIZONTAL:DELAY:POSITION '+self.args[1]),
                'HORIZONTAL?','HORIZONTAL:MAIN?','HORIZONTAL:MAIN:SCALE?','HORIZONTAL:MAIN:POSITION?',
                'HORIZONTAL:VIEW?','HORIZONTAL:DELAY:SCALE?','HORIZONTAL:DELAY:POSITION?',
                '****TRIG****','TRIGGER FORCE','TRIGGER:MAIN SETLEVEL',str('TRIGGER:MAIN:MODE '+self.args[1]),
                str('TRIGGER:MAIN:TYPE '+self.args[1]),str('TRIGGER:MAIN:LEVEL '+self.args[1]),
                str('TRIGGER:MAIN:EDGE:COUPLING '+self.args[1]),str('TRIGGER:MAIN:EDGE:SLOPE '+self.args[1]),
                str('TRIGGER:MAIN:EDGE:SOURCE '+self.args[1]),str('TRIGGER:MAIN:HOLDOFF:VALUE '+self.args[1]),
                str('TRIGGER:MAIN:VIDEO:POLARITY '+self.args[1]),str('TRIGGER:MAIN:VIDEO:SOURCE '+self.args[1]),
                str('TRIGGER:MAIN:VIDEO:SYNC '+self.args[1]),'TRIGGER?','TRIGGER:MAIN?','TRIGGER:MAIN:MODE?',
                'TRIGGER:MAIN:TYPE?','TRIGGER:MAIN:LEVEL?','TRIGGER:MAIN:EDGE:COUPLING?',
                'TRIGGER:MAIN:EDGE:SLOPE?','TRIGGER:MAIN:EDGE:SOURCE?','TRIGGER:MAIN:HOLDOFF?',
                'TRIGGER:MAIN:VIDEO:POLARITY?','TRIGGER:MAIN:VIDEO:SOURCE?','TRIGGER:MAIN:VIDEO:SYNC?',
                'TRIGGER:STATE?','****ACQUIRE****',str('ACQUIRE:MODE '+self.args[1]),str('ACQUIRE:NUMAVG '+self.args[1]),
                str('ACQUIRE:STATE '+self.args[1]),str('ACQUIRE:STOPAFTER '+self.args[1]),'ACQUIRE?','ACQUIRE:MODE?',
                'ACQUIRE:NUMAVG?','ACQUIRE:STATE?','ACQUIRE:STOPAFTER?','****MEAS****',
                str('MEASUREMENT:MEAS1:SOURCE '+self.args[1]),str('MEASUREMENT:MEAS1:TYPE '+self.args[1]),
                str('MEASUREMENT:MEAS2:SOURCE '+self.args[1]),str('MEASUREMENT:MEAS2:TYPE '+self.args[1]),
                str('MEASUREMENT:MEAS3:SOURCE '+self.args[1]),str('MEASUREMENT:MEAS3:TYPE '+self.args[1]),
                str('MEASUREMENT:MEAS4:SOURCE '+self.args[1]),str('MEASUREMENT:MEAS4:TYPE '+self.args[1]),
                str('MEASUREMENT:IMMED:SOURCE '+self.args[1]),str('MEASUREMENT:IMMED:TYPE '+self.args[1]),
                'MEASUREMENT?','MEASUREMENT:MEAS1:SOURCE?','MEASUREMENT:MEAS1:TYPE?','MEASUREMENT:MEAS1:VALUE?',
                'MEASUREMENT:MEAS1:UNITS?','MEASUREMENT:MEAS2:SOURCE?','MEASUREMENT:MEAS2:TYPE?',
                'MEASUREMENT:MEAS2:VALUE?','MEASUREMENT:MEAS2:UNITS?','MEASUREMENT:MEAS3:SOURCE?',
                'MEASUREMENT:MEAS3:TYPE?','MEASUREMENT:MEAS3:VALUE?','MEASUREMENT:MEAS3:UNITS?',
                'MEASUREMENT:MEAS4:SOURCE?','MEASUREMENT:MEAS4:TYPE?','MEASUREMENT:MEAS4:VALUE?',
                'MEASUREMENT:MEAS4:UNITS?','MEASUREMENT:IMMED:SOURCE?','MEASUREMENT:IMMED:TYPE?',
                'MEASUREMENT:IMMED:VALUE?','MEASUREMENT:IMMED:UNITS?','****DATA,CURVE,WFMPRE****','DATA INIT',
                str('DATA:DESTINATION '+self.args[1]),str('DATA:ENCDG '+self.args[1]),str('DATA:SOURCE '+self.args[1]),
                str('DATA:START '+self.args[1]),str('DATA:STOP '+self.args[1]),str('DATA:WIDTH '+self.args[1]),
                'DATA?','CURVE?','CURVE?','DATA:DESTINATION?','DATA:ENCDG?','DATA:SOURCE?','DATA:START?',
                'DATA:STOP?','DATA:WIDTH?','WFMPRE:NR_PT?','WFMPRE:XINCR?','WFMPRE:YOFF?','WFMPRE:YMULT?',
                'WFMPRE:YZERO?', '**** CURSOR ****',str('CURSOR:FUNCTION '+self.args[1]),
                str('CURSOR:SELECT:SOURCE '+self.args[1]),str('CURSOR:HBARS:POSITION1 '+self.args[1]),
                str('CURSOR:HBARS:POSITION2 '+self.args[1]),str('CURSOR:VBARS:POSITION1 '+self.args[1]),
                str('CURSOR:VBARS:POSITION2 '+self.args[1]),str('CURSOR:VBARS:UNITS '+self.args[1]),
                'CURSOR?','CURSOR:FUNCTION?','CURSOR:SELECT:SOURCE?','CURSOR:HBARS:POSITION1?','CURSOR:HBARS:POSITION2?',
                'CURSOR:HBARS:UNITS?','CURSOR:HBARS?','CURSOR:HBARS:DELTA?','CURSOR:VBARS:POSITION1?',
                'CURSOR:VBARS:POSITION2?','CURSOR:VBARS:UNITS?','CURSORS:VBARS?','CURSOR:VBARS:DELTA?']
            if len(TDS210.TDS_FUNCTS)!=len(TDS_CMDS):# Make Sure Both List Have The Same Indices.
                msg1='Lists TDS_FUNCTS And TDS_CMDS Have Different Indices:\n'
                msg2='They Must Be Equal For Proper Code Execution!\n'
                msg3='Ending Program! Please Correct The Associated Code.'
                messagebox.showerror('TDS 210',msg1+msg2+msg3)
                destroy()
            try:
                if not '?' in TDS_CMDS[self.index]:# WRITES
                    Oscope.write(TDS_CMDS[self.index])
                    self.rtn_val=self.args[1]
                else: #QUERIES  
                    if TDS_CMDS[self.index]=='CURVE?':
                        if self.funct=='get_curve_xdata':# Calculate And Return Time In Seconds    
                            pts=Oscope.query('WFMPRE:NR_PT?').split(" ")
                            num_pts=int(pts[1])
                            inc=Oscope.query('WFMPRE:XINCR?').split(" ")
                            xinc=float(inc[1])
                            curve_x=[]
                            xnow=0.0
                            for p in range(num_pts):# Place Curve X Data Into List
                                curve_x.append(round(xnow,14))
                                xnow+=xinc
                            self.rtn_val=str(curve_x)
                        elif self.funct=='get_curve_ydata':# Convert Digitized Value To Y Values (Volts)
                            rtn=Oscope.query(TDS_CMDS[self.index])
                            ymult=Oscope.query('WFMPRE:YMULT?').split(" ")
                            ymult=float(ymult[1])
                            yoffset=Oscope.query('WFMPRE:YOFF?').split(" ")
                            yoffset=float(yoffset[1])
                            #  YZERO Always Returns 0.0 For This Oscilloscope Version, So Use Position Instead.
                            source=Oscope.query('DATA:SOURCE?').split(" ")
                            pos=Oscope.query(source[1]+':POSITION?').split(" ")
                            volt_div=Oscope.query(source[1]+':SCALE?').split(" ")
                            scale=float(volt_div[1])
                            yzero=float(pos[1])*scale
                            curve_y=[]
                            digitized=rtn.replace(':CURVE ','')# Remove ':CURVE ' From String
                            curve=digitized.split(",") # Place String Values In List
                            curve_y=[((float(elements) -yoffset)*ymult)+yzero for elements in curve] # Convert To Volts
                            self.rtn_val=str(curve_y)
                    else:# All Other Commands Except Curve
                        val=Oscope.query(TDS_CMDS[self.index])
                        if ";" in val:
                            params=val.split(";") # > 1, Queries With Multiple Parameters
                            self.rtn_val=params
                        elif " " in val:# Extract Only Numbers
                            nums=val.split(" ") # > 1, Queries With 1 Value
                            self.rtn_val=nums[1]
                return(self.rtn_val)
            except Exception as e:
                msg1='Exception occurred while code execution:\n'
                msg2='Bus Command = '+TDS_CMDS[self.index]
                msg3=repr(e)+'GPIB Bus '+self.funct
                messagebox.showerror('TDS 210',msg1+msg2+msg3)
                return 'break'
        try: # If Bus And/Or Instrument Is Not Initialized, Then Initialize First
            if self.funct=='gpib_initialize':status=gpib_initialize()
            elif self.funct=='oscope_initialize':
                if not Gpib_Initialized.get():gpib_initialize() 
                status=oscope_initialize()
            elif self.funct=='oscope_self_cal':       
                if not Gpib_Initialized.get():gpib_initialize() 
                if not Oscope_Initialized.get():oscope_initialize()
                status=oscope_self_cal()
            elif self.funct=='oscope_auto_set':
                if not Gpib_Initialized.get():gpib_initialize() 
                if not Oscope_Initialized.get():oscope_initialize()
                status=oscope_auto_set()
            else:
                if not Gpib_Initialized.get():gpib_initialize() 
                if not Oscope_Initialized.get():oscope_initialize()
                status=gpib_send()    
            return(status)
        except Exception as e:
            msg1='Exception occurred while code execution:\n'
            msg2=repr(e)+'GPIB '+self.funct
            messagebox.showerror('GPIB Error',msg1+msg2)
            return 'break'
class Test():
    def log(exe_style):# Example
        clear_graph()  # Always Call clear_graph() To Start Fresh.
        if exe_style=='loop':Title.set("X Scale = Log, Draw Style = Loop Update Using Lists")
        elif exe_style=='instant':Title.set("X Scale = Log, Draw Style = Instant Update Using Lists")
        elif exe_style=='live':Title.set("X Scale = Log, Draw Style = Live Update")
        X_Text.set('Frequency In Hertz')
        X_Style.set('log')
        X_Scale.set('20,20000')
        X_Tick_Inc.set("")# If Null, Determined by Default Increments or x_locs,x_lbls 
        Y_Text.set('Amplitude In dB')
        Y_Style.set('linear')
        Y_Scale.set('-10,10')
        Y_Tick_Inc.set("2.5")
        set_axes()
        # Customize X and/or Y Asis Tick Labels And Locations Without affecting Limits
        x_locs=[20,50,100,200,500,1000,2000,5000,10000,20000]
        x_lbls=['20','50','100','200','500','1k','2k','5k','10k','20k']
        change_tick_labels('x',x_locs,x_lbls)# Change X Tick Labels And Locations
# ****************************** Plot 1 ******************************
        plt_num=1 # Make Sure To Set The Plot Number Even If Only One Plot Will Exist.
        num_pts=200 # Set Number Of Data points
        #Set Plot 1 2DLine  Properties
        plt1_color='aqua'# Set The line2d Color
        plt1_style='solid'# Set The line2d Style
        plt1_width=1# Set The line2d Width
        # Present Your Lists Data Here Or Inside Loop
        axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
        line2d,=ax.plot([],c=plt1_color,ls=plt1_style,lw=plt1_width)
        if exe_style=='loop':
            frames=0
            t_0=timeit.default_timer()
            xdata=geomspace(20.0,20000.0,num=num_pts,endpoint=True)# Cannot Be Zero! Use geospace or logspace For Logs
            ydata=random.uniform(low=-10.0,high=10.0,size=(num_pts,))
            for i in arange(1,num_pts+1): # Start Should Always Be 1 With Stop At Length + 1
                line2d.set_data(xdata[:i],ydata[:i])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,xdata[i-1],ydata[i-1],plt1_color,plt1_style,plt1_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        elif exe_style=='instant':# Instantly Update Graph With List Data
            xdata=geomspace(20.0,20000.0,num=num_pts,endpoint=True)# Cannot Be Zero! Use geospace or logspace For Logs
            ydata=random.uniform(low=-10.0,high=10.0,size=(num_pts,))
            line2d.set_data(xdata,ydata)# Update The Artist
            fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
            ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
            fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
            frames=0
            t_0=timeit.default_timer()
            for i in range(0,num_pts): # Data For Saving To File
                newline=[plt_num,xdata[i],ydata[i],plt1_color,plt1_style,plt1_width]
                Plot_Data.append(str(newline))
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        elif exe_style=='live': # Live Update
            xdata=geomspace(20.0,20000.0,num=num_pts,endpoint=True)# Cannot Be Zero! Use geospace or logspace For Logs
            ydata=random.uniform(low=-10.0,high=10.0,size=(num_pts,))
            # Generate Your X,Y Data Here And Create Seperate List For X Data And Y Data As They Arrive.
            # Each Time The Lists Gets Inserted Or Appended, The List Data Will Be Executed Inside The Loop.
            # This Should Be Used For Live Update Type Plots.
            x,y=[],[]    
            axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
            line2d,=ax.plot([],c=plt1_color,ls=plt1_style,lw=plt1_width)
            frames=0
            t_0=timeit.default_timer()
            for i in arange(num_pts):
                #////////////////////////////////////////////////////////    
                # Incomming Live Data From Sensors / Test Equip. etc...  
                # Retrieve New x,y Values Here And Place In x,y Lists
                # 2 x values (xdata[0]),(xdata[1]) And 2 y values (ydata[0]),(ydata[1]) 
                # Need To Be Present In Lists Before Loop Execution.
                x.insert(i,xdata[i])
                y.insert(i,ydata[i])
                #////////////////////////////////////////////////////////    
                line2d.set_data(x[:i+1],y[:i+1])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,x[i-1],y[i-1],plt1_color,plt1_style,plt1_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        ymax=str(round(max(ydata),3))# Max Y Value In List        
        ymin=str(round(min(ydata),3))# Max Y Value In List        
        legend_text=['Plot 1','Pts. = '+str(num_pts),'FPS = '+fps,'Style = '+exe_style,'Max.='+ymax+'dB','Min.='+ymin+'dB','']    
        Test.plot_legends(plt_num,plt1_color,ydata,legend_text)
        canvas.draw()
# ****************************** Plot 2 ******************************
        plt_num=2 # Make Sure To Set The Plot Number
        # Generate Data To Plot Herev
        # Data Can Be 2 List. X Data List And Y Data List Or
        # Place Your Data Here
        #Set Plot 2 2DLine  Properties
        plt2_color='yellow'# Set The line2d Color
        plt2_style='dotted'# Set The line2d Style
        plt2_width=2# Set The line2d Width
        xdata=geomspace(20.0,20000.0,num=num_pts,endpoint=True)# Cannot Be Zero! Use geospace or logspace For Logs
        ydata=random.uniform(low=-10.0,high=10.0,size=(num_pts))
        axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
        line2d,=ax.plot([],c=plt2_color,ls=plt2_style,lw=plt2_width)
        if exe_style=='loop': # Loop Through Lists Data
            frames=0
            t_0=timeit.default_timer()
            for i in arange(1,num_pts+1): # Start Should Always Be 1 With Stop At Length + 1
                line2d.set_data(xdata[:i],ydata[:i])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,xdata[i-1],ydata[i-1],plt2_color,plt2_style,plt2_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        elif exe_style=='instant': # Instantly Update Graph With List Data
            line2d.set_data(xdata,ydata)# Update The Artist
            fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
            ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
            fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
            frames=0
            t_0=timeit.default_timer()
            for i in range(0,num_pts): # Data For Saving To File
                newline=[plt_num,xdata[i],ydata[i],plt2_color,plt2_style,plt2_width]
                Plot_Data.append(str(newline))
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        elif exe_style=='live': # Incomming Data Inside Test Loop
            xdata=geomspace(20.0,20000.0,num=num_pts,endpoint=True)# Cannot Be Zero! Use geospace or logspace For Logs
            ydata=random.uniform(low=-10.0,high=10.0,size=(num_pts,))
            # Generate Your X,Y Data Here And Create Seperate List For X Data And Y Data As They Arrive.
            # Each Time The Lists Gets Inserted Or Appended, The List Data Will Be Executed Inside The Loop.
            # This Should Be Used For Live Update Type Plots.
            x,y=[],[]    
            axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
            line2d,=ax.plot([],c=plt2_color,ls=plt2_style,lw=plt2_width)
            frames=0
            t_0=timeit.default_timer()
            for i in arange(num_pts):
                #////////////////////////////////////////////////////////    
                # Incomming Live Data From Sensors / Test Equip. etc...  
                # Retrieve New x,y Values Here And Place In x,y Lists
                # 2 x values (xdata[0]),(xdata[1]) And 2 y values (ydata[0]),(ydata[1]) 
                # Need To Be Present In Lists Before Loop Execution.
                x.insert(i,xdata[i])
                y.insert(i,ydata[i])
                #////////////////////////////////////////////////////////    
                line2d.set_data(x[:i+1],y[:i+1])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,x[i-1],y[i-1],plt2_color,plt2_style,plt2_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        ymax=str(round(max(ydata),3))# Max Y Value In List        
        ymin=str(round(min(ydata),3))# Max Y Value In List        
        legend_text=['Plot 2','Pts. = '+str(num_pts),'FPS = '+fps,'Style = '+exe_style,'Max.='+ymax+'dB','Min.='+ymin+'dB','']    
        Test.plot_legends(plt_num,plt2_color,ydata,legend_text)
        Test.stamp_time()
        canvas.draw()
    def linear(exe_style):# Example
        clear_graph() # Always Call clear_graph() To Start Fresh.
        if exe_style=='loop':Title.set('X Scale = Linear, Draw Style = Loop Update Using Lists')
        elif exe_style=='instant':Title.set('X Scale = Linear, Draw Style = Instant Update Using Lists')
        elif exe_style=='live':Title.set('X Scale = Linear, Draw Style = Live Update')
        X_Text.set('Time In Milliseconds')
        X_Style.set('linear')
        X_Scale.set('0.0,300.0')
        X_Tick_Inc.set("")# If Null, Determined by Default Increments or x_locs, x_lbls 
        Y_Text.set('Current In Amperes')
        Y_Style.set('linear')
        Y_Scale.set('0,500')
        Y_Tick_Inc.set("")# If Null, Determined by Default Increments or y_locs, y_lbls 
        set_axes()
        # Change X and/or Y Asis Tick Labels Without affecting Limits
        x_locs=[0,30,60,90,120,150,180,210,240,270,300]
        x_lbls=['0','30m','60m','90m','120m','150m','180m','210m','240m','270m','300m']
        change_tick_labels('x', x_locs,x_lbls)
        y_locs=[0,100,200,300,400,500]
        y_lbls=['0','100m','200m','300m','400m','500m']
        change_tick_labels('y',y_locs,y_lbls)
# ****************************** Plot 1 ******************************
        plt_num=1 # Make Sure To Set The Plot Number Even If Only One Plot Will Exist.
        num_pts=200 # Set Number Of Data points
        # Generate Data To Plot Here
        # Data Can Be 2 List. X Data List And Y Data List Or
        # Data Can Also Be Incomming X And Y Data From Test Equipment Or Sensors.
        # Place Your Lists Data Here
        #Set Plot 1 2DLine  Properties
        plt1_color='aqua'# Set The line2d Color
        plt1_style='solid'# Set The line2d Style
        plt1_width=1# Set The line2d Width
        xdata=linspace(0.0,500.0,num=num_pts)# 100 linear x values 0.0 to 500
        ydata=random.uniform(low=0.0,high=500.0,size=(num_pts,))
        axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
        line2d,=ax.plot([],c=plt1_color,ls=plt1_style,lw=plt1_width)
        frames=0
        t_0=timeit.default_timer()
        if exe_style=='loop':
            for i in arange(1,num_pts+1): # Start Should Always Be 1 With Stop At Length + 1
                line2d.set_data(xdata[:i],ydata[:i])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,xdata[i-1],ydata[i-1],plt1_color,plt1_style,plt1_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        elif exe_style=='instant': # Instantly Update Graph With List Data
            xdata=linspace(0.0,500.0,num=num_pts)# linear x values 0.0 to 500
            ydata=random.uniform(low=0.0,high=500.0,size=(num_pts,))
            line2d.set_data(xdata,ydata)# Update The Artist
            fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
            # redraw just the points
            ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
            fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
            frames=0
            t_0=timeit.default_timer()
            for i in range(0,num_pts): # Data For Saving To File
                newline=[plt_num,xdata[i],ydata[i],plt1_color,plt1_style,plt1_width]
                Plot_Data.append(str(newline))
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        elif exe_style=='live':
            xdata=linspace(0.0,500.0,num=num_pts)# 100 linear x values 0.0 to 500
            ydata=random.uniform(low=0.0,high=500.0,size=(num_pts,))
            x,y=[],[]
            axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
            line2d,=ax.plot([],c=plt1_color,ls=plt1_style,lw=plt1_width)
            frames=0
            t_0=timeit.default_timer()
            for i in arange(num_pts):# Range Must Be Predetermined If Using Loop
                #////////////////////////////////////////////////////////    
                # Incomming Live Data From Sensors / Test Equip. etc...  
                # Retrieve New x,y Values Here And Place In x,y Lists
                # 2 x values (xdata[0]),(xdata[1]) And 2 y values (ydata[0]),(ydata[1]) 
                # Need To Be Present In Lists Before Loop Execution.
                x.insert(i,xdata[i])
                y.insert(i,ydata[i])
                #////////////////////////////////////////////////////////    
                line2d.set_data(x[:i+1],y[:i+1])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,x[i-1],y[i-1],plt1_color,plt1_style,plt1_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        ymax=str(round(max(ydata),3))# Max Y Value In List        
        ymin=str(round(min(ydata),3))# Max Y Value In List        
        legend_text=['Plot 1','Pts. = '+str(num_pts),'FPS = '+fps,'Style = '+exe_style,'Max.='+ymax+'dB','Min.='+ymin+'dB','']    
        Test.plot_legends(plt_num,plt1_color,ydata,legend_text)
        canvas.draw()
# ****************************** Plot 2 ******************************
        plt_num=2 # Set The Plot Number
        num_pts=200
        # Generate Data To Plot Here
        # Data Can Be 2 List. X Data List And Y Data List Or
        # Data Can Also Be Incomming X And Y Data From Test Equipment Or Sensors.
        #Set Plot 2 2DLine  Properties
        plt2_color='yellow'# Set The line2d Color
        plt2_style='dashed'# Set The line2d Style
        plt2_width=1# Set The line2d Width
        x=linspace(0.0,500.0,num=num_pts)# linear x values 0.0 to 500
        y=random.uniform(low=0.0,high=500.0,size=(num_pts,))
        axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
        line2d,=ax.plot([],c=plt2_color,ls=plt2_style,lw=plt2_width)
        frames=0
        t_0=timeit.default_timer()
        if exe_style=='loop':
            for i in arange(1,num_pts+1):
                line2d.set_data(x[:i],y[:i])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,x[i-1],y[i-1],plt2_color,plt2_style,plt2_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        elif exe_style=='instant': # Instantly Update Graph With np.array Data
            line2d.set_data(x,y)# Update The Artist
            fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
            ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
            fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
            frames=0
            t_0=timeit.default_timer()
            for i in range(0,num_pts): # Data For Saving To File
                newline=[plt_num,x[i],y[i],plt2_color,plt2_style,plt2_width]
                Plot_Data.append(str(newline))
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        elif exe_style=='live':
            xdata=linspace(0.0,500.0,num=num_pts)# 100 linear x values 0.0 to 500
            ydata=random.uniform(low=0.0,high=500.0,size=(num_pts,))
            # Generate Your X,Y Data Here And Create Seperate List For X Data And Y Data As They Arrive.
            # Each Time The Lists Gets Inserted Or Appended, The List Data Will Be Executed Inside The Loop.
            # This Should Be Used For Live Update Type Plots.
            x,y=[],[]    
            axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
            line2d,=ax.plot([],c=plt2_color,ls=plt2_style,lw=plt2_width)
            frames=0
            t_0=timeit.default_timer()
            for i in arange(num_pts):
                #////////////////////////////////////////////////////////    
                # Incomming Live Data From Sensors / Test Equip. etc...  
                # Retrieve New x,y Values Here And Place In x,y Lists
                # 2 x values (xdata[0]),(xdata[1]) And 2 y values (ydata[0]),(ydata[1]) 
                # Need To Be Present In Lists Before Loop Execution.
                x.insert(i,xdata[i])
                y.insert(i,ydata[i])
                #////////////////////////////////////////////////////////    
                line2d.set_data(x[:i+1],y[:i+1])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,x[i-1],y[i-1],plt2_color,plt2_style,plt2_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
                frames+=1
            t_1=timeit.default_timer()-t_0    
            fps=str(int(frames/t_1))
        ymax=str(round(max(ydata),3))# Max Y Value In List        
        ymin=str(round(min(ydata),3))# Max Y Value In List        
        legend_text=['Plot 2','Pts. = '+str(num_pts),'FPS = '+fps,'Style = '+exe_style,'Max.='+ymax+'dB','Min.='+ymin+'dB','']    
        Test.plot_legends(plt_num,plt2_color,ydata,legend_text)
        Test.stamp_time()
        canvas.draw()
    def plot_tds210_curves(exe_style):# Example
        if not Oscope_Initialized.get():
            status=str(TDS210('oscope_initialize'))# Initialize Controller And Instrument
            if 'Failed' in status:return
        clear_graph() # Always Call clear_graph() To Start Fresh.
        # Setup The Oscilloscope Curve Data For Transfer From The Oscilloscope
        # All Calls To The TDS210 Class Must Be Of String Type With Or Without Return Values
        # Get First Plot Ready on Channel 1
        str(TDS210('set_horiz_main_scale, 250e-6'))
        str(TDS210('set_horiz_main_position, 0.0'))
        str(TDS210('set_horiz_view, MAIN'))
        str(TDS210('set_vert_math, OFF'))
        str(TDS210('set_vert_select, CH1, ON')) 
        str(TDS210('set_vert_bandwidth, OFF, CH1')) 
        str(TDS210('set_vert_coupling, DC, CH1')) 
        str(TDS210('set_vert_position, 1, CH1')) 
        str(TDS210('set_vert_probe, 10, CH1')) 
        str(TDS210('set_vert_scale, 2, CH1')) 
        str(TDS210('set_data_encoding, ASCII')) # Make Sure Format Is ASCII For Transfer
        str(TDS210('set_data_source, CH1'))
        str(TDS210('set_data_start, 1'))
        str(TDS210('set_data_stop, 2500'))
        str(TDS210('set_data_width, 1'))
        str(TDS210('set_trig_mode, NORMAL'))
        str(TDS210('set_trig_type, EDGE'))# Make Sure Trigger Is OK
        str(TDS210('set_trig_edge_source, CH1'))
        str(TDS210('set_trig_edge_coupling, DC'))
        str(TDS210('set_trig_50%'))
        # Set Scope Measurements For Channel 1
        str(TDS210('set_meas1_source, CH1'))
        str(TDS210('set_meas1_type, PK2PK'))
        str(TDS210('set_meas2_source,CH1'))
        str(TDS210('set_meas2_type, CRMS'))
        str(TDS210('set_meas3_source,CH1'))
        str(TDS210('set_meas3_type, FREQ'))
        str(TDS210('set_meas4_source, CH1'))
        str(TDS210('set_meas4_type, PERIOD'))
        data_source=str(TDS210('get_data_source'))# (CH1,CH2,MATH,REFA,REFB), Waveform To Be Transfered
        num_pts=str(TDS210('get_waveform_num_pts'))# Should Not Exceed 2500 (data_stop - data_start)
        data_xincr=str(TDS210('get_waveform_xincr'))# Time Increments Per Data Point
        xmax=int(num_pts)*float(data_xincr)# Time In Seconds
        sec_per_div=str(rnd_time(xmax/10))
        volts_per_div=str(TDS210('get_vert_scale, '+data_source))
        Title.set('Tektronix TDS 210 CH1/CH2 Curve Data ('+num_pts+' Data Points)')
        X_Text.set('Time In Seconds (' +sec_per_div+' Sec/Div)')
        X_Style.set('linear')
        X_Scale.set('0.0,'+str(xmax))
        y_scale=str(TDS210('get_vert_scale,'+data_source))# Get Scale Of Curve Data Waveform
        Y_Text.set('Amplitude In Volts ('+str(y_scale)+' Volts/Div)')
        Y_Style.set('linear')
        Y_Scale.set('-8.0,8.0')
        Y_Tick_Inc.set("2.0")# If Null, Determined by y_locs, y_lbls
        # Reconfigure X Axis Major Ticks For 10 And Round Major Ticks Labels
        xstep=round(float(xmax/10),14)
        X_Tick_Inc.set(str(xstep))# If Null, Determined by x_locs, x_lbls 
        if xmax>=1:fmtr='%0.2f'
        elif xmax>=0.1:fmtr='%0.3f'
        elif xmax>=0.01:fmtr='%0.4f'
        elif xmax>=0.001:fmtr='%0.5f'
        elif xmax>=0.0001:fmtr='%0.6f'
        elif xmax>=0.00001:fmtr='%0.7f'
        elif xmax>=0.000001:fmtr='%0.8f'
        elif xmax>=0.0000001:fmtr='%0.9f'
        elif xmax>=0.00000001:fmtr='%0.10f'
        elif xmax>=0.000000001:fmtr='%0.11f'
        elif xmax>=0.0000000001:fmtr='%0.12f'
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter(fmtr))# Format Major XTicks Same As Oscilloscope
        Y_Style.set('linear')
        Y_Scale.set('-8.0,8.0')
        Y_Tick_Inc.set("2.0")
        y_scale=str(TDS210('get_vert_scale,'+data_source))# Get Scale Of Curve Data Waveform
        y_scale=float(y_scale)
        Y_Text.set('Amplitude In Volts ('+str(y_scale)+' Volts/Div)')
        ymax=(y_scale*8)/2 # Get rid Of Scientific Notation, Oscilloscope Has 8 Amplitude Divisions
        ymin=ymax*-1 # Set Horizontal Center To Zero 
        Y_Scale.set(str(ymin)+','+str(ymax))
        set_axes()
# ****************************** Channel 1 ******************************
        plt_num=1 # Make Sure To Set The Plot Number Even If Only One Plot Will Exist.
        plt1_color='aqua'# Set The line2d Color
        plt1_style='solid'# Set The line2d Style
        plt1_width=1# Set The line2d Width
        xdata=str(TDS210('get_curve_xdata'))
        xdata=xdata.replace('[','').replace(']','')# Remove Bracketst
        xdata=xdata.split(',')# Place String Values Into List
        xdata=[float(x) for x in xdata]#Convert String Values To Floats
        ydata=str(TDS210('get_curve_ydata'))
        ydata=ydata.replace('[','').replace(']','')# Remove Bracketst
        ydata=ydata.split(',')# Place String Values Into List
        ydata=[float(x) for x in ydata]#Convert String Values To Floats
        axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
        line2d,=ax.plot([],c=plt1_color,ls=plt1_style,lw=plt1_width)
        if exe_style=='loop':
            for i in arange(1,int(num_pts)+1): # Start Should Always Be 1 With Stop At Length + 1
                line2d.set_data(xdata[:i],ydata[:i])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,xdata[i-1],ydata[i-1],plt1_color,plt1_style,plt1_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
        elif exe_style=='instant': # Instantly Update Graph With List Data
            line2d.set_data(xdata,ydata)# Update The Artist
            fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
            # redraw just the points
            ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
            fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
            for i in range(0,int(num_pts)): # Get Data Ready For Saving To File
                newline=[plt_num,xdata[i],ydata[i],plt1_color,plt1_style,plt1_width]
                Plot_Data.append(str(newline))
        # Each Plot Has 7 Legions Possible
        source=str(TDS210('get_data_source'))
        meas1=str(TDS210('get_meas1_value'))
        meas2=str(TDS210('get_meas2_value'))
        meas3=str(TDS210('get_meas3_value'))
        meas4=str(TDS210('get_meas4_value'))
        legend_text=[source,'Pts. = '+str(num_pts),str(round(float(meas1),3))+' Vpk-pk',str(round(float(meas2),3))+' Vrms',str(round(float(meas3),3))+' HZ',str(round(float(meas4),3))+' Sec.','']    
        Test.plot_legends(plt_num,plt1_color,ydata,legend_text)
        canvas.draw()
# ****************************** Channel 2 ******************************
        # Set Scope Measurements For Channel 2
        str(TDS210('set_vert_select, CH2, ON')) 
        str(TDS210('set_vert_bandwidth, OFF, CH2')) 
        str(TDS210('set_vert_coupling, DC, CH2')) 
        str(TDS210('set_vert_position, -3.5, CH2')) 
        str(TDS210('set_vert_probe, 10, CH2')) 
        str(TDS210('set_vert_scale, 2, CH2')) 
        str(TDS210('set_data_source, CH2'))
        str(TDS210('set_meas1_source, CH2'))
        str(TDS210('set_meas1_type, PK2PK'))
        str(TDS210('set_meas2_source,CH2'))
        str(TDS210('set_meas2_type, CRMS'))
        str(TDS210('set_meas3_source,CH2'))
        str(TDS210('set_meas3_type, FREQ'))
        str(TDS210('set_meas4_source, CH2'))
        str(TDS210('set_meas4_type, PERIOD'))
        plt_num=2 # Make Sure To Set The Plot Number Even If Only One Plot Will Exist.
        plt2_color='yellow'# Set The line2d Color
        plt2_style='solid'# Set The line2d Style
        plt2_width=1# Set The line2d Width
        xdata=str(TDS210('get_curve_xdata'))
        xdata=xdata.replace('[','').replace(']','')# Remove Bracketst
        xdata=xdata.split(',')# Place String Values Into List
        xdata=[float(x) for x in xdata]#Convert String Values To Floats
        ydata=str(TDS210('get_curve_ydata'))
        ydata=ydata.replace('[','').replace(']','')# Remove Bracketst
        ydata=ydata.split(',')# Place String Values Into List
        ydata=[float(x) for x in ydata]#Convert String Values To Floats
        axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
        line2d,=ax.plot([],c=plt2_color,ls=plt2_style,lw=plt2_width)
        if exe_style=='loop':
            for i in arange(1,int(num_pts)+1): # Start Should Always Be 1 With Stop At Length + 1
                line2d.set_data(xdata[:i],ydata[:i])# Update The Artist
                fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
                ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
                fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
                newline=[plt_num,xdata[i-1],ydata[i-1],plt2_color,plt2_style,plt2_width]
                Plot_Data.append(str(newline))
                fig.canvas.flush_events()# Flush Pending Events And Re-paint Canvas
        elif exe_style=='instant': # Instantly Update Graph With List Data
            line2d.set_data(xdata,ydata)# Update The Artist
            fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
            # redraw just the points
            ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
            fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
            for i in range(0,int(num_pts)): # Get Data Ready For Saving To File
                newline=[plt_num,xdata[i],ydata[i],plt2_color,plt2_style,plt2_width]
                Plot_Data.append(str(newline))
        # Each Plot Has 7 Legions Possible
        source=str(TDS210('get_data_source'))
        meas1=str(TDS210('get_meas1_value'))
        meas2=str(TDS210('get_meas2_value'))
        meas3=str(TDS210('get_meas3_value'))
        meas4=str(TDS210('get_meas4_value'))
        legend_text=[source,'Pts. = '+str(num_pts),str(round(float(meas1),3))+' Vpk-pk',str(round(float(meas2),3))+' Vrms',str(round(float(meas3),3))+' HZ',str(round(float(meas4),3))+' Sec.','']    
        Test.plot_legends(plt_num,plt2_color,ydata,legend_text)
        Test.stamp_time()
        canvas.draw()
    def test_menu():
        #////******* Here You Can Modify The Menu To Suit Your Needs *******\\\\#
        tst=Menu(menubar,background='aqua',foreground='black',tearoff=0)
        menubar.add_cascade(label ='Plot Examples',menu=tst)
        tst.add_command(label ='Log Scale "Loop" Example',command=lambda:Test.log('loop'))
        tst.add_separator()
        tst.add_command(label ='Log Scale "Instant" Example',command=lambda:Test.log('instant'))
        tst.add_separator()
        tst.add_command(label ='Log Scale "Live" Example',command=lambda:Test.log('live'))
        tst.add_separator()
        tst.add_command(label ='Linear Scale "Loop" Example',command=lambda:Test.linear('loop'))
        tst.add_separator()
        tst.add_command(label ='Linear Scale "Instant" Example',command=lambda:Test.linear('instant'))
        tst.add_separator()
        tst.add_command(label ='Linear Scale "Live" Example',command=lambda:Test.linear('live'))
        tst.add_separator()
        tst.add_command(label ='Plot TDS 210 Curve Data "Loop Example"',command=lambda:Test.plot_tds210_curves('loop'))
        tst.add_separator()
        tst.add_command(label ='Plot TDS 210 Curve Data "Instant Example"',command=lambda:Test.plot_tds210_curves('instant'))
        root.config(menu=menubar)
    def plot_legends(plt_num,color,ydata,text=None):
        if plt_num==1:
            if text==None:
                Legends[1]=pat.Patch(color=color,label=Legends1_Source1.get())
                Legends[2]=pat.Patch(color=color,label=Legends1_Source2.get())
                Legends[3]=pat.Patch(color=color,label=Legends1_Source3.get())
                Legends[4]=pat.Patch(color=color,label=Legends1_Source4.get())
                Legends[5]=pat.Patch(color=color,label=Legends1_Source5.get())
                Legends[6]=pat.Patch(color=color,label=Legends1_Source6.get())
                Legends[7]=pat.Patch(color=color,label=Legends1_Source7.get())
            else:
                Legends[1]=pat.Patch(color=color,label=text[0])
                Legends1_Source1.set(text[0])
                Legends[2]=pat.Patch(color=color,label=text[1])
                Legends1_Source2.set(text[1])
                Legends[3]=pat.Patch(color=color,label=text[2])
                Legends1_Source3.set(text[2])
                Legends[4]=pat.Patch(color=color,label=text[3])
                Legends1_Source4.set(text[3])
                Legends[5]=pat.Patch(color=color,label=text[4])
                Legends1_Source5.set(text[4])
                Legends[6]=pat.Patch(color=color,label=text[5])
                Legends1_Source6.set(text[5])
                Legends[7]=pat.Patch(color=color,label=text[6])
                Legends1_Source7.set(text[6])
            # Horizontally Track The Waveform With The Legends
            ylim=ax.get_ylim()
            ymax=max(ydata)# Max Y Value In List        
            b1=0.03
            b2=1.03# Botton, Top Of Graph
            y=get_porportion(ylim[0],ylim[1],b1,b2,ymax,None)
            if y>1.03:y=1.03# Limit To Top Of Graph
            if y<0.3:y=0.3
            Legends1_Y.set(str(y))
        elif plt_num==2:
            if text==None:
                Legends[8]=pat.Patch(color=color,label=Legends2_Source1.get())
                Legends[9]=pat.Patch(color=color,label=Legends2_Source2.get())
                Legends[10]=pat.Patch(color=color,label=Legends2_Source3.get())
                Legends[11]=pat.Patch(color=color,label=Legends2_Source4.get())
                Legends[12]=pat.Patch(color=color,label=Legends2_Source5.get())
                Legends[13]=pat.Patch(color=color,label=Legends2_Source6.get())
                Legends[14]=pat.Patch(color=color,label=Legends2_Source7.get())
            else:
                Legends[8]=pat.Patch(color=color,label=text[0])
                Legends2_Source1.set(text[0])
                Legends[9]=pat.Patch(color=color,label=text[1])
                Legends2_Source2.set(text[1])
                Legends[10]=pat.Patch(color=color,label=text[2])
                Legends2_Source3.set(text[2])
                Legends[11]=pat.Patch(color=color,label=text[3])
                Legends2_Source4.set(text[3])
                Legends[12]=pat.Patch(color=color,label=text[4])
                Legends2_Source5.set(text[4])
                Legends[13]=pat.Patch(color=color,label=text[5])
                Legends2_Source6.set(text[5])
                Legends[14]=pat.Patch(color=color,label=text[6])
                Legends1_Source7.set(text[6])
            # Horizontally Track The Waveform With The Legends
            ylim=ax.get_ylim()
            ymax=max(ydata)# Max Y Value In List        
            b1=0.03
            b2=1.03# Botton, Top Of Graph
            y=get_porportion(ylim[0],ylim[1],b1,b2,ymax,None)
            if y>1.03:y=1.03# Limit To Top Of Graph
            if y<0.3:y=0.3
            Legends2_Y.set(str(y))
        if plt_num==1:
            plt.legend(bbox_to_anchor=(0.958,float(Legends1_Y.get())),facecolor=Graph_Color.get(),labelcolor='linecolor',frameon=False,
                fontsize=int(Legend_Fontsize.get()),framealpha=0,loc='upper left',handles=[Legends[1],Legends[2],Legends[3],Legends[4],Legends[5],Legends[6],Legends[7]])
        elif plt_num==2:    
            plt.legend(bbox_to_anchor=(0.958,1.15),facecolor=Graph_Color.get(),labelcolor='linecolor',frameon=False,
                fontsize=int(Legend_Fontsize.get()),framealpha=0,loc='upper left',handles=[Legends[1],Legends[2],Legends[3],Legends[4],
                                    Legends[5],Legends[6],Legends[7],Legends[8],Legends[9],Legends[10],Legends[11],Legends[12],Legends[13],Legends[14]])
    def stamp_time():
        TimeStamp.set(datetime.now())
        ax.text(-0.15, 1.1, TimeStamp.get(),
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes,
                color=Title_Color.get(), fontsize=10)        
class Init_Graph:
    def __init__(self,funct,exist=None,file_name=None):
        self.funct=funct
        self.exist=exist
        self.file_name=file_name
        X_Max_Inc.set(40)
        Y_Max_Inc.set(20)
        if self.funct=='read' or self.funct=='write':
            dir=pathlib.Path(__file__).parent.absolute()
            filename='graph_it.ini' # Program ini file
            self.ini_path=os.path.join(dir,filename)
            if self.exist==None:
                if not os.path.exists(self.ini_path):
                    set_defaults()
                    return
        config=configparser.ConfigParser()
        def read_ini_data():
            if self.funct=='read':
                dir=pathlib.Path(__file__).parent.absolute()
                filename='graph_it.ini' # Program ini file
                self.ini_path=os.path.join(dir,filename)
                if self.exist==None:
                    if not os.path.exists(self.ini_path):set_defaults()
            elif self.funct=='load':
                if self.file_name==None:
                    types=[('Plot Files', '*.plt'),('Text Document', '*.txt'),('All Files', '*.*')] 
                    directory=askopenfile(mode='r',initialdir=pathlib.Path(__file__).parent.absolute(),defaultextension=".plt",
                        filetypes=types)
                    if directory is None:return
                    else:self.ini_path=directory.name
                else:self.ini_path=os.path.join(path, self.file_name )
            config.read(self.ini_path)
            keys=["graph_color","viewport_color","title_color","major_color","minor_color",
                "x_color","xtick_color","xtick_angle","y_color","ytick_color","ytick_angle"]
            for key in keys:
                try:
                    value=config.get("COLORS",key)
                    if key=="graph_color":Graph_Color.set(value)
                    elif key=="viewport_color":Viewport_Color.set(value)
                    elif key=="title_color":Title_Color.set(value)
                    elif key=="major_color":Major_Color.set(value)
                    elif key=="minor_color":Minor_Color.set(value)
                    elif key=="x_color":X_Color.set(value)
                    elif key=="xtick_color":XTick_Color.set(value)
                    elif key=="xtick_angle":XTick_Rotation.set(value)
                    elif key=="y_color":Y_Color.set(value)
                    elif key=="ytick_color":YTick_Color.set(value)
                    elif key=="ytick_angle":YTick_Rotation.set(value)
                except configparser.NoOptionError:
                    pass
            if self.funct=='load':
                config.read(self.ini_path)
                key="timestamp"
                value=config.get("TIME_STAMP",key)
                if key=="timestamp":TimeStamp.set(value)
                config.read(self.ini_path)
                keys=["legend1_y","legend1_source1","legend1_source2","legend1_source3","legend1_source4","legend1_source5","legend1_source6","legend1_source7"]
                for key in keys:
                    try:
                        value=config.get("LEGENDS_1",key)
                        if key=="legend1_y":Legends1_Y.set(value)
                        elif key=="legend1_source1":Legends1_Source1.set(value)
                        elif key=="legend1_source2":Legends1_Source2.set(value)
                        elif key=="legend1_source3":Legends1_Source3.set(value)
                        elif key=="legend1_source4":Legends1_Source4.set(value)
                        elif key=="legend1_source5":Legends1_Source5.set(value)
                        elif key=="legend1_source6":Legends1_Source6.set(value)
                        elif key=="legend1_source7":Legends1_Source7.set(value)
                    except configparser.NoOptionError:
                        pass
                config.read(self.ini_path)
                keys=["legend2_y","legend2_source1","legend2_source2","legend2_source3","legend2_source4","legend2_source5","legend2_source6","legend2_source7"]
                for key in keys:
                    try:
                        value=config.get("LEGENDS_2",key)
                        if key=="legend2_y":Legends2_Y.set(value)
                        elif key=="legend2_source1":Legends2_Source1.set(value)
                        elif key=="legend2_source2":Legends2_Source2.set(value)
                        elif key=="legend2_source3":Legends2_Source3.set(value)
                        elif key=="legend2_source4":Legends2_Source4.set(value)
                        elif key=="legend2_source5":Legends2_Source5.set(value)
                        elif key=="legend2_source6":Legends2_Source6.set(value)
                        elif key=="legend2_source7":Legends2_Source7.set(value)
                    except configparser.NoOptionError:
                        pass
                config.read(self.ini_path)
            keys=["title","x_label","y_label"]
            for key in keys:
                try:
                    value=config.get("TEXT",key)
                    if key=="title":
                        ax.set_title(value)
                        Title.set(value)
                    elif key=="x_label":    
                        ax.set_xlabel(value)
                        X_Text.set(value)
                    elif key=="y_label":    
                        ax.set_ylabel(value)
                        Y_Text.set(value)
                except configparser.NoOptionError:
                    pass
            config.read(self.ini_path)
            keys=["major","minor","show_minor"]
            for key in keys:
                try:
                    value=config.get("GRID_STYLE",key)
                    if key=="major":Major_Style.set(value)
                    elif key=="minor":Minor_Style.set(value)    
                    elif key=="show_minor":
                        value=bool(value)
                        Show_Minor.set(value)    
                except configparser.NoOptionError:
                    pass
            config.read(self.ini_path)
            keys=["font family","title_fontsize","legend_fontsize","x_fontsize","xtick_fontsize",
                "y_fontsize","ytick_fontsize"]
            for key in keys:
                try:
                    value=config.get("FONT_SIZES",key)
                    if key=="font family":
                        family=parse_expr(value,evaluate=False)
                        ax.set_title(Title.get(),**family)
                        ax.set_xlabel(X_Text.get(),**family)
                        ax.set_ylabel(Y_Text.get(),**family)
                        Font_Family.set(value)
                    elif key=="title_fontsize":Title_Fontsize.set(value)
                    elif key=="legend_fontsize":Legend_Fontsize.set(value)
                    elif key=="x_fontsize":X_Fontsize.set(value)
                    elif key=="xtick_fontsize":XTick_Fontsize.set(value)
                    elif key=="y_fontsize":Y_Fontsize.set(value)
                    elif key=="ytick_fontsize":YTick_Fontsize.set(value)
                except configparser.NoOptionError:
                    pass
            config.read(self.ini_path)
            keys=["x_style","x_scale","x_tick_inc","x_tick_loc","x_tick_lbl","y_style","y_scale","y_tick_inc","y_tick_loc","y_tick_lbl"]
            for key in keys:
                try:
                    value=config.get("SCALE_STYLES",key)
                    if key=="x_style":X_Style.set(value)
                    elif key=="x_scale":X_Scale.set(value)
                    elif key=="x_tick_inc":X_Tick_Inc.set(value)
                    elif key=="x_tick_loc":X_Tick_Locs.set(value)
                    elif key=="x_tick_lbl":X_Tick_Lbls.set(value)
                    elif key=="y_style":Y_Style.set(value)
                    elif key=="y_scale":Y_Scale.set(value)
                    elif key=="y_tick_inc":Y_Tick_Inc.set(value)
                    elif key=="y_tick_loc":Y_Tick_Locs.set(value)
                    elif key=="y_tick_lbl":Y_Tick_Lbls.set(value)
                except configparser.NoOptionError:
                    pass
            config.read(self.ini_path)
            keys=["x","y","state","width","height"]
            for key in keys:
                try:
                    value=config.get("WINDOW",key)
                    if key=="x":x=float(value)
                    elif key=="y":y=float(value)
                    elif key=="state":root.state(value)
                    elif key=="width":width=float(value)    
                    elif key=="height":height=float(value)    
                except configparser.NoOptionError:
                    pass
            if funct=='load':# Place Data In List
                try:
                    Plot_Data.clear()
                    config.read(self.ini_path)
                    for key,value in config.items('LINE_DATA'):# Check For x,y Data
                        index=parse_expr(value)
                        Plot_Data.append(index)
                except Exception:
                    pass
            root.geometry('%dx%d+%d+%d' % (width,height,x,y))
            root.update()
            set_axes()
            if X_Tick_Locs.get()!="" and X_Tick_Lbls.get()!="":
                if X_Style.get()=="log":X_Tick_Inc.set("")
                res=X_Tick_Locs.get().strip('][').split(', ')# Convert string representation of list of Floats into list of Strings
                x_locs=list(map(float, res))# Convert List of Strings Into List of Floats
                x_lbls=X_Tick_Lbls.get().strip('[]').replace("'", "").replace(' ', '').split(',')# Convert string representation of list of Strings into list of Strings
                change_tick_labels('x',x_locs,x_lbls)# Change X Tick Labels And Locations
            if Y_Tick_Locs.get()!="" and Y_Tick_Lbls.get()!="":
                if Y_Style.get()=="log":Y_Tick_Inc.set("")
                res=Y_Tick_Locs.get().strip('][').split(', ')# Convert string representation of list of Floats into list of Strings
                y_locs=list(map(float, res))# Convert List of Strings Into List of Floats
                y_lbls=Y_Tick_Lbls.get().strip('[]').replace("'", "").replace(' ', '').split(',')# Convert string representation of list of Strings into list of Strings
                change_tick_labels('y',y_locs,y_lbls)# Change X Tick Labels And Locations
        def write_ini_data():
            if self.funct=='write':
                dir=pathlib.Path(__file__).parent.absolute()
                filename='graph_it.ini' # Program ini file
                self.ini_path=os.path.join(dir,filename)
                if self.exist==None:
                    if not os.path.exists(self.ini_path):set_defaults()
            elif self.funct=='save':
                types=[('Plot Files', '*.plt'),('Text Document', '*.txt'),('All Files', '*.*')] 
                directory=asksaveasfile(initialdir=pathlib.Path(__file__).parent.absolute(),
                    defaultextension=".plt",filetypes=types)     
                if directory is None:return
                else: self.ini_path=directory.name
            config=configparser.ConfigParser()
            config.read(self.ini_path)
            try:
                config.add_section("COLORS")
            except configparser.DuplicateSectionError:
                pass
            config.set("COLORS", "graph_color", Graph_Color.get())
            config.set("COLORS", "viewport_color", Viewport_Color.get())
            config.set("COLORS", "title_color", Title_Color.get())
            config.set("COLORS", "major_color", Major_Color.get())
            config.set("COLORS", "minor_color", Minor_Color.get())
            config.set("COLORS", "x_color", X_Color.get())
            config.set("COLORS", "xtick_color", XTick_Color.get())
            config.set("COLORS", "xtick_angle", XTick_Rotation.get())
            config.set("COLORS", "y_color", Y_Color.get())
            config.set("COLORS", "ytick_color", YTick_Color.get())
            config.set("COLORS", "ytick_angle", YTick_Rotation.get())
            if self.funct=='save':
                try:
                    config.add_section("TIME_STAMP")
                except configparser.DuplicateSectionError:
                    pass
                config.set("TIME_STAMP", "timestamp", TimeStamp.get())
                try:
                    config.add_section("LEGENDS_1")
                except configparser.DuplicateSectionError:
                    pass
                config.set("LEGENDS_1", "legend1_y", Legends1_Y.get())
                config.set("LEGENDS_1", "legend1_source1", Legends1_Source1.get())
                config.set("LEGENDS_1", "legend1_source2", Legends1_Source2.get())
                config.set("LEGENDS_1", "legend1_source3", Legends1_Source3.get())
                config.set("LEGENDS_1", "legend1_source4", Legends1_Source4.get())
                config.set("LEGENDS_1", "legend1_source5", Legends1_Source5.get())
                config.set("LEGENDS_1", "legend1_source6", Legends1_Source6.get())
                config.set("LEGENDS_1", "legend1_source7", Legends1_Source7.get())
                try:
                    config.add_section("LEGENDS_2")
                except configparser.DuplicateSectionError:
                    pass
                config.set("LEGENDS_2", "legend2_y", Legends2_Y.get())
                config.set("LEGENDS_2", "legend2_source1", Legends2_Source1.get())
                config.set("LEGENDS_2", "legend2_source2", Legends2_Source2.get())
                config.set("LEGENDS_2", "legend2_source3", Legends2_Source3.get())
                config.set("LEGENDS_2", "legend2_source4", Legends2_Source4.get())
                config.set("LEGENDS_2", "legend2_source5", Legends2_Source5.get())
                config.set("LEGENDS_2", "legend2_source6", Legends2_Source6.get())
                config.set("LEGENDS_2", "legend2_source7", Legends2_Source7.get())
            try:
                config.add_section("TEXT")
            except configparser.DuplicateSectionError:
                pass
            if exist!='keep':# Keep Default .ini Values 
                config.set("TEXT", "title", Title.get())
                config.set("TEXT", "x_label", X_Text.get())
                config.set("TEXT", "y_label", Y_Text.get())
                try:
                    config.add_section("GRID_STYLE")
                except configparser.DuplicateSectionError:
                    pass
            config.set("GRID_STYLE", "major", Major_Style.get())
            config.set("GRID_STYLE", "minor", Minor_Style.get())
            status=str(Show_Minor.get())
            config.set("GRID_STYLE", "show_minor", status)
            try:
                config.add_section("FONT_SIZES")
            except configparser.DuplicateSectionError:
                pass
            config.set("FONT_SIZES", "font family", Font_Family.get())
            config.set("FONT_SIZES", "title_fontsize", Title_Fontsize.get())
            config.set("FONT_SIZES", "legend_fontsize", Legend_Fontsize.get())
            config.set("FONT_SIZES", "x_fontsize", X_Fontsize.get())
            config.set("FONT_SIZES", "xtick_fontsize", XTick_Fontsize.get())
            config.set("FONT_SIZES", "y_fontsize", Y_Fontsize.get())
            config.set("FONT_SIZES", "ytick_fontsize", YTick_Fontsize.get())
            try:
                config.add_section("SCALE_STYLES")
            except configparser.DuplicateSectionError:
                pass
            if exist!='keep':# Keep Default .ini Values 
                config.set("SCALE_STYLES", "x_style",X_Style.get())
                config.set("SCALE_STYLES", "x_scale", X_Scale.get())
                config.set("SCALE_STYLES", "x_tick_inc", X_Tick_Inc.get())
                config.set("SCALE_STYLES", "x_tick_loc", X_Tick_Locs.get())
                config.set("SCALE_STYLES", "x_tick_lbl", X_Tick_Lbls.get())
                config.set("SCALE_STYLES", "y_style", Y_Style.get())
                config.set("SCALE_STYLES", "y_scale", Y_Scale.get())
                config.set("SCALE_STYLES", "y_tick_inc", Y_Tick_Inc.get())
                config.set("SCALE_STYLES", "y_tick_loc", Y_Tick_Locs.get())
                config.set("SCALE_STYLES", "y_tick_lbl", Y_Tick_Lbls.get())
                try:
                    config.add_section("WINDOW")
                except configparser.DuplicateSectionError:
                    pass
            if root.state()=='normal':
                config.set("WINDOW", "x", str(root.winfo_x()))
                config.set("WINDOW", "y", str(root.winfo_y()))
                config.set("WINDOW", "state", str(root.state()))
                config.set("WINDOW", "width", str(root.winfo_width()))
                config.set("WINDOW", "height", str(root.winfo_height()))
            if Plot_Data and self.funct=='save':
                try:
                    config.add_section("LINE_DATA")
                except configparser.DuplicateSectionError:
                    pass
                for i, item in enumerate(Plot_Data):
                    config.set("LINE_DATA", str(i), str(item))
            with open(self.ini_path, 'w') as configfile:
                config.write(configfile)
        if funct=='read' or funct=='load':read_ini_data()        
        elif funct=='write' or funct=='save':write_ini_data()
def get_porportion(a1,a2,b1,b2,a3=None,b3=None):
    # Returns Only 1 Value. If a3 exist, Returns b_unknown. If be Exist, Returns a_unknown
    # Only Provide 1 Value, Eigther a3 Or b3. 
    # Check for ratio inversions
    if a1 > a2: a_inverse=True
    else: a_inverse=False
    if b1 > b2: b_inverse=True
    else: b_inverse=False
    # Set inversion true or false for calculations
    if a_inverse and not b_inverse: inverse=True
    if not a_inverse and b_inverse: inverse=True
    if not a_inverse and not b_inverse: inverse=False
    if a_inverse and b_inverse: inverse=False
    # Get the numerical sizes of the ratios for K-Factor calculations
    if(a1 >= 0) and (a2 > 0):
        asize=abs(a2 - a1)
        bsize=abs(b1 - b2)
    elif(b1 > 0) and (b2 >= 0):
        asize=abs(a1 - a2)
        bsize=abs(b2 - b1)
    else:
        asize=abs(a1 - a2) #0,-100 or -10,-100 Examples
        bsize=abs(b1 - b2) #0,-100 or 10,-100
    # Calculate the K=Factors using the sizes
    Kfactor_ba=round(abs(bsize / asize),7) #X Amount Of B's Per X Amount Of A's
    Kfactor_ab=round(abs(asize / bsize),7) #X Amount Of A's Per X Amount Of B's
    # Final Calculations
    if inverse == False: # Case Not A_Inverse And Not B_Inverse Or A_Inverse And B_Inverse
        if a3 != None:# B=B1 - (K * (A1 - A))
            a3=float(a3)
            b_unknown=round(b1 - (Kfactor_ba * (a1 - a3)), 3)
            return b_unknown
        if b3!=None:# A=A1 - (K * (B1 - B))
            b3=float(b3)
            a_unknown=round(a1 - (Kfactor_ab * (b1 - b3)), 3) 
            return a_unknown
    else: # Case A_Inverse And Not B_Inverse Or Not A_Inverse And B_Inverse
        if a3!= None:# B=B1 - ((A - A1) * K)
            a3=float(a3)
            b_unknown=round(b1 - ((a3 - a1) * Kfactor_ba), 3)
            return b_unknown
        if b3!= None:# A=A1 - ((B - B1) * K)
            b3=float(b3)
            a_unknown=round(a1 - ((b3 - b1) * Kfactor_ab), 3) 
            return a_unknown
    return
def open_plot_file():
    path=askopenfile(mode='r',initialdir=pathlib.Path(__file__).parent.absolute(),defaultextension=".plt",
        filetypes=[("PLT","*.plt"),("TXT","*.txt")])
    if path is None:return
    os.popen("notepad "+path.name).read()
def load_plot_file(file_name=None):
    if file_name==None:Init_Graph('load')# Write Properties To File
    else:Init_Graph('load',None,file_name)# Write Properties To File
    if not Plot_Data:return
    t_num,p_num=0,0
    num_plts,start_index,end_index=[],[],[]
    for i in arange(0,len(Plot_Data)):# Get Number Of Plots And Set Start Points
        t_num=Plot_Data[i][0]
        if t_num>p_num:# Next Plot Number
            p_num=t_num
            num_plts.append(p_num)
            start_index.append(i)
    if len(num_plts)==1:end_index.append(len(Plot_Data))# Index 0
    else:
        if len(num_plts)>=2:# Set The End Points Of Each Plot
            for i in arange(0,len(num_plts)-1):        
                end_index.append(start_index[i+1])        
                if i==len(num_plts):end_index.append(len(Plot_Data))
            end_index.append(len(Plot_Data))# Final End Point     
    if len(num_plts)>=1:
        for p in arange(1,len(num_plts)+1):
            if p==1:index=0
            xdata,ydata=[],[]
            color=Plot_Data[index][3]# Set The line2d Color
            style=Plot_Data[index][4]# Set The line2d Style
            width=Plot_Data[index][5]# Set The line2d Width
            for i in arange(start_index[p-1],end_index[p-1]):
                xdata.append(Plot_Data[index][1])
                ydata.append(Plot_Data[index][2])
                index+=1
            axbackground=fig.canvas.copy_from_bbox(ax.bbox) # Get Copy Of Everything Inside fig.bbox
            line2d,=ax.plot([],c=color,ls=style,lw=width)
            line2d.set_data(xdata,ydata)# Update The Artist
            fig.canvas.restore_region(axbackground)# Reset Background To Copy Of fig.bbox
            # redraw just the points
            ax.draw_artist(line2d)# Draw The Animated Artist (points) From The cached Renderer
            fig.canvas.blit(ax.bbox)# Renderer To The GUI Framework For Visualization
            if p==1:Test.plot_legends(p,color,ydata)
            elif p==2:Test.plot_legends(p,color,ydata)
    ax.text(-0.15, 1.1, TimeStamp.get(),
            verticalalignment='bottom', horizontalalignment='left',
            transform=ax.transAxes,
            color=Title_Color.get(), fontsize=10)        
    canvas.draw()
def destroy():# X Icon Was Clicked Or File/Exit
    Plot_Data.clear()
    Legends.clear()
    Init_Graph('write','keep')
    for widget in root.winfo_children():
        if isinstance(widget,tk.Canvas):widget.destroy()
        else: widget.destroy()
        os._exit(0)
    return
def help():
    dir=pathlib.Path(__file__).parent.absolute()
    filename='graph-it_help.txt' # Program help file
    help_path=os.path.join(dir,filename)
    exist=os.path.exists(help_path)
    if exist:os.popen("notepad "+help_path).read()
    else:
        msg='Help File Not Found!'
        msg2='\nPlease Include graph-it_help.txt In Your Application Path.'
        messagebox.showerror("<graph-it_help>",msg+msg2)
def about():
    messagebox.showinfo('About Graph-It Easy With Tektronix TDS 210', 'Creator: Ross Waters\nEmail: RossWatersjr@gmail.com'\
        '\nLanguage: Python version 3.11.4 64-bit'\
        '\nProgram: graph-it_easy.py Created Using\ntkinter version 8.6,\nmatplotlib version 3.6.2'\
        '\nRevision \ Date: 1.3 \ 10/21/2023'\
        '\nCreated For Windows 10/11')
def config_g(which): # Configure Graph Menu
    if which=='graph color':        
        color_code=colorchooser.askcolor(title ="Choose Graph Color",initialcolor=Graph_Color.get())
        if color_code[1]==None:return
        Graph_Color.set(color_code[1])
        fig.patch.set_facecolor(Graph_Color.get())# Set the Figure Facecolor
    elif which=='font family':
        name=parse_expr(Font_Family.get(),evaluate=False)
        plt.rcParams.update({'font.family': name['fontname'][-1]})
        sample='Only Select Font Family!'
        new_font=askfont(root,text=sample,title="Choose Graph Font Family" ,family=name['fontname'][-1],
            size=14,weight='normal',slant='roman')
        if new_font=='' or new_font==None:return
        new_font['family']=new_font['family'].replace('\\', '')
        plt.rcParams.update({'font.family': new_font['family']})
        family={'fontname':plt.rcParams["font.family"]}
        Font_Family.set(str(family))
        ax.set_title(Title.get(),**family,ha='center',color=Title_Color.get(),
            fontsize=int(Title_Fontsize.get()),weight='normal',style='italic')
        ax.set_xlabel(X_Text.get(),**family,ha='center',color=X_Color.get(),
            fontsize=int(X_Fontsize.get()),weight='normal',style='italic')
        ax.set_ylabel(Y_Text.get(),**family,ha='center',color=Y_Color.get(),
            fontsize=int(Y_Fontsize.get()),weight='normal',style='italic')
    elif which=='viewport color':        
        color_code=colorchooser.askcolor(title ="Choose Viewport Color",initialcolor=Viewport_Color.get())
        if color_code[1]==None:return
        Viewport_Color.set(color_code[1])
        ax.set_facecolor(Viewport_Color.get())# Set the Graph Facecolor
    elif which=='text':        
        txt=simpledialog.askstring("<Graph Title Text>","Enter Text To Display For Graph Title.",
            parent=root,initialvalue=Title.get())
        if txt==''or txt==None:return
        set_title(txt)
    elif which=='legends':
        size=simpledialog.askinteger("<Graph Legend Font Size>","Enter Font Size To Display For Graph Legends.",
            parent=root,minvalue=6,maxvalue=32,initialvalue=Legend_Fontsize.get())
        if size is None:return
        Legend_Fontsize.set(size)
    elif which=='color':
        color_code=colorchooser.askcolor(title ="Choose Title Color",initialcolor=Title_Color.get())
        if color_code[1]==None:return
        ax.set_title(Title.get(),ha='center',color=color_code[1],
            fontsize=int(Title_Fontsize.get()),weight='normal',style='italic')
        Title_Color.set(color_code[1])
    elif which=='fontsize':
        size=simpledialog.askinteger("<Graph Title Fontsize>","Enter Font Size To Display For Graph Title.",
            parent=root,minvalue=6,maxvalue=32,initialvalue=int(Title_Fontsize.get()))
        if size is None:return
        ax.set_title(Title.get(),ha='center',color=Title_Color.get(),
        fontsize=size,weight='normal',style='italic')
        Title_Fontsize.set(str(size))
    elif which=='show minor':
        if Show_Minor.get():
            msg='Turn "Off" Graph Minor Grid Lines?'
        else:msg='Turn "On" Graph Minor Grid Lines?'
        answer=messagebox.askyesno("Show Minor Ticks",msg)
        if answer==True and Show_Minor.get():
            Show_Minor.set(False)
            plt.minorticks_off()
        elif answer==True and not Show_Minor.get():
            Show_Minor.set(True)
            plt.minorticks_on()
        elif answer==False:return    
    elif which=='major color':        
        color_code=colorchooser.askcolor(title ="Choose Major Grid Line Color",initialcolor=Major_Color.get())
        if color_code[1]==None:return
        Major_Color.set(color_code[1])
        ax.grid(which='major',color=Major_Color.get(),linestyle='solid')
        ax.grid(which='major',color=Major_Color.get(),linestyle=Major_Style.get()) 
    elif which=='minor color':        
        color_code=colorchooser.askcolor(title ="Choose Minor Grid Line Color",initialcolor=Major_Color.get())
        if color_code[1]==None:return
        Minor_Color.set(color_code[1])
        ax.grid(which='minor',color=Minor_Color.get(),linestyle='solid') 
        ax.grid(which='minor',color=Minor_Color.get(),linestyle=Minor_Style.get()) 
    # Major Grid Lines
    elif which=='major style solid':
        Major_Style.set('solid')
        ax.grid(which='major',color=Major_Color.get(),linestyle=Major_Style.get()) 
    elif which=='major style dotted':
        Major_Style.set('dotted')
        ax.grid(which='major',color=Major_Color.get(),linestyle=Major_Style.get()) 
    elif which=='major style dashed':
        Major_Style.set('dashed')
        ax.grid(which='major',color=Major_Color.get(),linestyle=Major_Style.get()) 
    elif which=='major style dashdot':
        Major_Style.set('dashdot')
        ax.grid(which='major',color=Major_Color.get(),linestyle=Major_Style.get())
    # Minor Grid Lines
    elif which=='minor style solid':
        Minor_Style.set('solid')
        ax.grid(which='minor',color=Minor_Color.get(),linestyle=Minor_Style.get()) 
    elif which=='minor style dotted':
        Minor_Style.set('dotted')
        ax.grid(which='minor',color=Minor_Color.get(),linestyle=Minor_Style.get()) 
    elif which=='minor style dashed':
        Minor_Style.set('dashed')
        ax.grid(which='minor',color=Minor_Color.get(),linestyle=Minor_Style.get()) 
    elif which=='minor style dashdot':
        Minor_Style.set('dashdot')
        ax.grid(which='minor',color=Minor_Color.get(),linestyle=Minor_Style.get())
    elif which=='clear':
        clear_graph()
    fig.canvas.draw()
def config_x(which): # Configure X Axis Menu
    if which=='text':
        txt=simpledialog.askstring("<X Label Text>","Enter Text To Display For X Label.",
            parent=root,initialvalue='X Label')
        if txt==''or txt==None:return
        X_Text.set(txt)
    elif which=='fontsize':        
        size=simpledialog.askinteger("<X Label Fontsize>","Enter Font Size To Display For X Label.",
            parent=root,minvalue=6,maxvalue=32,initialvalue=int(X_Fontsize.get()))
        if size is None:return
        X_Fontsize.set(str(size))
    elif which=='color':        
        color_code=colorchooser.askcolor(title ="Choose X Label Text Color",initialcolor=X_Color.get())
        if color_code[1]==None:return
        X_Color.set(color_code[1])
    elif which=='tick fontsize':        
        size=simpledialog.askinteger("<X Tick Labels Fontsize>","Enter Font Size To Display For X Tick Labels.",
            parent=root,minvalue=6,maxvalue=32,initialvalue=int(XTick_Fontsize.get()))
        if size is None:return
        XTick_Fontsize.set(str(size))
        ax.tick_params(axis='x',which='major',labelsize=int(XTick_Fontsize.get()))
    elif which=='tick increment':        
        x=X_Scale.get().split(",")
        x0=float(x[0])
        x1=float(x[1])
        max_inc=x1-x0
        min_inc=float(max_inc/X_Max_Inc.get())
        inc=simpledialog.askfloat("<X Major Tick Increment>","Enter Major XTick Increment.",
            parent=root,minvalue=min_inc,maxvalue=max_inc,initialvalue=X_Tick_Inc.get())
        if inc==''or inc==None:return
        X_Tick_Inc.set(inc)
        if X_Style.get()=="linear":
            start,end=ax.get_xlim()
            ax.xaxis.set_ticks(arange(start, (end+float(inc)), float(inc)))
            X_Tick_Inc.set(str(inc))
    elif which=='tick color':        
        color_code=colorchooser.askcolor(title ="Choose X Tick Label Color",initialcolor=XTick_Color.get())
        if color_code[1]==None:return
        XTick_Color.set(color_code[1])
        ax.tick_params(axis='x',colors=XTick_Color.get()) # Grid And Label The Axis Ticks
    elif which=='tick rotation':        
        angle=simpledialog.askinteger("<X Tick Labels Rotation>","Enter Enter Rotation Angle For X Tick Labels.",
            parent=root,minvalue=0,maxvalue=90,initialvalue=int(XTick_Rotation.get()))
        if angle is None:return
        plt.xticks(rotation=angle)
        XTick_Rotation.set(str(angle))
    elif which=='linear' or which=='log' or which=='symlog':
        set_scale_style('x',which)
    elif which=='x limits':
        x=simpledialog.askstring("<X Axis Scale>","Set X Axis Scale 'Left, Right'. Example: 0.0, 10.0",
            parent=root,initialvalue=X_Scale.get())
        set_scale('x',x)
        return    
    ax.set_xlabel(X_Text.get(),ha='center',color=X_Color.get(),
        fontsize=int(X_Fontsize.get()),weight='normal',style='italic')
    fig.canvas.draw()
def config_y(which): # Configure Y Axis Menu
    if which=='text':
        txt=simpledialog.askstring("<Y Label Text>","Enter Text To Display For Y Label.",
            parent=root,initialvalue='Y Label')
        if txt==''or txt==None:return
        Y_Text.set(txt)
    elif which=='fontsize':        
        size=simpledialog.askinteger("<Y Label Fontsize>","Enter Font Size To Display For Y Label.",
            parent=root,minvalue=6,maxvalue=32,initialvalue=int(Y_Fontsize.get()))
        if size is None:return
        Y_Fontsize.set(str(size))
    elif which=='color':        
        color_code=colorchooser.askcolor(title ="Choose Y Label Text Color",initialcolor=Y_Color.get())
        if color_code[1]==None:return
        Y_Color.set(color_code[1])
    elif which=='tick fontsize':        
        size=simpledialog.askinteger("<Y Tick Labels Fontsize>","Enter Font Size To Display For Y Tick Labels.",
            parent=root,minvalue=6,maxvalue=32,initialvalue=int(YTick_Fontsize.get()))
        if size is None:return
        YTick_Fontsize.set(str(size))
        ax.tick_params(axis='y',which='major',labelsize=int(YTick_Fontsize.get()))
    elif which=='tick increment':        
        y=Y_Scale.get().split(",")
        y0=float(y[0])
        y1=float(y[1])
        max_inc=y1-y0
        min_inc=float(max_inc/Y_Max_Inc.get())
        inc=simpledialog.askfloat("<X Major Tick Increment>","Enter Major XTick Increment.",
            parent=root,minvalue=min_inc,maxvalue=max_inc,initialvalue=Y_Tick_Inc.get())
        if inc==''or inc==None:return
        Y_Tick_Inc.set(inc)
        if Y_Style.get()=="linear":
            start,end=ax.get_ylim()
            ax.yaxis.set_ticks(arange(start, (end+float(inc)), float(inc)))
            Y_Tick_Inc.set(str(inc))
    elif which=='tick color':        
        color_code=colorchooser.askcolor(title ="Choose Y Tick Label Color",initialcolor=YTick_Color.get())
        if color_code[1]==None:return
        YTick_Color.set(color_code[1])
        ax.tick_params(axis='y',colors=YTick_Color.get()) # Grid And Label The Axis Ticks
    elif which=='tick rotation':        
        angle=simpledialog.askinteger("<Y Tick Labels Rotation>","Enter Enter Rotation Angle For Y Tick Labels.",
            parent=root,minvalue=0,maxvalue=90,initialvalue=int(YTick_Rotation.get()))
        plt.yticks(rotation=angle)
        if angle is None:return
        YTick_Rotation.set(str(angle))
    elif which=='linear' or which=='log' or which=='symlog':
        set_scale_style('y',which)
    elif which=='y limits':
        y=simpledialog.askstring("<Y Axis Scale>","Set Y Axis Scale 'Bottom, Top'. Example: 0.0, 10.0",
            parent=root,initialvalue=Y_Scale.get())
        set_scale('y',y)
        return
    ax.set_ylabel(Y_Text.get(),ha='center',color=Y_Color.get(),
        fontsize=int(Y_Fontsize.get()),weight='normal',style='italic')
    fig.canvas.draw()
def clear_graph(): # Gets Things Ready For New Plot Sequence
    Plot_Data.clear()
    Legends.clear()
    TimeStamp.set("")
    ax.cla()
    set_axes()
def set_title(txt):
    family=Font_Family.get()
    family=parse_expr(Font_Family.get(),evaluate=False)
    ax.set_title(txt,**family,ha='center',color=Title_Color.get(),
        fontsize=int(Title_Fontsize.get()),weight='normal',style='italic')
    Title.set(txt)    
def set_xlabel(txt):
    family=Font_Family.get()
    family=parse_expr(Font_Family.get(),evaluate=False)
    ax.set_xlabel(txt,**family,ha='center',color=X_Color.get(),
        fontsize=int(X_Fontsize.get()),weight='normal',style='italic')
    X_Text.set(txt)
def set_ylabel(txt):
    family=Font_Family.get()
    family=parse_expr(Font_Family.get(),evaluate=False)
    ax.set_ylabel(txt,**family,ha='center',color=Y_Color.get(),
        fontsize=int(Y_Fontsize.get()),weight='normal',style='italic')
    Y_Text.set(txt)
def set_scale_style(axis,style):
    if axis=='x':
        x=X_Scale.get()
        x=x.split(",")
        if style!='linear':
            x0=float(x[0])
            x1=float(x[1])
            if x0<=0 or x1<=0: 
                msg='X Axis Scale Style '+style+' Values Cannot Be Zero Or Less! Please Correct.'
                messagebox.showerror("<X Axis Scale>",msg)
                return
            ax.xaxis.reset_ticks()
            X_Tick_Inc.set("")
    if axis=='y':
        y=Y_Scale.get()
        y=y.split(",")
        if style!='linear':
            y0=float(y[0])
            y1=float(y[1])
            if y0<=0 or y1<=0: 
                msg='Y Axis Scale Style '+style+' Values Cannot Be Zero Or Less! Please Correct.'
                messagebox.showerror("<Y Axis Scale>",msg)
                return
            ax.yaxis.reset_ticks()
            Y_Tick_Inc.set("")
    if axis=='x':    
        plt.xscale(style)
        X_Style.set(style)
    elif axis=='y':    
        plt.yscale(style)
        Y_Style.set(style)
    if Show_Minor.get():plt.minorticks_on()
    else:plt.minorticks_off()
def delay(sec):
    t1=0
    t0=timeit.default_timer()
    while t1<=sec:t1=timeit.default_timer()-t0
def rnd_time(t):
    if t==2.5:new_t=round(t,2)
    elif t==0.25:new_t=round(t,3)
    elif t==0.025:new_t=round(t,4)
    elif t==0.0025:new_t=round(t,5)
    elif t==0.00025:new_t=round(t,6)
    elif t==0.000025:new_t=round(t,7)
    elif t==0.0000025:new_t=round(t,8)
    elif t==0.00000025:new_t=round(t,9)
    elif t>=0.000000025:new_t=round(t,10)
    return new_t
def change_tick_labels(axis,locs=None,lbls=None):# Changes X-Y Axis Tick Labels Without affecting Limits
    if axis=='x':
        if locs is None:    
            X_Tick_Locs.set('')
            X_Tick_Lbls.set('')
        else:    
            ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())        
            plt.xticks(locs, lbls)
            X_Tick_Locs.set(str(locs))
            X_Tick_Lbls.set(str(lbls))
            global X_Labels
            global X_Locations
            X_Labels=[item.get_text() for item in ax.get_xticklabels()]
            X_Locations=ax.get_xticks()
            ax.set_xticklabels(X_Labels)
            ax.set_xticks(X_Locations)
            fig.canvas.draw()
            fig.canvas.flush_events()
            delay(0.2)# Give Time To Update New locs,labels
    elif axis=='y':
        if locs is None:    
            Y_Tick_Locs.set('')
            Y_Tick_Lbls.set('')
        else:    
            ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())        
            plt.yticks(locs, lbls)
            Y_Tick_Locs.set(str(locs))
            Y_Tick_Lbls.set(str(lbls))
            global Y_Labels
            global Y_Locations
            Y_Labels=[item.get_text() for item in ax.get_yticklabels()]
            Y_Locations=ax.get_yticks()
            ax.set_yticklabels(Y_Labels)
            ax.set_yticks(Y_Locations)
            fig.canvas.draw()
            fig.canvas.flush_events()
            delay(0.2)# Give Time To Update New locs,labels
def set_scale(axis,scale):# Argument is String value Of X1, X2. Example: "10.0, 100.0"         
    if scale==None or scale=='':return
    try:
        if axis=='x':
            x=scale.split(",")
            x0=float(x[0])
            x1=float(x[1])
            style=X_Style.get()
            if style!='linear':
                if x0<=0 or x1<=0: 
                    msg='X Axis Scale "Log" Values Cannot Be Zero Or Less! Please Try Again.'
                    messagebox.showerror("<X Axis Scale>",msg)
                    return
            X_Scale.set(scale)
            ax.xaxis.reset_ticks()
            X_Tick_Inc.set("")
        if axis=='y':
            y=scale.split(",")
            y0=float(y[0])
            y1=float(y[1])
            style=Y_Style.get()
            if style!='linear':
                if y0<=0 or y1<=0: 
                    msg='Y Axis Scale "Log" Values Cannot Be Zero Or Less! Please Try Again.'
                    messagebox.showerror("<Y Axis Scale>",msg)
                    return
            Y_Scale.set(scale)
            ax.yaxis.reset_ticks()
            Y_Tick_Inc.set("")
        set_axes()    
    except Exception as e:
        msg=repr(e)+'Something Is Incorrect With The X Axis Values Entered! Please Try Again.'
        messagebox.showerror("<X Axis Scale>",msg)
        return 'break'
def set_axes():
    plt.cla()
    plt.grid(True)
    plt.xscale(X_Style.get())
    plt.yscale(Y_Style.get())
    if Show_Minor.get():plt.minorticks_on()
    else:plt.minorticks_off()
    x=X_Scale.get().split(',')
    if X_Style.get()!='linear':
        if float(x[0])<=0 or float(x[1])<=0: 
            msg='X Axis Scale "Log" Values Cannot Be Zero Or Less! Please Try Again.'
            messagebox.showerror("<X Axis Scale>",msg)
            return
    ax.set_xlim([float(x[0]),float(x[1])])
    if X_Style.get()=="linear":
        if X_Tick_Inc.get()!="": 
            max_inc=float(x[1])-float(x[0])
            min_inc=float(max_inc/X_Max_Inc.get())
            if float(X_Tick_Inc.get())>max_inc:
                X_Tick_Inc.set(max_inc)
            elif float(X_Tick_Inc.get())<min_inc:    
                X_Tick_Inc.set(min_inc)
            start,end=ax.get_xlim()
            inc=float(X_Tick_Inc.get())
            ax.xaxis.set_ticks(arange(start, end+inc, inc))
    y=Y_Scale.get().split(',')
    if Y_Style.get()!='linear':
        if float(y[0])<=0 or float(y[1])<=0: 
            msg='Y Axis Scale "Log" Values Cannot Be Zero Or Less! Please Try Again.'
            messagebox.showerror("<Y Axis Scale>",msg)
            return
    ax.set_ylim([float(y[0]),float(y[1])])
    if Y_Style.get()=="linear": 
        if Y_Tick_Inc.get()!="": 
            max_inc=float(y[1])-float(y[0])
            min_inc=float(max_inc/Y_Max_Inc.get())
            if float(Y_Tick_Inc.get())>max_inc:
                Y_Tick_Inc.set(max_inc)
            elif float(Y_Tick_Inc.get())<min_inc:    
                Y_Tick_Inc.set(min_inc)
            start,end=ax.get_ylim()
            inc=float(Y_Tick_Inc.get())
            ax.yaxis.set_ticks(arange(start, end+inc, inc))
    fig.patch.set_facecolor(Graph_Color.get())# Set the Graph Facecolor
    ax.set_facecolor(Viewport_Color.get())# Set the Graph Facecolor
    fig.add_axes(ax)        
    ax.tick_params(axis='x',colors=XTick_Color.get()) # Grid And Label The Axis Ticks
    ax.tick_params(axis='y',colors=YTick_Color.get())
    ax.tick_params(axis='x',which='major',labelsize=int(XTick_Fontsize.get()))
    ax.tick_params(axis='y',which='major',labelsize=int(YTick_Fontsize.get()))
    ax.grid(which='major',color=Major_Color.get(),linestyle=Major_Style.get()) # Turn Both Major and Minor Ticks On
    ax.grid(which='minor',color=Minor_Color.get(),linestyle=Minor_Style.get())
    plt.xticks(rotation=int(XTick_Rotation.get()))
    plt.yticks(rotation=int(YTick_Rotation.get()))
    name=parse_expr(Font_Family.get(),evaluate=False)
    plt.rcParams.update({'font.family':name['fontname'][-1]})
    family=parse_expr(Font_Family.get(),evaluate=False)
    ax.set_title(Title.get(),**family,ha='center',color=Title_Color.get(),
        fontsize=int(Title_Fontsize.get()),weight='normal',style='italic')
    ax.set_xlabel(X_Text.get(),**family,ha='center',color=X_Color.get(),
        fontsize=int(X_Fontsize.get()),weight='normal',style='italic')
    ax.set_ylabel(Y_Text.get(),**family,ha='center',color=Y_Color.get(),
        fontsize=int(Y_Fontsize.get()),weight='normal',style='italic')
    ax.autoscale_view(False,False,False)
    ax.format_coord = lambda x, y: 'x={:g}, y={:g}'.format(x, y)# Restore Mouse Coords.
    fig.canvas.draw()
    fig.canvas.flush_events()
def set_defaults():# If No INI FILE Exist, Setup With tk Variables And Create File
    Gpib_Initialized.set(False)
    Oscope_Initialized.set(False)
    Graph_Color.set('#420021')
    Font_Family.set("{'fontname': ['Arial']}")
    Viewport_Color.set('#000024')
    Title_Color.set('#00ffff')
    Title_Fontsize.set('14')
    Title.set('Title Text')
    Major_Color.set('#808080')
    Minor_Color.set('#808080')
    Major_Style.set('solid')
    Minor_Style.set('dotted')
    Show_Minor.set('True')
    Legend_Fontsize.set('9')
    X_Color.set('#00ffff')
    XTick_Color.set('#ffffff')
    X_Tick_Lbls.set('')
    X_Tick_Locs.set('')
    XTick_Rotation.set('0') 
    X_Fontsize.set('12')
    XTick_Fontsize.set('8')
    X_Text.set('X Axis Text')
    X_Style.set('linear')
    X_Scale.set('0.0, 100.0')
    X_Tick_Inc.set("10.0")
    Y_Tick_Lbls.set('')
    Y_Tick_Locs.set('')
    YTick_Rotation.set('0') 
    Y_Color.set('#00ffff')
    YTick_Color.set('#ffffff')
    Y_Fontsize.set('12')
    YTick_Fontsize.set('8')
    Y_Text.set('Y Axis Text')
    Y_Style.set('linear')
    Y_Scale.set('-10.0, 10.0')
    Y_Tick_Inc.set("2.5")
    Legends1_Y.set("")
    Legends1_Source1.set("")
    Legends1_Source2.set("")
    Legends1_Source3.set("")
    Legends1_Source4.set("")
    Legends1_Source5.set("")
    Legends1_Source6.set("")
    Legends1_Source7.set("")
    Legends2_Y.set("")
    Legends2_Source1.set("")
    Legends2_Source2.set("")
    Legends2_Source3.set("")
    Legends2_Source4.set("")
    Legends2_Source5.set("")
    Legends2_Source6.set("")
    Legends2_Source7.set("")
    x=(screen_width/2)-(root_wid/2)
    y=(screen_height/2)-(root_hgt/2)
    Gpib_Initialized.set(False)
    Oscope_Initialized.set(False)
    root.geometry('%dx%d+%d+%d' % (root_wid,root_hgt,x,y,))
    root.update()
    Init_Graph('write','pass')
    Init_Graph('read')
if __name__ == "__main__":
    root=tk.Tk()
    dir=pathlib.Path(__file__).parent.absolute()
    filename='graph-it.ico' # Program icon
    ico_path=os.path.join(dir, filename)
    root.iconbitmap(default=ico_path) # root and children
    root.font=font.Font(family='Lucida Sans',size=9,weight='normal',slant='italic')# Menu Font
    pb_font=font.Font(family='Lucida Sans',size=12,weight='normal',slant='italic')# Menu Font
    root.title('Graph-It Easy With GPIB')
    monitor_info=GetMonitorInfo(MonitorFromPoint((0,0)))
    work_area=monitor_info.get("Work")
    monitor_area=monitor_info.get("Monitor")
    screen_width=work_area[2]
    screen_height=work_area[3]
    taskbar_hgt=(monitor_area[3]-work_area[3])
    root.configure(bg='gray')
    root.option_add("*Font",root.font)
    root.protocol("WM_DELETE_WINDOW",destroy)
    fig=plt.figure(figsize=(10,10),facecolor='black',frameon=True,)
    ax=plt.axes()
    fig.add_axes(ax)
    canvas=FigureCanvasTkAgg(fig,master=root) # Create The Canvas
    toolbar=NavigationToolbar2Tk(canvas,root) # create Matplotlib toolbar
    tb_hgt=toolbar.winfo_reqheight()
    root_hgt=((screen_height-taskbar_hgt)/2.0)+tb_hgt 
    root_wid=root_hgt*2.0
    canvas.get_tk_widget().pack(fill='both',pady=(0,0)) # place Canvas and Toolbar on Tkinter window
    Plot_Data=[]
    Graph_Color=tk.StringVar()
    GraphIt_Folder=tk.StringVar()
    Font_Family=tk.StringVar()
    Viewport_Color=tk.StringVar()
    Title_Color=tk.StringVar()
    Major_Color=tk.StringVar()
    Minor_Color=tk.StringVar()
    X_Color=tk.StringVar()
    X_Labels=[]
    Empty_X_Lbls=[]
    X_Tick_Lbls=tk.StringVar()
    X_Tick_Locs=tk.StringVar()
    XTick_Rotation=tk.StringVar()
    XTick_Color=tk.StringVar()
    Y_Color=tk.StringVar()
    Y_Labels=[]
    Empty_Y_Lbls=[]
    Y_Tick_Lbls=tk.StringVar()
    Y_Tick_Locs=tk.StringVar()
    YTick_Rotation=tk.StringVar()
    YTick_Color=tk.StringVar()
    Title_Fontsize=tk.StringVar()
    X_Fontsize=tk.StringVar()
    XTick_Fontsize=tk.StringVar()
    Y_Fontsize=tk.StringVar()
    YTick_Fontsize=tk.StringVar()
    Title=tk.StringVar()
    Major_Style=tk.StringVar()
    Minor_Style=tk.StringVar()
    Show_Minor=tk.BooleanVar()
    X_Text=tk.StringVar()
    X_Style=tk.StringVar()
    X_Scale=tk.StringVar()
    X_Tick_Inc=tk.StringVar()
    X_Max_Inc=tk.IntVar()
    Y_Text=tk.StringVar()
    Y_Style=tk.StringVar()
    Y_Scale=tk.StringVar()
    Y_Tick_Inc=tk.StringVar()
    Y_Max_Inc=tk.IntVar()
    # Plot 1 Legends
    Legends={}
    Legends1_Y=tk.StringVar()
    Legends1_Source1=tk.StringVar()
    Legends1_Source2=tk.StringVar()
    Legends1_Source3=tk.StringVar()
    Legends1_Source4=tk.StringVar()
    Legends1_Source5=tk.StringVar()
    Legends1_Source6=tk.StringVar()
    Legends1_Source7=tk.StringVar()
    # Plot 2 Legends    
    Legends2_Y=tk.StringVar()
    Legends2_Source1=tk.StringVar()
    Legends2_Source2=tk.StringVar()
    Legends2_Source3=tk.StringVar()
    Legends2_Source4=tk.StringVar()
    Legends2_Source5=tk.StringVar()
    Legends2_Source6=tk.StringVar()
    Legends2_Source7=tk.StringVar()
    Gpib_Initialized=tk.BooleanVar() # For TDS210 Class
    Oscope_Initialized=tk.BooleanVar() # For TDS210 Class
    Legend_Fontsize=tk.StringVar()
    TimeStamp=tk.StringVar()
    menubar=Menu(root)# Create Menubar
    file=Menu(menubar,background='aqua',foreground='black',tearoff=0)# File Menu and commands
    menubar.add_cascade(label='File',menu=file)
    file.add_command(label='Open Plot File Data To View',command=lambda:open_plot_file())
    file.add_separator()
    file.add_command(label='Save Plot File Data As',command=lambda:Init_Graph('save'))
    file.add_separator()
    file.add_command(label='Load Plot File Data To Graph',command=lambda:load_plot_file())
    file.add_separator()
    file.add_command(label='Exit',command=lambda:destroy())
    file.add_separator()
    configure_g=Menu(menubar,background='aqua',foreground='black',tearoff=0)# Configure Graph Menu and commands
    menubar.add_cascade(label ='Configure Graph',menu=configure_g)
    configure_g.add_command(label='Graph Face Color',command=lambda:config_g('graph color'))
    configure_g.add_separator()
    configure_g.add_command(label='Graph Font Family',command=lambda:config_g('font family'))
    configure_g.add_separator()
    configure_g.add_command(label='Graph Legend Font Size',command=lambda:config_g('legends'))
    configure_g.add_separator()
    title=Menu(menubar,background='aqua',foreground='black',tearoff=0) # SubMenu
    title.add_command(label='Text',command=lambda:config_g('text'))
    title.add_command(label='Color',command=lambda:config_g('color'))
    title.add_command(label='Font Size',command=lambda:config_g('fontsize'))
    configure_g.add_cascade(label='Graph Title',menu=title)
    configure_g.add_separator()
    configure_vp=Menu(menubar,background='aqua',foreground='black',tearoff=0)# Configure Viewport Menu and commands
    menubar.add_cascade(label='Configure Viewport',menu=configure_vp)
    configure_vp.add_command(label='Viewport Face Color',command=lambda:config_g('viewport color'))
    configure_vp.add_separator()
    configure_vp.add_command(label='Viewport Major Grid Line Color',command=lambda:config_g('major color'))
    configure_vp.add_separator()
    major=Menu(menubar,background='aqua',foreground='black',tearoff=0) # SubMenu
    major.add_command(label='Solid',command=lambda:config_g('major style solid'))
    major.add_command(label='Dotted',command=lambda:config_g('major style dotted'))
    major.add_command(label='Dashed',command=lambda:config_g('major style dashed'))
    major.add_command(label='DashDot',command=lambda:config_g('major style dashdot'))
    configure_vp.add_cascade(label='Viewport Major Grid Line Style',menu=major)
    configure_vp.add_separator()
    configure_vp.add_command(label ='Viewport Minor Grid Line Color',command=lambda:config_g('minor color'))
    configure_vp.add_separator()
    minor=Menu(menubar,background='aqua',foreground='black',tearoff=0) # SubMenu
    minor.add_command(label='Solid',command=lambda:config_g('minor style solid'))
    minor.add_command(label='Dotted',command=lambda:config_g('minor style dotted'))
    minor.add_command(label='Dashed',command=lambda:config_g('minor style dashed'))
    minor.add_command(label='DashDot',command=lambda:config_g('minor style dashdot'))
    configure_vp.add_cascade(label='Viewport Minor Grid Line Style',menu=minor)
    configure_vp.add_separator()
    configure_vp.add_command(label='Show Minor Grid Lines',command=lambda:config_g('show minor'))
    configure_vp.add_separator()
    configure_vp.add_command(label='Clear Viewport Data',command=lambda:config_g('clear'))
    configure_vp.add_separator()
    configure_x=Menu(menubar,background='aqua',foreground='black',tearoff=0)# Configure X Menu and commands
    menubar.add_cascade(label ='Configure X Axis',menu=configure_x)
    x_label=Menu(menubar,background='aqua',foreground='black',tearoff=0) # SubMenu
    x_label.add_command(label='Text',command=lambda:config_x('text'))
    x_label.add_command(label='Color',command=lambda:config_x('color'))
    x_label.add_command(label='Font Size',command=lambda:config_x('fontsize'))
    configure_x.add_cascade(label='X Axis Label',menu=x_label)
    configure_x.add_separator()
    style_x=Menu(menubar,background='aqua',foreground='black',tearoff=0) # SubMenu
    style_x.add_command(label='Linear',command=lambda:config_x('linear'))
    style_x.add_command(label='Log',command=lambda:config_x('log'))
    style_x.add_command(label='SymLog',command=lambda:config_x('symlog'))
    configure_x.add_command(label='X Axis Scale',command=lambda:config_x('x limits'))
    configure_x.add_separator()
    configure_x.add_cascade(label='X Axis Scale Style',menu=style_x)
    configure_x.add_separator()
    configure_x.add_command(label='X Major Tick Increment',command=lambda:config_x('tick increment'))
    configure_x.add_separator()
    configure_x.add_command(label='X Tick Label Color',command=lambda:config_x('tick color'))
    configure_x.add_separator()
    configure_x.add_command(label='X Tick Label Font Size',command=lambda:config_x('tick fontsize'))
    configure_x.add_separator()
    configure_x.add_command(label='X Tick Label Rotation',command=lambda:config_x('tick rotation'))
    configure_x.add_separator()
    configure_y=Menu(menubar,background='aqua',foreground='black',tearoff=0)# Configure Y Menu and commands
    menubar.add_cascade(label ='Configure Y Axis',menu=configure_y)
    y_label=Menu(menubar,background='aqua',foreground='black',tearoff=0) # SubMenu
    y_label.add_command(label='Text',command=lambda:config_y('text'))
    y_label.add_command(label='Color',command=lambda:config_y('color'))
    y_label.add_command(label='Font Size',command=lambda:config_y('fontsize'))
    configure_y.add_cascade(label='Y Axis Label',menu=y_label)
    configure_y.add_separator()
    style_y=Menu(menubar,background='aqua',foreground='black',tearoff=0) # SubMenu
    style_y.add_command(label='Linear',command=lambda:config_y('linear'))
    style_y.add_command(label='Log',command=lambda:config_y('log'))
    style_y.add_command(label='SymLog',command=lambda:config_y('symlog'))
    configure_y.add_command(label ='Y Axis Scale',command=lambda:config_y('y limits'))
    configure_y.add_separator()
    configure_y.add_cascade(label='Y Axis Scale Style',menu=style_y)
    configure_y.add_separator()
    configure_y.add_command(label='Y Major Tick Increment',command=lambda:config_y('tick increment'))
    configure_y.add_separator()
    configure_y.add_command(label='Y Tick Label Color',command=lambda:config_y('tick color'))
    configure_y.add_separator()
    configure_y.add_command(label='Y Tick Label Font Size',command=lambda:config_y('tick fontsize'))
    configure_y.add_separator()
    configure_y.add_command(label='Y Tick Label Rotation',command=lambda:config_y('tick rotation'))
    configure_y.add_separator()
    Test.test_menu()# Create Test Menu
    configure_help=Menu(menubar,background='aqua',foreground='black',tearoff=0)# File Menu and commands
    menubar.add_cascade(label='Help',menu=configure_help)
    configure_help.add_command(label='Help',command=lambda:help())
    configure_help.add_separator()
    configure_help.add_command(label='About',command=lambda:about())
    configure_help.add_separator()
    root.config(menu=menubar)
    dir=os.path.expanduser( '~' )# Create Save Folder For .plt Files
    path=os.path.join(dir,'Graph-it Files', '' )
    GraphIt_Folder.set(path)
    if not os.path.isdir(GraphIt_Folder.get()):os.mkdir(path,mode = 0o666) #Read/Write
    Init_Graph('read') # Read And Initialize Properties
root.mainloop()    
