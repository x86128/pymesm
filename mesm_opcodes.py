OP_ATX = 0o000
OP_STX = 0o001
OP_MOD = 0o002
OP_XTS = 0o003
OP_ADD = 0o004
OP_SUB = 0o005
OP_RSUB = 0o006
OP_AMX = 0o007
OP_XTA = 0o010
OP_AAX = 0o011
OP_AEX = 0o012
OP_ARX = 0o013
OP_AVX = 0o014
OP_AOX = 0o015
OP_DIV = 0o016
OP_MUL = 0o017
OP_APX = 0o020
OP_AUX = 0o021
OP_ACX = 0o022
OP_ANX = 0o023
OP_EADDX = 0o024
OP_ESUBX = 0o025
OP_ASX = 0o026
OP_XTR = 0o027
OP_RTE = 0o030
OP_YTA = 0o031
OP_E32 = 0o032
OP_E33 = 0o033
OP_EADDN = 0o034
OP_ESUB = 0o035
OP_ASN = 0o036
OP_NTR = 0o037
OP_ATI = 0o040
OP_STI = 0o041
OP_ITA = 0o042
OP_ITS = 0o043
OP_MTJ = 0o044
OP_JADDM = 0o045
OP_E46 = 0o046
OP_E47 = 0o047
OP_E50 = 0o050
OP_E51 = 0o051
OP_E52 = 0o052
OP_E53 = 0o053
OP_E54 = 0o054
OP_E55 = 0o055
OP_E56 = 0o056
OP_E57 = 0o057
OP_E60 = 0o060
OP_E61 = 0o061
OP_E62 = 0o062
OP_E63 = 0o063
OP_E64 = 0o064
OP_E65 = 0o065
OP_E66 = 0o066
OP_E67 = 0o067
OP_E70 = 0o070
OP_E71 = 0o071
OP_E72 = 0o072
OP_E73 = 0o073
OP_E74 = 0o074
OP_E75 = 0o075
OP_E76 = 0o076
OP_E77 = 0o077
OP_E20 = 0o100  # 200
OP_E21 = 0o101  # 210
OP_UTC = 0o102  # 220
OP_WTC = 0o103  # 230
OP_VTM = 0o104  # 240
OP_UTM = 0o105  # 250
OP_UZA = 0o106  # 260
OP_UIA = 0o107  # 270
OP_UJ = 0o110  # 300
OP_VJM = 0o111  # 310
OP_IJ = 0o112  # 320
OP_STOP = 0o113  # 330
OP_VZM = 0o114  # 340
OP_VIM = 0o115  # 350
OP_E36 = 0o116  # 360
OP_VLM = 0o117  # 370

OP_NAME = {'ATX': 0o000,
           'STX': 0o001,
           'MOD': 0o002,
           'XTS': 0o003,
           'ADD': 0o004,
           'SUB': 0o005,
           'RSUB': 0o006,
           'AMX': 0o007,
           'XTA': 0o010,
           'AAX': 0o011,
           'AEX': 0o012,
           'ARX': 0o013,
           'AVX': 0o014,
           'AOX': 0o015,
           'DIV': 0o016,
           'MUL': 0o017,
           'APX': 0o020,
           'AUX': 0o021,
           'ACX': 0o022,
           'ANX': 0o023,
           'EADDX': 0o024,
           'ESUBX': 0o025,
           'ASX': 0o026,
           'XTR': 0o027,
           'RTE': 0o030,
           'YTA': 0o031,
           'E32': 0o032,
           'E33': 0o033,
           'EADDN': 0o034,
           'ESUB': 0o035,
           'ASN': 0o036,
           'NTR': 0o037,
           'ATI': 0o040,
           'STI': 0o041,
           'ITA': 0o042,
           'ITS': 0o043,
           'MTJ': 0o044,
           'JADDM': 0o045,
           'E46': 0o046,
           'E47': 0o047,
           'E50': 0o050,
           'E51': 0o051,
           'E52': 0o052,
           'E53': 0o053,
           'E54': 0o054,
           'E55': 0o055,
           'E56': 0o056,
           'E57': 0o057,
           'E60': 0o060,
           'E61': 0o061,
           'E62': 0o062,
           'E63': 0o063,
           'E64': 0o064,
           'E65': 0o065,
           'E66': 0o066,
           'E67': 0o067,
           'E70': 0o070,
           'E71': 0o071,
           'E72': 0o072,
           'E73': 0o073,
           'E74': 0o074,
           'E75': 0o075,
           'E76': 0o076,
           'E77': 0o077,
           'E20': 0o100,
           'E21': 0o101,
           'UTC': 0o102,
           'WTC': 0o103,
           'VTM': 0o104,
           'UTM': 0o105,
           'UZA': 0o106,
           'UIA': 0o107,
           'UJ': 0o110,
           'VJM': 0o111,
           'IJ': 0o112,
           'STOP': 0o113,
           'VZM': 0o114,
           'VIM': 0o115,
           'E36': 0o116,
           'VLM': 0o117}

OP_CODE = {0o000: 'ATX',
           0o001: 'STX',
           0o002: 'MOD',
           0o003: 'XTS',
           0o004: 'ADD',
           0o005: 'SUB',
           0o006: 'RSUB',
           0o007: 'AMX',
           0o010: 'XTA',
           0o011: 'AAX',
           0o012: 'AEX',
           0o013: 'ARX',
           0o014: 'AVX',
           0o015: 'AOX',
           0o016: 'DIV',
           0o017: 'MUL',
           0o020: 'APX',
           0o021: 'AUX',
           0o022: 'ACX',
           0o023: 'ANX',
           0o024: 'EADDX',
           0o025: 'ESUBX',
           0o026: 'ASX',
           0o027: 'XTR',
           0o030: 'RTE',
           0o031: 'YTA',
           0o032: 'E32',
           0o033: 'E33',
           0o034: 'EADDN',
           0o035: 'ESUB',
           0o036: 'ASN',
           0o037: 'NTR',
           0o040: 'ATI',
           0o041: 'STI',
           0o042: 'ITA',
           0o043: 'ITS',
           0o044: 'MTJ',
           0o045: 'JADDM',
           0o046: 'E46',
           0o047: 'E47',
           0o050: 'E50',
           0o051: 'E51',
           0o052: 'E52',
           0o053: 'E53',
           0o054: 'E54',
           0o055: 'E55',
           0o056: 'E56',
           0o057: 'E57',
           0o060: 'E60',
           0o061: 'E61',
           0o062: 'E62',
           0o063: 'E63',
           0o064: 'E64',
           0o065: 'E65',
           0o066: 'E66',
           0o067: 'E67',
           0o070: 'E70',
           0o071: 'E71',
           0o072: 'E72',
           0o073: 'E73',
           0o074: 'E74',
           0o075: 'E75',
           0o076: 'E76',
           0o077: 'E77',
           0o100: 'E20',
           0o101: 'E21',
           0o102: 'UTC',
           0o103: 'WTC',
           0o104: 'VTM',
           0o105: 'UTM',
           0o106: 'UZA',
           0o107: 'UIA',
           0o110: 'UJ',
           0o111: 'VJM',
           0o112: 'IJ',
           0o113: 'STOP',
           0o114: 'VZM',
           0o115: 'VIM',
           0o116: 'E36',
           0o117: 'VLM'}
