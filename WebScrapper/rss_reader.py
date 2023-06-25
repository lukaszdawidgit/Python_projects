# You shouldn't change  name of function or their arguments
# but you can change content of the initial functions.
from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from abc import abstractmethod
import json as Json


class UnhandledException(Exception):
    pass


class Channel:
    def __init__(self, el: Element):
        self.title = getattr(el.find('title'), 'text', None)
        self.link = getattr(el.find('link'), 'text', None)
        self.description = getattr(el.find('description'), 'text', None)
        self.lastBuildDate = getattr(el.find('lastBuildDate'), 'text', None)
        self.pubDate = getattr(el.find('pubDate'), 'text', None)
        self.language = getattr(el.find('language'), 'text', None)
        self.category = getattr(el.find('category'), 'text', None)
        self.managingEditor = getattr(el.find('managingEditor'), 'text', None)

    def __str__(self):
        return f'Feed: {self.title}\nLink: {self.link}\n' \
               f'Description: {self.description}\n'


class Item(object):
    def __init__(self, item: Element):
        self.title = getattr(item.find('title'), 'text', None)
        self.author = getattr(item.find('author'), 'text', None)
        self.pubDate = getattr(item.find('pubDate'), 'text', None)
        self.link = getattr(item.find('link'), 'text', None)
        self.category = self.get_cat(item)
        self.description = getattr(item.find('description'), 'text', None)

    def get_cat(self, item: Element):
        categories = [el.text for el in item.findall('.//category')]
        return categories if categories else None


class FormatInterface:
    @abstractmethod
    def format(self, channel: Channel, items: List[Item]) -> List[str]:
        pass


class JsonForm(FormatInterface):
    def format(self, channel: Channel, items: List[Item]) -> List[str]:
        result = self._get_channel(channel)
        item_list = self._get_items(items)

        if len(items) > 0:
            result["items"] = item_list
        return [Json.dumps(result)]

    def _get_items(self, items: List[Item]) -> List[dict]:
        item_list = []
        for item in items:
            item_dict = {}
            for key, value in item.__dict__.items():
                if value is not None:
                    item_dict[key] = value
            item_list.append(item_dict)
        return item_list

    def _get_channel(self, channel: Channel) -> dict:
        result = {}
        for key, value in channel.__dict__.items():
            if value is not None:
                result[key] = value
        return result


class ConsoleForm(FormatInterface):
    _key_texts = {
        "pubDate": "Date"
    }
    _key_channel_texts = {"title": "Feed"}

    def format(self, channel: Channel, items: List[Item]) -> List[str]:
        return [self._get_channel_str(channel), *self._get_items(items)]

    def _get_channel_str(self, channel: Channel) -> str:
        result = ""
        for key, value in channel.__dict__.items():
            if value is not None:
                key_capitalized = self._key_channel_texts[key] if key in self._key_channel_texts else key.capitalize()
                result += f"{key_capitalized}: {value}\n"
        return result

    def _get_items(self, items: List[Item]) -> List[str]:
        result = []
        for item in items:
            item_str = ""
            for key, value in item.__dict__.items():
                if value is not None:
                    key_capitalized = self._key_texts[key] if key in self._key_texts else key.capitalize()
                    formatted_value = ",".join(value) if key == "category" else value
                    item_str_formatted = f"{key_capitalized}: {formatted_value}\n"
                    item_str += f"\n{item_str_formatted}\n" if key == "description" else item_str_formatted
            result.append(item_str)
        return result


def rss_parser(
        xml: str,
        limit: Optional[int] = None,
        json: bool = False,
) -> List[str]:
    """
    RSS parser.
        Which then can be printed to stdout or written to file as a separate lines.

    Examples:
        >>> xml = '<rss><channel><title>Some RSS Channel</title><link>https://some.rss.com</link><description>Some RSS Channel</description></channel></rss>'
        >>> rss_parser(xml)
        ["Feed: Some RSS Channel",
        "Link: https://some.rss.com"]
        >>> print("\\n".join(rss_parser(xmls)))
        Feed: Some RSS Channel
        Link: https://some.rss.com
    """
    formatter = JsonForm() if json else ConsoleForm()
    root = ET.fromstring(xml)
    channel = Channel(root.find('.//channel'))

    items = []
    item_list = root.findall(".//item")
    item_limit = limit if limit is not None and len(item_list) > limit > 0 else len(item_list)
    for item in item_list[0:item_limit]:
        items.append(Item(item))

    return formatter.format(channel, items)


def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)
    xml = requests.get(args.source).text
    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()
