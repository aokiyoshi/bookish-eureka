import asyncio
import PySimpleGUI as sg

from client import Client


class App:
    def __init__(self):
        self.layout = [
            [
                sg.Listbox(values=[f'client{i}' for i in range(10)], size=(20, 20)),
                sg.Output(size=(110, 20), font=('Helvetica 10'))
            ],

            [   
                sg.Button('ADD_CONT', button_color=(sg.YELLOWS[0], sg.GREENS[0])),
                sg.Multiline(size=(90, 5), enter_submits=True, key='-QUERY-', do_not_clear=True, pad=(0, 10)),
                sg.Button('SEND', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=True),
                sg.Button('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))
            ],
        ]

        self.window = sg.Window('Chat window', self.layout, font=(
            'Helvetica', ' 13'), default_button_element_size=(10, 2), use_default_focus=False, finalize=True)

        self.client = Client()

    async def ouput(self):
        await self.client.send_presence()
        while True:
            await self.client.get_new_messages()
            await asyncio.sleep(0.05)

    async def ui(self):
        while True:
            event, value = self.window.read(timeout=1000)
            if event in (sg.WIN_CLOSED, 'EXIT'):
                raise KeyboardInterrupt
                break
            if event == 'SEND':
                query = value['-QUERY-'].rstrip()
                try:
                    await self.client.send_message(f'{query}')
                except Exception as e:
                    print(e)
            await asyncio.sleep(0.001)


async def main():
    app = App()
    await app.client.init("InterfaceUser")
    await asyncio.wait([
        asyncio.create_task(app.ui()), 
        asyncio.create_task(app.ouput()),
    ])


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        print(e)
