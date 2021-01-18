import tkinter as tk
import character

window = tk.Tk()
party_list = []
display_text = ['']


def character_sheet(selected_character):
    class_frame = tk.Frame(master=window, relief=tk.RIDGE, borderwidth=4, bg='#000000')
    attrs_frame = tk.Frame(master=window, relief=tk.RIDGE, borderwidth=4, bg='#000000')
    misc_frame = tk.Frame(master=window, relief=tk.RIDGE, borderwidth=4, bg='#000000')
    party_frame = tk.Frame(master=window, relief=tk.FLAT, borderwidth=4, bg='#000000')
    acs_frame = tk.Frame(master=window, relief=tk.FLAT, borderwidth=4, bg='#000000')
    hps_frame = tk.Frame(master=window, relief=tk.FLAT, borderwidth=4, bg='#000000')
    control_frame = tk.Frame(master=window, relief=tk.RIDGE, borderwidth=4, bg='#000000')
    display_frame = tk.Frame(master=window, relief=tk.RIDGE, borderwidth=4, bg='#000000')

    class_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    attrs_frame.grid(row=1, column=0, sticky="ns")
    misc_frame.grid(row=1, column=1, sticky="nsew")
    party_frame.grid(row=0, column=2, rowspan=2, sticky="nsew")
    acs_frame.grid(row=0, column=3, rowspan=2, sticky="nsew")
    hps_frame.grid(row=0, column=4, rowspan=2, sticky="nsew")
    control_frame.grid(row=3, column=0, columnspan=5, sticky="nsew")
    display_frame.grid(row=4, column=0, columnspan=5, sticky="nsew")

    class_label = tk.Label(master=class_frame, width=55, anchor='w', justify="left",
                           bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                           text="\n{} {} {}".format(selected_character.display_level,
                                                    selected_character.race,
                                                    selected_character.display_class))
    attrs_label = tk.Label(master=attrs_frame,
                           width=12, anchor='w',
                           bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                           text="HP: {}\nAC: {}\nTH: {}\n\n{}".format(selected_character.hp,
                                                                      10+selected_character.calculate_ac(),
                                                                      20,
                                                                      stacked_attrs(selected_character)[0:-1]),
                           justify="left")
    misc_label = tk.Label(master=misc_frame,
                          width=45, justify="left", anchor='w',
                          bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                          text="\n {}\n {} years old ({})\n\n XP: {:,}\n     {:,} xp to next level "
                               "({})\n\n {}' {}   {} lbs\n\n Movement: \n Alignment: ".format(
                              selected_character.gender,
                              selected_character.age[0],
                              selected_character.age[1],
                              selected_character.xp,
                              int(selected_character.next_level[0]) - selected_character.xp,
                              selected_character.next_level[1],
                              int(selected_character.size[0] / 12),
                              str(selected_character.size[0] % 12) + '"' if selected_character.size[0] % 12 > 0 else '',
                              str(selected_character.size[1])))
    party_label = tk.Label(master=party_frame, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                           width=15, justify='left', anchor='w', text=stacked_classes(party_list))
    acs_label = tk.Label(master=acs_frame, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                         width=3, justify='left', text=stacked_acs(party_list))
    hps_label = tk.Label(master=hps_frame, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                         width=3, justify='left', text=stacked_hps(party_list))
    control_label = tk.Label(master=control_frame, height=6, bg='#000000')
    display_label = tk.Label(master=display_frame, fg="#FFFFFF", font=('Courier', 12),
                             text=display_text[0], height=6, bg='#000000')

    class_label.pack(ipadx=5, ipady=5, anchor="w")
    attrs_label.pack(ipadx=5, ipady=0, anchor="w")
    misc_label.pack(ipadx=5, ipady=5, anchor="w")
    party_label.pack(ipadx=5, ipady=5, side="top")
    acs_label.pack(ipadx=5, ipady=5, side="top")
    hps_label.pack(ipadx=5, ipady=5, side="top")
    control_label.pack(ipadx=5, ipady=5)
    display_label.pack(ipadx=5, ipady=5)

    # for a in range(7):
    #     button = tk.Button(attrs_frame, text="<", command=lambda: adjust_attribute(selected_character, a, -1),
    #                        bg='#000000', fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT)
    #     button.place(width=6, x=110, y=68 + 17.8 * a)
    #     button = tk.Button(attrs_frame, text=">", command=lambda: adjust_attribute(selected_character, a, 1),
    #                        bg='#000000', fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT)
    #     button.place(width=6, x=120, y=68 + 17.8 * a)

    button = tk.Button(control_frame, text="New", command=reroll,
                       bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
    button.place(width=75, x=25, y=25)
    window.bind('n', lambda event: reroll())
    if selected_character in party_list:
        button = tk.Button(control_frame, text="Remove", command=lambda: remove_party_member(selected_character),
                           bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
        button.place(width=75, x=105, y=25)
        window.bind('r', lambda event: remove_party_member(selected_character))
    else:
        button = tk.Button(control_frame, text="Add", command=lambda: add_party_member(selected_character),
                       bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
        button.place(width=75, x=105, y=25)
        window.bind('a', lambda event: add_party_member(selected_character))
    if not selected_character.display_class == 'Wight':
        button = tk.Button(control_frame, text="Drain", command=lambda: drain(selected_character),
                           bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
        button.place(width=75, x=185, y=25)
        window.bind('d', lambda event: drain(selected_character))
        button = tk.Button(control_frame, text="+1000xp", command=lambda: boost(selected_character),
                           bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=5, relief=tk.FLAT)
        button.place(width=75, x=265, y=25)
        window.bind('x', lambda event: boost(selected_character))

    for member in range(len(party_list)):
        def make_lambda(memb):                                          # helper prevents lambda from capturing member
            return lambda event: character_sheet(party_list[memb])      # NEVER FORGET
        window.bind(member+1, make_lambda(member))                      # syncs up number keys with party members
    selected_character.display_attributes()
    display_text[0] = ''
    return


def reroll():
    selected_character = character.Character(3)
    character_sheet(selected_character)
    pass


def drain(selected_character):
    display_text[0] = str(selected_character.calculate_level(-1))
    character_sheet(selected_character)
    pass


def boost(selected_character):
    selected_character.modify_xp(1000)
    display_text[0] = selected_character.calculate_level(0)
    character_sheet(selected_character)
    pass


def adjust_attribute(selected_character, indexposition, amount):
    att_list = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
    selected_character.modify_attribute(att_list[indexposition], amount)
    character_sheet(selected_character)
    pass


def add_party_member(member):
    if len(party_list) < 8 and member not in party_list:
        party_list.append(member)
        display_text[0] = "{} has been added to the party".format(member.display_class)
        reroll()
    pass


def remove_party_member(member):
    if len(party_list) > 0 and member in party_list:
        party_list.remove(member)
        display_text[0] = "{} has been removed from the party".format(member.display_class)
        reroll()
    pass


def stacked_attrs(relevant):
    temp, other_atts = "", ["Int", "Wis", "Dex", "Con", "Cha", "Com"]
    temp = "Str: {}\n".format(relevant.display_strength())
    for a in other_atts:
        temp = temp + "{}: {}\n".format(a, relevant.attributes[a])
    return temp


def stacked_classes(party):  # this will become stacked names
    temp = 'Party Members\n'
    for a in range(len(party)):
        temp += '\n\u0332{} {}'.format(a+1, party[a].display_class)
    for b in range(len(party), 8):
        temp += '\n{} '.format(b+1)
    return temp


def stacked_acs(party):
    temp = 'AC\n'
    for a in range(len(party)):
        temp += '\n{}'.format(10+party[a].calculate_ac())
    return temp


def stacked_hps(party):
    temp = 'HP\n'
    for a in range(len(party)):
        temp += '\n{}'.format(party[a].hp)
    return temp


reroll()
window.configure(bg='#000000')
window.mainloop()
