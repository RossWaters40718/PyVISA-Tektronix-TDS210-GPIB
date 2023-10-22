import tkinter as tk
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, StringVar, Menu, IntVar, font, messagebox
from win32api import GetMonitorInfo, MonitorFromPoint
import pathlib
import os
import pyvisa
class TDS210():
# All Calls Outside This Class Must Be Of String Type With Or Without Return Values.
# Examples: Set Command, str(TDS210('set_data_encoding, ASCII')), Get Command, encdg=str(TDS210('get_data_encoding'))
# Return Values May Or May not Be Specified With The Set Commands Which Will Return The Set Value If Completed.  
# The Oscilloscope GPIB Address Is Set At Address '5' And Is Set During Initialization Of This Class.
# You May Change The Oscilloscope Address To Your Preference In def __init__.

########### REQUIREMENTS ##########
# NI VISA For Windows 11 64 Bit, (2022 Q3) Or (2023 Q2) Installed
# PyVISA 1.13.0 Or Latest Version
# Tektronix TDS 210/220 Oscilloscope Or Equivalent With GPIB Interface
# Tested With (NI GPIB-USB-HS+) Controller
# Tested Using Python Version 3.11.4 64 Bit
# This Class Assumes That Pyvisa And NI-VISA Are Installed And Working Correctly.

# ////////// Tektronix TDS 210/220 Oscilloscope \\\\\\\\\\
# TDS_Dic Has 2 Keys. 'Functions' Is Used To Populate Select Combobox ,'Arguments' Is Used To
# Display Argument Choices. List TDS_CMDS Which Contains The Actual 
# GPIB Messages Sent. TDS_CMDS Is Located In gpib_send() And Is Dynamic Type (Changing). 
# Both Dictionary Keys And List Must Have The Same Corresponding Indices For The Commands Being Called.
# The Dictionary Key List Values Must Correlate!
# This Greatly Reduces Code By Using 1 Function gpib_send() For Almost All Commands
# If TDS210 Class Is To be Used Without A GUI Interface, TDS_Dic['Arguments'] May Be deleted
# And Send Commands As Shown In TDS_Dic['Functions']. Example: response=str(TDS210('set_vert_coupling, DC, CH1'))   
    TDS_Dic={'Functions':['**** Select GPIB Command ****','**** UTILITIES ****','oscope_self_cal','oscope_auto_set','oscope_factory_set','oscope_reset',
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
        'get_vbars_pos2','get_vbars_units','get_cursors_vbars','get_vbars_delta'],
        #/////////////////////////////////////////////ARGUMENTS///////////////////////////////////////////////////
        'Arguments':['None','**** UTIL ****','None','None','None','None','None','(ALL, NONE)','Memory Location: (1 - 5)',
        'Memory Location: (1 - 5)','**** DISPLAY ****','Style: (DOTS, VECTORS)','Persistence: (1, 2, 5, INF, OFF)',
        'Format: (XY, YT)','Contrast: (1 - 100)','Style: (None) Returns Display Style','Persistence: (None) Returns Display Persistence',
        'FORMAT: (None) Returns Display Format', 'Contrast: (None) Returns Display Contrast','**** VERT ****',
        'Waveform: (CH1, CH2, MATH, REFA, REFB), (ON, OFF),','Bandwidth: (ON, OFF), Channel: (CH1, CH2)',
        'Coupling: (AC, DC, GND), Channel: (CH1, CH2)','Position: (+- Divisions From Center), Channel: (CH1, CH2)',
        'Probe: (1, 10, 100, 1000), Channel: (CH1, CH2)',
        'Scale: (1X Probe(2mv/div - 5v/div), 10x Probe(20mv/div - 50v/div) 2mv="2E-3"), Channel: (CH1, CH2)',
        'Math: ("CH1 + CH2", "CH1 - CH2","CH2 - CH1","-CH1", "-CH2") Quotes Are Required!',
        'Select Waveform: (CH1, CH2, MATH, REFA, REFB) Returns Selected Display Waveform Status',
        'Select (None) Returns Display Status Of All Waveforms','Bandwidth, Channel: (CH1, CH2) Returns Channel Bandwidth',
        'Coupling Channel: (CH1, CH2) Returns Channel Coupling','Position Channel: (CH1, CH2) Returns Channel Position',
        'Probe Channel: (CH1, CH2) Returns Channel Probe Setting','Scale Channel: (CH1, CH2) Returns Channel Scale',
        'Math: (None) Returns Math Defined','**** HORIZ ****','Main Window Scale: (5 nsec - 5 sec In 1-2.5-5 Sequence)',
        'Main Window Position: (+- Center Gratical To Trigger Point In Seconds)','Horizontal View: (MAIN, WINDOW, ZONE)',
        'Delay Scale For Window And Window Zone, Scale (5 nsec - 5 sec In 1-2.5-5 Sequence)',
        'Delay Position For Window And Window Zone Position: (+- Center Gratical To Trigger Point In Seconds)',
        'Horizontal All: (None) Returns All Horizontal Settings','Horizontal Main: (None) Returns Main Timebase Settings',
        'Horizontal Scale: (None Returns Horizontal Main Scale)','Horizontal Position: (None) Returns Horizontal Main Position',
        'Horizontal View: (None) Returns Horizontal Display View',
        'Horizontal Delay Scale: (None) Returns Timebase For Window Or Window Zone',
        'Horizontal_delay_position: (None) Returns Timebase Horizontal Position For Window And Window Zone',
        '**** TRIG ****','(None), Forces A Trigger Event','(None), Sets Trigger Level At 50% Of The Signal Value',
        'Mode: (AUTO, NORMAL)','Type: (EDGE, VIDEO)','Level In Volts: (Somewhere Along The Signal Amplitude)',
        'Edge Coupling: (AC, DC, HFREJ, LFREJ)','Edge Slope: (FALL, RISE)','Edge Source: (CH1, CH2, EXT, EXT5, LINE)',
        'HoldOff Value: (500nsec - 10sec)','Video Polarity: (INVERTED, NORMAL)','Video Source: (CH1, CH2, EXT, EXT5)',
        'Video Sync: (FIELD, LINE)','Trigger: (None) Returns All Trigger Settings',
        'Trigger Main: (None) Returns The Main Trigger Settings','Trigger Mode: (None) Returns The Main Trigger Mode',
        'Trigger Type: (None) Returns The Main Trigger Type','Trigger Level: (None) Returns The Main Trigger Level',
        'Edge Coupling: (None) Returns The Main Trigger Edge Coupling','Edge Slope: (None) Returns The Main Trigger Edge Slope',
        'Edge Source: (None) Returns The Main Trigger Edge Source','Holdoff: (None) Returns The Main Trigger Holdoff Value',
        'Video Polarity: (None) Returns The Main Trigger Video Polarity',
        'Video Source: (None) Returns The Main Trigger Video Source','Video Sync: (None) Returns The Main Trigger Video Sync',
        'Trigger State: (None) Returns The Triggering System State','**** AQUIRE SECTION ****',
        'Mode: (SAMPLE, PEAKDETECT, AVERAGE)','Averages: (4, 16, 64, 128)','State: (OFF, ON, RUN, STOP)',
        'Stop Ater: (RUNSTOP, SEQUENCE)','Acquire: (None) Returns All Current Acquisition Parameters',
        'Mode: (None) Returns Acquisition Mode','Average: (None) Returns Waveform Acquisition Average',
        'State: (None) Returns State Of The Acquisition Mode','Stop After: (None) Returns Run Sequence Of The Acquisition Mode',
        '**** MEAS ****','Source: (CH1, CH2)','Type: (FREQ, MEAN, PERIOD, PK2PK, CRMS, NONE)','Source: (CH1, CH2)',
        'Type: (FREQ, MEAN, PERIOD, PK2PK, CRMS, NONE)','Source: (CH1, CH2)','Type: (FREQ, MEAN, PERIOD, PK2PK, CRMS, NONE)',
        'Source: (CH1, CH2)','Type: (FREQ, MEAN, PERIOD, PK2PK, CRMS, NONE)','Source: (CH1, CH2)',
        'Type: (FREQ, MEAN, PERIOD, PK2PK, CRMS, NONE)','Settings: (None) Returns All Measurement Settings',
        'Source: (None) Returns Meas1 Source','Type: (None) Returns Meas1 Type','Value: (None) Returns Meas1 Value',
        'Units: (None) Returns Meas1 Units','Source: (None) Returns Meas2 Source','Type: (None) Returns Meas2 Type',
        'Value: (None) Returns Meas2 Value','Units: (None) Returns Meas2 Units','Source: (None) Returns Meas3 Source',
        'Type: (None) Returns Meas3 Type','Value: (None) Returns Meas3 Value','Units: (None) Returns Meas3 Units',
        'Source: (None) Returns Meas4 Source','Type: (None) Returns Meas4 Type','Value: (None) Returns Meas4 Value',
        'Units: (None) Returns Meas4 Units','Source: (None) Returns Immed Source','Type: (None) Returns Immed Type',
        'Value: (None) Returns Immed Value','Units: (None) Returns Immed Units','**** DATA, CURVE, WFM ****',
        'Data Init: (None) Sets Waveform Data To Factory Default','Destination: (REFA, REFB) Incomming Waveform Data Storage Location ',
        'Encoding: (ASCII, RIBINARY, RPBINARY, SRIBINARY) Sets Waveform Data Formatting',
        'Source: (CH1, CH2, MATH, REFA, REFB2) Sets Which Data Will Be Transfered From Instrument To CURVE?, WFMPRE?, WAVFRM?',
        'Start: (1 - 2500) Sets The Starting Data Point For Waveform Transfer',
        'Stop: (1 - 2500) Sets The End Data point For Waveform Transfer',
        'Width: (1, 2) Sets The Number Of Bytes Per Waveform Data Point To Be Transfered',
        'Data: (None) Returns All Waveform Data Parameters',
        'X Curve: (None) Retrieve X Data Specified By Data Source, Data Start, Data Stop, Data Width',
        'Y Curve: (None) Retrieve Y Data Specified By Data Source, Data Start, Data Stop, Data Width',
        'Destination (None) Retrieve Waveform Data Storage Location ','Encoding: (None) Retrieves Waveform Data Formatting',
        'Source: (None) Retrieves Which Data Will Be Transfered From Instrument To CURVE?, WFMPRE?, WAVFRM? ',
        'Start: (None) Retrieves The Starting Data Point For Waveform Transfer',
        'Stop: (None) Retrieves The End Data point For Waveform Transfer ',
        'Width: (None) Retrieves The Number Of Bytes Per Waveform Data Point To Be Transfered',
        'Points: (None) Retrieves Number Of Waveform Points',
        'X Increment: (None) Retrieves Waveform Increment Between Points',"Offset: (None): Retrieves Waveform Y Offset",
        'Y Multiple: (None) Retrieves Multiplier For Waveform Digitized Points.',
        'Y Zero: (None) Retrieves Waveform Y Zero','**** CURSOR ****','Type: (HBARS, VBARS, OFF) Sets The Curson Type',
        'Source: (CH1, CH2, MATH, REFA, REFB) Sets Type For Vertical And Horizontal Cursors',
        'Position 1: (Volts) Sets HBAR Cursor Position 1 In Volts Units','Position 2: (Volts) Sets HBAR Cursor Position 2 In Volts Units',
        'Position 1: (Time In Seconds) Center = 0, Sets VBAR Cursor Position 1 In Time Units',
        'Position 2: (Time In Seconds) Center = 0, Sets VBAR Cursor Position 2 In Time Units',
        'UNITS: (SECONDS. HERTZ) Sets Units For The VBAR Cursor','Cursor: (None) Returns All Cursor Settings',
        'Type: (None) Returns The Selected Cursor Type','Source: (None) Returns The Selected Waveform Associated With The Cursor',
        'Position 1: (None) Returns The Horizontal Cursor Bar Position 1','Position 2: (None) Returns The Horizontal Cursor Bar Position 2',
        'Units: (None) Returns The Horizontal Cursor Bar Units','HBARS (None) Returns Horizontal Bar Settings',
        'Delta (None) Returns Difference Between The 2 Horizontal Bars In Horizontal Units',
        'Position 1: (None) Returns The Vertical Cursor Bar Position 1','Position 2: (None) Returns The Vertical Cursor Bar Position 2',
        'Units: (None) Returns The Vertical Cursor Bar Units','VBARS (None) Returns Vertical Bar Settings',
        'Delta (None) Returns Difference Between The 2 Vertical Bars In Vertical Units']}
    def __init__(self, function): # function Contains Function Name And Arguments. See TDS_Dic['Functions']
        super().__init__()
        self.args=[]# Make Sure All Arguments Are In Correct Format Before Call.
        args=function.split(",")# Extract Function And Arguments Into List
        if args[0][-1]=='*':return # cbo Section Seperators
        if len(args)>=1:# Sets Function
            self.args.append(str(args[0]).replace(" ", ""))# Function Argument
            self.funct=str(args[0])
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
        for i, items in enumerate(TDS210.TDS_Dic['Functions']):# Find Index Based On Function Text Instead Of Using cbo Index.
            if self.funct in items:                            # This Allows TDS210 Class To Be Used Without GUI Later.
                self.index=i
                break        
        query.focus()
        query.delete('1.0','end')
        Waveform_Data.focus()
        Waveform_Data.delete('1.0','end')
        Waveform_Data.insert('end','Curve Data')
    def __str__(self):
        def gpib_initialize():#********** Controller  Initialization **********
            try:
                global Gpib_Initialized
                global res
                msg1='GPIB Bus Could Take Up To 30 Seconds To Initialize.\n'
                msg2='You Will Be Prompted When Completed!\n'
                msg3='Press OK Button To Start.'
                msg=msg1+msg2+msg3
                messagebox.showinfo('GPIB Bus Initialization', msg)
                res=self.rm.list_resources() # Time Consuming
                ctrl=self.rm.open_resource('GPIB::INTFC')
                interface_num=ctrl.interface_number
                interface_name["text"]=ctrl.resource_manufacturer_name
                interface_address["text"]='Controller'+str(interface_num)+ ' @ '+str(ctrl.resource_name)[ctrl.resource_name.find("'")+1:ctrl.resource_name.find(':')]
                self.ctrl_port=str(ctrl.resource_name)[ctrl.resource_name.find("'")+1:ctrl.resource_name.find(':')]
                self.rtn_val='Initialization Passed'
                interface_stat["text"]=self.rtn_val
                msg1=interface_name["text"]+' Controller Initialization Complete!\n'
                if len(res)!=0:msg2='Instruments Detected @ '+str(self.rm.list_resources())
                else:msg2='No Instruments Detected Connected To GPIB Bus!'
                messagebox.showinfo(interface_name["text"]+' GPIB Bus Initialization', msg1+msg2)
                Gpib_Initialized=True
                return(self.rtn_val)
            except Exception as e:
                self.rtn_val='Initialization Failed'
                interface_stat["text"]='Initialization Failed'
                msg1='Exception occurred while code execution:\n'
                msg2=repr(e)+'GPIB Bus Controller Initialization'
                messagebox.showerror('GPIB Controller Initialization',msg1+msg2)
                return 'break'
        def oscope_initialize():#********** Instrument Initialization **********        
            try:
                global Oscope
                global Oscope_Initialized
                if len(res)>=1:
                    oscope_port=str(self.ctrl_port+'::'+self.oscope_address+'::INSTR')
                    if oscope_port in res:
                        Oscope=self.rm.open_resource(oscope_port)
                        idn=(Oscope.query("*IDN?"))
                        if idn!='0' and idn!='':
                            Oscope.timeout=100000# 100s
                            Oscope.write_termination='\n'
                            Oscope.read_termination='\n'
                            Oscope.write("DISPLAY:CONTRAST 70")
                            oscope_stat["text"]='Initialization Passed'
                            name=idn.split(',')
                            oscope_name["text"]=name[0]+ ' '+name[1]
                            oscope_address["text"]='Oscilloscope @ '+str('GPIB'+ self.oscope_address)
                            msg1=oscope_name["text"]+' Initialization Complete!\n'
                            msg2='Oscilloscope Detected @ '+str(oscope_port)
                            msg3='\nOscilloscope IDN: '+str(idn)
                            messagebox.showinfo(oscope_name["text"]+' Oscilloscope Initialization',msg1+msg2+msg3)
                            Oscope_Initialized=True
                            self.rtn_val='Pass'
                            return(self.rtn_val)
                    else:
                        self.rtn_val='Failed'
                        oscope_stat["text"]=self.rtn_val
                        msg1='Oscilloscope Not Detected!\n'
                        msg2='Please Make Sure That The Instrument Is Powered On\n'
                        msg3='And The GPIB Cable Is Connected To The Instrument.\n'
                        msg4='Then Try Again!'
                        msg=msg1+msg2+msg3+msg4
                        messagebox.showerror('Oscilloscope Initialization',msg)
                        return(self.rtn_val)
                else:    
                        msg1='Oscilloscope Initialization Failed!\n'
                        msg2='No Oscilloscope Detected Connected To GPIB Bus!'
                        messagebox.showerror('Oscilloscope Initialization', msg1+msg2)
                        Oscope_Initialized=False
                        self.rtn_val='Failed'
                        return(self.rtn_val)
            except Exception as e:
                self.rtn_val='Initialization Failed'
                oscope_stat["text"]='Initialization Failed'
                msg1='Exception occurred while code execution:\n'
                msg2=repr(e)+'GPIB Bus "oscope_initialize()"'
                messagebox.showerror('Oscilloscope Initialization',msg1+msg2)
                return 'break'
        def oscope_self_cal():# Returns "PASS", "FAIL"        
            try:
                msg1='The Oscilloscope Self Calibration Could Take Several\n'
                msg2='Minutes To Complete! Remove All Probes From The\n'
                msg3='Oscilloscope Inputs And Allow At Least A 5 Minute\n'
                msg4='Warm-Up Period Before Continuing. You Will Be Prompted\n'
                msg5='When Completed! Press OK Button To Start Self Cal.'
                msg=msg1+msg2+msg3+msg4+msg5
                messagebox.showinfo('Oscilloscope Self Calibration',msg)
                sent_lbl.configure(text="CAL:INTERNAL;*OPC?")
                (Oscope.write("CAL:INTERNAL;*OPC?"))
                busy='1'
                while busy=='1':
                    busy=(Oscope.query("BUSY?"))# Busy "1", Not Busy "0"
                self.rtn_val=(Oscope.query("CAL:STATUS?"))# "PASS", "FAIL"
                query.focus()
                query.delete('1.0','end')
                query.insert('end',self.rtn_val)
                if 'PASS' in self.rtn_val:messagebox.showinfo('Oscilloscope Self Calibration',self.rtn_val)
                elif 'FAIL' in self.rtn_val:
                    msg='Make Sure All Probes Are Disconnected And Try Again!\n'
                    messagebox.showerror('Oscilloscope Self Calibration',msg+self.rtn_val)
                return 'break'
            except Exception as e:
                query.focus()
                query.delete('1.0','end')
                query.insert('end','Self Calibration FAILED')
                msg1='Exception occurred while code execution:\n'
                msg2='Function = TDS210.oscope_self_calibrate()'
                msg2=repr(e)+'Command = CAL:INTERNAL;*OPC?'
                messagebox.showerror('Oscilloscope Self Calibration',msg1+msg2+msg3)
                return 'break'
        def oscope_auto_set():    
            try:
                sent_lbl.configure(text="AUTOSET EXECUTE;*OPC?")
                Oscope.write("AUTOSET EXECUTE;*OPC?")
                busy='1'
                while busy=='1':
                    busy=(Oscope.query("BUSY?"))# Busy "1", Not Busy "0"
                self.rtn_val='OK'
                query.focus()
                query.delete('1.0','end')
                query.insert('end','Autoset OK')
                return(self.rtn_val)
            except Exception as e:
                query.focus()
                query.delete('1.0','end')
                query.insert('end','Autoset Failed')
                msg1='Exception occurred while code execution:\n'
                msg2=repr(e)+'GPIB Bus "oscope_autoset()"'
                messagebox.showerror('Oscilloscope Autoset',msg1+msg2)
                return 'break'
        def gpib_send():
            # '****XXXX*****' Indicates Combobox Group Dividers
            TDS_CMDS=['********','****UTIL****','CAL:INTERNAL','AUTOSET EXECUTE','FACTORY','*RST',
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
            if len(TDS_CMDS)!=len(TDS210.TDS_Dic['Functions']) or len(TDS_CMDS)!=len(TDS210.TDS_Dic['Arguments']):# Make Sure All Dicts. Have The Same Indices.
                msg1='Dictionaries TDS_CMDS And TDS_Dic Have Different Indices:\n'
                msg2='They Must Be Equal For Proper Code Execution!\n'
                msg3='Ending Program! Please Correct The Associated Code.'
                messagebox.showerror('TDS 210',msg1+msg2+msg3)
                destroy()
            try:
                if not '?' in TDS_CMDS[self.index]:# WRITES
                    Oscope.write(TDS_CMDS[self.index])
                    self.rtn_val=self.funct+ ' Passed'
                    query.delete('1.0','end')
                    query.focus()
                    query.insert('end',self.rtn_val)
                else: #QUERIES  
                    if TDS_CMDS[self.index]=='CURVE?':# Convert Digitized Value To Y Values (Volts)
                        Oscope.write('DATA:ENCDG ASCII') # Make Sure Formatting Is ASCII                   
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
                            Waveform_Data.focus()
                            Waveform_Data.delete('1.0','end')
                            Waveform_Data.insert('end','Curve X Data: '+self.rtn_val)
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
                            Waveform_Data.focus()
                            Waveform_Data.delete('1.0','end')
                            Waveform_Data.insert('end','Curve Y Data: '+self.rtn_val)
                    else:
                        self.rtn_val=Oscope.query(TDS_CMDS[self.index])
                        params=self.rtn_val.split(";")
                        query.delete('1.0','end')
                        query.focus()
                        for p in range(0,len(params)):
                            query.insert('end',params[p]+"\n")
                sent_lbl.focus()
                sent_lbl.config(text=TDS_CMDS[self.index])
                return(self.rtn_val)
            except Exception as e:
                query.focus()
                query.delete('1.0','end')
                query.insert('end',params[0]+ ' Failed')
                msg1='Exception occurred while code execution:\n'
                msg2='Bus Command = '+TDS_CMDS[self.index]
                msg3=repr(e)+'GPIB Bus '+self.funct
                messagebox.showerror(params[0],msg1+msg2+msg3)
                return 'break'
        try: # If Bus And/Or Instrument Is Not Initialized, Then Initialize First
            if self.funct=='gpib_initialize':status=gpib_initialize()
            elif self.funct=='oscope_initialize':
                if not Gpib_Initialized:gpib_initialize() 
                status=oscope_initialize()
            elif self.funct=='oscope_self_cal':       
                if not Gpib_Initialized:gpib_initialize() 
                if not Oscope_Initialized:oscope_initialize()
                status=oscope_self_cal()
            elif self.funct=='oscope_auto_set':
                if not Gpib_Initialized:gpib_initialize() 
                if not Oscope_Initialized:oscope_initialize()
                status=oscope_auto_set()
            else:status=gpib_send()    
            return(status)
        except Exception as e:
            msg1='Exception occurred while code execution:\n'
            msg2=repr(e)+'GPIB '+self.funct
            messagebox.showerror('GPIB Error',msg1+msg2)
            return 'break'
def execute_cmd(event):
    cmd=Write_Cmd.get()
    if cmd[0][-1]=='*':return# Section Seperator
    response=str(TDS210(cmd))# Combobox Selection
    return 'break'
def set_choices(event):# ComboBox Selection Made, Update arguments_lbl
    Selected_Index.set(select.current())
    arguments_lbl.focus()
    arguments_lbl.config(text='Argument Choices: '+str(TDS210.TDS_Dic['Arguments'][Selected_Index.get()]))
    arguments_lbl.update()
    return
def destroy():# X Icon Was Clicked Or File/Exit
    for widget in root.winfo_children():
        if isinstance(widget,tk.Canvas):widget.destroy()
        else: widget.destroy()
        os._exit(0)
def menu_popup(event):# display the popup menu
   try:
      popup.tk_popup(event.x_root, event.y_root)
   finally:
      popup.grab_release()#Release the grab
def about():
    messagebox.showinfo('About PyVISA Tektronix TDS 210', 'Creator: Ross Waters\nEmail: RossWatersjr@gmail.com'\
        '\nNI VISA For Windows 11 64 Bit, (2022 Q3) Or 2023 Q2'\
        '\nPyVISA 1.13.0 Or Latest Version'\
        '\nLanguage: Python version 3.11.4 64-bit'\
        '\nRevision \ Date: 1.2 \ 10/05/2023'\
        '\nTested With (NI GPIB-USB-HS+) Controller')
if __name__ == "__main__":
    root=tk.Tk()
    dir=pathlib.Path(__file__).parent.absolute()
    filename='TDS_210.ico' # Program icon
    ico_path=os.path.join(dir, filename)
    root.iconbitmap(default=ico_path) # root and children
    root.font=font.Font(family='Lucida Sans',size=11,weight='normal',slant='italic')# Menu Font
    title_font=font.Font(family='Lucida Sans',size=12,weight='normal',slant='italic')# Menu Font
    title=('PyVISA Tektronix TDS 210/220 Oscilloscope')
    options='Right Click Window For About'
    root.title(title + options.rjust(45+len(options)))
    monitor_info=GetMonitorInfo(MonitorFromPoint((0,0)))
    work_area=monitor_info.get("Work")
    monitor_area=monitor_info.get("Monitor")
    screen_width=work_area[2]
    screen_height=work_area[3]
    taskbar_hgt=(monitor_area[3]-work_area[3])
    root.configure(bg='gray')
    root.option_add("*Font",root.font)
    root.protocol("WM_DELETE_WINDOW",destroy)
    root_hgt=((screen_height-taskbar_hgt)/2.5)
    root_wid=root_hgt*2.7
    x=(screen_width/2)-(root_wid/2)
    y=(screen_height/2.5)-(root_hgt/2.5)
    root.geometry('%dx%d+%d+%d' % (root_wid,root_hgt,x,y,))
    root.update()
    popup=Menu(root, tearoff=0) # PopUp Menu
    popup.add_command(label="About PyVISA Tektronix TDS 210", background='aqua', command=lambda:about())
    root.bind("<Button-3>", menu_popup)
    Write_Cmd=StringVar()
    Selected_Index=IntVar()
    cmd_lbl=tk.Label(root,background='gray',font=title_font,text='Select / Modify Command Arguments')
    cmd_lbl.place(relx=0.01,rely=0.03,relwidth=0.28,relheight=0.07)
    style= ttk.Style()
    style.theme_use('default')
    style.configure("TCombobox",fieldbackground= '#f0ffff',background= '#f0ffff')
    style.configure( 'Horizontal.TScrollbar',width=22 )
    select=ttk.Combobox(root,font=root.font,textvariable=Write_Cmd)
    select['values']=TDS210.TDS_Dic['Functions']
    select['state']='normal'
    select.place(relx=0.014,rely=0.1,relwidth=0.28,relheight=0.07)
    select.bind("<<ComboboxSelected>>",set_choices)
    select.bind("<Return>",execute_cmd)
    select['values']=TDS210.TDS_Dic['Functions']
    select.current(0)
    execute_btn=tk.Button(root,text='Execute Command',bg='navy',fg='#ffffff',
            activebackground='#ffffff',borderwidth=5,relief="raised",font=title_font)
    execute_btn.place(relx=0.014,rely=0.18,relwidth=0.28,relheight=0.07)
    execute_btn.bind("<Button-1>",execute_cmd)
    sent_lbl=tk.Label(root,background='#E5E5E5',font=title_font,text='Command Sent')
    sent_lbl.place(relx=0.014,rely=0.26,relwidth=0.28,relheight=0.07)
    interface_stat_lbl=tk.Label(root,background='gray',font=title_font,text='GPIB Interface Status')
    interface_stat_lbl.place(relx=0.314,rely=0.03,relwidth=0.20,relheight=0.07)
    interface_name=tk.Label(root,background='#E5E5E5',font=root.font,text='Interface Name',borderwidth=2,relief="groove")
    interface_name.place(relx=0.304,rely=0.1,relwidth=0.20,relheight=0.07)
    interface_stat=tk.Label(root,background='#E5E5E5',font=root.font,text='Not Initialized',borderwidth=2,relief="groove")
    interface_stat.place(relx=0.304,rely=0.18,relwidth=0.20,relheight=0.07)
    interface_address=tk.Label(root,background='#E5E5E5',font=root.font, text='Interface Address',borderwidth=2,relief="groove")
    interface_address.place(relx=0.304,rely=0.26,relwidth=0.20,relheight=0.07)
    oscope_stat_lbl=tk.Label(root,background='gray',font=title_font,text='Oscilloscope Interface Status')
    oscope_stat_lbl.place(relx=0.514,rely=0.03,relwidth=0.20,relheight=0.07)
    oscope_name=tk.Label(root,background='#E5E5E5',font=root.font,text='Oscilloscope Name',borderwidth=2,relief="groove")
    oscope_name.place(relx=0.514,rely=0.1,relwidth=0.20,relheight=0.07)
    oscope_stat=tk.Label(root,background='#E5E5E5',font=root.font,text='Not Initialized',borderwidth=2,relief="groove")
    oscope_stat.place(relx=0.514,rely=0.18,relwidth=0.20,relheight=0.07)
    oscope_address=tk.Label(root,background='#E5E5E5',font=root.font,text='Oscilloscope Address',borderwidth=2,relief="groove")
    oscope_address.place(relx=0.514,rely=0.26,relwidth=0.20,relheight=0.07)
    query_lbl=tk.Label(root,background='gray',font=title_font, text='Oscilloscope Query Value')
    query_lbl.place(relx=0.724,rely=0.03,relwidth=0.265,relheight=0.07)
    query=ScrolledText(root,background='#E5E5E5',font=root.font,borderwidth=2,relief="groove")
    query.place(relx=0.724,rely=0.1,relwidth=0.265,relheight=0.23)
    arguments_lbl=tk.Label(root,background='#E5E5E5',font=title_font,anchor="w",justify='left',text='Argument Choices:',borderwidth=2,relief="groove")
    arguments_lbl.place(relx=0.01,rely=0.36,relwidth=0.98,relheight=0.07)
    Waveform_Data=ScrolledText(root,bg='#FFFFFF',fg="#000000",font=root.font,borderwidth=5,relief="sunken",wrap=tk.WORD) 
    Waveform_Data.place(relx=0.01,rely=0.45,relwidth=0.98,relheight=0.53)
    Waveform_Data.focus()
    Waveform_Data.delete('1.0','end')
    Waveform_Data.insert('end','Curve Data')
    Gpib_Initialized=False
    Oscope_Initialized=False
    response=str(TDS210('oscope_initialize'))# Initialize Controller And Instrument
    root.mainloop()    
