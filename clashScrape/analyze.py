import pickle
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

BUILDINGS = [
    'Cannon',
    'Archer_Tower',
    'Mortar',
    'Air_Defense',
    'Wizard_Tower',
    'Air_Sweeper',
    'Hidden_Tesla',
    'Bomb_Tower',
    'X-Bow',
    'Inferno_Tower',
    'Eagle_Artillery',
    'Scattershot',
    'Town_Hall',
    'Gold_Mine',
    'Elixir_Collector',
    'Dark_Elixir_Drill',
    'Gold_Storage',
    'Elixir_Storage',
    'Dark_Elixir_Storage',
    'Clan_Castle',
    'Army_Camp',
    'Barracks',
    'Dark_Barracks',
    'Laboratory',
    'Spell_Factory',
    'Dark_Spell_Factory',
    'Workshop',
]

with open('building_to_level_to_hp.pickle', 'rb') as handle:
    building_to_level_to_hp = pickle.load(handle)

with open('building_to_level_to_th.pickle', 'rb') as handle:
    building_to_level_to_th = pickle.load(handle)

# fix inferno
hp = [1500, 1800, 2100, 2400, 2700, 3000, 3300]
th = [  10,   10,   10,   11,   11,   12,   13]
building_to_level_to_hp['Inferno_Tower'] = {}
building_to_level_to_th['Inferno_Tower'] = {}
for level in range(1, 8):
    building_to_level_to_hp['Inferno_Tower'][level] = hp[level-1]
    building_to_level_to_th['Inferno_Tower'][level] = th[level-1]

# rage spell info
rage_r_boost = [2.3, 2.4, 2.5, 2.6, 2.7, 2.8]

# config
TH_LEVEL = 11
RAGE_LEVEL = 5

TEST_DMG_CHAIN = [945 * (0.8 ** i) for i in range(5)]
BOOST_R_DMG = rage_r_boost[RAGE_LEVEL-1]

# intro
print('[INFO] testing raw vs boost damage chains of:')
for i, dmg in enumerate(TEST_DMG_CHAIN):
    boost_dmg = BOOST_R_DMG * dmg
    print(f'target {i+1}: {int(round(dmg))} dmg vs {int(round(boost_dmg))} dmg')

# helper funcs
def get_level(building, th):
    level_to_th = building_to_level_to_th[building]
    prev_level = 0
    for level in range(1, max(level_to_th.keys())):
        if level_to_th[level] > th:
            break
        prev_level = level
    return prev_level

def get_hp(building, level):
    return building_to_level_to_hp[building][level]

def get_stk(hp, dmg):
    stk = math.ceil(hp / float(dmg))
    return stk

# calculations
NAME_WIDTH = 22

num_raw_boost = [[0 for _ in range(20)] for _ in range(20)]

for building in BUILDINGS:
    level = get_level(building, TH_LEVEL)
    if level == 0: continue
    hp = get_hp(building, level)

    stk_raw_l = [get_stk(hp, dmg) for dmg in TEST_DMG_CHAIN]
    stk_boost_l = [get_stk(hp, BOOST_R_DMG * dmg) for dmg in TEST_DMG_CHAIN]
    
    for stk_raw, stk_boost in zip(stk_raw_l, stk_boost_l):
        num_raw_boost[stk_raw][stk_boost] += 1

    space = (22 - len(building)) * ' '
    print('-'*60)
    print(f'{building} ' + space + f'[  RAW  ]    {stk_raw_l[0]} | {stk_raw_l[1]} | {stk_raw_l[2]} | {stk_raw_l[3]} | {stk_raw_l[4]}')
    print(f'{building} ' + space + f'[ BOOST ]    {stk_boost_l[0]} | {stk_boost_l[1]} | {stk_boost_l[2]} | {stk_boost_l[3]} | {stk_boost_l[4]}')
print('-'*60)

ax = sns.heatmap(np.array(num_raw_boost).astype(np.uint), linewidth=0.5)
plt.show()

for orig in range(1,20):
    for new in range(1,orig+1):
        if (q := num_raw_boost[orig][new]) > 0:
            print(f'{q} occurances {orig} stk -> {new}')