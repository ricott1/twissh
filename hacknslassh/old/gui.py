class GameFrame(Scene, urwid.Frame):
    def __init__(self, mind):
        self.mind = mind

        _header = urwid.LineBox(
            urwid.BoxAdapter(
                SelectableListBox(urwid.SimpleFocusListWalker([urwid.Text("")])),
                self.header_height,
            )
        )

        self._menu_view = True
        self.map = MapFrame(self, mind)
        self.menu = MenuFrame(self, mind)

        super().__init__(
            mind,
            urwid.Columns(
                [(self.map_width, self.map), (self.menu_width, self.menu)],
                focus_column=1,
            ),
            header=_header,
            footer=None,
            focus_part="body",
        )

        self.update_footer()
        self.header_widget = self.header.original_widget.box_widget
        self.footer_content_size = 0

    @property
    def header_height(self):
        return MIN_HEADER_HEIGHT  # max(MIN_HEADER_HEIGHT, self.mind.screen_size[1]//8)

    @property
    def menu_width(self):
        if self.menu_view:
            return min(MAX_MENU_WIDTH, (3 * self.mind.screen_size[0]) // 7)
        return 0

    @property
    def map_width(self):
        if self.menu_view:
            return self.mind.screen_size[0] - self.menu_width
        return self.mind.screen_size[0]

    @property
    def menu_view(self):
        return self._menu_view

    @menu_view.setter
    def menu_view(self, value):
        self._menu_view = value
        _columns = [(self.map_width, self.map), (self.menu_width, self.menu)]
        self.contents["body"] = (urwid.Columns(_columns, focus_column=1), None)

    @property
    def header_list(self):
        return sorted(
            [
                ent
                for k, ent in self.player.location.entities.items()
                if distance(self.player.position, ent.position) <= 3 and ent.status
            ],
            key=lambda ent: distance(self.player.position, ent.position),
        )

    def update_footer(self):
        _size = 0
        inv_btns = []
        for i, obj in self.player.inventory.content.items():
            if obj:
                _size += 1
                if obj.is_equipment and obj.is_equipped:
                    _marker = ["[", (obj.color, f"{obj.marker[0]}"), "]"]
                elif obj.is_equipment and not obj.is_equipped:
                    _marker = ["]", (obj.color, f"{obj.marker[0]}"), "["]
                elif obj.is_consumable:
                    _marker = ["(", (obj.color, f"{obj.marker[0]}"), ")"]
                else:
                    _marker = [f" {obj.marker[0]} "]
            else:
                _marker = [f"  "]
            if i < 9:
                _num = f"\n {i+1} "
            elif i == 9:
                _num = "\n 0 "
            elif i == 10:
                _num = "\n - "
            elif i == 11:
                _num = "\n = "
            if obj and obj is self.player.inventory.selection:
                _marker += [("line", _num)]
            else:
                _marker += [("top", _num)]
            btn = urwid.Text(_marker, align="center")
            inv_btns.append((5, urwid.LineBox(btn)))

        if self.mind.screen_size != (80, 24):
            inv_btns.append(urwid.Text("\nSET TERMINAL\nTO 80X24", align="center"))

        self.contents["footer"] = (SelectableColumns(inv_btns, dividechars=0), None)
        self.footer_content_size = _size

    def on_update(self) -> None:
        self.update_header()
        if self.footer_content_size != len(self.player.inventory.all):
            self.update_footer()
        if self.mind.screen_size != (80, 24):
            self.update_footer()
        self.map.on_update()
        if self.menu_view:
            self.menu.on_update()

    def handle_input(self, _input):
        if _input == "tab":
            self.menu_view = not self.menu_view
        elif _input == "enter" and self.player.inventory.selection:
            self.player.use_quick_item(self.player.inventory.selection)
            self.update_footer()
        elif _input == "Q" and self.player.inventory.selection:
            self.player.actions["drop"].use(self.player, obj=self.player.inventory.selection)
            self.update_footer()
        elif _input.isnumeric() or _input in ("-", "="):
            self.select_item(_input)
            self.update_footer()
        elif _input == KeyMap["status-menu"] and self.menu_view:
            self.menu.update_body("Status")
        elif _input == KeyMap["help-menu"] and self.menu_view:
            self.menu.update_body("Help")
        elif _input == KeyMap["equipment-menu"] and self.menu_view:
            self.menu.update_body("Equipment")
        elif _input == KeyMap["inventory-menu"] and self.menu_view:
            self.menu.update_body("Inventory")
        else:
            self.player.handle_input(_input)

    def select_item(self, _input):
        if _input.isnumeric() and int(_input) > 0:
            _input = int(_input) - 1
        elif _input == "0":
            s_input = 9
        elif _input == "-":
            _input = 10
        elif _input == "=":
            _input = 11
        self.player.inventory.selection = self.player.inventory.get(_input)

    def update_header(self):
        widgets = []
        for p in self.header_list:
            widgets.append(
                urwid.AttrMap(
                    urwid.AttrMap(urwid.Text(p.status, wrap="clip"), {self.player.id: "player"}),
                    {p.id: "other" for i, p in self.mind.master.players.items()},
                )
            )
        if widgets:
            self.header_widget.body[:] = widgets

