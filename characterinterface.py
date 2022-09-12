import tkinter as tk
import random           # only in make_party()
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import character
import datalocus
import selectclass
import attributes


class CharacterInterface:
    def __init__(self, master, level=1):
        self.party_list = []
        self.display_text = ['']
        self.level = level
        self.minmaxlevel = {"min": level, "max": level}       # only used during bulk party gen
        self.master = master
        self.selected_character = character.Character(self.level)
        self.master.attributes('-fullscreen', True)
        self.master.title("Interface Template")
        self.master.configure(bg='#000000', relief=tk.RIDGE, borderwidth=16)

        self.gender = "random"                  # accepts "random", "male" or "female"
        self.tk_variable = tk.IntVar()          # this is establishing type=Int for the dropdown menu in head_controls

        self.master.grid_propagate(False)       # locks the internal configuration of self.master's grid
        for k in range(4):                      # generates the 6x4 grid
            self.master.grid_rowconfigure(k, weight=1, uniform=1)
        for i in range(6):
            self.master.grid_columnconfigure(i, weight=1, uniform=1)
            for j in range(4):
                self.dummy_frame = tk.Frame(self.master, relief=tk.RIDGE, borderwidth=4,
                                            bg='#'+str(2*j)+str(2*j)+str(2*j)+str(i)+str(i)+str(i))
                self.dummy_frame.grid(row=j, column=i, sticky='nsew')

        self.start_frame = tk.Frame(self.master, bg='#000000', relief=tk.RIDGE, borderwidth=4)  # generates start screen
        self.start_frame.grid(row=0, column=0, rowspan=4, columnspan=6, sticky="nsew")
        self.start_frame.grid_columnconfigure(0, weight=1, uniform=1)
        self.start_frame.grid_rowconfigure(0, weight=2, uniform=1)
        for i in range(1, 7):
            self.start_frame.grid_rowconfigure(i, weight=1, uniform=1)
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
        self.methodvi_button = tk.Button(self.start_frame, command=lambda: self.methodvi_header(), bg='#000000',
                                         fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                         text="METHOD VI\nhybrid of Methods I & V, order is locked")
        self.methodvi_button.grid(row=6, column=0, sticky='nsew')

        self.char_frame = tk.Frame(self.master, bg='#000077')   # generates character sheet frame
        self.char_frame.grid(row=0, column=0, rowspan=2, columnspan=3, sticky="nsew")
        self.char_frame.grid_propagate(False)                   # locks char_frame's right border
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

        self.contdisp_frame = tk.Frame(self.master, bg='#000077')    # generates control/display frame
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
                                      font=('Courier', 12), text=self.display_label_text, anchor='w', padx=60)
        self.return_label = tk.Label(master=self.contdisp_frame, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                     font=('Courier', 12), justify="left", anchor='w')
        self.control_label.grid(row=1, column=0, sticky='nsew')
        self.display_label.grid(row=0, column=0, sticky='nsew')
        self.return_label.grid(row=2, column=0, sticky='nsew')        # AND NOW THE CONTROL PANEL BUTTONS:
        self.new_button = tk.Button(self.control_label, text="New Character", command=self.reroll, width=16,
                                    bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=4, relief=tk.FLAT)
        self.drain_button = tk.Button(self.control_label, command=lambda: self.drain(), text="Drain Level", width=16,
                                      bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT)
        self.add_button = tk.Button(self.control_label, command=lambda: self.add_party_member(), width=16,
                                    text="Add Member", bg='#000000', fg="#FFFFFF", font=('Courier', 12), underline=0,
                                    relief=tk.FLAT)
        self.re_name = tk.Button(self.control_label, command=lambda: self.select_name(), text="Name", bg='#000000',
                                 fg="#FFFFFF", font=('Courier', 12), underline=0, relief=tk.FLAT, width=16)
        self.remove_button = tk.Button(self.control_label, text="Remove", bg='#000000', fg="#FFFFFF", underline=0,
                                       command=lambda: self.remove_party_member(), font=('Courier', 12), relief=tk.FLAT,
                                       width=16)
        self.xp_button = tk.Button(self.control_label, text="Award 1000xp", command=lambda: self.boost(), bg='#000000',
                                   fg="#FFFFFF", font=('Courier', 12), underline=10, relief=tk.FLAT, width=16)
        self.set_name = tk.Button(self.control_label, command=lambda: self.name_character(), width=16,
                                  text="Accept", bg='#000000', fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT)
        self.marching_order = tk.Button(self.control_label, command=lambda: self.arrange_party(self.selected_character),
                                        text="Marching Order", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                        relief=tk.FLAT, underline=9, width=16)
        self.name_slot = tk.Entry(self.control_label, bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                  insertbackground="#FFFFFF")
        self.main_menu_bn = tk.Button(self.return_label, text="return to main menu", bg='#000000', font=('Courier', 12),
                                      fg="#FFFFFF", relief=tk.FLAT, anchor='w',  command=lambda: self.startlift())

        self.start_label = ''    # establishes all label_text values as strings

        self.new_button.pack(side='left')
        self.add_button.pack(side='left')
        self.re_name.pack(side='left')
        self.drain_button.pack(side='left')
        self.remove_button.pack(side='left')
        self.xp_button.pack(side='left')
        self.set_name.pack(side='left')
        self.marching_order.pack(side='left')
        self.name_slot.pack(side='left')                            # this one is actually a text input field
        self.main_menu_bn.pack(side='bottom')
        self.remove_button.pack_forget()
        self.set_name.pack_forget()
        self.marching_order.pack_forget()
        self.name_slot.pack_forget()

        self.master.bind('<Escape>', lambda event: self.escape_function())

        self.member_frame = tk.Frame()              # generate_party_frame() PARTY DISPLAY parent
        self.party_frame = tk.Frame()               # generate_party_frame() PARTY DISPLAY child
        self.acs_label = tk.Label()                 # generate_party_frame() PARTY DISPLAY child
        self.hps_label = tk.Label()                 # generate_party_frame() PARTY DISPLAY child
        self.th_label = tk.Label()                  # generate_party_frame() PARTY DISPLAY child
        self.attributes_frame = tk.Frame()          # header_defaults() ATTRIBUTES parent
        self.attribs_fr = tk.Frame()                # header_defaults() ATTRIBUTES child
        self.hcontrol_fr = tk.Frame()               # header_defaults() ATTRIBUTES child
        self.header_control_frame = tk.Frame()      # header_controls() ATTRIBUTES sub-child
        self.selection_frame = tk.Frame()           # selection_frame_open() RACE/CLASS OPTIONS parent
        self.selection_body = tk.Frame()            # selection_frame() child: methodvi -> full party POPUP
        self.temp_frame = tk.Frame()                # party_frame_popup() POPUP parent
        self.close_popup_frame = tk.Frame()         # party_frame_popup() POPUP child
        self.temp_control_frame = tk.Frame()        # party_frame_popup() POPUP sub-child
        self.expanded_party_label = tk.Label()      # party_frame_popup() DISPLAY child
        self.inner_frame = tk.Frame()               # party_frame_popup() POPUP sub-child
        self.frame = tk.Frame()                     # all-purpose temp frame
        self.method_frame = tk.Frame()              # all-purpose temp frame
        self.method_label = tk.Label()              # all-purpose temp label
        self.methodiv_label = tk.Label()            # needed in order to reset the header when race is set to "human"

        self.button = tk.Button()
        self.rc_opts = tk.Button()
        self.close_selection_frame = tk.Button()
        self.reroll_header = tk.Button()
        self.gender_select = tk.Button()

        self.generate_party_frame()                 # this is the _init_ method for member_frame
        self.start_frame.lift()                     # raises the start frame
        self.make_another_character = self.reroll   # self.m_a_c()
        return

    def update_charsheet(self):
        self.update_character_frame()
        self.update_party_frame()
        self.display_label['text'] = self.display_text[0]

    def generate_party_frame(self):
        self.member_frame = tk.Frame(self.master, bg='#000077')
        self.member_frame.grid(row=0, column=3, rowspan=2, columnspan=3, sticky="nsew")
        self.member_frame.grid_propagate(False)
        for a, value in enumerate([5, 1, 1, 1]):
            self.member_frame.grid_columnconfigure(a, weight=value, uniform=1)
        self.member_frame.grid_rowconfigure(0, weight=1, uniform=1)
        self.party_frame = tk.Frame(master=self.member_frame, relief=tk.FLAT, borderwidth=4, bg='#000077')
        self.acs_label = tk.Label(master=self.member_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                  font=('Courier', 12), justify="left", anchor='nw')
        self.hps_label = tk.Label(master=self.member_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                  font=('Courier', 12), justify="left", anchor='nw')
        self.th_label = tk.Label(master=self.member_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                 font=('Courier', 12), justify="left", anchor='nw')
        self.party_frame.grid(row=0, column=0, rowspan=2, sticky='nsew')
        self.hps_label.grid(row=0, column=1, rowspan=2, sticky='nsew')
        self.acs_label.grid(row=0, column=2, rowspan=2, sticky='nsew')
        self.th_label.grid(row=0, column=3, rowspan=2, sticky='nsew')

    def update_party_frame(self, buttons=True):                     # updates the party frame
        self.member_frame.lift()                                    # undoes the lower() from clear_party_popup()
        self.party_frame.destroy()                                  # resets party label frame
        self.party_frame = tk.Frame(master=self.member_frame, relief=tk.FLAT, bg='#000000')
        self.party_frame.grid(row=0, column=0, rowspan=2, sticky='nsew')
        display_acs, display_hps, display_th = 'AC', 'HP', 'TH'
        display_names = tk.Label(master=self.party_frame, fg="#FFFFFF", bg='#000000', font=('Courier', 12), anchor='w',
                                 relief=tk.FLAT, justify="left", text='   Members')
        display_names.place(x=5, y=4, height=20, relwidth=1.0)
        for a, member in enumerate(self.party_list, 1):             # constructs member buttons
            display_names = tk.Button(self.party_frame, text='\u0332{}  {}'.format(str(a), member.character_name),
                                      bg='#000000', fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, justify="left",
                                      command=lambda pos=a: self.refresh(self.party_list[pos - 1]), anchor='w')
            display_names.place(x=3, y=5 + 18 * a, height=18, relwidth=1.0)
            display_hps += '\n{}'.format(member.hp)                 # constructs attribute column text
            display_acs += '\n{}'.format(10 + member.calculate_ac())
            display_th += '\n{}'.format(20 + member.calculate_thaco())
        for b in range(len(self.party_list) + 1, 9):                # constructs placeholders for empty member slots
            display_names = tk.Label(self.party_frame, text=str(b), bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                     relief=tk.FLAT, justify="left", anchor='w')
            display_names.place(x=5, y=5 + 18 * b, height=18, relwidth=1)
        if not buttons:                                             # temporarily overwrites self.party_frame
            self.method_label = tk.Label(master=self.party_frame, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="left", anchor='nw', padx=4)
            nonbutton_names = '   Members'
            for a, member in enumerate(self.party_list, 1):
                nonbutton_names += '\n\u0332{}  {}'.format(str(a), member.character_name)
            for b in range(len(self.party_list) + 1, 9):
                nonbutton_names += '\n{}'.format(str(b))
            self.method_label.configure(text=nonbutton_names)
            self.method_label.pack(fill="both")                     # THIS LABEL MUST LATER BE MANUALLY DESTROYED
        self.acs_label['text'] = display_acs                        # x (above) displaced by 1 vs button margin
        self.hps_label['text'] = display_hps                        # assigns attribute column text
        self.th_label['text'] = display_th

    def update_character_frame(self):
        self.chtop_label['text'] = "{}\n{} {} {}"\
            .format(self.selected_character.character_name, self.selected_character.display_level,
                    self.selected_character.race, self.selected_character.display_class)
        chleft_label_widgets = self.chleft_label.place_slaves()     # we need to completely clear chleft_label...
        for y in chleft_label_widgets:
            y.destroy()                                             # ...in order to PLACE fresh attribute buttons
        self.chleft_label['text'] = "HP: {}\nAC: {}\nTH: {}\n\n{}"\
            .format(self.selected_character.hp, 10 + self.selected_character.calculate_ac(),
                    20 + self.selected_character.calculate_thaco(), self.stacked_attrs()[0:-1])
        for x in range(7):
            self.button = tk.Button(self.chleft_label, text="<", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                    command=lambda decrease=x: self.adjust_attribute(decrease, -1), relief=tk.FLAT)
            self.button.place(height=8, width=6, x=110, y=80 + 18 * x)
            self.button = tk.Button(self.chleft_label, text=">", bg='#000000', fg="#FFFFFF", font=('Courier', 12),
                                    command=lambda increase=x: self.adjust_attribute(increase, 1), relief=tk.FLAT)
            self.button.place(height=8, width=6, x=120, y=80 + 18 * x)
        self.chright_label['text'] = "\n{}\n{} years old ({})\n\nXP: {:,}\n    {:,} xp to next level ({})\n\n{}' "\
                                     "{}   {} lbs\n\nMovement: {}\u0022\nAlignment: \nPsionics: "\
            .format(self.selected_character.gender, self.selected_character.age[0], self.selected_character.age[1],
                    self.selected_character.xp, int(self.selected_character.next_level[0]) - self.selected_character.xp,
                    self.selected_character.next_level[1], int(self.selected_character.size[0] / 12),
                    str(self.selected_character.size[0] % 12) + '"' if self.selected_character.size[0] % 12 > 0 else '',
                    str(self.selected_character.size[1]), self.selected_character.class_movement())

    def reroll(self, dummy_val=''):                 # generates a new character and refreshes label text
        self.display_text[0] = dummy_val            # look, I'm just getting rid of that argument warning
        self.selected_character = character.Character(self.level)
        self.nonmember_buttons()
        self.update_charsheet()                     # this is the only char-gen method that doesn't unbind hotkeys

    def member_buttons(self):                       # updates control panel
        for key in self.master.bind():              # unbinds all hotkeys
            self.master.unbind(key)
        control_panel_buttons = self.control_label.pack_slaves()
        for y in control_panel_buttons:             # unbinds all buttons
            y.pack_forget()
        for i, member in enumerate(self.party_list, 1):
            self.bind_member(i)                     # re-binds party index positions
        self.new_button.pack(side='left')           # re-binds buttons
        self.re_name.pack(side='left')
        self.remove_button.pack(side='left')
        self.drain_button.pack(side='left')
        self.xp_button.pack(side='left')
        if len(self.party_list) > 1:                # re-binds hotkeys
            self.marching_order.pack(side='left')
            self.master.bind('o', lambda event: self.arrange_party(self.selected_character))
        self.master.bind('c', lambda event: self.make_another_character())
        self.master.bind('r', lambda event: self.remove_party_member())
        self.master.bind('d', lambda event: self.drain())
        self.master.bind('x', lambda event: self.boost())
        self.master.bind('n', lambda event: self.select_name())
        self.master.bind('<Escape>', lambda event: self.escape_function())

    def nonmember_buttons(self):                    # updates control panel
        for key in self.master.bind():              # unbinds all hotkeys
            self.master.unbind(key)
        control_panel_buttons = self.control_label.pack_slaves()
        for y in control_panel_buttons:
            y.pack_forget()
        for i, member in enumerate(self.party_list, 1):
            self.bind_member(i)                     # re-binds party index positions
        self.new_button.pack(side='left')
        self.re_name.pack(side='left')
        if len(self.party_list) < 8:
            self.add_button.pack(side='left')
        self.drain_button.pack(side='left')
        self.xp_button.pack(side='left')
        self.master.bind('c', lambda event: self.make_another_character())
        self.master.bind('a', lambda event: self.add_party_member())
        self.master.bind('d', lambda event: self.drain())
        self.master.bind('x', lambda event: self.boost())
        self.master.bind('n', lambda event: self.select_name())
        self.master.bind('<Escape>', lambda event: self.escape_function())

    def update_newchar_button(self, replacement_function):
        self.make_another_character = replacement_function  # switches NEW button from reroll to passed-argument method
        self.new_button.config(command=lambda: self.make_another_character())
        self.master.bind('n', lambda event: self.make_another_character())

    def refresh(self, current_char):                        # establishes new selected_character and refreshes the label
        self.selected_character = current_char
        self.display_text[0] = ''
        self.member_buttons()
        self.update_charsheet()

    def drain(self):                                        # drains one level from current character
        self.display_text[0] = str(self.selected_character.calculate_level(-1))
        self.update_charsheet()
        self.display_text[0] = ''

    def boost(self):                                        # awards 1,000 xp to current character
        self.selected_character.modify_xp(1000)
        self.display_text[0] = self.selected_character.calculate_level(0)
        self.update_charsheet()
        self.display_text[0] = ''

    def adjust_attribute(self, attr, adj):                  # modifies an attribute by the value of adj
        attr_list = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
        self.selected_character.modify_attribute(attr_list[attr], adj)
        self.update_charsheet()

    def stacked_attrs(self):                    # generates text for display_label
        temp, other_atts = "", ["Int", "Wis", "Dex", "Con", "Cha", "Com"]
        temp = "Str: {}\n".format(self.selected_character.display_strength())
        for a in other_atts:
            temp = temp + "{}: {}\n".format(a, self.selected_character.attributes[a])
        return temp

    def remove_party_member(self):              # removes current character from party
        if len(self.party_list) > 0 and self.selected_character in self.party_list:
            self.master.unbind(len(self.party_list))
            self.party_list.remove(self.selected_character)
            temp_name = self.selected_character.character_name
            self.make_another_character()
            self.display_text[0] = "{} has been removed from the party".format(temp_name)
            self.update_charsheet()

    def add_party_member(self):                 # adds current character to party
        if len(self.party_list) < 8 and self.selected_character not in self.party_list:
            self.party_list.append(self.selected_character)
            self.select_name(add_member=True)

    def bind_member(self, party_index):          # binds a number key to current character's
        self.master.bind(party_index, lambda event: self.refresh(self.party_list[party_index-1]))

    def select_name(self, add_member=False):                # CREATES FIELD FOR ASSIGNING CHARACTER NAME
        if add_member and len(self.selected_character.character_name) > 0:      # (1/4) named non-member (ADD=True)
            self.display_text[0] = "{} has been added to the party".format(self.selected_character.character_name)
            self.update_charsheet()
            self.member_buttons()
        else:
            self.update_party_frame(buttons=False)          # blanks out party buttons
            self.main_menu_bn.configure(state='disabled')   # blanks out return to main menu button
            self.name_slot.delete(0, 'end')                 # clears Entry field
            self.name_slot.insert(tk.END, self.selected_character.character_name)   # populates the Entry field
            for key in self.master.bind():
                self.master.unbind(key)                     # unbinds hotkeys
            for widget in self.control_label.winfo_children():
                widget.pack_forget()                        # forgets control panel widgets
            self.control_label['text'] = '   Enter character name:'
            self.name_slot.pack(side='left')                # packs input field
            self.set_name.pack(side='left')                 # packs 'Enter' button (<Return> key bound below)
            self.name_slot.focus_set()                      # places cursor in input field
            self.master.bind('<Return>', lambda event: self.name_character(add_member))

    def name_character(self, add_member=False):             # names character
        temp_n = self.name_slot.get()                       # captures name text...
        if add_member and len(self.selected_character.character_name) == 0:     # (2/4) unnamed non-member (ADD=True)
            self.display_text[0] = "{} has been added to the party".format(temp_n)
        elif len(self.selected_character.character_name) == 0:                  # (3/4) unnamed non-member (ADD=False)
            self.display_text[0] = "{}'s name has been assigned".format(temp_n)
        else:                                                                   # (4/4) update name (ADD=False)
            self.display_text[0] = "{} is now {}".format(self.selected_character.character_name, temp_n)
        self.selected_character.assign_name(temp_n)
        self.method_label.destroy()                     # manual rem. of temp label (update_party_frame(buttons=False))
        self.main_menu_bn.configure(state='normal')     # restoration of main menu button
        self.update_charsheet()                         # update_charsheet()
        self.member_buttons() if self.selected_character in self.party_list else self.nonmember_buttons()
        for i, member in enumerate(self.party_list, 1):
            self.bind_member(i)                         # re-binds party hotkeys
        self.master.unbind('<Return>')                  # releases <Return> key
        self.display_text[0] = ''
        self.control_label['text'] = ''

    def arrange_party(self, selected_character):
        self.display_text[0] = ''
        self.update_charsheet()
        self.update_party_frame(buttons=False)          # blanks out party buttons
        self.main_menu_bn.configure(state='disabled')   # blanks out return to main menu button
        for widget in self.control_label.winfo_children():
            widget.pack_forget()                        # forgets control panel widgets
        for key in self.master.bind():
            self.master.unbind(key)                     # unbinds hotkeys
        self.control_label['text'] = "  Assign {}'s new position with a NUMBER key (1 through {})"\
            .format(selected_character.character_name, len(self.party_list))
        for position, member in enumerate(self.party_list):
            self.intermediate_move(position)        # passes user to intermediate function to re-bind number keys

    def intermediate_move(self, position):          # binds number keys to helper function
        self.master.bind(position + 1, lambda event: self.move_member(position))

    def move_member(self, position):                # moves selected_character and removes control label text
        self.method_label.destroy()                 # manual rem. of temp label (update_party_frame(buttons=False))
        self.main_menu_bn.configure(state='normal')     # restoration of main menu button
        self.party_list.insert(position, self.party_list.pop(self.party_list.index(self.selected_character)))
        self.control_label['text'] = ''             # move_member() is a helper method to intermediate_move()
        self.member_buttons()                       # ...for preserving the assignments through the incrementer
        self.update_charsheet()

    def clbutt(self):
        self.attributes_frame.destroy()
        self.selection_frame.destroy()
        self.start_frame.lift()                     # startframe.lift needed in case charsheet has been lifted

    def startlift(self):                            # method required for "return to main menu" button lambda
        self.start_frame.lift()
        for key in self.master.bind():              # unbinds hotkeys
            self.master.unbind(key)
        self.master.bind('<Escape>', lambda event: self.escape_function())  # restores <escape> key

    def escape_function(self):
        self.master.destroy()

    def startframe_close(self):
        self.start_frame.lower()                    # formerly forget() but we don't want to de-grid this frame
        self.attributes_frame.destroy()
        self.selection_frame.destroy()
        self.update_newchar_button(self.reroll)     # sets make_another_character() to reroll()
        self.make_another_character()
        if len(self.party_list) == 8:                # these are for party_maker() so that if we have generated an...
            self.selected_character = self.party_list[0]
            self.update_character_frame()           # ...entire party we arrive at charsheet on character #1

    def common_header_elements(self):
        for key in self.master.bind():                  # unbinds hotkeys
            self.master.unbind(key)                     # ...but restores <escape> key
        self.master.bind('<Escape>', lambda event: self.escape_function())
        self.attributes_frame.destroy()
        self.attributes_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.attributes_frame.grid(row=0, column=0, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        for i, width in enumerate([3, 1]):
            self.attributes_frame.grid_columnconfigure(i, weight=width, uniform=1)
        self.attributes_frame.grid_rowconfigure(0, weight=1, uniform=1)
        self.attributes_frame.grid_propagate(False)
        self.attribs_fr = tk.Frame(master=self.attributes_frame, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.attribs_fr.grid(row=0, column=0, sticky="nsew")
        self.hcontrol_fr = tk.Frame(master=self.attributes_frame, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.hcontrol_fr.grid(row=0, column=1, sticky="nsew")
        for i, width in enumerate([1, 3, 1]):           # assigns column widths
            self.hcontrol_fr.grid_columnconfigure(i, weight=width, uniform=1)

    def headerdefaults(self, attribs):                  # generates common elements for methods I & II headers
        self.common_header_elements()
        for i, width in enumerate([5, 1, 1, 1, 1, 1, 1, 1, 1]):     # column widths
            self.attribs_fr.grid_columnconfigure(i, weight=width, uniform=1)
        for j in range(3):
            self.attribs_fr.grid_rowconfigure(j, weight=1, uniform=1)
        for k, value in enumerate(["Str", "Int", "Wis", "Dex", "Con", "Cha", "Com"], 1):
            self.method_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="left", anchor='s')
            self.method_label.grid(row=0, column=k, sticky='nsew')
            self.method_label['text'] = value
        for m, attribute in enumerate(attribs, 1):      # generates attribute buttons (for swapping attributes)
            self.method_label = tk.Button(master=self.attribs_fr, relief=tk.RIDGE, borderwidth=8, fg="#FFFFFF",
                                          bg='#000000', font=('Courier', 12), justify="left", anchor='center',
                                          command=lambda new_val=m-1: self.method_suspension(attribs, new_val))
            self.method_label.grid(row=1, column=m, columnspan=1, sticky='nsew')
            self.method_label['text'] = attribute
        self.method_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, borderwidth=8, fg="#FFFFFF",
                                     bg='#000000', font=('Courier', 12), justify="left", anchor='center')
        self.method_label.grid(row=1, column=7, sticky='nsew')
        self.method_label['text'] = attribs[6]          # generates the non-interactive COM column
        self.header_controls()                          # uses self.m_a_c(), which must first be updated by self.u_n_b()

    def methodi_header(self, attribs=None):
        if attribs is None:
            attribs = attributes.methodi()
        self.update_newchar_button(self.methodi_header)
        self.headerdefaults(attribs)
        self.selectionframe_open(attribs)

    def methodii_header(self, attribs=None):
        if attribs is None:
            attribs = attributes.methodii()
        self.update_newchar_button(self.methodii_header)
        self.headerdefaults(attribs)
        self.selectionframe_open(attribs)

    def method_suspension(self, attribs, selected_attribute):
        self.attributes_frame.destroy()
        self.headerdefaults(attribs)
        for v in range(6):                      # generates attribute buttons (for swapping attributes)
            if v == selected_attribute:         # we still send the un-do command to att_swap ("swap pos1 for pos1")
                self.method_label = tk.Button(master=self.attribs_fr, relief=tk.RIDGE, borderwidth=8,
                                              fg="#000000", bg='#FFFFFF', font=('Courier', 12), justify="left",
                                              anchor='center', command=lambda pos=v: self.att_swap(attribs, pos, pos))
            else:
                self.method_label = tk.Button(master=self.attribs_fr, relief=tk.RIDGE, bg='#000000', fg="#FFFFFF",
                                              font=('Courier', 12), justify="left", borderwidth=8, anchor='center',
                                              command=lambda pos=v: self.att_swap(attribs, selected_attribute, pos))
            self.method_label.grid(row=1, column=v+1, columnspan=1, sticky='nsew')
            self.method_label['text'] = attribs[v]

    def att_swap(self, attribs, pos1, pos2):
        attribs[pos1], attribs[pos2] = attribs[pos2], attribs[pos1]
        self.make_another_character(attribs)

    def methodiii_header(self, attribs=None):
        if attribs is None:
            attribs = attributes.methodiii()
        self.update_newchar_button(self.methodiii_header)
        self.common_header_elements()
        for i, width in enumerate([5, 1, 1, 1, 1, 1, 1, 1, 1]):  # column widths
            self.attribs_fr.grid_columnconfigure(i, weight=width, uniform=1)
        for j in range(3):
            self.attribs_fr.grid_rowconfigure(j, weight=1, uniform=1)
        for k, (name, value) in enumerate(zip(["Str", "Int", "Wis", "Dex", "Con", "Cha", "Com"], attribs), 1):
            self.method_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="left", anchor='s')
            self.method_label.grid(row=0, column=k, sticky='nsew')
            self.method_label['text'] = name
            self.method_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, borderwidth=8, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="left", anchor='center')
            self.method_label.grid(row=1, column=k, sticky='nsew')
            self.method_label['text'] = value
        self.selectionframe_open(attribs)
        self.header_controls()                          # uses self.m_a_c(), which must first be updated by self.u_n_b()

    def methodiv_header(self, attribs=None, selection=13):
        if attribs is None:
            attribs = attributes.methodiv()
        self.update_newchar_button(self.methodiv_header)
        self.common_header_elements()
        attr_names = [["Str:", "Int:", "Wis:", "Dex:", "Con:", "Cha:", "Com:"]]
        attribs.append([3, 3, 3, 3, 3, 3, 3])               # for blanking out the selection frame
        attribs = attr_names + attribs                      # adds attribute names to front of attributes lists
        self.attribs_fr.grid_propagate(False)
        for i, width in enumerate([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]):         # generates column widths
            self.attribs_fr.grid_columnconfigure(i, weight=width, uniform=1)
        self.attribs_fr.grid_rowconfigure(0, weight=1, uniform=1)
        for k in range(13):                                 # generates attribute sets
            if k == 0:                                      # assigns attribute names to first column
                self.methodiv_button = tk.Label(master=self.attribs_fr, relief=tk.FLAT, anchor='s', bg='#000000',
                                                fg="#FFFFFF", borderwidth=4, font=('Courier', 12), justify="center")
            elif k == selection:                            # sets lambda to de-highlight and de-select
                self.methodiv_button = tk.Button(master=self.attribs_fr, relief=tk.FLAT, anchor='s', bg='#FFFFFF',
                                                 fg="#000000", borderwidth=4, font=('Courier', 12), justify="center",
                                                 command=lambda des=k: self.methodiv_header(attribs[1:14], 13))
            else:                                           # sets lambda to highlight and populate the selectionframe
                self.methodiv_button = tk.Button(master=self.attribs_fr, relief=tk.FLAT, anchor='s', bg='#000000',
                                                 fg="#FFFFFF", borderwidth=4, font=('Courier', 12), justify="center",
                                                 command=lambda sel=k: self.methodiv_header(attribs[1:14], sel))
            self.methodiv_button.grid(row=0, column=k+1, columnspan=1, sticky='nsew')
            self.methodiv_button['text'] = '{}\n{}\n{}\n{}\n{}\n{}\n{}'.\
                format(attribs[k][0], attribs[k][1], attribs[k][2], attribs[k][3], attribs[k][4], attribs[k][5],
                       attribs[k][6])
        self.header_controls()                          # uses self.m_a_c(), which is updated by self.u_n_b()
        self.selectionframe_open(attribs[selection])

    def methodv_header(self, charclass=None, attribs=(18, 18, 18, 18, 18, 18, 18)):
        self.update_newchar_button(self.methodv_header)
        self.common_header_elements()
        self.attributes_frame.grid_propagate(False)
        for i, width in enumerate([5, 1, 1, 1, 1, 1, 1, 1, 1]):         # generates column widths
            self.attribs_fr.grid_columnconfigure(i, weight=width, uniform=1)
        for j in range(3):
            self.attribs_fr.grid_rowconfigure(j, weight=1, uniform=1)
        if charclass is None:
            self.method_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                         bg='#000000', font=('Courier', 12), justify="center", anchor='s')
            self.method_label.grid(row=1, column=0, columnspan=4, sticky='nse')
            self.method_label['text'] = "Select a class"
        else:
            self.method_label.destroy()
            for k, (attribute, value) in enumerate(zip(["Str", "Int", "Wis", "Dex", "Con", "Cha", "Com"], attribs), 1):
                self.method_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                             bg='#000000', font=('Courier', 12), justify="left", anchor='s')
                self.method_label.grid(row=0, column=k, columnspan=1, sticky='nsew')
                self.method_label['text'] = attribute
                self.method_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, borderwidth=8, fg="#FFFFFF",
                                             bg='#000000', font=('Courier', 12), justify="left", anchor='center')
                self.method_label.grid(row=1, column=k, columnspan=1, sticky='nsew')
                self.method_label['text'] = value
        self.selectionframe_methodv(charclass, attribs)

    def methodvi_header(self):
        # what we need to do in here:
        # DONE  a) pass onto single char generation
        # DONE  b) pass onto 8-person party generated (locking only level?)
        # c) race selection dropdown
        # d) class selection dropdown
        # e) sample size dropdown/text box
        # f) the 15-attr baseline
        # g) the per-level / per class comparisons (primarily hp, but also thaco)
        self.update_newchar_button(self.reroll)
        self.common_header_elements()
        # self.header_controls(rr=False)            # controls will live in selectionframe
        for i, width in enumerate([1, 1, 1, 1]):    # column widths
            self.attribs_fr.grid_columnconfigure(i, weight=width, uniform=1)
        for j in range(3):
            self.attribs_fr.grid_rowconfigure(j, weight=1, uniform=1)
        self.button = tk.Button(self.attribs_fr, text="GENERATE\nINDIVIDUAL\nCHARACTERS", bg='#000000', relief=tk.FLAT,
                                fg="#FFFFFF", font=('Courier', 12), anchor='center',
                                command=lambda: self.startframe_close())
        self.button.grid(row=0, column=0, rowspan=3, sticky='nsew')
        self.button = tk.Button(self.attribs_fr, text="GENERATE\nFULL\nPARTY", bg='#000000', relief=tk.FLAT,
                                fg="#FFFFFF", font=('Courier', 12), anchor='center',
                                command=lambda: self.party_maker())
        self.button.grid(row=0, column=1, rowspan=3, sticky='nsew')
        self.selectionframe_methodvi()

    def return_to_main_menu(self):      # only for MethodVI - the other methods just pack it at the bottom
        self.method_frame = tk.Frame(master=self.selection_frame, relief=tk.FLAT, bg='#000000')
        self.method_frame.grid(row=1, column=0, sticky="nsew")
        self.close_selection_frame = tk.Button(self.method_frame, text="return to main menu", bg='#000000',
                                               fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                               command=lambda: self.clbutt())
        self.close_selection_frame.pack(side='bottom')

    def selectionframe_methodvi(self):
        self.selection_frame.destroy()
        self.selection_frame = tk.Label(master=self.master, relief=tk.FLAT, fg="#FFFFFF", bg='#000000',
                                        font=('Courier', 12), justify="center")
        self.selection_frame.grid_propagate(False)
        self.selection_frame.grid(row=1, column=0, rowspan=3, columnspan=6, sticky="nsew")
        self.selection_frame.grid_columnconfigure(0, weight=1, uniform=1)
        self.selection_frame.grid_rowconfigure(0, weight=9, uniform=1)
        self.selection_frame.grid_rowconfigure(1, weight=1, uniform=1)
        self.return_to_main_menu()

    def party_maker(self):          # this generates the "Full Party" control frame
        self.party_list = []
        self.selection_body.destroy()
        self.selection_body = tk.Frame(master=self.selection_frame, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.selection_body.grid(row=0, column=0, sticky="nsew")
        self.selection_body.grid_propagate(False)
        for i in range(20):
            self.selection_body.grid_columnconfigure(i, weight=1, uniform=1)
        for i in range(12):
            self.selection_body.grid_rowconfigure(i, weight=1, uniform=1)
        self.method_label = tk.Label(master=self.selection_body, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                     bg='#000000', font=('Courier', 12), justify="left", text="Level Range")
        self.method_label.grid(row=2, column=2, columnspan=3, sticky='sw')
        options = list(range(1, 17))
        self.tk_variable = tk.IntVar(self.selection_body, self.minmaxlevel['min'])
        level_dropdown = tk.OptionMenu(self.selection_body, self.tk_variable, *options, command=self.minlevelset)
        level_dropdown.config(bg='#000000', fg='#FFFFFF', font=('Courier', 12), activebackground='#000000',
                              activeforeground='#FFFFFF')
        level_dropdown["menu"].config(bg='#000000', fg='#FFFFFF', font=('Courier', 12))
        level_dropdown.grid(row=3, column=2, sticky='new')
        self.method_label = tk.Label(master=self.selection_body, relief=tk.FLAT, borderwidth=4, fg="#FFFFFF",
                                     bg='#000000', font=('Courier', 12), justify="center", text="to")
        self.method_label.grid(row=3, column=3, sticky='new')
        self.tk_variable = tk.IntVar(self.selection_body, self.minmaxlevel['max'])
        level_dropdown = tk.OptionMenu(self.selection_body, self.tk_variable, *options, command=self.maxlevelset)
        level_dropdown.config(bg='#000000', fg='#FFFFFF', font=('Courier', 12), activebackground='#000000',
                              activeforeground='#FFFFFF')
        level_dropdown["menu"].config(bg='#000000', fg='#FFFFFF', font=('Courier', 12))
        level_dropdown.grid(row=3, column=4, sticky='new')
        self.frame = tk.Frame(self.selection_body)
        self.frame.pack_propagate(False)
        self.frame.grid(row=3, column=6, columnspan=4, sticky='nsew')
        self.button = tk.Button(self.frame, text="GENERATE PARTY", bg='#000000', relief=tk.FLAT, fg="#FFFFFF",
                                font=('Courier', 12), anchor='center', command=lambda: self.make_party())
        self.button.pack(expand=True, fill='both')
        self.return_to_main_menu()

    def make_party(self):                       # this advances "Full Party" control frame to the results interface
        self.party_list, level = [], 1
        for unit in range(8):                   # generates fully-random party
            level = random.randrange(self.minmaxlevel['min'], self.minmaxlevel['max'] + 1)
            self.party_list.append(character.Character(level))
        for butt_name, row_loc, command_def in zip(["REROLL", "VIEW PARTY", "PROCEED TO\nCHARACTER SHEET"], [3, 7, 5],
                                                   [self.make_party, self.party_frame_popup, self.startframe_close]):
            self.frame = tk.Frame(self.selection_body)
            self.frame.pack_propagate(False)    # this loop creates three buttons
            self.frame.grid(row=row_loc, column=6, columnspan=4, sticky='nsew')
            self.button = tk.Button(self.frame, text=butt_name, bg='#000000', relief=tk.FLAT, fg="#FFFFFF",
                                    font=('Courier', 12), anchor='center', command=lambda x=command_def: x())
            self.button.pack(expand=True, fill='both')
        self.frame = tk.Frame(self.selection_body)
        self.frame.pack_propagate(False)        # if disabled/changed to grid_prop- the window starts resizing
        self.frame.grid(row=3, column=10, rowspan=7, columnspan=9, sticky='nsew')
        arch_list, arch_dict = [], {"Cleric": 0, "Fighter": 0, "Magic User": 0, "Thief": 0}
        for char in self.party_list:            # populates arch_dict with a proportional archetype count
            for sub_class in char.classes:
                arch_list.append(datalocus.archetype(sub_class))
                arch_dict[datalocus.archetype(sub_class)] += 1 / len(char.classes)
        fig = Figure(facecolor='#000000')       # creates a black matplotlib frame
        ax = fig.add_subplot(2, 6, (1, 10))     # creates a 2x6 grid within fig and places the chart from 1,1 to 2,4
        ax.pie(list(arch_dict.values()), radius=1.4, labels=list(arch_dict.keys()), shadow=True, labeldistance=None,
               colors=["#5B9BD5", "#FFC000", "#C00000", "#70AD47"])     # labeldistance passes key values to legend
        ax.legend(loc=1, bbox_to_anchor=(1.5, 0., 0.5, 1.), fontsize=12, frameon=False, labelcolor='#FFFFFF',
                  prop='monospace')
        chart1 = FigureCanvasTkAgg(fig, self.frame)
        chart1.get_tk_widget().pack(fill='both')

    def minlevelset(self, level):
        self.minmaxlevel["min"] = level
        if self.minmaxlevel["max"] < self.minmaxlevel["min"]:
            self.minmaxlevel["max"] = self.minmaxlevel["min"]
        self.selectionframe_methodvi()
        self.party_maker()

    def maxlevelset(self, level):
        self.minmaxlevel["max"] = level
        if self.minmaxlevel["min"] > self.minmaxlevel["max"]:
            self.minmaxlevel["min"] = self.minmaxlevel["max"]
        self.selectionframe_methodvi()
        self.party_maker()

    def selectionframe_open(self, attribs):                 # attribs is an ordered list of the SIX primary attributes
        self.racial_modifiers('Human')                      # blanks out the racial modifier field
        eligibility_object = selectclass.IsEligible()       # creates an IsEligible object using attribs
        eligibility_object.eligible(attribs)
        eligible_races = eligibility_object.eligible_races
        eligible_classes = eligibility_object.eligible_classes
        self.selection_frame.destroy()                      # destroys and re-creates its own frame
        self.selection_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.selection_frame.grid(row=1, column=0, rowspan=3, columnspan=6, sticky="nsew")
        for y, race in enumerate(eligible_races):          # generates race buttons from IsEligible object
            self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#000000', fg="#FFFFFF",
                                     font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                     command=lambda r=race: self.selectionframe_suspension(attribs, eligibility_object,
                                                                                           eligible_races,
                                                                                           eligible_classes, 1, r))
            self.rc_opts.place(height=20, width=254, x=10 + 254 * int(y / 23), y=10 + 20 * (y % 23))
        for z, ch_cl in enumerate(eligible_classes):              # generates class buttons from IsEligible object
            self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#000000', fg="#FFFFFF",
                                     font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                     command=lambda c=ch_cl: self.selectionframe_suspension(attribs, eligibility_object,
                                                                                            eligible_races,
                                                                                            eligible_classes, 0, c))
            self.rc_opts.place(height=20, width=254, x=640 + 254 * int((z / 23)), y=10 + 20 * (z % 23))
        self.close_selection_frame = tk.Button(self.selection_frame, text="return to main menu", bg='#000000',
                                               fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                               command=lambda: self.clbutt())
        self.close_selection_frame.pack(side='bottom')      # places return_to_main_menu button

    def selectionframe_suspension(self, attribs, elig_object, all_races, all_classes, race_is_selected, selection):
        self.racial_modifiers(selection)
        elig_object.filtered_eligibility(attribs, selection)
        remaining_races = elig_object.eligible_races
        remaining_classes = elig_object.eligible_classes
        self.selection_frame.destroy()
        self.selection_frame = tk.Frame(master=self.master, relief=tk.RIDGE, borderwidth=4, bg='#000000')
        self.selection_frame.grid(row=1, column=0, rowspan=3, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        if race_is_selected:
            for y, race in enumerate(all_races):
                if race in remaining_races:
                    self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#FFFFFF', fg="#000000",
                                             font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda rac=race: self.selectionframe_open(attribs))
                    self.rc_opts.place(height=20, width=254, x=10 + 254 * int(y / 23), y=10 + 20 * (y % 23))
                else:
                    self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#000000', fg="#666666",
                                             font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda r=race: self.selectionframe_suspension(attribs, elig_object,
                                                                                                   all_races,
                                                                                                   all_classes,
                                                                                                   race_is_selected, r))
                    self.rc_opts.place(height=20, width=254, x=10 + 254 * int(y / 23), y=10 + 20 * (y % 23))
            for z, ch_cl in enumerate(all_classes):
                if ch_cl in remaining_classes:
                    self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#000000',
                                             fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda c=ch_cl: self.charsheet_transition(selection, c, attribs))
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
                                             command=lambda r=race: self.charsheet_transition(r, selection, attribs))
                    self.rc_opts.place(height=20, width=254, x=10 + 254 * int(y / 23), y=10 + 20 * (y % 23))
                else:           # these labels need their x-axis location adjusted by +2 for the text to line up
                    self.rc_opts = tk.Label(self.selection_frame, text=race, bg='#000000', fg="#666666",
                                            font=('Courier', 12), relief=tk.FLAT, anchor='w')
                    self.rc_opts.place(height=20, width=254, x=12 + 254 * int(y / 23), y=10 + 20 * (y % 23))
            for z, ch_cl in enumerate(all_classes):
                if ch_cl in remaining_classes:
                    self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#FFFFFF', fg="#000000",
                                             font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda c=ch_cl: self.selectionframe_open(attribs))
                    self.rc_opts.place(height=20, width=254, x=640 + 254 * int((z / 23)), y=10 + 20 * (z % 23))
                else:
                    self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#000000',
                                             fg="#666666", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                             command=lambda c=ch_cl: self.selectionframe_suspension(attribs,
                                                                                                    elig_object,
                                                                                                    all_races,
                                                                                                    all_classes,
                                                                                                    race_is_selected,
                                                                                                    c))
                    self.rc_opts.place(height=20, width=254, x=640 + 254 * int((z / 23)), y=10 + 20 * (z % 23))
        self.close_selection_frame = tk.Button(self.selection_frame, text="return to main menu", bg='#000000',
                                               fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                               command=lambda: self.clbutt())
        self.close_selection_frame.pack(side='bottom')

    def selectionframe_methodv(self, charclass, attribs):      # charclass initially = None
        eligibility_object = selectclass.IsEligible()
        eligibility_object.eligible(attribs)
        self.selection_frame.destroy()
        self.selection_frame = tk.Label(master=self.master, relief=tk.RIDGE, borderwidth=4, fg="#FFFFFF", bg='#000000',
                                        font=('Courier', 12), justify="center")
        self.selection_frame.grid(row=1, column=0, rowspan=3, columnspan=6, sticky="nsew", ipadx=5, ipady=5)
        if charclass is None:
            eligible_classes = eligibility_object.eligible_classes
            self.header_controls(rr=False)  # creates a control panel without the reroll button
            for z, ch_cl in enumerate(eligible_classes):
                self.rc_opts = tk.Button(self.selection_frame, text=ch_cl, bg='#000000', anchor='w',
                                         fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                         command=lambda c=ch_cl: self.methodv_header(charclass=c,
                                                                                     attribs=attributes.methodv(c)))
                self.rc_opts.place(height=20, width=274, x=320 + 404 * int((z / 23)), y=10 + 20 * (z % 23))
        else:
            eligibility_object.filtered_eligibility(attribs, charclass)
            charraces = eligibility_object.eligible_races
            self.header_controls()          # creates reroll button, then immediately re-defines the lambda
            self.reroll_header.config(command=lambda: self.methodv_header(charclass=charclass,
                                                                          attribs=attributes.methodv(charclass)))
            if len(charraces) == 0:         # if there are zero eligible races...
                self.selection_frame['text'] = "Attributes do not meet class minimum"
            else:
                for z, race in enumerate(charraces):
                    self.rc_opts = tk.Button(self.selection_frame, text=race, bg='#000000', anchor='w',
                                             fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT,
                                             command=lambda r=race: self.charsheet_transition(r, charclass, attribs))
                    self.rc_opts.place(height=20, width=274, x=320 + 404 * int((z / 23)), y=10 + 20 * (z % 23))
        self.close_selection_frame = tk.Button(self.selection_frame, text="return to main menu", bg='#000000',
                                               fg="#FFFFFF", font=('Courier', 12), relief=tk.FLAT, anchor='w',
                                               command=lambda: self.clbutt())
        self.close_selection_frame.pack(side='bottom')

    def racial_modifiers(self, chcl_selection):                     # previews racial bonuses/penalties in the header
        racial_bons = attributes.display_racial_bonuses_i(chcl_selection)
        if self.make_another_character == self.methodiv_header:     # bonuses display vertically in method iv...
            self.methodiv_label.destroy()
            temp = ''
            for u, bonus in enumerate(racial_bons):
                temp += '\n{}'.format(bonus)
            self.methodiv_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, fg="#00FFFF", borderwidth=4,
                                           bg='#000000', font=('Courier', 12), justify="right", anchor='s')
            self.methodiv_label.grid(row=0, column=0, sticky='nse')
            self.methodiv_label['text'] = temp
        else:                                                       # ...otherwise they go under the respective attr
            for i, bonus in enumerate(racial_bons, 1):
                self.method_label = tk.Label(master=self.attribs_fr, relief=tk.FLAT, borderwidth=4, fg="#00FFFF",
                                             bg='#000000', font=('Courier', 12), justify="left", anchor='n')
                self.method_label.grid(row=2, column=i, columnspan=1, sticky='nsew')
                self.method_label['text'] = bonus

    def charsheet_transition(self, charrace, charclass, attribs):
        self.display_text[0] = ''
        formatted_atts = attributes.apply_race_modifiers(charrace, attribs)     # applies racial modifier and formats
        class_list = selectclass.string_to_list(charclass, '/')
        self.selected_character = character.Character(level=self.level, race=charrace, classes=class_list,
                                                      attrib_list=formatted_atts, gender=self.gender)
        self.selection_frame.destroy()
        self.attributes_frame.destroy()
        self.nonmember_buttons()                                                # activates character sheet hotkeys
        self.update_charsheet()                                                 # populates character sheet
        self.char_frame.lift()
        self.member_frame.lift()
        self.contdisp_frame.lift()                                  # print('test', self.selected_character.__dict__)

    def header_controls(self, rr=True):
        self.header_control_frame = tk.Frame(master=self.hcontrol_fr, bg='#000000', borderwidth=0)
        self.header_control_frame.grid(row=0, column=1, sticky='nsew')
        for k in range(5):
            self.header_control_frame.grid_rowconfigure(k, weight=1, uniform=1)
        for m in range(2):
            self.header_control_frame.grid_columnconfigure(m, weight=1, uniform=1)
        self.reroll_header = tk.Button(master=self.header_control_frame, relief=tk.RIDGE, fg="#FFFFFF",
                                       bg='#000000', font=('Courier', 12), justify="left", anchor='center',
                                       text='Reroll', command=lambda: self.make_another_character(), borderwidth=4)
        if rr:
            self.reroll_header.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.method_label = tk.Label(master=self.header_control_frame, relief=tk.FLAT, fg="#FFFFFF", text='Gender:',
                                     bg='#000000', font=('Courier', 12), justify="left", anchor='center')
        self.gender_select = tk.Button(master=self.header_control_frame, relief=tk.RIDGE, fg="#FFFFFF",
                                       bg='#000000', font=('Courier', 12), justify="left", anchor='center',
                                       width=7,
                                       text=str(self.gender), command=lambda: self.select_gender(), borderwidth=4)
        self.method_label.grid(row=1, column=0, sticky='nsew')
        self.gender_select.grid(row=1, column=1, sticky='nsew')
        self.method_label = tk.Label(master=self.header_control_frame, relief=tk.FLAT, fg="#FFFFFF", text=' Level:',
                                     bg='#000000', font=('Courier', 12), justify="left", anchor='center')
        self.method_label.grid(row=2, column=0, sticky='nsew')
        options = list(range(1, 17))
        self.tk_variable = tk.IntVar(self.header_control_frame, self.level)
        level_dropdown = tk.OptionMenu(self.header_control_frame, self.tk_variable, *options, command=self.levelset)
        level_dropdown.config(bg='#000000', fg='#FFFFFF', font=('Courier', 12), activebackground='#000000',
                              activeforeground='#FFFFFF')
        level_dropdown["menu"].config(bg='#000000', fg='#FFFFFF', font=('Courier', 12))
        level_dropdown.grid(row=2, column=1, sticky='nsew')
        self.button = tk.Button(master=self.header_control_frame, relief=tk.RIDGE, fg="#FFFFFF", bg='#000000',
                                font=('Courier', 12), justify="left", anchor='center', borderwidth=4,
                                text="view party", command=lambda: self.party_frame_popup(top_button=True))
        self.button.grid(row=3, column=0, columnspan=2, sticky='nsew')

    def party_frame_popup(self, top_button=False):
        self.temp_frame = tk.Frame(master=self.master, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.temp_frame.grid(row=0, column=0, columnspan=6, sticky='nsew', ipadx=5, ipady=5)
        for i, width in enumerate([3, 1]):
            self.temp_frame.grid_columnconfigure(i, weight=width, uniform=1)
        self.temp_frame.grid_rowconfigure(0, weight=1, uniform=1)
        self.temp_frame.grid_propagate(False)
        self.close_popup_frame = tk.Frame(master=self.temp_frame, relief=tk.FLAT, borderwidth=4, bg='#000000')
        self.close_popup_frame.grid(row=0, column=1, sticky="nsew")
        for i, width in enumerate([1, 3, 1]):       # NOT defining row width is what allows the spillover/large button
            self.close_popup_frame.grid_columnconfigure(i, weight=width, uniform=1)
        self.expanded_party_display(top_button)

    def clear_party_popup(self):
        self.temp_frame.destroy()
        self.member_frame.destroy()
        self.generate_party_frame()
        self.member_frame.lower()

    def expanded_party_display(self, top_button=False):
        self.member_frame, final_list = tk.Frame(self.master, bg='#000000'), []
        self.member_frame.grid(row=1, column=0, rowspan=3, columnspan=6, sticky="nsew")
        for a, value in enumerate([3, 3, 1, 3, 1, 1, 1, 1, 1]):
            self.member_frame.grid_columnconfigure(a, weight=value, uniform=1)
        self.member_frame.grid_rowconfigure(0, weight=1, uniform=1)
        self.member_frame.grid_rowconfigure(1, weight=1, uniform=1)
        display_name, display_class, display_hp, display_th = ['\n    Member\n'], ['\nClass\n'], ['\nHP\n'], ['\nTH\n']
        display_race, display_move, display_dmg, display_acs = ['\nRace\n'], ['\nMV\n'], ['\nDmg\n'], ['\nAC\n']
        levels_d = ['\nLevel\n']
        for a, member in enumerate(self.party_list, 1):
            display_name.append('\n  {} {}'.format(str(a), member.character_name))
            display_hp.append('\n{}'.format(member.hp))
            display_acs.append('\n{}'.format(10 + member.calculate_ac()))
            display_th.append('\n{}'.format(20 + member.calculate_thaco()))
            display_race.append('\n{}'.format(member.race))
            display_class.append('\n{}'.format(member.display_class))
            display_move.append('\n{}"'.format(member.class_movement()))
            damage_bon = int(member.str_damage_bonus())
            display_dmg.append('\n{0:{1}}'.format(damage_bon, '+' if damage_bon else ''))   # ...-1, 0, +1, etc...
            levels_d.append('\n{}'.format(member.display_level))
        for b in range(len(self.party_list) + 1, 9):                        # numbers empty portion of display
            display_name.append('\n  {} '.format(b))
        display_list = [display_name, display_race, levels_d, display_class, display_hp, display_acs, display_th,
                        display_dmg, display_move]
        for c in display_list:
            final_list.append("".join(c))                                   # joins each vertical string
        for n, str_val in enumerate(final_list):
            self.expanded_party_label = tk.Label(master=self.member_frame, borderwidth=4, fg="#FFFFFF",
                                                 font=('Courier', 12), bg='#000000', relief=tk.FLAT, justify="left",
                                                 anchor='nw', text=str_val)
            self.expanded_party_label.grid(row=0, column=n, rowspan=1, sticky='nsew')
        self.partypopup_highclose() if top_button else self.partypopup_lowclose()

    def partypopup_lowclose(self):      # this is the close button for Method VI's bulk view
        self.frame = tk.Frame(self.member_frame, bg='#000000', borderwidth=6)
        self.frame.grid(row=1, column=0, columnspan=9, sticky="nsew")
        self.inner_frame = tk.Frame(self.frame, bg='#FFF000')
        self.inner_frame.pack_propagate(False)
        for i in range(10):
            self.frame.grid_columnconfigure(i, weight=1, uniform=1)
        for i in range(20):             # 20 since LCD of 9 and 12 is 36 (+4 for footer) and we're using the bottom half
            self.frame.grid_rowconfigure(i, weight=1, uniform=1)
        self.inner_frame.grid(row=1, column=3, rowspan=3, columnspan=2, sticky='nsew')
        self.button = tk.Button(self.inner_frame, text="CLOSE", bg='#000000', fg="#FFFFFF", anchor='center',
                                font=('Courier', 12), relief=tk.FLAT, command=lambda: self.clear_party_popup())
        self.button.pack(expand=True, fill='both')

    def partypopup_highclose(self):     # ...and this is the close button for everything else
        self.temp_control_frame = tk.Frame(master=self.close_popup_frame, bg='#000000', borderwidth=0)
        self.temp_control_frame.grid(row=0, column=1, sticky='nsew')
        for k in range(5):
            self.temp_control_frame.grid_rowconfigure(k, weight=1, uniform=1)
        for m in range(2):
            self.temp_control_frame.grid_columnconfigure(m, weight=1, uniform=1)
        self.method_label = tk.Label(master=self.temp_control_frame, relief=tk.FLAT, fg="#FFFFFF", bg='#000000',
                                     font=('Courier', 12), justify="left", anchor='center', borderwidth=4)
        for n in range(3):
            self.method_label.grid(row=n, column=0, columnspan=2, sticky='nsew')
        self.button = tk.Button(master=self.temp_control_frame, relief=tk.RIDGE, fg="#FFFFFF", bg='#000000',
                                font=('Courier', 12), justify="left", anchor='center', width=14,
                                text="close", command=lambda: self.clear_party_popup(), borderwidth=4)
        self.button.grid(row=3, column=0, columnspan=2, sticky='nsew')

    def select_gender(self):        # temporarily replaces header_control_frame with the gender select menu
        self.header_control_frame.destroy()
        self.header_control_frame = tk.Frame(master=self.hcontrol_fr, bg='#000000', borderwidth=0)
        self.header_control_frame.grid(row=0, column=1, sticky='nsew')
        for k in range(5):
            self.header_control_frame.grid_rowconfigure(k, weight=1, uniform=1)
        for m in range(2):
            self.header_control_frame.grid_columnconfigure(m, weight=1, uniform=1)
        for x, gender in enumerate(["random", "male", "female"]):
            self.button = tk.Button(master=self.header_control_frame, relief=tk.RIDGE, fg="#FFFFFF", anchor='center',
                                    bg='#222222', font=('Courier', 12), justify="left", text=gender, width=7,
                                    borderwidth=4, command=lambda gen=gender: self.genderset(gen))
            self.button.grid(row=x+1, column=1, sticky='nsew')

    def genderset(self, selection):
        self.gender = selection          # self.gender_select.config(text=self.gender)
        self.header_control_frame.destroy()
        self.header_controls()           # not using the config / re-building instead

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
