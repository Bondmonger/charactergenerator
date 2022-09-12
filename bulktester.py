import character
import time
import random
import datalocus

character_list = []
some_number = 0
ac_number = 0
strength = 0
intelligence = 0
wisdom = 0
constitution = 0
dexterity = 0
charisma = 0
comeliness = 0
maxhp = 0
minhp = 1000


def random_prop(proportional_dict):
    return random.choices(list(proportional_dict.keys()), weights=proportional_dict.values(), k=1)
    # probability_sum, proportional_sum = sum(proportions["single_dict"].values()), 0
    # rand_value = random.randrange(0, probability_sum)
    # for key in proportions["single_dict"]:
    #     proportional_sum += proportions["single_dict"][key]
    #     if proportional_sum >= rand_value:
    #         return string_to_list(key, '/')


start = time.time()
# prop_dict = {"Apple": 65, "Pineapple": 1, "Mango": 1525, "Kiwi": 189, "Cherry": 255, "Pomegranate": 1100,
#              "Banana": 412, "Grape": 165, "Melon": 700, "Watermelon": 700, "Peach": 1210, "Plum": 71, "Lychee": 1000,
#              "Orange": 3285}
# for element in range(1000):
#     print(random_prop(prop_dict))

for element in range(8):
    # test_char = character.Character(1)
    rara = random.randrange(3, 5+1)
    test_char = character.Character(rara)
    # test_char = character.Character(5, race='Hengeyokai: Raccoon Dog', classes=['Kensai'])
    # test_char = character.Character(8, race='Human', classes=['Ninja', 'Wu-jen'])
    # test_char.display_attributes()
    character_list.append(test_char)
    print("rara", rara)
char_lev, arch_list, arch_dict = [], [], {"Cleric": 0, "Fighter": 0, "Magic User": 0, "Thief": 0}
for aaa in character_list:
    for sub_class in aaa.classes:
        arch_list.append(datalocus.archetype(sub_class))
        arch_dict[datalocus.archetype(sub_class)] += 1/len(aaa.classes)
    char_lev.append(aaa.display_level)
    maxhp = aaa.hp if aaa.hp > maxhp else maxhp
    minhp = aaa.hp if aaa.hp < minhp else minhp
    some_number += aaa.hp
    ac_number += aaa.calculate_ac()
    strength += aaa.attributes["Str"]
    intelligence += aaa.attributes["Int"]
    wisdom += aaa.attributes["Wis"]
    dexterity += aaa.attributes["Dex"]
    constitution += aaa.attributes["Con"]
    charisma += aaa.attributes["Cha"]
    comeliness += aaa.attributes["Com"]
print("levels:", char_lev)
print("arch_list:", arch_list)
print("arch_dict:", arch_dict)
print("min / average hp / max: ", minhp, "/", some_number/len(character_list), "/", maxhp)
print("average ac: ", 10+ac_number/len(character_list))
print("average str: ", strength/len(character_list))
print("average int: ", intelligence/len(character_list))
print("average wis: ", wisdom/len(character_list))
print("average dex: ", dexterity/len(character_list))
print("average con: ", constitution/len(character_list))
print("average cha: ", charisma/len(character_list))
print("average com: ", comeliness/len(character_list))
end = time.time()
print('time', end-start)
# print("bulk gen speed check with {} characters:".format(len(character_list)), end - start)


# start = time.time()

# end = time.time()
# print("hp/ac avg speed check:", end - start)

# print(test_char.__dict__)

# class BulkCharManager:
#     def __init__(self):
