import tkinter as tk
import character


class CharacterInterface:
    def __init__(self, master, level=1):
        self.party_list = []
        self.display_text = ['']
        self.level = level
        self.master = master
        self.selected_character = character.Character(self.level)
        master.title("Interface Template")
        master.configure(bg='#000000')

        self.class_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.attrs_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.misc_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.party_frame = tk.Frame(master, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.acs_frame = tk.Frame(master, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.hps_frame = tk.Frame(master, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.control_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.display_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')

        self.class_label_text = "\n{} {} {}"\
            .format(self.selected_character.display_level, self.selected_character.race,
                    self.selected_character.display_class)
        self.attrs_label_text = "HP: {}\nAC: {}\nTH: {}\n\n{}"\
            .format(self.selected_character.hp, 10 + self.selected_character.calculate_ac(),
                    20 + self.selected_character.calculate_thaco(), self.stacked_attrs(self.selected_character)[0:-1])
        self.misc_label_text = "\n {}\n {} years old ({})\n\n XP: {:,}\n     {:,} xp to next level ({})\n\n {}' {}   " \
                               "{} lbs\n\n Movement: \n Alignment: "\
            .format(self.selected_character.gender, self.selected_character.age[0], self.selected_character.age[1],
                    self.selected_character.xp, int(self.selected_character.next_level[0]) - self.selected_character.xp,
                    self.selected_character.next_level[1], int(self.selected_character.size[0] / 12),
                    str(self.selected_character.size[0] % 12) + '"' if self.selected_character.size[0] % 12 > 0 else '',
                    str(self.selected_character.size[1]))
        self.party_label_text = self.stacked_classes(self.party_list)
        self.acs_label_text = self.stacked_acs(self.party_list)
        self.hps_label_text = self.stacked_hps(self.party_list)
        self.display_label_text = self.display_text[0]

        self.class_label = tk.Label(master=self.class_frame, text=self.class_label_text, width=55, anchor='w',
                                    justify="left", bg='#000000', fg="#FFFFFF", font=('Courier', 12))
        self.attrs_label = tk.Label(master=self.attrs_frame, text=self.attrs_label_text, width=12, anchor='w',
                                    bg='#000000', fg="#FFFFFF", font=('Courier', 12), justify="left")
        self.misc_label = tk.Label(master=self.misc_frame, text=self.misc_label_text, width=45, justify="left",
                                   anchor='w', bg='#000000', fg="#FFFFFF", font=('Courier', 12))
        self.party_label = tk.Label(master=self.party_frame, text=self.party_label_text, bg='#000000', fg="#FFFFFF",
                                    font=('Courier', 12), width=15, justify='left', anchor='w')
        self.acs_label = tk.Label(master=self.acs_frame, text=self.acs_label_text, bg='#000000', fg="#FFFFFF",
                                  font=('Courier', 12), width=3, justify='left')
        self.hps_label = tk.Label(master=self.hps_frame, text=self.hps_label_text, bg='#000000', fg="#FFFFFF",
                                  font=('Courier', 12), width=3, justify='left')
        self.control_label = tk.Label(master=self.control_frame, bg='#000000', height=6)
        self.display_label = tk.Label(master=self.display_frame, text=self.display_label_text, fg="#FFFFFF",
                                      font=('Courier', 12), height=6, bg='#000000')

        self.class_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.attrs_frame.grid(row=1, column=0, sticky="ns")
        self.misc_frame.grid(row=1, column=1, sticky="nsew")
        self.party_frame.grid(row=0, column=2, rowspan=2, sticky="nsew")
        self.acs_frame.grid(row=0, column=3, rowspan=2, sticky="nsew")
        self.hps_frame.grid(row=0, column=4, rowspan=2, sticky="nsew")
        self.control_frame.grid(row=3, column=0, columnspan=5, sticky="nsew")
        self.display_frame.grid(row=4, column=0, columnspan=5, sticky="nsew")

        self.class_label.pack(ipadx=5, ipady=5, anchor="w")
        self.attrs_label.pack(ipadx=5, ipady=0, anchor="w")
        self.misc_label.pack(ipadx=5, ipady=5, anchor="w")
        self.party_label.pack(ipadx=5, ipady=5, side="top")
        self.acs_label.pack(ipadx=5, ipady=5, side="top")
        self.hps_label.pack(ipadx=5, ipady=5, side="top")
        self.control_label.pack(ipadx=5, ipady=5, side="left")
        self.display_label.pack(ipadx=5, ipady=5)

        for y in range(7):
            self.button = tk.Button(self.attrs_frame, text="<", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                    command=lambda y=y: self.adjust_attribute(y, -1), relief=tk.FLAT)
            self.button.place(height=8, width=6, x=110, y=80 + 18 * y)
            self.button = tk.Button(self.attrs_frame, text=">", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                    command=lambda y=y: self.adjust_attribute(y, 1), relief=tk.FLAT)
            self.button.place(height=8, width=6, x=120, y=80 + 18 * y)

        self.new_button = tk.Button(self.control_frame, text="New", command=self.reroll, width=7,
                           bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
        self.new_button.pack(side='left', fill='y')
        root.bind('n', lambda event: self.reroll())

        self.add_button = tk.Button(self.control_frame, command=lambda: self.add_party_member(self.selected_character),
                                    text="Add", bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0,
                                    relief=tk.FLAT, width=7)
        self.add_button.pack(side='left', fill='y')
        root.bind('a', lambda event: self.add_party_member(self.selected_character))

        self.remove_button = tk.Button(self.control_frame, text="Remove", bg='#000000', fg="#FFFFFF",
                                       command=lambda: self.remove_party_member(self.selected_character),
                                       font=('Courier', 12), underline=0, relief=tk.FLAT, width=7)
        self.remove_button.pack(side='left', fill='y')
        self.remove_button.pack_forget()
        root.bind('r', lambda event: self.remove_party_member(self.selected_character))

        self.drain_button = tk.Button(self.control_frame, command=lambda: self.drain(),
                                      text="Drain", bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0,
                                      relief=tk.FLAT, width=7)
        self.drain_button.pack(side='left', fill='y')
        root.bind('d', lambda event: self.drain())

        self.xp_button = tk.Button(self.control_frame, text="+1000xp", command=lambda: self.boost(), width=7,
                                   bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=5, relief=tk.FLAT)
        self.xp_button.pack(side='left', fill='y')
        root.bind('x', lambda event: self.boost())

        self.selected_character.display_attributes()

        # if not self.selected_character.display_class == 'Wight':
        #     self.drain_button = tk.Button(self.control_frame, command=lambda: self.drain(),
        #                             text="Drain", bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0,
        #                             relief=tk.FLAT)
        #     self.drain_button.place(width=75, x=185, y=25)
        #     root.bind('d', lambda event: self.drain())
        #     self.xp_button = tk.Button(self.control_frame, text="+1000xp", command=lambda: self.boost(),
        #                        bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=5, relief=tk.FLAT)
        #     self.xp_button.place(width=75, x=265, y=25)
        #     root.bind('x', lambda event: self.boost())
        # else:
        #     root.unbind('d')
        #     root.unbind('x')

    def update(self):
        self.class_label['text'] = "\n{} {} {}"\
            .format(self.selected_character.display_level, self.selected_character.race,
                    self.selected_character.display_class)
        self.attrs_label['text'] = "HP: {}\nAC: {}\nTH: {}\n\n{}"\
            .format(self.selected_character.hp, 10 + self.selected_character.calculate_ac(),
                    20 + self.selected_character.calculate_thaco(), self.stacked_attrs(self.selected_character)[0:-1])
        self.misc_label['text'] = "\n {}\n {} years old ({})\n\n XP: {:,}\n     {:,} xp to next level ({})\n\n {}' " \
                                  "{}   {} lbs\n\n Movement: \n Alignment: "\
            .format(self.selected_character.gender, self.selected_character.age[0], self.selected_character.age[1],
                    self.selected_character.xp, int(self.selected_character.next_level[0]) - self.selected_character.xp,
                    self.selected_character.next_level[1], int(self.selected_character.size[0] / 12),
                    str(self.selected_character.size[0] % 12) + '"' if self.selected_character.size[0] % 12 > 0 else '',
                    str(self.selected_character.size[1]))
        self.party_label['text'] = self.stacked_classes(self.party_list)
        self.acs_label['text'] = self.stacked_acs(self.party_list)
        self.hps_label['text'] = self.stacked_hps(self.party_list)
        self.display_label['text'] = self.display_text[0]
        self.selected_character.display_attributes()

    def reroll(self):
        self.selected_character = character.Character(self.level)
        self.non_member_buttons()
        self.update()
        self.display_text[0] = ''
        pass

    def refresh(self, current_char):
        self.selected_character = current_char
        self.display_text[0] = ''
        self.member_buttons()
        self.update()
        pass

    def drain(self):
        self.display_text[0] = str(self.selected_character.calculate_level(-1))
        self.update()
        self.display_text[0] = ''
        pass

    def boost(self):
        self.selected_character.modify_xp(1000)
        self.display_text[0] = self.selected_character.calculate_level(0)
        self.update()
        self.display_text[0] = ''
        pass

    def adjust_attribute(self, attr, adj):
        attr_list = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
        self.selected_character.modify_attribute(attr_list[attr], adj)
        self.update()
        pass

    def stacked_attrs(self, selected_character):
        temp, other_atts = "", ["Int", "Wis", "Dex", "Con", "Cha", "Com"]
        temp = "Str: {}\n".format(selected_character.display_strength())
        for a in other_atts:
            temp = temp + "{}: {}\n".format(a, selected_character.attributes[a])
        return temp

    def add_party_member(self, selected_character):
        if len(self.party_list) < 8 and selected_character not in self.party_list:
            self.party_list.append(selected_character)
            self.display_text[0] = "{} has been added to the party".format(selected_character.display_class)
            self.bind_member(len(self.party_list))
            self.reroll()
        pass

    def bind_member(self, party_index):
        root.bind(party_index, lambda event: self.refresh(self.party_list[party_index-1]))

    def remove_party_member(self, selected_character):
        if len(self.party_list) > 0 and selected_character in self.party_list:
            root.unbind(len(self.party_list))
            self.party_list.remove(selected_character)
            self.display_text[0] = "{} has been removed from the party".format(selected_character.display_class)
            self.reroll()
        pass

    def stacked_classes(self, party):  # this will become stacked names
        temp = 'Party Members\n'
        for a in range(len(party)):
            temp += '\n\u0332{} {}'.format(str(a + 1), party[a].display_class)
        for b in range(len(party), 8):
            temp += '\n{} '.format(b + 1)
        return temp

    def stacked_acs(self, party):
        temp = 'AC\n'
        for a in range(len(party)):
            temp += '\n{}'.format(10 + party[a].calculate_ac())
        return temp

    def stacked_hps(self, party):
        temp = 'HP\n'
        for a in range(len(party)):
            temp += '\n{}'.format(party[a].hp)
        return temp

    def member_buttons(self):
        if self.selected_character in self.party_list:
            self.add_button.pack_forget()
            self.drain_button.pack_forget()
            self.xp_button.pack_forget()
            self.remove_button.pack(side='left', fill='y')
            self.drain_button.pack(side='left', fill='y')
            self.xp_button.pack(side='left', fill='y')

    def non_member_buttons(self):
        if self.selected_character not in self.party_list:
            self.remove_button.pack_forget()
            self.drain_button.pack_forget()
            self.xp_button.pack_forget()
            self.add_button.pack(side='left', fill='y')
            self.drain_button.pack(side='left', fill='y')
            self.xp_button.pack(side='left', fill='y')


root = tk.Tk()
my_gui = CharacterInterface(root, 5)
root.mainloop()
