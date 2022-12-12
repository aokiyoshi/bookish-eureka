import asyncio
import PySimpleGUI as sg

from client import Client


class App:
    selected_contact = None
    messages = {}

    def __init__(self):
        self.layout = [
            [
                sg.Listbox(values=[], size=(
                    20, 20), key='contact_list'),
                sg.Output(size=(100, 25), font=('Helvetica 10'), key='output')
            ],

            [
                sg.Input(size=(100, 5), key='message',
                         do_not_clear=True, enable_events=True),
                sg.Button('SEND', visible=False, bind_return_key=True)
            ],
        ]

        self.window = sg.Window('Chat window', self.layout, font=(
            'Helvetica', ' 13'), default_button_element_size=(10, 5), use_default_focus=False, finalize=True, element_padding=0)

        self.client = Client()

    async def update_contacts(self):
        contact_list = await self.client.get_contact_list()
        self.window['contact_list'].update(contact_list)

    async def ui(self):
        self.window.TKroot.title(f'Chat: {self.client.username}')

        await self.client.send_presence()
        await self.update_contacts()

        while True:
            event, value = self.window.read(timeout=1000)

            self.selected_contact = value.get('contact_list', [])

            if event in (sg.WIN_CLOSED, 'EXIT'):
                raise KeyboardInterrupt

            if not self.selected_contact:
                self.selected_contact = ['Server']

            if event == 'SEND' and self.selected_contact:
                try:
                    # Get params
                    query = value['message'].rstrip()

                    if not query:
                        await self.update_contacts()
                        continue

                    # Trying to send message
                    await self.client.send_message(f'{query}', reciever=self.selected_contact[0])

                    if query.startswith('!add'):
                        await self.update_contacts()

                    if query.startswith('!login'):
                        await self.update_contacts()
                        self.window.TKroot.title(
                            f'Chat: {self.client.username}')

                except Exception as e:
                    raise Exception(f'Произошла ошибка {e=}')
                finally:
                    # Clear input
                    self.window['message']('')

            # await self.update_contacts()

            self.window['output']('')
            if self.selected_contact:
                await self.client.get_new_messages(self.selected_contact[0])

            await asyncio.sleep(1/144)


async def main():
    app = App()
    await app.client.init()
    await asyncio.wait([
        asyncio.create_task(app.ui()),
    ])
    app.client.close()


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        print(e)
