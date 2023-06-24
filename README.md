# PyVISA-Tektronix-TDS210-GPIB
PyVISA/NI-VISA GUI Interface For Tektronix TDS 210/220 Oscilloscope

########### REQUIREMENTS ##########
# NI VISA For Windows 11 64 Bit, (2022 Q3) Or (2023 Q2) Installed
# PyVISA 1.13.0 Or Latest Version
# Tektronix TDS 210/220 Oscilloscope Or Equivalent With GPIB Interface
# Tested With (NI GPIB-USB-HS+) Controller
# Tested Using Python Version 3.11.2 64 Bit
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

# All Calls Outside This Class Must Be Of String Type With Or Without Return Values.
# Examples: Set Command, str(TDS210('set_data_encoding, ASCII')), Get Command, encdg=str(TDS210('get_data_encoding'))
# Return Values May Or May not Be Specified With The Set Commands Which Will Return The Set Value If Completed.  
# The Oscilloscope GPIB Address Is Set At Address '5' And Is Set During Initialization Of This Class.
# You May Change The Oscilloscope Address To Your Preference In def __init__.
