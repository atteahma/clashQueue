import requests
from bs4 import BeautifulSoup

BUILDING_URL_ENDS = [
    '/wiki/Cannon/Home_Village',
    '/wiki/Archer_Tower/Home_Village',
    '/wiki/Mortar',
    '/wiki/Air_Defense',
    '/wiki/Wizard_Tower',
    '/wiki/Air_Sweeper',
    '/wiki/Hidden_Tesla/Home_Village',
    '/wiki/Bomb_Tower',
    '/wiki/X-Bow',
    '/wiki/Inferno_Tower',
    '/wiki/Eagle_Artillery',
    '/wiki/Scattershot',
    '/wiki/Town_Hall',
    '/wiki/Gold_Mine/Home_Village',
    '/wiki/Elixir_Collector/Home_Village',
    '/wiki/Dark_Elixir_Drill',
    '/wiki/Gold_Storage/Home_Village',
    '/wiki/Elixir_Storage/Home_Village',
    '/wiki/Dark_Elixir_Storage',
    '/wiki/Clan_Castle',
    '/wiki/Army_Camp/Home_Village',
    '/wiki/Barracks',
    '/wiki/Dark_Barracks',
    '/wiki/Laboratory',
    '/wiki/Spell_Factory',
    '/wiki/Dark_Spell_Factory',
    '/wiki/Workshop',
]

BASE_URL = 'https://clashofclans.fandom.com'


building_to_level_to_hp = {}
building_to_level_to_th = {}

failed_buildings = []

for url_end in BUILDING_URL_ENDS:
    
    url_split = url_end.split('/')
    if url_split[-1] == 'Home_Village':
        building_name = url_split[-2]
    else:
        building_name = url_split[-1]

    print(f'[INFO] working on {building_name}')

    url = BASE_URL + url_end
    page_data = requests.get(url)

    soup = BeautifulSoup(page_data.text, 'html.parser')

    level_to_hp = {}
    level_to_th = {}
    level_i = None
    hp_i = None
    th_i = None
    table_found = False

    for table in soup.find_all('table'):
        if table.tr:
            for th in table.tr.find_all('th'):
                val = th.text.replace(' ', '').replace('\n', '').replace('*','')
                if val in ['Hitpoints', 'HP']:
                    table_found = True
                    break
        if table_found:
            break

    for i, th in enumerate(table.tr.find_all('th')):
        val = th.text.replace(' ', '').replace('\n', '')

        if val == 'Level' or (val == 'THLevel' and building_name == 'Town_Hall'):
            level_i = i
        if val in ['Hitpoints', 'HP']:
            hp_i = i
        if val == 'TownHallLevelRequired':
            th_i = i
    
    num_cols = len(table.tr.find_all('th'))

    if len(table.find_all('tr')[1].find_all('th')) > 0:
        print(f'[ERROR] {building_name} has invalid table')
        failed_buildings.append(building_name)
        continue
    
    if (level_i is None) or (hp_i is None) or (th_i is None):
        if building_name == 'Town_Hall' and (level_i is not None) and (hp_i is not None):
            th_i = level_i
        else:
            print(f'[ERROR] {building_name} failed to find table')
            print(f'[ERROR] level_i={level_i}\nhp_i={hp_i}\nth_i={th_i}')
            failed_buildings.append(building_name)
            continue

    rows = table.find_all('tr')
    for r_i in range(1, len(rows)):
        row = rows[r_i]
        
        for c_i, col in enumerate(row.find_all('td')):
            val = col.text.replace(',', '').replace(' ', '').replace('\n', '').replace('*', '')

            if c_i == hp_i:
                if not val:
                    print(f'[ERROR] {building_name} failed to find hp at level {r_i}')
                    continue

                level_to_hp[r_i] = int(val)
            if c_i == th_i:
                if not val:
                    print(f'[ERROR] {building_name} failed to find th at level {r_i}')
                    continue

                level_to_th[r_i] = int(val)

    building_to_level_to_hp[building_name] = level_to_hp
    building_to_level_to_th[building_name] = level_to_th

print('[INFO] finished running')

print('[INFO] failed buildings:')
if len(failed_buildings) > 0:
    print(failed_buildings)
else:
    print('none')

print('[INFO] results:')
print(building_to_level_to_hp)
print(building_to_level_to_th)

import pickle

with open('building_to_level_to_hp.pickle', 'wb') as handle:
    pickle.dump(building_to_level_to_hp, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('building_to_level_to_th.pickle', 'wb') as handle:
    pickle.dump(building_to_level_to_th, handle, protocol=pickle.HIGHEST_PROTOCOL)