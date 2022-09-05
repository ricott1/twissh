class ExtendedListBox(urwid.ListBox):
    """
    Listbow widget with embeded autoscroll
    """

    __metaclass__ = urwid.MetaSignals
    signals = ["set_auto_scroll"]

    def set_auto_scroll(self, switch):
        if type(switch) != bool:
            return
        self._auto_scroll = switch
        urwid.emit_signal(self, "set_auto_scroll", switch)

    auto_scroll = property(lambda s: s._auto_scroll, set_auto_scroll)

    def __init__(self, body):
        urwid.ListBox.__init__(self, body)
        self.auto_scroll = True

    def switch_body(self, body):
        if self.body:
            urwid.disconnect_signal(body, "modified", self._invalidate)

        self.body = body
        self._invalidate()

        urwid.connect_signal(body, "modified", self._invalidate)

    def handle_input(self, _input):
        if _input == "shift left":
            _input = "page up"
        elif _input == "shift right":
            _input = "page down"
        urwid.ListBox.keypress(self, (80, 24), _input)

        if _input in ("page up", "page down"):
            if self.get_focus()[1] == len(self.body) - 1:
                self.auto_scroll = True
            else:
                self.auto_scroll = False

    def scroll_to_bottom(self):
        if self.auto_scroll:
            # at bottom -> scroll down
            self.set_focus(len(self.body) - 1)


class ListInventoryFrame(UiFrame):
    def __init__(self, parent, mind):
        self.inventory = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        super(InventoryFrame, self).__init__(parent, mind, self.inventory)
        self.selection = "normal"

    def on_update(self):
        def show_item(item, button):
            self.selection = item.id

        def back(button):
            self.selection = "normal"

        def drop_item(item, button):
            self.player.actions["drop"].use(self.player, obj=item)

        def consume_item(item, button):
            self.player.actions["consume"].use(self.player, obj=item)

        widgets = []
        items = [i for i in self.player.inventory.all]
        if self.selection == "normal":
            for i in items:
                line = []
                btn = create_button(i.name, show_item, attr=i.color, user_args=[i])
                line.append((16, btn))
                bdrop = create_button("Drop", drop_item, user_args=[i])
                line.append((8, bdrop))
                if i.is_consumable:
                    btn = create_button("Use", consume_item, user_args=[i])
                    line.append((8, btn))

                if i.is_equipment:
                    description = urwid.Text(f"- {i.eq_description}")
                else:
                    description = urwid.Text(f"- {i.description}")  # , wrap="clip"
                line.append(description)

                columns = SelectableColumns(line, dividechars=2)
                try:
                    index = self.inventory.focus_position
                    columns.focus_position = self.inventory.body[:][index].focus_position
                except:
                    pass

                widgets.append(columns)
        else:
            i = next((it for it in items if it.id == self.selection), None)
            if i == None:
                self.selection = "normal"
            else:
                widgets.append(urwid.Text(i.status))
                if i.is_equipment:
                    description = urwid.Text((" - {} {}".format(i.eq_description, "(eq)" * int(i.is_equipped))))
                else:
                    description = urwid.Text(f"- {i.description}")
                widgets.append(description)

                bback = create_button("Back", back)

                widgets.append(SelectableColumns([(8, bback)]))
        self.body.body[:] = widgets


class EquipmentFrame(UiFrame):
    def __init__(self, parent, mind):
        super(EquipmentFrame, self).__init__(parent, mind, SelectableListBox(urwid.SimpleListWalker([urwid.Text("")])))
        self.selection = "normal"

    def on_update(self):
        def open_equipment(typ, button):
            self.selection = typ

        def send_equip(item, button):
            if not item.is_equipped:
                self.player.equip(item, self.selection)
            self.selection = "normal"

        def send_unequip(button):
            if self.selection in self.player.equipment and self.player.equipment[self.selection]:
                self.player.unequip(self.selection)
            self.selection = "normal"

        widgets = []

        if self.selection == "normal":
            t = urwid.Text("", align="center")
            widgets.append(t)

            for part, eqp in self.player.equipment.items():
                equip_btn = create_button(f"{' '.join(part.split('_'))}", open_equipment, user_args=[part])

                if eqp:
                    text = urwid.Text([(eqp.color, f"{eqp.name} "), eqp.eq_description])
                else:
                    text = urwid.Text("None")
                line = [(16, equip_btn), text]
                columns = SelectableColumns(line, dividechars=2)
                widgets.append(columns)

        else:
            t = urwid.Text(f"{' '.join(self.selection.split('_'))}", align="center")
            widgets.append(t)
            unequip_btn = create_button("None", send_unequip)
            text = urwid.Text("")
            line = [(16, unequip_btn), text]
            columns = SelectableColumns(line, dividechars=2)
            widgets.append(columns)
            eqs = [i for i in self.player.inventory.all if self.selection in i.type and i.requisites(self.player)]
            for i in eqs:
                btn = create_button(i.name, send_equip, attr=i.rarity, user_args=[i])
                text = urwid.Text(f"{'(eq)'*int(i.is_equipped)}")
                line = [(16, btn), text]
                columns = SelectableColumns(line, dividechars=2)
                widgets.append(columns)

        self.body.body[:] = widgets


class ChatFrame(UiFrame):
    def __init__(self, parent, mind):

        self.footer = urwid.Edit("> ")

        self.output_walker = urwid.SimpleListWalker([])
        self.output_size = 0
        self.body = ExtendedListBox(self.output_walker)

        self.footer.set_wrap_mode("space")
        super(ChatFrame, self).__init__(parent, mind, self.body, footer=self.footer)
        self.set_focus("footer")

    def on_update(self):
        for i in range(self.output_size, len(self.player.chat_received_log)):
            self.print_received_message(self.player.chat_received_log[i])
            self.output_size += 1

    def handle_input(self, _input):
        """
        Handle user inputs
        """

        # scroll the top panel
        if _input in ("page up", "page down", "shift left", "shift right"):
            self.body.handle_input(_input)
        elif _input == "enter":
            # Parse data or (if parse failed)
            # send it to the current world
            text = self.footer.get_edit_text()

            self.footer.set_edit_text(" " * len(text))
            self.footer.set_edit_text("")

            if text.strip():
                self.print_sent_message(text)
                self.player.chat_sent_log.append(
                    {
                        "sender_id": self.player.id,
                        "sender": self.player.name,
                        "time": time.time(),
                        "text": text,
                    }
                )

    def print_sent_message(self, text):
        self.output_walker.append(urwid.AttrMap(urwid.Text(f"You: {text}"), "uncommon"))
        self.body.scroll_to_bottom()

    def print_received_message(self, message):
        self.output_walker.append(urwid.Text(f"{message['sender']}: {message['text']}"))
        self.body.scroll_to_bottom()
