# desgoblin
a game about a small goblin and it's quest to fell the gods
the structure of the code is as such:

desgoblin{
    -->game_system{
        ->main.py:
        ->menu.py:
    }
    -->battle_system{
        ->battlesys:
        ->character:
        ->enemy:
        ->weapon: 
        ->item: 
        ->healthbar:
    }
    -->map_system{
        ->main:
        ->map:
        ->tiles:
    }
    -->assets{
        -->png{
            #all the #####.png files for the tiles
        
        }
    }
}
