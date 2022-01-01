# coding=utf-8
"""
Biomes Handler file.

This file will contain the functions and containers for handling room
biomes. Generally, the map symbol set for a room should match the primary
biome type of the room, except when the room has a major road running
through it or the room is indoors.

Biome types will affect climate/weather, but will also be affected by other
factors such as elevation, time of year, climate/weather, the actions of
mobile characters & NPCs, etc.

"""
# map symbols for overhead mapping. This is herte as a reference.
MAP_SYMBOLS = {
    'Crossroads' : ['|155╬|n','|255╬|n','|355╬|n','|455╬|n','|555╬|n'],
    'EW Road' : ['|155═|n', '|255═|n', '|355═|n', '|455═|n', '|555═|n'],
    'NS Road' : ['|155║|n', '|255║|n', '|355║|n', '|455║|n', '|555║|n'],
    'NW Road' : ['|155╗|n', '|255╗|n', '|355╗|n', '|455╗|n', '|555╗|n'],
    'SW Road' : ['|155╝|n', '|255╝|n', '|355╝|n', '|455╝|n', '|555╝|n'],
    'NE Road' : ['|155╔|n', '|255╔|n', '|355╔|n', '|455╔|n', '|555╔|n'],
    'SE Road' : ['|155╚|n', '|255╚|n', '|355╚|n', '|455╚|n', '|555╚|n'],
    'WT Road' : ['|155╣|n', '|255╣|n', '|355╣|n', '|455╣|n', '|555╣|n'],
    'ET Road' : ['|155╠|n', '|255╠|n', '|355╠|n', '|455╠|n', '|555╠|n'],
    'NT Road' : ['|155╩|n', '|255╩|n', '|355╩|n', '|455╩|n', '|555╩|n'],
    'ST Road' : ['|155╦|n', '|255╦|n', '|355╦|n', '|455╦|n', '|555╦|n'],
    'Plains' : ['|155■|n', '|255■|n', '|355■|n', '|455■|n', '|555■|n'],
    'Forest' : ['|043¡|n', '|143¡|n', '|243¡|n', '|343¡|n', '|443¡|n'],
    'Jungle' : ['|043▓|n', '|143▓|n', '|243▓|n', '|343▓|n', '|443▓|n'],
    'Mountains/Hills' : ['|110^|n', '|210^|n', '|310^|n', '|410^|n', '|510^|n'],
    'Desert/Badlands' : ['|110°|n', '|210°|n', '|310°|n', '|410°|n', '|510°|n'],
    'Taiga' : ['|155¶|n', '|255¶|n', '|355¶|n', '|455¶|n', '|555¶|n'],
    'Tundra' : ['|155≡|n', '|255≡|n', '|355≡|n', '|455≡|n', '|555≡|n'],
    'Swamp' : ['|040§|n', '|140§|n', '|240§|n', '|340§|n', '|440§|n'],
    'Savannah' : ['|120░|n', '|220░|n', '|320░|n', '|420░|n', '|520░|n'],
    'Shore' : ['|025▄|n', '|024▄|n', '|023▄|n', '|022▄|n', '|021▄|n',],
    'Water' : ['|001█|n', '|002█|n', '|003█|n', '|004█|n', '|005█|n',],
    'Fields' : ['|041▒|n', '|141▒|n', '|241▒|n', '|341▒|n', '|441▒|n',],
    'City' : ['|155©|n', '|255©|n', '|355©|n', '|455©|n', '|555©|n']
}


_BIOME_DATA = {
    # Outdoor Biomes
    'road': {
        'name': 'Road',
        'type': 'Outdoor',
        'desc': ("|mRoad|n is the biome that indicates there is a road "
                 "running through the room. Although the road may only take up "
                 "a small percentage of the actual land area in the room, it "
                 "may be prominenant enough to warrant setting the overhead "
                 "map symbol to be a road type. Roads can degrade to trail "
                 "if they remain unrepaired for long enough."),
        'vegetation_min': 0,
        'vegetation_max': 0.25,
        'biome_ratio': 0, # this should total to 1 across all biomes assocated to the room
        'extra': {'condition' : 1, # 0-1, 1 is perfect condition
                  'quality': .75, # 0-1, 1 is the best quality road known
                  'width': 5, # road width in meters
                  'road_type': 'pavement_stones'}
    },
    'trail': {
        'name': 'Trail',
        'type': 'Outdoor',
        'desc': ("|mTrail|n is the biome that indicates there is a trail "
                 "running through the room. Although the trail may only take up "
                 "a small percentage of the actual land area in the room, it "
                 "may be prominenant enough to warrant setting the overhead "
                 "map symbol to be a road/trail type. Roads can degrade to trail"
                 "if they remain unrepaired for long enough and trails can "
                 "degrade to sonme other biome given enough time."),
        'vegetation_min': 0,
        'vegetation_max': 0.35,
        'biome_ratio': 0, # this should total to 1 across all biomes assocated to the room
        'extra': {'condition' : 1, # 0-1, 1 is perfect condition
                  'quality': .75, # 0-1, 1 is the best quality trail known
                  'width': 2, # trail width in meters
                  'trail_type': 'compacted_earth'}
    },
    'plain': {
        'name': 'Plains',
        'type': 'Outdoor',
        'desc': ("|mPlains|n is a temperate grassland biome. The primary "
                 "vegetation type is grasses, but trees can be found in well "
                 "watered areas. Plains tend to be inhabited by herd animals, "
                 "small rodents, and some predators. Plains are often converted "
                 "into fields by human activity."),
        'vegetation_min': 0.1,
        'vegetation_max': 0.75,
        'biome_ratio': 0, # this should total to 1 across all biomes assocated to the room
        'extra': {}
    },
