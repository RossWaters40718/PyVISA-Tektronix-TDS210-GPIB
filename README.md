# PyVISA-Tektronix-TDS210-GPIB
PyVISA/NIVISA Intrface For Tektronix TDS 210/220 Oscilloscope
########### REQUIREMENTS ##########
    # NI VISA For Windows 11 64 Bit, (2022 Q3) Or (2023 Q2) Installed
    # PyVISA 1.13.0 Or Latest Version
    # Tektronix TDS 210/220 Oscilloscope Or Equivalent With GPIB Interface
    # Tested With (NI GPIB-USB-HS+) Controller
    # Tested Using Python Version 3.11.2 64 Bit
    # ////////// Tektronix TDS 210/220 Oscilloscope \\\\\\\\\\
    # TDS_Dic Has 2 Keys. 'Functions' Is Used To Populate Select Combobox ,'Arguments' Is Used To
    # Display Argument Choices. Another Dictionary is TDS_CMDS 'Commands' Which Contains The Actual 
    # GPIB Messages Sent. TDS_CMDS 'Commands' Is Located In gpib_send() And Is Dynamic Type (Changing). 
    # All 3 Keys Must Have The Same Corresponding Index For The Command Being Called.
    # All Dictionary Key Values Must Correlate!
    # This Greatly Reduces Code By Using 1 Function gpib_send() For Almost All Commands
    # If TDS210 Class Is To be Used Without A GUI Interface, TDS_Dic['Arguments'] May Be deleted
    # And Send Commands As Shown In TDS_Dic['Functions']. Example: response=str(TDS210('set_vert_coupling, DC, CH1'))   
