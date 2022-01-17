import tkinter as tk
import character
import selectclass
import attributes


class CharacterInterface:
    def __init__(self, master, level=1):
        self.party_list = []
        self.display_text = ['']
        self.level = level
        self.master = master
        self.selected_character = character.Character(self.level)
        self.master.attributes('-fullscreen', True)
        self.master.title("Interface Template")
        self.master.configure(bg='#000000', relief=tk.RIDGE, borderwidth=16)

        self.gender = "random"                  # takes "random", "male" or "female"
        self.tk_variable = tk.IntVar()          # this is establishing a type for the dropdown menu in head_controls

        # generates the 6x4 grid
        self.master.grid_propagate(False)
        for k in range(4):
            self.master.grid_rowconfigure(k, weight=1, uniform=1)
        for i in range(6):
            self.master.grid_columnconfigure(i, weight=1, uniform=1)
            for j in range(4):
                self.dummy_frame = tk.Frame(self.master, relief=tk.RIDGE, borderwidth=4,
                                            bg='#'+str(2*j)+str(2*j)+str(2*j)+str(i)+str(i)+str(i))
                self.dummy_frame.grid(row=j, column=i, sticky='nsew')

        # generates start screen
        self.start_frame = tk.Frame(self.master, bg='#000000', relief=tk.RIDGE, borderwidth=4)
        self.start_frame.grid(row=0, column=0, rowspan=4, columnspan=6, sticky="nsew")
        self.start_frame.grid_propagate(False)                  # this locks start_frame's right border
        self.start_frame.grid_columnconfigure(0, weight=1, uniform=1)
        self.start_frame.grid_rowconfigure(0, weight=2, uniform=1)
        for i in range(6):
            self.start_frame.grid_rowconfigure(i+1, weight=1, uniform=1)
        self.start_label = tk.Label(master=self.start_frame, relief=tk.FLAT, fg="#FFFFFF",
                                    bg='#000000', font=('Courier', 12), justify="center")
        self.start_label.grid(row=0, column=0, sticky='nsew')
        self.start_label['text'] = "***WELCOME TO NATHAN'S 1E AD&D CHARACTER GENERATOR***\n\n\nWHICH METHOD WOULD YOU" \
                                   " LIKE TO USE?\n\n\n--------------------"
        self.methodi_button = tk.Button(self.start_frame, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                        command=lambda: self.methodi_header(attributes.methodi()), relief=tk.FLAT,
                                        text="METHOD I\n4d6, keep the top three, player selects order")
        self.methodi_button.grid(row=1, column=0, sticky='nsew')
        self.methodii_button = tk.Button(self.start_frame, command=lambda: self.methodii_header(attributes.methodii()),
                                         bg='#000000', fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                         text="METHOD II\n3d6 twelve times, keep the top six, player selects order")
        self.methodii_button.grid(row=2, column=0, sticky='nsew')
        self.methodiii_button = tk.Button(self.start_frame, fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                          command=lambda: self.methodiii_header(attributes.methodiii()),
                                          bg='#000000', text="METHOD III\n3d6 six times per attribute, order is locked")
        self.methodiii_button.grid(row=3, column=0, sticky='nsew')
        self.methodiv_button = tk.Button(self.start_frame, bg='#000000', font=('Courier', 12), relief=tk.FLAT,
                                         command=lambda: self.methodiv_header(attributes.methodiv()), fg="#FFFFFF",
                                         text="METHOD IV\ncreate 12 characters via 3d6, player selects one, order is "
                                              "locked")
        self.methodiv_button.grid(row=4, column=0, sticky='nsew')
        self.methodv_button = tk.Button(self.start_frame, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                        relief=tk.FLAT, command=lambda: self.methodv_header(),
                                        text="METHOD V\nclass-based 3d6 to 9d6 method, order is locked")
        self.methodv_button.grid(row=5, column=0, sticky='nsew')
        self.methodvi_button = tk.Button(self.start_frame, command=lambda: self.startframe_close(), bg='#000000',
                                         fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                         text="METHOD VI\nhybrid of Methods I & V, order is locked")
        self.methodvi_button.grid(row=6, column=0, sticky='nsew')

        # generates character sheet frame
        self.char_frame = tk.Frame(self.master, bg='#000077')
        self.char_frame.grid(row=0, column=0, rowspan=2, columnspan=3, sticky="nsew")
        self.char_frame.grid_propagate(False)                   # this locks char_frame's right border
        self.char_frame.grid_columnconfigure(0, weight=1, uniform=1)
        self.char_frame.grid_columnconfigure(1, weight=3, uniform=1)
        self.char_frame.grid_rowconfigure(0, weight=1, uniform=1)
        self.char_frame.grid_rowconfigure(1, weight=6, uniform=1)
        self.chtop_label = tk.Label(master=self.char_frame, relief=tk.RIDGE, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                    font=('Courier', 12), justify="left", anchor='nw')
        self.chtop_label.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.chleft_label = tk.Label(master=self.char_frame, relief=tk.RIDGE, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                     font=('Courier', 12), justify="left", anchor='nw')
        self.chleft_label.grid(row=1, column=0, sticky='nsew')
        self.chright_label = tk.Label(master=self.char_frame, relief=tk.RIDGE, borderwidth=4, fg="#FFFFFF",
                                      bg='#000000', font=('Courier', 12), justify="left", anchor='nw')
        self.chright_label.grid(row=1, column=1, sticky='nsew')

        # generates party frame
        self.member_frame = tk.Frame(self.master, bg='#000077')
        self.member_frame.grid(row=0, column=3, rowspan=2, columnspan=3, sticky="nsew")
        self.member_frame.grid_propagate(False)
        self.member_frame.grid_columnconfigure(0, weight=5, uniform=1)
        self.member_frame.grid_columnconfigure(1, weight=1, uniform=1)
        self.member_frame.grid_columnconfigure(2, weight=1, uniform=1)
        self.member_frame.grid_rowconfigure(0, weight=1, uniform=1)
        self.party_label = tk.Label(master=self.member_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                    font=('Courier', 12), justify="left", anchor='nw')
        self.party_label.grid(row=0, column=0, rowspan=2, sticky='nsew')
        self.acs_label = tk.Label(master=self.member_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                  font=('Courier', 12), justify="left", anchor='nw')
        self.acs_label.grid(row=0, column=1, rowspan=2, sticky='nsew')
        self.hps_label = tk.Label(master=self.member_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                  font=('Courier', 12), justify="left", anchor='nw')
        self.hps_label.grid(row=0, column=2, rowspan=2, sticky='nsew')

        # generates control/display frame
        self.contdisp_frame = tk.Frame(self.master, bg='#000077')
        self.contdisp_frame.grid(row=2, column=0, rowspan=2, columnspan=6, sticky="nsew")
        self.contdisp_frame.grid_propagate(False)
        self.contdisp_frame.grid_columnconfigure(0, weight=1, uniform=1)
        self.contdisp_frame.grid_rowconfigure(0, weight=3, uniform=1)
        self.contdisp_frame.grid_rowconfigure(1, weight=3, uniform=1)
        self.contdisp_frame.grid_rowconfigure(2, weight=1, uniform=1)
        self.display_label_text = ''
        self.control_label = tk.Label(master=self.contdisp_frame, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                      font=('Courier', 12), justify="left", anchor='nw')
        self.display_label = tk.Label(master=self.contdisp_frame, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                      font=('Courier', 12), text=self.display_label_text, justify="left", anchor='w')
        self.return_label = tk.Label(master=self.contdisp_frame, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                     font=('Courier', 12), justify="left", anchor='w')
        self.control_label.grid(row=1, column=0, sticky='nsew')
        self.display_label.grid(row=0, column=0, sticky='nsew')
        self.return_label.grid(row=2, column=0, sticky='nsew')        # AND NOW THE BUTTONS
        self.new_button = tk.Button(self.control_label, text="New", command=self.reroll, width=7, bg='#000000',
                                    fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
        self.drain_button = tk.Button(self.control_label, command=lambda: self.drain(), text="Drain  ", bg='#000000',
                                      fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
        self.add_button = tk.Button(self.control_label, command=lambda: self.add_party_member(self.selected_character),
                                    text="Add    ", bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0,
                                    relief=tk.FLAT)
        self.remove_button = tk.Button(self.control_label, text="Remove ", bg='#000000', fg="#FFFFFF", underline=0,
                                       command=lambda: self.remove_party_member(self.selected_character),
                                       font=('Courier', 12), relief=tk.FLAT)
        self.xp_button = tk.Button(self.control_label, text="+1000xp", command=lambda: self.boost(), bg='#000000',
                                   fg="#FFFFFF", font=('Courier', 12), underline=5, relief=tk.FLAT)
        self.set_name = tk.Button(self.control_label, command=lambda: self.name_character(self.selected_character),
                                  text="Accept ", bg='#000000', fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT)
        self.marching_order = tk.Button(self.control_label, command=lambda: self.arrange_party(self.selected_character),
                                        text="Order  ", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                        relief=tk.FLAT, underline=0)
        self.name_slot = tk.Entry(self.control_label, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                  insertbackground="#FFFFFF")
        self.test_button = tk.Button(self.return_label, text="return to main menu", bg='#000000', fg="#FFFFFF",
                                     font=('Courier', 12), relief=tk.FLAT, anchor='w', command=lambda: self.startlift())

        # establishes all label_text values as strings
        self.chtop_label_text, self.chleft_label_text, self.chright_label_text, self.party_label_text = '', '', '', ''
        self.acs_label_text, self.hps_label_text, self.start_label = '', '', ''

        # packs and unpacks buttons
        self.new_button.pack(side='left')
        self.add_button.pack(side='left')
        self.drain_button.pack(side='left')
        self.remove_button.pack(side='left')
        self.xp_button.pack(side='left')
        self.set_name.pack(side='left')
        self.marching_order.pack(side='left')
        self.name_slot.pack(side='left')                            # this one is actually a text input field
        self.test_button.pack(side='bottom')
        self.remove_button.pack_forget()
        self.set_name.pack_forget()
        self.marching_order.pack_forget()
        self.name_slot.pack_forget()
        
        self.master.bind('<Escape>', lambda event: self.escape_function())

        self.start_frame.lift()                     # raises the start frame
        self.update_charsheet()                     # rolls up a method VI character and populates the character sheet

        # initializes elements used in intermediate frames
        self.selection_frame = tk.Frame()
        self.attributes_frame = tk.Frame()
        self.header_control_frame = tk.Frame()
        self.gray_frame = tk.Frame()
        self.swap_frame = tk.Frame()
        self.method_label = tk.Label()
        self.methodiv_label = tk.Label()            # in order to reset header when race is set to "human"
        self.newlabel = tk.Label()

        self.button = tk.Button()
        self.rc_opts = tk.Button()
        self.close_selection_frame = tk.Button()
        self.reroll_header = tk.Button()
        self.gender_select = tk.Button()
        self.level_select = tk.Button()
        self.choice_button = tk.Button()
        self.dropdown_button = tk.Button()

        self.make_another_character = self.reroll   # self.m_a_c()
        return

    def update_charsheet(self):
        self.generate_character_label()
        self.generate_party_label()
        self.display_label['text'] = self.display_text[0]

    def generate_character_label(self):
        self.chtop_label['text'] = "{}\n{} {} {}"\
            .format(self.selected_character.character_name, self.selected_character.display_level,
                    self.selected_character.race, self.selected_character.display_class)
        chleft_label_widgets = self.chleft_label.pack_slaves()      # we need to completely clear chleft_label...
        for y in chleft_label_widgets:
            y.pack_forget()                                         # ...in order to reset the attribute buttons
        self.chleft_label['text'] = "HP: {}\nAC: {}\nTH: {}\n\n{}"\
            .format(self.selected_character.hp, 10 + self.selected_character.calculate_ac(),
                    20 + self.selected_character.calculate_thaco(), self.stacked_attrs(self.selected_character)[0:-1])
        for x in range(7):
            self.button = tk.Button(self.chleft_label, text="<", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                    command=lambda x=x: self.adjust_attribute(x, -1), relief=tk.FLAT)
            self.button.place(height=8, width=6, x=110, y=80 + 18 * x)
            self.button = tk.Button(self.chleft_label, text=">", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                    command=lambda x=x: self.adjust_attribute(x, 1), relief=tk.FLAT)
            self.button.place(height=8, width=6, x=120, y=80 + 18 * x)
        self.chright_label['text'] = "\n{}\n{} years old ({})\n\nXP: {:,}\n    {:,} xp to next level ({})\n\n{}' "\
                                     "{}   {} lbs\n\nMovement: {}\u0022\nAlignment: \nPsionics: "\
            .format(self.selected_character.gender, self.selected_character.age[0], self.selected_character.age[1],
                    self.selected_character.xp, int(self.selected_character.next_level[0]) - self.selected_character.xp,
                    self.selected_character.next_level[1], int(self.selected_character.size[0] / 12),
                    str(self.selected_character.size[0] % 12) + '"' if self.selected_character.size[0] % 12 > 0 else '',
                    str(self.selected_character.size[1]), self.selected_character.class_movement())

    def generate_party_label(self):
        self.party_label['text'] = self.stacked_names(self.party_list)
        self.acs_label['text'] = self.stacked_acs(self.party_list)
        self.hps_label['text'] = self.stacked_hps(self.party_list)

    def reroll(self):                                       # generates a new character and refreshes label text
        self.selected_character = character.Character(self.level)
        self.nonmember_buttons()
        self.update_charsheet()
        self.display_text[0] = ''
        pass

    def update_newchar_button(self, replacement_function):
        self.make_another_character = replacement_function  # switches NEW button from VI reroll to argument method
        self.new_button.config(command=lambda: self.make_another_character())
        self.master.bind('n', lambda event: self.make_another_character())
        self.nonmember_buttons()                            # ...and refreshes charsheet buttons

    def refresh(self, current_char):                        # establishes new selected_character and refreshes the label
        self.selected_character = current_char
        self.display_text[0] = ''
        self.member_buttons()
        self.update_charsheet()
        pass

    def drain(self):                                        # drains one level from current character
        self.display_text[0] = str(self.selected_character.calculate_level(-1))
        self.update_charsheet()
        self.display_text[0] = ''
        pass

    def boost(self):                                        # awards 1,000 xp to current character
        self.selected_character.modify_xp(1000)
        self.display_text[0] = self.selected_character.calculate_level(0)
        self.update_charsheet()
        self.display_text[0] = ''
        pass

    def adjust_attribute(self, attr, adj):                  # modifies an attribute by the value of adj
        attr_list = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
        self.selected_character.modify_attribute(attr_list[attr], adj)
        self.update_charsheet()
        pass

    @staticmethod
    def stacked_attrs(selected_character):                  # generates text for display_label
        temp, other_atts = "", ["Int", "Wis", "Dex", "Con", "Cha", "Com"]
        temp = "Str: {}\n".format(selected_character.display_strength())
        for a in other_atts:
            temp = temp + "{}: {}\n".format(a, selected_character.attributes[a])
        return temp

    def add_party_member(self, selected_character):                                 # adds current character to party
        if len(self.party_list) < 8 and selected_character not in self.party_list:  # ...unless they're already in it
            self.select_name(selected_character)
            self.party_list.append(selected_character)                              # display_text is in name_character
            self.bind_member(len(self.party_list))
        pass

    def bind_member(self, party_index):  # binds a number key to the current character's location in the party (1 to 8)
        self.master.bind(party_index, lambda event: self.refresh(self.party_list[party_index-1]))

    def remove_party_member(self, selected_character):  # removes current character from party
        if len(self.party_list) > 0 and selected_character in self.party_list:
            self.master.unbind(len(self.party_list))
            self.party_list.remove(selected_character)
            self.display_text[0] = "{} has been removed from the party".format(selected_character.character_name)
            self.make_another_character()
        pass

    @staticmethod
    def stacked_names(party):  # displays character names in party_label
        temp = 'Party Members\n'
        for a, member in enumerate(party, 1):
            temp += '\n\u0332{} {}'.format(str(a), member.character_name)
        for b in range(len(party)+1, 9):
            temp += '\n{} '.format(b)
        return temp

    @staticmethod
    def stacked_acs(party):  # displays ACs in party_label
        temp = 'AC\n'
        for member in party:
            temp += '\n{}'.format(10 + member.calculate_ac())
        return temp

    @staticmethod
    def stacked_hps(party):  # displays hps in party_label
        temp = 'HP\n'
        for member in party:
            temp += '\n{}'.format(member.hp)
        return temp

    def member_buttons(self):                       # updates control panel
        for key in root.bind():                     # unbinds all hotkeys
            root.unbind(key)
        control_panel_buttons = self.control_label.pack_slaves()
        for y in control_panel_buttons:             # unbinds all buttons
            y.pack_forget()
        for member in range(len(self.party_list)):
            self.bind_member(member + 1)            # re-binds party index positions
        self.new_button.pack(side='left')           # re-binds buttons
        self.remove_button.pack(side='left')
        self.drain_button.pack(side='left')
        self.xp_button.pack(side='left')
        if len(self.party_list) > 1:                # re-binds hotkeys
            self.marching_order.pack(side='left')
            self.master.bind('o', lambda event: self.arrange_party(self.selected_character))
        self.master.bind('n', lambda event: self.make_another_character())
        self.master.bind('r', lambda event: self.remove_party_member(self.selected_character))
        self.master.bind('d', lambda event: self.drain())
        self.master.bind('x', lambda event: self.boost())
        self.master.bind('<Escape>', lambda event: self.escape_function())

    def nonmember_buttons(self):                    # updates control panel
        for key in root.bind():                     # unbinds all hotkeys
            self.master.unbind(key)
        control_panel_buttons = self.control_label.pack_slaves()
        for y in control_panel_buttons:
            y.pack_forget()
        for member in range(len(self.party_list)):
            self.bind_member(member + 1)            # re-binds party index positions
        self.new_button.pack(side='left')
        if len(self.party_list) < 8:
            self.add_button.pack(side='left')
        self.drain_button.pack(side='left')
        self.xp_button.pack(side='left')
        self.master.bind('n', lambda event: self.make_another_character())
        self.master.bind('a', lambda event: self.add_party_member(self.selected_character))
        self.master.bind('d', lambda event: self.drain())
        self.master.bind('x', lambda event: self.boost())
        self.master.bind('<Escape>', lambda event: self.escape_function())

    def select_name(self, selected_character):      # CREATES THE FIELD FOR ASSIGNING CHARACTER NAME
        self.name_slot.delete(0, 'end')             # clears the Entry field
        self.new_button.pack_forget()               # unpacks the buttons
        self.add_button.pack_forget()
        self.drain_button.pack_forget()
        self.xp_button.pack_forget()
        for key in root.bind():                     # unbinds all hotkeys
            self.master.unbind(key)
        self.control_label['text'] = '   Enter character name:'
        self.name_slot.pack(side='left')            # packs input field
        self.set_name.pack(side='left')             # packs 'Enter' button (Enter key is bound as well)
        self.name_slot.focus_set()                  # places cursor in input field
        self.master.bind('<Return>', lambda event: self.name_character(selected_character))

    def name_character(self, selected_character):   # names character AND places them in the party
        temp_name = self.name_slot.get()            # captures name text...
        selected_character.assign_name(temp_name)   # assigns name to character...
        self.display_text[0] = "{} has been added to the party".format(selected_character.character_name)
        self.update_charsheet()                     # here update_charsheet / member_buttons replaces reroll()...
        self.member_buttons()                       # ...so that we stay on the selected character
        for member in range(len(self.party_list)):
            self.bind_member(member + 1)            # re-binds party index positions
        self.master.unbind('<Return>')              # releases 'Enter' key
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
        for position, member in enumerate(self.party_list):
            self.intermediate_move(position)        # passes user to intermediate function to re-bind number keys
        pass

    def intermediate_move(self, position):          # binds number keys to helper function
        root.bind(position + 1, lambda event: self.move_member(position))

    def move_member(self, position):                # moves selected_character and removes control label text
        self.party_list.insert(position, self.party_list.pop(self.party_list.index(self.selected_character)))
        self.update_charsheet()
        self.control_label['text'] = ''             # move_member() is a helper method to intermediate_move()
        self.member_buttons()                       # ...for preserving the assignments through the incrementer

    def clbutt(self):
        self.selection_frame.destroy()
        self.attributes_frame.destroy()
        self.start_frame.lift()                     # startframe lift required in case charsheet has been lifted

    def startlift(self):                            # method required for "return to main menu" button lambda
        self.start_frame.lift()

    def escape_function(self):
        self.master.destroy()

    def startframe_close(self):
        self.start_frame.lower()    # formerly self.start_frame.grid_forget() - don't want to un-pack/un-grid this frame
        self.update_newchar_button(self.reroll)
        self.reroll()

    def headerdefaults(self, attribs):                  # generates common elements for method I & II headers & susps.
        self.attributes_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.attributes_frame.grid(row=0, column=0, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        method_colform, attr_names = [5, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1], \
                                     ["Str", "Int", "Wis", "Dex", "Con", "Cha", "Com"]
        for i, width in enumerate(method_colform):    # generates columns from widths listed in methodi_columnform
            self.attributes_frame.grid_columnconfigure(i, weight=width, uniform=1)
        for j in range(3):                              # generates rows
            self.attributes_frame.grid_rowconfigure(j, weight=1, uniform=1)
        for k in range(7):                              # generates attribute labels (Str, Int, Wis, etc)
            self.method_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="left", anchor='s')
            self.method_label.grid(row=0, column=k+1, columnspan=1, sticky='nsew')
            self.method_label['text'] = attr_names[k]
        self.header_controls()                          # uses self.m_a_c(), which must first be updated by self.u_n_b()
        self.method_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=8, fg="#FFFFFF",
                                     bg='#000000', font=('Courier', 12), justify="left", anchor='center')
        self.method_label.grid(row=1, column=7, columnspan=1, sticky='nsew')
        self.method_label['text'] = attribs[6]          # these final four lines generate the non-interactive COM column

    def methodi_header(self, attribs=None):
        if attribs is None:
            attribs = attributes.methodi()
        self.update_newchar_button(self.methodi_header)
        self.headerdefaults(attribs)
        for v in range(6):                          # generates attribute buttons (for swapping attributes)
            self.method_label = tk.Button(master=self.attributes_frame, relief=tk.RIDGE, borderwidth=8, fg="#FFFFFF",
                                          bg='#000000', font=('Courier', 12), justify="left", anchor='center',
                                          command=lambda v=v: self.methodi_suspension(attribs, v))
            self.method_label.grid(row=1, column=v+1, columnspan=1, sticky='nsew')
            self.method_label['text'] = attribs[v]
        self.selectionframe_open(attribs)

    def methodi_suspension(self, attribs, selected_attribute):
        self.attributes_frame.destroy()
        self.headerdefaults(attribs)
        for v in range(6):                      # generates attribute buttons (for swapping attributes)
            if v == selected_attribute:         # we still send the un-do command to att_swap ("swap pos1 for pos1")
                self.method_label = tk.Button(master=self.attributes_frame, relief=tk.RIDGE, borderwidth=8,
                                              fg="#000000", bg='#FFFFFF', font=('Courier', 12), justify="left",
                                              anchor='center', command=lambda v=v: self.att_swap(attribs, v, v))
            else:
                self.method_label = tk.Button(master=self.attributes_frame, relief=tk.RIDGE, bg='#000000', fg="#FFFFFF",
                                              font=('Courier', 12), justify="left", borderwidth=8, anchor='center',
                                              command=lambda v=v: self.att_swap(attribs, selected_attribute, v))
            self.method_label.grid(row=1, column=v+1, columnspan=1, sticky='nsew')
            self.method_label['text'] = attribs[v]

    def methodii_header(self, attribs=None):
        if attribs is None:
            attribs = attributes.methodii()
        self.attributes_frame.destroy()
        self.update_newchar_button(self.methodii_header)
        self.headerdefaults(attribs)
        for v in range(6):                          # generates attribute buttons (for swapping attributes)
            self.method_label = tk.Button(master=self.attributes_frame, relief=tk.RIDGE, borderwidth=8, fg="#FFFFFF",
                                          bg='#000000', font=('Courier', 12), justify="left", anchor='center',
                                          command=lambda v=v: self.methodii_suspension(attribs, v))
            self.method_label.grid(row=1, column=v+1, columnspan=1, sticky='nsew')
            self.method_label['text'] = attribs[v]
        self.selectionframe_open(attribs)

    def methodii_suspension(self, attribs, selected_attribute):
        self.attributes_frame.destroy()
        self.headerdefaults(attribs)
        for v in range(6):                      # generates attribute buttons (for swapping attributes)
            if v == selected_attribute:         # we still send the un-do command to att_swap ("swap pos1 for pos1")
                self.method_label = tk.Button(master=self.attributes_frame, relief=tk.RIDGE, borderwidth=8,
                                              fg="#000000", bg='#FFFFFF', font=('Courier', 12), justify="left",
                                              anchor='center', command=lambda v=v: self.att_swap(attribs, v, v))
            else:
                self.method_label = tk.Button(master=self.attributes_frame, fg="#FFFFFF", bg='#000000', relief=tk.RIDGE,
                                              borderwidth=8, font=('Courier', 12), justify="left", anchor='center',
                                              command=lambda v=v: self.att_swap(attribs, selected_attribute, v))
            self.method_label.grid(row=1, column=v+1, columnspan=1, sticky='nsew')
            self.method_label['text'] = attribs[v]

    def att_swap(self, attribs, pos1, pos2):
        attribs[pos1], attribs[pos2] = attribs[pos2], attribs[pos1]
        self.make_another_character(attribs)

    def methodiii_header(self, attribs=None):
        if attribs is None:
            attribs = attributes.methodiii()
        self.update_newchar_button(self.methodiii_header)
        self.attributes_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.attributes_frame.grid(row=0, column=0, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        methodiii_colform, attr_names = [5, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1], \
                                        ["Str", "Int", "Wis", "Dex", "Con", "Cha", "Com"]
        for i, width in enumerate(methodiii_colform):  # generates columns from widths listed in methodiii_columnform
            self.attributes_frame.grid_columnconfigure(i, weight=width, uniform=1)
        for j in range(3):                              # generates rows
            self.attributes_frame.grid_rowconfigure(j, weight=1, uniform=1)
        for k in range(7):                              # generates attribute labels (Str, Int, Wis, etc)
            self.method_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="left", anchor='s')
            self.method_label.grid(row=0, column=k+1, columnspan=1, sticky='nsew')
            self.method_label['text'] = attr_names[k]
            self.method_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=8, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="left", anchor='center')
            self.method_label.grid(row=1, column=k+1, columnspan=1, sticky='nsew')
            self.method_label['text'] = attribs[k]
        self.header_controls()                        # uses self.m_a_c(), which must first be updated by self.u_n_b()
        self.selectionframe_open(attribs)

    def methodiv_header(self, attribs=None, selection=13):
        if attribs is None:
            attribs = attributes.methodiv()
        self.update_newchar_button(self.methodiv_header)
        self.attributes_frame.destroy()
        self.attributes_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.attributes_frame.grid(row=0, column=0, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        methodiv_colform, attr_names = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1], \
                                       [["Str:", "Int:", "Wis:", "Dex:", "Con:", "Cha:", "Com:"]]
        attribs.append([3, 3, 3, 3, 3, 3, 3])               # blanks out the selection frame
        attribs = attr_names + attribs                      # concatenates attribute names with attribute lists
        for i, width in enumerate(methodiv_colform):        # generates columns via widths listed in methodiv_columnform
            self.attributes_frame.grid_columnconfigure(i, weight=width, uniform=1)
        self.attributes_frame.grid_rowconfigure(0, weight=1, uniform=1)
        for k in range(13):                                 # generates attribute sets
            if k == 0:                                      # sets the attributes labels to Label
                self.methodiv_button = tk.Label(master=self.attributes_frame, relief=tk.FLAT, anchor='s', bg='#000000',
                                                fg="#FFFFFF", borderwidth=4, font=('Courier', 12), justify="center")
            elif k == selection:                            # sets lambda to de-highlight and de-select
                self.methodiv_button = tk.Button(master=self.attributes_frame, relief=tk.FLAT, anchor='s', bg='#FFFFFF',
                                                 fg="#000000", borderwidth=4, font=('Courier', 12), justify="center",
                                                 command=lambda k=k: self.methodiv_header(attribs[1:14], 13))
            else:                                           # sets lambda to highlight and populate the selectionframe
                self.methodiv_button = tk.Button(master=self.attributes_frame, relief=tk.FLAT, anchor='s', bg='#000000',
                                                 fg="#FFFFFF", borderwidth=4, font=('Courier', 12), justify="center",
                                                 command=lambda k=k: self.methodiv_header(attribs[1:14], k))
            self.methodiv_button.grid(row=0, column=k+1, columnspan=1, sticky='nsew')
            self.methodiv_button['text'] = '{}\n{}\n{}\n{}\n{}\n{}\n{}'.\
                format(attribs[k][0], attribs[k][1], attribs[k][2], attribs[k][3], attribs[k][4], attribs[k][5],
                       attribs[k][6])
        self.header_controls()                              # uses self.m_a_c(), which is updated by self.u_n_b()
        self.selectionframe_open(attribs[selection])

    def methodv_header(self, charclass=None, attribs=(18, 18, 18, 18, 18, 18, 18)):
        self.update_newchar_button(self.methodv_header)
        self.attributes_frame.destroy()
        self.attributes_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.attributes_frame.grid(row=0, column=0, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        methodv_colform, attr_names = [5, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1], \
                                      ["Str", "Int", "Wis", "Dex", "Con", "Cha", "Com"]
        for i, width in enumerate(methodv_colform):         # generates column widths from values in methodv_columnform
            self.attributes_frame.grid_columnconfigure(i, weight=width, uniform=1)
        for j in range(3):                                  # generates rows
            self.attributes_frame.grid_rowconfigure(j, weight=1, uniform=1)
        if charclass is None:
            self.method_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="left", anchor='s')
            self.method_label.grid(row=1, column=1, columnspan=7, sticky='nsew')
            self.method_label['text'] = "Select a class"
        else:
            self.method_label.destroy()
            for k in range(7):                              # generates attribute labels (Str, Int, Wis, etc)
                self.method_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                             bg='#000000', font=('Courier', 12), justify="left", anchor='s')
                self.method_label.grid(row=0, column=k + 1, columnspan=1, sticky='nsew')
                self.method_label['text'] = attr_names[k]
                self.method_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=8, fg="#FFFFFF",
                                             bg='#000000', font=('Courier', 12), justify="left", anchor='center')
                self.method_label.grid(row=1, column=k + 1, columnspan=1, sticky='nsew')
                self.method_label['text'] = attribs[k]
        self.selectionframe_methodv(charclass, attribs)

    def selectionframe_open(self, attribs):                 # attribs is an ordered list of the SIX primary attributes
        self.racial_modifiers('blank')                      # blanks out the racial modifier field
        eligibility_object = selectclass.IsEligible()       # creates an IsEligible object using attribs
        eligibility_object.eligible(attribs)
        eligible_races = eligibility_object.eligible_races
        eligible_classes = eligibility_object.eligible_classes
        self.selection_frame.destroy()                      # destroys and re-creates its own label
        self.selection_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.selection_frame.grid(row=1, column=0, rowspan=3, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        for y, race in enumerate(eligible_races):          # generates race buttons from IsEligible object
            self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#000000', fg="#FFFFFF",
                                     font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                     command=lambda race=race: self.selectionframe_suspension(attribs,
                                                                                              eligibility_object,
                                                                                              eligible_races,
                                                                                              eligible_classes,
                                                                                              1, race))
            self.rc_opts.place(height=20, width=254, x=10 + 254 * int(y / 23), y=10 + 20 * (y % 23))
        for z, ch_cl in enumerate(eligible_classes):              # generates class buttons from IsEligible object
            self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#000000', fg="#FFFFFF",
                                     font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                     command=lambda ch_cl=ch_cl: self.selectionframe_suspension(attribs,
                                                                                                eligibility_object,
                                                                                                eligible_races,
                                                                                                eligible_classes,
                                                                                                0, ch_cl))
            self.rc_opts.place(height=20, width=254, x=640 + 254 * int((z / 23)), y=10 + 20 * (z % 23))
        self.close_selection_frame = tk.Button(self.selection_frame, text="return to main menu", bg='#000000',
                                               fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                               command=lambda: self.clbutt())
        self.close_selection_frame.pack(side='bottom')      # places the return to main menu button

    def selectionframe_suspension(self, attribs, elig_object, all_races, all_classes, is_race_selected, selection):
        self.racial_modifiers(selection)
        elig_object.filtered_eligibility(attribs, selection)
        remaining_races = elig_object.eligible_races
        remaining_classes = elig_object.eligible_classes
        self.selection_frame.destroy()
        self.selection_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.selection_frame.grid(row=1, column=0, rowspan=3, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        if is_race_selected:
            for y, race in enumerate(all_races):
                if race in remaining_races:
                    self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#FFFFFF', fg="#000000",
                                             font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda race=race: self.selectionframe_open(attribs))
                    self.rc_opts.place(height=20, width=254, x=10 + 254 * int(y / 23), y=10 + 20 * (y % 23))
                else:
                    self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#000000', fg="#666666",
                                             font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda race=race: self.selectionframe_suspension(attribs,
                                                                                                      elig_object,
                                                                                                      all_races,
                                                                                                      all_classes,
                                                                                                      is_race_selected,
                                                                                                      race))
                    self.rc_opts.place(height=20, width=254, x=10 + 254 * int(y / 23), y=10 + 20 * (y % 23))
            for z, ch_cl in enumerate(all_classes):
                if ch_cl in remaining_classes:
                    self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#000000',
                                             fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda ch_cl=ch_cl: self.charsheet_transition(selection, ch_cl,
                                                                                                   attribs))
                    self.rc_opts.place(height=20, width=254, x=640 + 254 * int((z / 23)), y=10 + 20 * (z % 23))
                else:
                    self.rc_opts = tk.Label(self.selection_frame, text=ch_cl, bg='#000000', fg="#666666",
                                            font=('Courier', 12), relief=tk.FLAT, anchor='w')
                    self.rc_opts.place(height=20, width=254, x=642 + 254 * int((z / 23)), y=10 + 20 * (z % 23))
        else:
            for y, race in enumerate(all_races):
                if race in remaining_races:
                    self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#000000', fg="#FFFFFF",
                                             font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda race=race: self.charsheet_transition(race, selection,
                                                                                                 attribs))
                    self.rc_opts.place(height=20, width=254, x=10 + 254 * int(y / 23), y=10 + 20 * (y % 23))
                else:
                    self.rc_opts = tk.Label(self.selection_frame, text=race, bg='#000000', fg="#666666",
                                            font=('Courier', 12), relief=tk.FLAT, anchor='w')
                    self.rc_opts.place(height=20, width=254, x=12 + 254 * int(y / 23), y=10 + 20 * (y % 23))
                    # in case you ever get around to iterating this properly, the two labels need their x-axis location
                    # adjusted by +2 for the text to line up
            for z, ch_cl in enumerate(all_classes):
                if ch_cl in remaining_classes:
                    self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#FFFFFF', fg="#000000",
                                             font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda ch_cl=ch_cl: self.selectionframe_open(attribs))
                    self.rc_opts.place(height=20, width=254, x=640 + 254 * int((z / 23)), y=10 + 20 * (z % 23))
                else:
                    self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#000000',
                                             fg="#666666", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda ch_cl=ch_cl: self.selectionframe_suspension(attribs,
                                                                                                        elig_object,
                                                                                                        all_races,
                                                                                                        all_classes,
                                                                                                        is_race_selected,
                                                                                                        ch_cl))
                    self.rc_opts.place(height=20, width=254, x=640 + 254 * int((z / 23)), y=10 + 20 * (z % 23))
        self.close_selection_frame = tk.Button(self.selection_frame, text="return to main menu", bg='#000000',
                                               fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                               command=lambda: self.clbutt())
        self.close_selection_frame.pack(side='bottom')

    def selectionframe_methodv(self, charclass, attribs):      # charclass initially "none"
        eligibility_object = selectclass.IsEligible()
        eligibility_object.eligible(attribs)
        self.selection_frame.destroy()
        self.selection_frame = tk.Label(master=self.master, relief=tk.RIDGE, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                        font=('Courier', 12), justify="center")
        self.selection_frame.grid(row=1, column=0, rowspan=3, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        self.close_selection_frame = tk.Button(self.selection_frame, text="return to main menu", bg='#000000',
                                               fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                               command=lambda: self.clbutt())
        if charclass is None:
            eligible_classes = eligibility_object.eligible_classes
            for z, ch_cl in enumerate(eligible_classes):
                self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#000000', anchor='w',
                                         fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                         command=lambda ch_cl=ch_cl: self.methodv_header(charclass=ch_cl,
                                                                                         attribs=attributes.methodv
                                                                                         (ch_cl)))
                self.rc_opts.place(height=20, width=274, x=320 + 404 * int((z / 23)), y=10 + 20 * (z % 23))
        else:
            eligibility_object.filtered_eligibility(attribs, charclass)
            charraces = eligibility_object.eligible_races
            self.header_controls()            # creates reroll button, then immediately re-defines the lambda
            self.reroll_header.config(command=lambda: self.methodv_header(charclass=charclass,
                                                                          attribs=attributes.methodv(charclass)))
            if len(charraces) == 0:         # if there are no eligible races...
                self.selection_frame['text'] = "Attributes do not meet class minimum"
            else:
                for z, race in enumerate(charraces):
                    self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#000000', anchor='w',
                                             fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                             command=lambda race=race: self.charsheet_transition(race, charclass,
                                                                                                 attribs))
                    self.rc_opts.place(height=20, width=274, x=320 + 404 * int((z / 23)), y=10 + 20 * (z % 23))
        self.close_selection_frame.pack(side='bottom')

    def racial_modifiers(self, chcl_selection):                     # previews racial bonuses/penalties in the header
        racial_bons = attributes.display_racial_bonuses_i(chcl_selection)
        if self.make_another_character == self.methodiv_header:     # bonuses displayed vertically for method iv...
            self.methodiv_label.destroy()
            temp = ''
            for u, bonus in enumerate(racial_bons):
                temp += '\n{}'.format(bonus)
            self.methodiv_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=4, fg="#00FFFF",
                                           bg='#000000', font=('Courier', 12), justify="left", anchor='n')
            self.methodiv_label.grid(row=0, column=0, columnspan=1, sticky='se')
            self.methodiv_label['text'] = temp
        else:                                                       # ...otherwise they go under the respective attr
            for w in range(7):
                self.method_label = tk.Label(master=self.attributes_frame, relief=tk.FLAT, borderwidth=4, fg="#00FFFF",
                                             bg='#000000', font=('Courier', 12), justify="left", anchor='n')
                self.method_label.grid(row=2, column=w + 1, columnspan=1, sticky='nsew')
                self.method_label['text'] = racial_bons[w]

    def charsheet_transition(self, charrace, charclass, attribs):
        formatted_atts = attributes.apply_race_modifiers(charrace, attribs)     # applies racial modifier and formats
        class_list = selectclass.string_to_list(charclass, '/')
        self.selected_character = character.Character(level=self.level, race=charrace, classes=class_list,
                                                      attrib_list=formatted_atts, gender=self.gender)
        self.selection_frame.destroy()
        self.attributes_frame.destroy()
        self.update_charsheet()
        self.char_frame.lift()
        self.member_frame.lift()
        self.contdisp_frame.lift()

    def header_controls(self):  # don't understand gender_select grid placement OR how level_dropdown passes its result
        self.header_control_frame = tk.Frame(master=self.attributes_frame, bg='#000000', borderwidth=0)
        self.header_control_frame.grid(row=0, column=(self.attributes_frame.grid_size()[0] - 2), sticky='nsw',
                                       rowspan=3, columnspan=5)
        for k in range(5):
            self.header_control_frame.grid_rowconfigure(k, weight=1, uniform=1)
        for l in range(2):
            self.header_control_frame.grid_columnconfigure(l, weight=1, uniform=1)
        self.reroll_header = tk.Button(master=self.header_control_frame, relief=tk.RIDGE, fg="#FFFFFF",
                                       bg='#000000', font=('Courier', 12), justify="left", anchor='center',
                                       text='Reroll', command=lambda: self.make_another_character(), borderwidth=4)
        self.reroll_header.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.newlabel = tk.Label(master=self.header_control_frame, relief=tk.FLAT, fg="#FFFFFF",
                                 bg='#000000', font=('Courier', 12), justify="left", anchor='center',
                                 text='Gender:')
        self.gender_select = tk.Button(master=self.header_control_frame, relief=tk.RIDGE, fg="#FFFFFF",
                                       bg='#000000', font=('Courier', 12), justify="left", anchor='center', width=7,
                                       text=str(self.gender), command=lambda: self.select_gender(), borderwidth=4)
        self.newlabel.grid(row=1, column=0, sticky='nsew')
        self.gender_select.grid(row=1, column=1, sticky='nsew')
        self.newlabel = tk.Label(master=self.header_control_frame, relief=tk.FLAT, fg="#FFFFFF",
                                 bg='#000000', font=('Courier', 12), justify="left", anchor='center',
                                 text=' Level:')
        self.newlabel.grid(row=2, column=0, sticky='nsew')
        options = list(range(1, 17))
        self.tk_variable = tk.IntVar(self.header_control_frame, self.level)
        level_dropdown = tk.OptionMenu(self.header_control_frame, self.tk_variable, *options, command=self.levelset)
        level_dropdown.config(bg='#000000', fg='#FFFFFF', font=('Courier', 12), activebackground='#000000',
                              activeforeground='#FFFFFF')
        level_dropdown["menu"].config(bg='#000000', fg='#FFFFFF', font=('Courier', 12))
        level_dropdown.grid(row=2, column=1, sticky='nsew')

    def select_gender(self):
        self.header_control_frame.destroy()
        self.swap_frame = tk.Frame(master=self.attributes_frame, bg='#000000', borderwidth=0)
        self.swap_frame.grid(row=0, column=(self.attributes_frame.grid_size()[0] - 2), sticky='nsw', rowspan=3,
                             columnspan=5)
        for k in range(5):
            self.swap_frame.grid_rowconfigure(k, weight=1, uniform=1)
        for l in range(2):
            self.swap_frame.grid_columnconfigure(l, weight=1, uniform=1)
        gender_options = ["random", "male", "female"]
        for x, gender in enumerate(gender_options):
            self.choice_button = tk.Button(master=self.swap_frame, relief=tk.RIDGE, fg="#FFFFFF", anchor='center',
                                           bg='#222222', font=('Courier', 12), justify="left", text=gender, width=7,
                                           borderwidth=4, command=lambda gender=gender: self.genderset(gender))
            self.choice_button.grid(row=x+1, column=1, sticky='nsew')
        return

    def genderset(self, selection):
        self.gender = selection          # self.gender_select.config(text=self.gender)
        self.swap_frame.destroy()
        self.header_controls()           # not using the config since we're re-building header_controls() instead

    def select_level(self):
        self.header_control_frame.destroy()
        self.swap_frame = tk.Frame(master=self.attributes_frame, bg='#000000', borderwidth=0)
        self.swap_frame.grid(row=0, column=(self.attributes_frame.grid_size()[0] - 2), sticky='nsw', rowspan=3,
                             columnspan=5)
        for row in range(5):
            self.swap_frame.grid_rowconfigure(row, weight=1, uniform=1)
        for column in range(2):
            self.swap_frame.grid_columnconfigure(column, weight=1, uniform=1)
        for lvl in range(15):
            self.choice_button = tk.Button(master=self.swap_frame, relief=tk.RIDGE, fg="#FFFFFF", anchor='center',
                                           bg='#222222', font=('Courier', 12), justify="left", text=lvl+1, width=7,
                                           borderwidth=4, command=lambda lvl=lvl: self.levelset(lvl+1))
            self.choice_button.grid(row=lvl+2, column=1, sticky='nsew')
        return

    def levelset(self, level):
        self.level = level


# character.Character(level=5, race="Halfling", classes=['Fighter', 'Thief'],
#                     attrib_list=[{'Str': 14, 'Int': 13, 'Wis': 9, 'Dex': 15, 'Con': 18, 'Cha': 11, 'Com': 4},
#                                  {'Str': 0, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 0, 'Cha': 0, 'Com': 0}])


root = tk.Tk()
my_gui = CharacterInterface(root)
# screen_width = root.winfo_screenwidth()
# print("screen width", screen_width)
root.mainloop()
