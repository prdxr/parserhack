import aiohttp


async def get_request(url: str, headers: dict = None) -> list[dict]:
    """
    Функция для выолнения GET-запросов к API
    :param url: URL для запроса
    :param headers: Заголовки для запроса
    :return: list[model]
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            data = await response.json(content_type="application/json")
            return data


async def post_request(url: str, data: dict, headers: dict = None) -> dict:
    """
    Функция для выполнения POST-запросов к API

    :param url: URL для запроса
    :param data: Данные для отправки в теле запроса
    :param headers: Заголовки для запроса
    :return: dict с данными ответа
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, headers=headers) as response:
            response_data = await response.json()
            return response_data

async def put_request(url: str, data: dict, headers: dict = None) -> dict:
    """
    Функция для выполнения PUT-запросов к API

    :param url: URL для запроса
    :param data: Данные для отправки в теле запроса
    :param headers: Заголовки для запроса
    :return: dict с данными ответа
    """
    async with aiohttp.ClientSession() as session:
        async with session.put(url=url, json=data, headers=headers) as response:
            response_data = await response.json()
            return response_data
