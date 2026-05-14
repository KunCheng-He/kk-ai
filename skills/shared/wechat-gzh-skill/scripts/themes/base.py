from abc import ABC, abstractmethod
from typing import Dict


class BaseTheme(ABC):
    name: str = ""
    description: str = ""

    colors: Dict[str, str] = {}
    typography: Dict[str, str] = {}

    @abstractmethod
    def get_container_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_heading_style(self, level: int) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_paragraph_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_blockquote_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_code_block_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_inline_code_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_image_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_list_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_list_item_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_table_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_table_cell_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_table_header_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_hr_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_strong_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_em_style(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_link_style(self) -> Dict[str, str]:
        pass

    def wrap_content(self, html: str) -> str:
        container_style = self.get_container_style()
        style_str = "; ".join(f"{k}: {v}" for k, v in container_style.items())
        return f'<section style="{style_str}">{html}</section>'