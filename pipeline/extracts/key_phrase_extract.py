import abc
import yaml
from pipeline.parsers.resource_parser import ResourceParser

class KeyPhraseExtract(metaclass=abc.ABCMeta):
    def __init__(self, yaml_path: str) -> None:
        with open(yaml_path) as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)

            for attr_name, attr_value in cfg['params'].items():
                setattr(self, attr_name, attr_value)

    @abc.abstractmethod
    def extract_key_phrases(self, resource_parser: ResourceParser) -> list:
        raise NotImplementedError