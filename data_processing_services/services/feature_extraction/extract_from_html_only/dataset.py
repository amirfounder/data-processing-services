from __future__ import annotations

from typing import Dict

from bs4.element import Tag


class DataPoint:
    def __init__(self, dataset: DataSet, _id, tag: Tag):
        self.dataset = dataset
        self.id = _id
        self.tag = tag

    def load_features(self):
        self.path_to_root = [self]
        if (parent := self.tag.parent) in self.dataset.map:
            self.path_to_root.extend(self.dataset.map[parent].path_to_root)
        else:
            self.path_to_root.append(DataPoint(self.dataset, 0, self.tag.parent))

        self.path_to_root_with_ids = [x.id for x in self.path_to_root]
        self.path_to_root_with_tag_names = [x.tag.name for x in self.path_to_root]

    def get_features(self):
        return {
            'ids_path': self.path_to_root_with_ids,
            'tag_names_path': self.path_to_root_with_tag_names,
            'id': self.id,
            'tag_name': self.tag.name,
            'content': self.tag.contents,
        }


class DataSet:
    def __init__(self):
        self.next_id = 0
        self.map: Dict[Tag, DataPoint] = {}

    def record(self, tag: Tag):
        self.next_id += 1
        self.map[tag] = (point := DataPoint(self, self.next_id, tag))
        return point

    def as_features_table(self):
        return [x.get_features() for x in self.map.values()]

