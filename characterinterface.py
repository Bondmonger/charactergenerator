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

        # adds the frames
        self.class_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.attrs_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.misc_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.party_frame = tk.Frame(master, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.acs_frame = tk.Frame(master, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.hps_frame = tk.Frame(master, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.control_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.display_frame = tk.Frame(master, relief=tk.RIDGE, borderwidth=4, bg='#000000')

        # establishes all label text values as strings
        self.class_label_text, self.attrs_label_text, self.misc_label_text, self.party_label_text = '', '', '', ''
        self.acs_label_text, self.hps_label_text, self.display_label_text = '', '', ''

        # creates labels
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
        self.control_label = tk.Label(master=self.control_frame, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                      height=6)
        self.display_label = tk.Label(master=self.display_frame, text=self.display_label_text, fg="#FFFFFF",
                                      font=('Courier', 12), height=6, bg='#000000')

        # updates label text values
        self.update()

        # places frames on grid
        self.class_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.attrs_frame.grid(row=1, column=0, sticky="ns")
        self.misc_frame.grid(row=1, column=1, sticky="nsew")
        self.party_frame.grid(row=0, column=2, rowspan=2, sticky="nsew")
        self.acs_frame.grid(row=0, column=3, rowspan=2, sticky="nsew")
        self.hps_frame.grid(row=0, column=4, rowspan=2, sticky="nsew")
        self.control_frame.grid(row=3, column=0, columnspan=5, sticky="nsew")
        self.display_frame.grid(row=4, column=0, columnspan=5, sticky="nsew")

        # packs labels
        self.class_label.pack(ipadx=5, ipady=5, anchor="w")
        self.attrs_label.pack(ipadx=5, ipady=0, anchor="w")
        self.misc_label.pack(ipadx=5, ipady=5, anchor="w")
        self.party_label.pack(ipadx=5, ipady=5, side="top")
        self.acs_label.pack(ipadx=5, ipady=5, side="top")
        self.hps_label.pack(ipadx=5, ipady=5, side="top")
        self.control_label.pack(ipadx=5, ipady=5, side="left")
        self.display_label.pack(ipadx=5, ipady=5)

        # generates buttons
        for y in range(7):
            self.button = tk.Button(self.attrs_frame, text="<", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                    command=lambda y=y: self.adjust_attribute(y, -1), relief=tk.FLAT)
            self.button.place(height=8, width=6, x=110, y=80 + 18 * y)
            self.button = tk.Button(self.attrs_frame, text=">", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                    command=lambda y=y: self.adjust_attribute(y, 1), relief=tk.FLAT)
            self.button.place(height=8, width=6, x=120, y=80 + 18 * y)
        self.new_button = tk.Button(self.control_frame, text="New", command=self.reroll, width=7, bg='#000000',
                                    fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
        self.add_button = tk.Button(self.control_frame, command=lambda: self.add_party_member(self.selected_character),
                                    text="Add", bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0,
                                    relief=tk.FLAT, width=7)
        self.remove_button = tk.Button(self.control_frame, text="Remove", bg='#000000', fg="#FFFFFF",
                                       command=lambda: self.remove_party_member(self.selected_character),
                                       font=('Courier', 12), underline=0, relief=tk.FLAT, width=7)
        self.drain_button = tk.Button(self.control_frame, command=lambda: self.drain(),
                                      text="Drain", bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0,
                                      relief=tk.FLAT, width=7)
        self.xp_button = tk.Button(self.control_frame, text="+1000xp", command=lambda: self.boost(), width=7,
                                   bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=5, relief=tk.FLAT)
        self.set_name = tk.Button(self.control_frame, command=lambda: self.name_character(self.selected_character),
                                  text="Accept", bg='#000000', fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                  width=7)
        self.marching_order = tk.Button(self.control_frame, command=lambda: self.arrange_party(self.selected_character),
                                        text="Order", bg='#000000', fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                        width=7, underline=0)
        self.name_slot = tk.Entry(self.control_frame, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                  insertbackground="#FFFFFF")

        # packs and unpacks buttons
        self.new_button.pack(side='left', fill='y')
        self.add_button.pack(side='left', fill='y')
        self.remove_button.pack(side='left', fill='y')
        self.drain_button.pack(side='left', fill='y')
        self.xp_button.pack(side='left', fill='y')
        self.set_name.pack(side='left', fill='y')
        self.marching_order.pack(side='left', fill='y')
        self.name_slot.pack(side='left')
        self.remove_button.pack_forget()                    # this one is actually a text input field
        self.set_name.pack_forget()
        self.marching_order.pack_forget()
        self.name_slot.pack_forget()

        # binds keys
        root.bind('n', lambda event: self.reroll())
        root.bind('a', lambda event: self.add_party_member(self.selected_character))
        root.bind('r', lambda event: self.remove_party_member(self.selected_character))
        root.bind('d', lambda event: self.drain())
        root.bind('x', lambda event: self.boost())

    def update(self):
        self.class_label['text'] = "{}\n{} {} {}"\
            .format(self.selected_character.character_name, self.selected_character.display_level,
                    self.selected_character.race, self.selected_character.display_class)
        self.attrs_label['text'] = "HP: {}\nAC: {}\nTH: {}\n\n{}"\
            .format(self.selected_character.hp, 10 + self.selected_character.calculate_ac(),
                    20 + self.selected_character.calculate_thaco(), self.stacked_attrs(self.selected_character)[0:-1])
        self.misc_label['text'] = "\n {}\n {} years old ({})\n\n XP: {:,}\n     {:,} xp to next level ({})\n\n {}' " \
                                  "{}   {} lbs\n\n Movement: {}\u0022\n Alignment: "\
            .format(self.selected_character.gender, self.selected_character.age[0], self.selected_character.age[1],
                    self.selected_character.xp, int(self.selected_character.next_level[0]) - self.selected_character.xp,
                    self.selected_character.next_level[1], int(self.selected_character.size[0] / 12),
                    str(self.selected_character.size[0] % 12) + '"' if self.selected_character.size[0] % 12 > 0 else '',
                    str(self.selected_character.size[1]), self.selected_character.class_movement())
        self.party_label['text'] = self.stacked_names(self.party_list)
        self.acs_label['text'] = self.stacked_acs(self.party_list)
        self.hps_label['text'] = self.stacked_hps(self.party_list)
        self.display_label['text'] = self.display_text[0]
        self.selected_character.display_attributes()

    def reroll(self):  # generates a new character and refreshes label text
        self.selected_character = character.Character(self.level)
        self.nonmember_buttons()
        self.update()
        self.display_text[0] = ''
        pass

    def refresh(self, current_char):  # establishes a new current character and refreshes label text
        self.selected_character = current_char
        self.display_text[0] = ''
        self.member_buttons()
        self.update()
        pass

    def drain(self):  # drains one level from current character
        self.display_text[0] = str(self.selected_character.calculate_level(-1))
        self.update()
        self.display_text[0] = ''
        pass

    def boost(self):  # awards 1,000 xp to current character
        self.selected_character.modify_xp(1000)
        self.display_text[0] = self.selected_character.calculate_level(0)
        self.update()
        self.display_text[0] = ''
        pass

    def adjust_attribute(self, attr, adj):  # modifies an attribute by the value of ADJ
        attr_list = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
        self.selected_character.modify_attribute(attr_list[attr], adj)
        self.update()
        pass

    @staticmethod
    def stacked_attrs(selected_character):  # generates text for display_label
        temp, other_atts = "", ["Int", "Wis", "Dex", "Con", "Cha", "Com"]
        temp = "Str: {}\n".format(selected_character.display_strength())
        for a in other_atts:
            temp = temp + "{}: {}\n".format(a, selected_character.attributes[a])
        return temp

    def add_party_member(self, selected_character):                                 # adds current character to party
        if len(self.party_list) < 8 and selected_character not in self.party_list:  # unless they're already in it
            self.select_name(selected_character)
            self.party_list.append(selected_character)                              # display_text is in name_character
            self.bind_member(len(self.party_list))
        pass

    def bind_member(self, party_index):  # binds a number key to the current character's location in the party (1 to 8)
        root.bind(party_index, lambda event: self.refresh(self.party_list[party_index-1]))

    def remove_party_member(self, selected_character):  # removes current character from party
        if len(self.party_list) > 0 and selected_character in self.party_list:
            root.unbind(len(self.party_list))
            self.party_list.remove(selected_character)
            self.display_text[0] = "{} has been removed from the party".format(selected_character.character_name)
            self.reroll()
        pass

    @staticmethod
    def stacked_names(party):  # displays character names in party_label
        temp = 'Party Members\n'
        for a in range(len(party)):
            temp += '\n\u0332{} {}'.format(str(a + 1), party[a].character_name)
        for b in range(len(party), 8):
            temp += '\n{} '.format(b + 1)
        return temp

    @staticmethod
    def stacked_acs(party):  # displays ACs in party_label
        temp = 'AC\n'
        for a in range(len(party)):
            temp += '\n{}'.format(10 + party[a].calculate_ac())
        return temp

    @staticmethod
    def stacked_hps(party):  # displays hps in party_label
        temp = 'HP\n'
        for a in range(len(party)):
            temp += '\n{}'.format(party[a].hp)
        return temp

    def member_buttons(self):                       # updates control panel
        for key in root.bind():                     # unbinds all hotkeys
            root.unbind(key)
        for member in range(len(self.party_list)):
            self.bind_member(member + 1)            # re-binds party index positions
        self.name_slot.pack_forget()
        self.set_name.pack_forget()
        self.add_button.pack_forget()
        self.drain_button.pack_forget()
        self.xp_button.pack_forget()
        self.marching_order.pack_forget()
        self.new_button.pack(side='left', fill='y')
        self.remove_button.pack(side='left', fill='y')
        self.drain_button.pack(side='left', fill='y')
        self.xp_button.pack(side='left', fill='y')
        if len(self.party_list) > 1:
            self.marching_order.pack(side='left', fill='y')
            root.bind('o', lambda event: self.arrange_party(self.selected_character))
        root.bind('n', lambda event: self.reroll())
        root.bind('r', lambda event: self.remove_party_member(self.selected_character))
        root.bind('d', lambda event: self.drain())
        root.bind('x', lambda event: self.boost())

    def nonmember_buttons(self):                    # updates control panel
        for key in root.bind():                     # unbinds all hotkeys
            root.unbind(key)
        for member in range(len(self.party_list)):
            self.bind_member(member + 1)            # re-binds party index positions
        self.remove_button.pack_forget()
        self.drain_button.pack_forget()
        self.xp_button.pack_forget()
        self.name_slot.pack_forget()
        self.set_name.pack_forget()
        self.marching_order.pack_forget()
        self.new_button.pack(side='left', fill='y')
        if len(self.party_list) < 8:
            self.add_button.pack(side='left', fill='y')
        self.drain_button.pack(side='left', fill='y')
        self.xp_button.pack(side='left', fill='y')
        root.bind('n', lambda event: self.reroll())
        root.bind('a', lambda event: self.add_party_member(self.selected_character))
        root.bind('d', lambda event: self.drain())
        root.bind('x', lambda event: self.boost())

    def select_name(self, selected_character):
        self.name_slot.delete(0, 'end')             # clears the Entry field
        self.new_button.pack_forget()               # unpacks the buttons
        self.add_button.pack_forget()
        self.drain_button.pack_forget()
        self.xp_button.pack_forget()
        for key in root.bind():                     # unbinds all hotkeys
            root.unbind(key)
        self.control_label['text'] = '   Enter character name:'
        self.name_slot.pack(side='left')            # packs input field
        self.set_name.pack(side='left', fill='y')   # packs 'Enter' button (Enter key is bound as well)
        self.name_slot.focus_set()                  # places cursor in input field
        root.bind('<Return>', lambda event: self.name_character(selected_character))

    def name_character(self, selected_character):
        temp_name = self.name_slot.get()            # captures name text
        selected_character.assign_name(temp_name)   # assigns name to character
        self.display_text[0] = "{} has been added to the party".format(selected_character.character_name)
        self.reroll()
        for member in range(len(self.party_list)):
            self.bind_member(member+1)              # re-binds party index positions
        root.unbind('<Return>')                     # releases 'Enter' key
        self.control_label['text'] = ''
        pass

    def arrange_party(self, selected_character):
        self.new_button.pack_forget()               # wipes out all buttons and key binds
        self.remove_button.pack_forget()
        self.drain_button.pack_forget()
        self.xp_button.pack_forget()
        self.marching_order.pack_forget()
        for key in root.bind():
            root.unbind(key)
        self.control_label['text'] = "  Assign {}'s new position with a NUMBER key (1 through {})"\
            .format(selected_character.character_name, len(self.party_list))
        for member in range(len(self.party_list)):
            self.intermediate_move(member)          # passes user to intermediate function to re-bind number keys
        pass

    def intermediate_move(self, position):          # binds number keys to helper function
        root.bind(position + 1, lambda event: self.move_member(position))

    def move_member(self, position):                # moves selected_character and removes control label text
        self.party_list.insert(position, self.party_list.pop(self.party_list.index(self.selected_character)))
        self.update()
        self.control_label['text'] = ''
        self.member_buttons()


root = tk.Tk()
my_gui = CharacterInterface(root, 5)
root.mainloop()
