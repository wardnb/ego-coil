from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

netlist = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'M4', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'M4'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'MountingHole:MountingHole_4.3mm_M4_Pad', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'SMCJ70A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SMCJ70A'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Diode_SMD:D_SMC', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE),
            Pin(num='2',name='A',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'1000uF/100V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'1000uF/100V'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Capacitor_THT:CP_Radial_D18.0mm_P7.50mm', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'1uF/100V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'1uF/100V'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Capacitor_SMD:C_1210_3225Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'47uH/20A', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'47uH/20A'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Inductor_THT:L_Toroid_Horizontal_D28.0mm_P30.00mm_Fastron_DSP', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'IRFP4332', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IRFP4332'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Package_TO_SOT_THT:TO-247-3_Vertical', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='G',func=pin_types.INPUT),
            Pin(num='2',name='D',func=pin_types.PASSIVE),
            Pin(num='3',name='S',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'100R/3W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'100R/3W'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_THT:R_Axial_DIN0918_L18.0mm_D6.0mm_P22.86mm_Horizontal', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'UF4007', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'UF4007'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE),
            Pin(num='2',name='A',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'15V/1.3W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'15V/1.3W'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE),
            Pin(num='2',name='A',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'10k', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'10k'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_SMD:R_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'IRFB4110', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IRFB4110'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Package_TO_SOT_THT:TO-220-3_Vertical', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='G',func=pin_types.INPUT),
            Pin(num='2',name='D',func=pin_types.PASSIVE),
            Pin(num='3',name='S',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'100R/5W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'100R/5W'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_THT:R_Axial_Power_L20.0mm_W6.4mm_P25.40mm', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'10R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'10R'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_SMD:R_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'2mR/3W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2mR/3W'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_SMD:R_2512_6332Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'INA180A2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'INA180A2'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Package_TO_SOT_SMD:SOT-23-5', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='OUT',func=pin_types.OUTPUT),
            Pin(num='2',name='GND',func=pin_types.PWRIN),
            Pin(num='3',name='IN+',func=pin_types.INPUT),
            Pin(num='4',name='IN-',func=pin_types.INPUT),
            Pin(num='5',name='V+',func=pin_types.PWRIN)] }),
        Part(**{ 'name':'100nF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'100nF'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Capacitor_SMD:C_0603_1608Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'10nF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'10nF'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Capacitor_SMD:C_0603_1608Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'1k', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'1k'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_SMD:R_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'100k', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'100k'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_SMD:R_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'5.6k', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'5.6k'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_SMD:R_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'HDR2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HDR2'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'HDR4', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HDR4'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE),
            Pin(num='3',name='3',func=pin_types.PASSIVE),
            Pin(num='4',name='4',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'100uF/25V', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'100uF/25V'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'10uF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'10uF'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Capacitor_SMD:C_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'TC4420CPA', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TC4420CPA'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Package_DIP:DIP-8_W7.62mm', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='NC',func=pin_types.PASSIVE),
            Pin(num='2',name='IN',func=pin_types.INPUT),
            Pin(num='3',name='NC2',func=pin_types.PASSIVE),
            Pin(num='4',name='GND',func=pin_types.PWRIN),
            Pin(num='5',name='GND2',func=pin_types.PWRIN),
            Pin(num='6',name='OUT',func=pin_types.OUTPUT),
            Pin(num='7',name='OUT2',func=pin_types.PASSIVE),
            Pin(num='8',name='VDD',func=pin_types.PWRIN)] }),
        Part(**{ 'name':'1uF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'1uF'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Capacitor_SMD:C_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'2N7002', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'2N7002'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Package_TO_SOT_SMD:SOT-23', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='G',func=pin_types.INPUT),
            Pin(num='2',name='S',func=pin_types.PASSIVE),
            Pin(num='3',name='D',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'1N4148W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'1N4148W'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Diode_SMD:D_SOD-123', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE),
            Pin(num='2',name='A',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'HDR3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HDR3'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE),
            Pin(num='3',name='3',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'330R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'330R'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Resistor_SMD:R_0805_2012Metric', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'HDR20', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HDR20'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE),
            Pin(num='3',name='3',func=pin_types.PASSIVE),
            Pin(num='4',name='4',func=pin_types.PASSIVE),
            Pin(num='5',name='5',func=pin_types.PASSIVE),
            Pin(num='6',name='6',func=pin_types.PASSIVE),
            Pin(num='7',name='7',func=pin_types.PASSIVE),
            Pin(num='8',name='8',func=pin_types.PASSIVE),
            Pin(num='9',name='9',func=pin_types.PASSIVE),
            Pin(num='10',name='10',func=pin_types.PASSIVE),
            Pin(num='11',name='11',func=pin_types.PASSIVE),
            Pin(num='12',name='12',func=pin_types.PASSIVE),
            Pin(num='13',name='13',func=pin_types.PASSIVE),
            Pin(num='14',name='14',func=pin_types.PASSIVE),
            Pin(num='15',name='15',func=pin_types.PASSIVE),
            Pin(num='16',name='16',func=pin_types.PASSIVE),
            Pin(num='17',name='17',func=pin_types.PASSIVE),
            Pin(num='18',name='18',func=pin_types.PASSIVE),
            Pin(num='19',name='19',func=pin_types.PASSIVE),
            Pin(num='20',name='20',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'M3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'M3'}), 'ref_prefix':'U', 'fplist':None, 'footprint':'MountingHole:MountingHole_3.2mm_M3', 'keywords':None, 'description':'', 'datasheet':None })])