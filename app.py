from dearpygui.core import *
from dearpygui.simple import *
from loguru import logger
from app_backend import App_backend
import random
import os
import traceback


class App:
    def __init__(self) -> None:
        self.cwd = os.getcwd()
        logger.info(f"CWD: {self.cwd}")
        self.init = False
        self.app_backend = None

    def check_init(self) -> None:
        if not self.init:
            self.app_backend = App_backend(os.getcwd(), "bingo.db")
            self.init = True

    def verify_game(self, sender, data):
        # TODO CHECK
        delete_item("Game")

    def close_window(self, window: str):
        delete_item(window)

    def generate_winning_combination(self) -> list:
        # TODO ADD ODDS, MUST CONFIRM W/ CLIENT
        numbers = list(range(1, 49))
        required_numbers = 35
        win_nums = []
        i = 1
        while i != required_numbers:
            index = random.randint(0, len(numbers) - 1)
            number = numbers.pop(index)
            win_nums.append(number)
            i += 1
        return win_nums

    def create_game(self, sender, data):
        # TODO Implement
        pass

    def create_game_window(self, sender, data):
        try:
            self.close_window("Create New Game")
            self.close_window("Load Game")
            self.check_init()
        except Exception:
            pass
        numbers = self.generate_winning_combination()
        with window("Create New Game", autosize=True):
            add_text("Winning numbers:")
            for index in range(1, len(numbers) + 1):
                if index % 5 == 0:
                    add_text(
                        f"{numbers[index-5]} {numbers[index-4]} {numbers[index-3]} {numbers[index-2]} {numbers[index-1]}"
                    )
            add_button("Create Game", callback=self.create_game)

    def open_game(self, sender, data):
        # TODO Implement
        self.check_init()
        pass

    def open_game_window(self, sender, data):
        # TODO Implement
        pass

    def check_numbers(self, numbers: list) -> tuple:
        valid = False
        index = 0
        error = ""
        try:
            for index, number in enumerate(numbers):
                valid_input = 1 <= int(number) <= 48
                if valid_input:
                    valid = True
                else:
                    valid = False
                    error = f"Number is not between 1 and 48. (Number: {index+1})"
                    break
            if len(set(numbers)) != 6:
                valid = False
                error = f"Duplicate numbers. Check input."
        except Exception:
            valid = False
            error = f"Did not enter a number (Number: {index+1})"
        finally:
            return valid, error, numbers

    def check_text(self, text: str) -> tuple:
        if text and not text.isspace():
            text = text.rstrip()
            text = text.lstrip()
            return True, text
        return False, text

    def check_number(self, number: str) -> tuple:
        valid = False
        try:
            number = int(number)
            valid = True
        except:
            pass
        finally:
            return valid, number

    def create_ticket(self, sender, data):
        # TODO Implement
        self.check_init()
        success = False
        ticket_id = 0
        name = get_value("ticket_name")
        valid_name, name = self.check_text(name)
        bet_amount = get_value("bet_amount")
        valid_amount, bet_amount = self.check_number(bet_amount)
        numbers = [get_value(f"ticket_num_{num}") for num in range(1, 7)]
        valid_numbers, error, numbers = self.check_numbers(numbers)
        if valid_name and valid_numbers and valid_amount:
            numbers = [int(x) for x in numbers]
            entry = {"name": name, "amount": bet_amount, "numbers": numbers}
            game_id = self.app_backend.game_id
            if game_id == 0:
                self.error_window("Please create or choose a game.")
            else:
                ticket_id = self.app_backend.create_ticket(entry)
                success = True
        else:
            if not valid_name:
                error = "Name and/or bet amount is not valid."
            elif not valid_amount:
                error = "Bet amount is not valid."
            self.error_window(error)
        if success:
            delete_item("Create New Ticket")
            with window(
                "Confirm new ticket", on_close=self.delete_new_ticket_confirmation, autosize=True
            ):
                add_text("Ticket created with the following information: ")
                add_text(f"Name: {name}")
                add_text(f"Bet Amount: {bet_amount}")
                add_text(f"Numbers: {', '.join([str(x) for x in numbers])}")
                add_button("View Ticket", callback=self.open_ticket, callback_data=ticket_id)
                add_button("Close Window", callback=self.delete_new_ticket_confirmation)

    def delete_new_ticket_confirmation(self, sender, data):
        delete_item("Confirm new ticket")

    def error_window(self, error: str):
        with window("Error", on_close=self.delete_error):
            add_text(error)
            add_button("OK", callback=self.delete_error)

    def delete_error(self, sender, data):
        delete_item("Error")

    def create_ticket_window(self, sender, data):
        try:
            self.close_window("Create New Ticket")
            self.close_window("Load Game")
            self.check_init()
        except Exception:
            pass
        with window("Create New Ticket", autosize=True):
            add_input_text("Name", source="ticket_name")
            add_input_text("Amount", source="bet_amount")
            add_input_text("Number 1", source="ticket_num_1")
            add_input_text("Number 2", source="ticket_num_2")
            add_input_text("Number 3", source="ticket_num_3")
            add_input_text("Number 4", source="ticket_num_4")
            add_input_text("Number 5", source="ticket_num_5")
            add_input_text("Number 6", source="ticket_num_6")
            add_button("Create Ticket", callback=self.create_ticket)

    def open_ticket(self, sender, data):
        if isinstance(data, list):
            path = f"{data[0]}/{data[1]}"
        else:
            path = f"{os.getcwd()}/tickets/game_{self.app_backend.game_id}/ticket_{data}.pdf"
        self.app_backend.open_ticket(path)

    def open_ticket_window(self, sender, data):
        open_file_dialog(callback=self.open_ticket)

    def show(self):
        with window("Bingo"):
            set_main_window_size(1024, 760)
            set_main_window_resizable(True)
            set_global_font_scale(1.25)
            with menu_bar("Main Menu Bar"):

                with menu("Game"):
                    add_menu_item("New game", callback=self.create_game_window)
                    add_menu_item("Open game", callback=self.open_game_window)

                with menu("Ticket"):
                    add_menu_item("New ticket", callback=self.create_ticket_window)
                    add_menu_item("Open ticket", callback=self.open_ticket_window)

                with menu("Settings"):
                    add_menu_item("Show style menu", callback=show_style_editor)

        with window("Load Game", autosize=True, on_close=self.verify_game):

            add_button("Create new game", callback=self.create_game_window)
            add_button("Load game", callback=self.open_game_window)

        start_dearpygui(primary_window="Bingo")


if __name__ == "__main__":
    app = App()
    app.show()
