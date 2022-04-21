from __future__ import annotations

from typing import Dict

from bs4.element import Tag, NavigableString


class DataPoint:
    def __init__(self, dataset: DataSet, _id, tag: Tag):
        self.dataset = dataset
        self.id = _id
        self._tag = tag
        self._tag['_id'] = _id

    def load_features(self):
        self.tag = self._tag.name
        self.id_path = [self._tag.attrs['_id'], *[x.attrs.get('_id', '0') for x in self._tag.parents]]
        self.tag_path = [
            self._tag.name, *[(x.name if x.name != '[document]' else 'document') for x in self._tag.parents]]
        self.text = self._tag.text
        self.node_only_texts = [str(child) for child in self._tag.contents if isinstance(child, NavigableString)]
        self.node_only_text = ''.join(self.node_only_texts)

    def load_feature_set_v1(self):
        self.feature_set_v1 = {
            'id': self.id,
            'id_path': self.id_path,
            'tag_path': self.tag_path,
            'tag': self.tag,
            'text': self.text,
            'node_only_texts': self.node_only_texts,
            'node_only_text': self.node_only_text
        }
        return self.feature_set_v1


class DataSet:
    def __init__(self):
        self.next_id = 0
        self.map: Dict[Tag, DataPoint] = {}

    def record(self, tag: Tag):
        self.next_id += 1
        self.map[tag] = (point := DataPoint(self, self.next_id, tag))
        return point

    def as_features_table(self):
        return [x.load_feature_set_v1() for x in self.map.values()]

